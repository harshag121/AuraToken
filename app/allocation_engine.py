from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from app.models import Token, TimeSlot, Doctor, TokenSource, TokenStatus
from app.schemas import TokenRequest
from app.config import settings


class TokenAllocationEngine:
    """
    Core token allocation algorithm with dynamic capacity management.
    
    Key Features:
    - Enforces per-slot hard limits
    - Priority-based allocation (Priority > Follow-up > Online > Walk-in)
    - Dynamic reallocation support
    - Handles cancellations, no-shows, and emergency insertions
    """
    
    # Priority weights for different token sources
    PRIORITY_WEIGHTS = {
        TokenSource.PRIORITY: 10,
        TokenSource.FOLLOW_UP: 5,
        TokenSource.ONLINE: 3,
        TokenSource.WALK_IN: 1,
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def allocate_token(self, request: TokenRequest) -> Token:
        """
        Allocate a token with intelligent priority management.
        
        Algorithm:
        1. Validate slot availability and capacity
        2. Calculate priority score based on source
        3. Determine sequence number within slot
        4. Create and persist token
        5. Update slot capacity
        
        Raises:
            ValueError: If slot is full or invalid
        """
        # Fetch slot with doctor information
        slot = await self._get_slot_with_validation(request.slot_id)
        
        # Check hard capacity limit
        if slot.current_count >= slot.max_capacity:  # type: ignore[operator]
            # Attempt to find alternative slot
            alternative = await self._find_alternative_slot(
                request.doctor_id, 
                slot.date  # type: ignore[arg-type]
            )
            if alternative:
                raise ValueError(
                    f"Slot {slot.id} is full. Alternative slot {alternative.id} "
                    f"({alternative.start_time}-{alternative.end_time}) available."
                )
            raise ValueError(f"Slot {slot.id} is at maximum capacity")
        
        # Calculate priority score
        priority_score = self._calculate_priority_score(
            request.source, 
            slot.current_count  # type: ignore[arg-type]
        )
        
        # Determine sequence number (position in queue)
        sequence_number = await self._get_next_sequence_number(slot.id)  # type: ignore[arg-type]
        
        # Generate unique token number
        token_number = await self._generate_token_number(
            slot.doctor_id,  # type: ignore[arg-type]
            slot.date  # type: ignore[arg-type]
        )
        
        # Create token
        token = Token(
            token_number=token_number,
            patient_name=request.patient_name,
            patient_phone=request.patient_phone,
            doctor_id=request.doctor_id,
            slot_id=request.slot_id,
            source=request.source,
            status=TokenStatus.ALLOCATED,
            priority_score=priority_score,
            sequence_number=sequence_number,
            notes=request.notes
        )
        
        self.db.add(token)
        
        # Update slot capacity
        slot.current_count += 1  # type: ignore[operator,assignment]
        
        await self.db.flush()
        await self.db.refresh(token)
        
        return token
    
    async def cancel_token(self, token_id: int, reason: Optional[str] = None) -> Token:
        """
        Cancel a token and free up slot capacity.
        
        Process:
        1. Validate token exists and is cancellable
        2. Update token status to cancelled
        3. Decrement slot capacity
        4. Resequence remaining tokens if needed
        """
        token = await self._get_token(token_id)
        
        if token.status in [TokenStatus.COMPLETED, TokenStatus.CANCELLED]:
            raise ValueError(f"Cannot cancel token in {token.status} status")
        
        # Update token status
        token.status = TokenStatus.CANCELLED  # type: ignore[assignment]
        token.completed_at = datetime.utcnow()  # type: ignore[assignment]
        if reason:
            token.notes = f"{token.notes or ''}\nCancellation: {reason}".strip()  # type: ignore[assignment]
        
        # Free up slot capacity
        slot = await self._get_slot_with_validation(token.slot_id)  # type: ignore[arg-type]
        slot.current_count = max(0, slot.current_count - 1)  # type: ignore[operator,assignment,arg-type]
        
        await self.db.flush()
        
        # Optionally resequence remaining tokens
        await self._resequence_slot_tokens(token.slot_id)  # type: ignore[arg-type]
        
        return token
    
    async def reallocate_token(
        self, 
        token_id: int, 
        new_slot_id: int, 
        reason: Optional[str] = None
    ) -> Token:
        """
        Reallocate token to a different slot (handle delays/changes).
        
        Process:
        1. Validate current token and new slot
        2. Check new slot capacity
        3. Update token's slot assignment
        4. Adjust capacity counts for both slots
        5. Recalculate sequence number
        """
        token = await self._get_token(token_id)
        old_slot = await self._get_slot_with_validation(token.slot_id)  # type: ignore[arg-type]
        new_slot = await self._get_slot_with_validation(new_slot_id)
        
        # Verify same doctor
        if token.doctor_id != new_slot.doctor_id:  # type: ignore[operator]
            raise ValueError("Cannot reallocate token to different doctor's slot")
        
        # Check new slot capacity
        if new_slot.current_count >= new_slot.max_capacity:  # type: ignore[operator]
            raise ValueError(f"Target slot {new_slot_id} is at maximum capacity")
        
        # Update capacities
        old_slot.current_count = max(0, old_slot.current_count - 1)  # type: ignore[operator,assignment,arg-type]
        new_slot.current_count += 1  # type: ignore[operator,assignment]
        
        # Update token
        token.slot_id = new_slot_id  # type: ignore[assignment]
        token.sequence_number = await self._get_next_sequence_number(new_slot_id)  # type: ignore[assignment]
        
        if reason:
            token.notes = f"{token.notes or ''}\nReallocation: {reason}".strip()  # type: ignore[assignment]
        
        await self.db.flush()
        
        # Resequence both slots
        await self._resequence_slot_tokens(old_slot.id)  # type: ignore[arg-type]
        await self._resequence_slot_tokens(new_slot.id)  # type: ignore[arg-type]
        
        return token
    
    async def handle_emergency_insertion(
        self, 
        request: TokenRequest, 
        force: bool = False
    ) -> Token:
        """
        Handle emergency patient insertion.
        
        Strategy:
        - If force=True, allow exceeding capacity by 1
        - Otherwise, attempt reallocation of lower priority tokens
        - Insert with highest priority score
        """
        slot = await self._get_slot_with_validation(request.slot_id)
        
        if slot.current_count >= slot.max_capacity and not force:  # type: ignore[operator]
            # Try to reallocate lowest priority walk-in patient
            reallocated = await self._reallocate_lowest_priority(slot.id)  # type: ignore[arg-type]
            if not reallocated:
                if force:
                    pass  # Proceed with forced insertion
                else:
                    raise ValueError(
                        "Cannot insert emergency patient: slot full and no reallocation possible"
                    )
        
        # Create emergency token with maximum priority
        request.source = TokenSource.PRIORITY
        token = await self.allocate_token(request)
        token.notes = f"{token.notes or ''}\nEMERGENCY INSERTION".strip()  # type: ignore[assignment]
        
        await self.db.flush()
        return token
    
    async def mark_no_show(self, token_id: int) -> Token:
        """Mark patient as no-show and free capacity."""
        token = await self._get_token(token_id)
        
        if token.status != TokenStatus.ALLOCATED:  # type: ignore[operator]
            raise ValueError(f"Cannot mark token as no-show in {token.status} status")
        
        token.status = TokenStatus.NO_SHOW  # type: ignore[assignment]
        token.completed_at = datetime.utcnow()  # type: ignore[assignment]
        
        # Free up slot capacity
        slot = await self._get_slot_with_validation(token.slot_id)  # type: ignore[arg-type]
        slot.current_count = max(0, slot.current_count - 1)  # type: ignore[operator,assignment,arg-type]
        
        await self.db.flush()
        return token
    
    async def get_slot_queue(self, slot_id: int) -> List[Token]:
        """
        Get ordered queue for a slot based on priority and sequence.
        
        Ordering:
        1. Priority score (descending)
        2. Sequence number (ascending)
        3. Allocation time (ascending)
        """
        result = await self.db.execute(
            select(Token)
            .where(
                and_(
                    Token.slot_id == slot_id,
                    Token.status.in_([
                        TokenStatus.ALLOCATED,
                        TokenStatus.CHECKED_IN,
                        TokenStatus.CONSULTING
                    ])
                )
            )
            .order_by(
                Token.priority_score.desc(),
                Token.sequence_number.asc(),
                Token.allocated_at.asc()
            )
        )
        return list(result.scalars().all())
    
    # Private helper methods
    
    async def _get_slot_with_validation(self, slot_id: int) -> TimeSlot:
        """Fetch and validate slot."""
        result = await self.db.execute(
            select(TimeSlot)
            .where(TimeSlot.id == slot_id)
            .options(selectinload(TimeSlot.doctor))
        )
        slot = result.scalar_one_or_none()
        
        if not slot:
            raise ValueError(f"Slot {slot_id} not found")
        
        if not slot.is_active:  # type: ignore[operator]
            raise ValueError(f"Slot {slot_id} is not active")
        
        return slot
    
    async def _get_token(self, token_id: int) -> Token:
        """Fetch token by ID."""
        result = await self.db.execute(
            select(Token).where(Token.id == token_id)
        )
        token = result.scalar_one_or_none()
        
        if not token:
            raise ValueError(f"Token {token_id} not found")
        
        return token
    
    def _calculate_priority_score(
        self, 
        source: TokenSource, 
        current_count: int
    ) -> int:
        """Calculate priority score based on source and timing."""
        base_score = self.PRIORITY_WEIGHTS.get(source, 1)
        # Early arrivals get slight bonus
        timing_bonus = max(0, 10 - current_count)
        return base_score * 10 + timing_bonus
    
    async def _get_next_sequence_number(self, slot_id: int) -> int:
        """Get next sequence number for slot."""
        result = await self.db.execute(
            select(func.max(Token.sequence_number))
            .where(Token.slot_id == slot_id)
        )
        max_seq = result.scalar()
        return (max_seq or 0) + 1
    
    async def _generate_token_number(self, doctor_id: int, date: str) -> str:
        """Generate unique token number: DOC{doctor_id}-{date}-{seq}."""
        result = await self.db.execute(
            select(func.count(Token.id))
            .where(
                and_(
                    Token.doctor_id == doctor_id,
                    Token.allocated_at >= datetime.strptime(date, "%Y-%m-%d")
                )
            )
        )
        count = result.scalar() or 0
        date_short = date.replace("-", "")
        return f"DOC{doctor_id}-{date_short}-{count + 1:04d}"
    
    async def _find_alternative_slot(
        self, 
        doctor_id: int, 
        date: str
    ) -> Optional[TimeSlot]:
        """Find alternative available slot for same doctor and date."""
        result = await self.db.execute(
            select(TimeSlot)
            .where(
                and_(
                    TimeSlot.doctor_id == doctor_id,
                    TimeSlot.date == date,
                    TimeSlot.is_active == True,
                    TimeSlot.current_count < TimeSlot.max_capacity
                )
            )
            .order_by(TimeSlot.start_time)
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def _resequence_slot_tokens(self, slot_id: int):
        """Resequence tokens in a slot after cancellation/reallocation."""
        tokens = await self.get_slot_queue(slot_id)
        
        for idx, token in enumerate(tokens, start=1):
            token.sequence_number = idx  # type: ignore[assignment]
        
        await self.db.commit()
    
    async def _reallocate_lowest_priority(self, slot_id: int) -> bool:
        """
        Try to reallocate lowest priority walk-in patient to another slot.
        Returns True if successful, False otherwise.
        """
        # Find lowest priority walk-in token
        result = await self.db.execute(
            select(Token)
            .where(
                and_(
                    Token.slot_id == slot_id,
                    Token.source == TokenSource.WALK_IN,
                    Token.status == TokenStatus.ALLOCATED
                )
            )
            .order_by(Token.priority_score.asc(), Token.allocated_at.desc())
            .limit(1)
        )
        token = result.scalar_one_or_none()
        
        if not token:
            return False
        
        # Find alternative slot
        slot = await self._get_slot_with_validation(slot_id)
        alternative = await self._find_alternative_slot(token.doctor_id, slot.date)  # type: ignore[arg-type]
        
        if alternative:
            await self.reallocate_token(
                token.id,  # type: ignore[arg-type]
                alternative.id,  # type: ignore[arg-type]
                "Auto-reallocation for emergency insertion"
            )
            return True
        
        return False
