from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Doctor, TimeSlot, Token, TokenStatus
from app.schemas import (
    DoctorCreate, DoctorResponse,
    TimeSlotCreate, TimeSlotResponse,
    TokenRequest, TokenResponse, TokenUpdateStatus, TokenReallocation,
    SlotAnalytics, DoctorDayAnalytics, SystemStatus
)
from app.allocation_engine import TokenAllocationEngine

router = APIRouter()


# ==================== Doctor Endpoints ====================

@router.post("/doctors", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor(doctor: DoctorCreate, db: AsyncSession = Depends(get_db)):
    """Create a new doctor in the system."""
    db_doctor = Doctor(**doctor.model_dump())
    db.add(db_doctor)
    await db.flush()
    await db.refresh(db_doctor)
    return db_doctor


@router.get("/doctors", response_model=List[DoctorResponse])
async def list_doctors(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """List all doctors."""
    query = select(Doctor)
    if active_only:
        query = query.where(Doctor.is_active == True)
    
    result = await db.execute(query.order_by(Doctor.name))
    doctors = result.scalars().all()
    return doctors


@router.get("/doctors/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(doctor_id: int, db: AsyncSession = Depends(get_db)):
    """Get doctor details by ID."""
    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return doctor


# ==================== Time Slot Endpoints ====================

@router.post("/slots", response_model=TimeSlotResponse, status_code=status.HTTP_201_CREATED)
async def create_time_slot(slot: TimeSlotCreate, db: AsyncSession = Depends(get_db)):
    """Create a new time slot for a doctor."""
    # Verify doctor exists
    result = await db.execute(select(Doctor).where(Doctor.id == slot.doctor_id))
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check for overlapping slots
    result = await db.execute(
        select(TimeSlot).where(
            and_(
                TimeSlot.doctor_id == slot.doctor_id,
                TimeSlot.date == slot.date,
                TimeSlot.is_active == True,
                or_(
                    and_(
                        TimeSlot.start_time <= slot.start_time,
                        TimeSlot.end_time > slot.start_time
                    ),
                    and_(
                        TimeSlot.start_time < slot.end_time,
                        TimeSlot.end_time >= slot.end_time
                    )
                )
            )
        )
    )
    
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400, 
            detail="Overlapping slot exists for this doctor"
        )
    
    db_slot = TimeSlot(**slot.model_dump())
    db.add(db_slot)
    await db.flush()
    await db.refresh(db_slot)
    return db_slot


@router.get("/slots", response_model=List[TimeSlotResponse])
async def get_slots(
    doctor_id: Optional[int] = None,
    date: Optional[str] = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """List time slots with optional filters."""
    query = select(TimeSlot)
    
    conditions = []
    if doctor_id:
        conditions.append(TimeSlot.doctor_id == doctor_id)
    if date:
        conditions.append(TimeSlot.date == date)
    if active_only:
        conditions.append(TimeSlot.is_active == True)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(TimeSlot.date, TimeSlot.start_time)
    
    result = await db.execute(query)
    slots = result.scalars().all()
    return slots


@router.get("/slots/{slot_id}", response_model=TimeSlotResponse)
async def get_slot(slot_id: int, db: AsyncSession = Depends(get_db)):
    """Get time slot details by ID."""
    result = await db.execute(select(TimeSlot).where(TimeSlot.id == slot_id))
    slot = result.scalar_one_or_none()
    
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    return slot


# ==================== Token Endpoints ====================

@router.post("/tokens", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def allocate_token(
    token_request: TokenRequest,
    emergency: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Allocate a new token to a patient.
    
    - **emergency**: Force allocation even if slot is full (use carefully)
    """
    engine = TokenAllocationEngine(db)
    
    try:
        if emergency:
            token = await engine.handle_emergency_insertion(token_request, force=True)
        else:
            token = await engine.allocate_token(token_request)
        
        await db.commit()
        await db.refresh(token)
        return token
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tokens", response_model=List[TokenResponse])
async def get_tokens(
    doctor_id: Optional[int] = None,
    slot_id: Optional[int] = None,
    status_filter: Optional[TokenStatus] = None,
    date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List tokens with optional filters."""
    query = select(Token)
    
    conditions = []
    if doctor_id:
        conditions.append(Token.doctor_id == doctor_id)
    if slot_id:
        conditions.append(Token.slot_id == slot_id)
    if status_filter:
        conditions.append(Token.status == status_filter)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(Token.allocated_at.desc())
    
    result = await db.execute(query)
    tokens = result.scalars().all()
    return tokens


@router.get("/tokens/{token_id}", response_model=TokenResponse)
async def get_token(token_id: int, db: AsyncSession = Depends(get_db)):
    """Get token details by ID."""
    result = await db.execute(select(Token).where(Token.id == token_id))
    token = result.scalar_one_or_none()
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    return token


@router.get("/tokens/number/{token_number}", response_model=TokenResponse)
async def get_token_by_number(token_number: str, db: AsyncSession = Depends(get_db)):
    """Get token details by token number."""
    result = await db.execute(
        select(Token).where(Token.token_number == token_number)
    )
    token = result.scalar_one_or_none()
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    return token


@router.patch("/tokens/{token_id}/status", response_model=TokenResponse)
async def update_token_status(
    token_id: int,
    status_update: TokenUpdateStatus,
    db: AsyncSession = Depends(get_db)
):
    """Update token status (check-in, start consultation, complete, etc.)."""
    result = await db.execute(select(Token).where(Token.id == token_id))
    token = result.scalar_one_or_none()
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    # Update status and timestamps
    token.status = status_update.status  # type: ignore[assignment]

    if status_update.status == TokenStatus.CHECKED_IN:
        setattr(token, 'checked_in_at', datetime.utcnow())
    elif status_update.status == TokenStatus.CONSULTING:
        setattr(token, 'consultation_started_at', datetime.utcnow())
    elif status_update.status in [TokenStatus.COMPLETED, TokenStatus.CANCELLED, TokenStatus.NO_SHOW]:
        setattr(token, 'completed_at', datetime.utcnow())
    
    await db.commit()
    await db.refresh(token)
    return token


@router.post("/tokens/{token_id}/cancel", response_model=TokenResponse)
async def cancel_token(
    token_id: int,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Cancel a token and free up slot capacity."""
    engine = TokenAllocationEngine(db)
    
    try:
        token = await engine.cancel_token(token_id, reason)
        await db.commit()
        await db.refresh(token)
        return token
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tokens/{token_id}/reallocate", response_model=TokenResponse)
async def reallocate_token(
    token_id: int,
    reallocation: TokenReallocation,
    db: AsyncSession = Depends(get_db)
):
    """Reallocate token to a different slot (handle delays/changes)."""
    engine = TokenAllocationEngine(db)
    
    try:
        token = await engine.reallocate_token(
            token_id, 
            reallocation.new_slot_id, 
            reallocation.reason
        )
        await db.commit()
        await db.refresh(token)
        return token
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tokens/{token_id}/no-show", response_model=TokenResponse)
async def mark_no_show(token_id: int, db: AsyncSession = Depends(get_db)):
    """Mark patient as no-show and free capacity."""
    engine = TokenAllocationEngine(db)
    
    try:
        token = await engine.mark_no_show(token_id)
        await db.commit()
        await db.refresh(token)
        return token
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/slots/{slot_id}/queue", response_model=List[TokenResponse])
async def get_slot_queue(slot_id: int, db: AsyncSession = Depends(get_db)):
    """Get ordered queue for a slot based on priority."""
    engine = TokenAllocationEngine(db)
    
    try:
        tokens = await engine.get_slot_queue(slot_id)
        return tokens
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Analytics Endpoints ====================

@router.get("/analytics/slots/{slot_id}", response_model=SlotAnalytics)
async def get_slot_analytics(slot_id: int, db: AsyncSession = Depends(get_db)):
    """Get analytics for a specific slot."""
    # Get slot
    result = await db.execute(
        select(TimeSlot, Doctor)
        .join(Doctor)
        .where(TimeSlot.id == slot_id)
    )
    slot_data = result.one_or_none()
    
    if not slot_data:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    slot, doctor = slot_data
    
    # Get tokens by source
    result = await db.execute(
        select(Token.source, func.count(Token.id))
        .where(Token.slot_id == slot_id)
        .group_by(Token.source)
    )
    
    tokens_by_source = {source: count for source, count in result.all()}
    
    utilization = (slot.current_count / slot.max_capacity * 100) if slot.max_capacity > 0 else 0
    
    return SlotAnalytics(
        slot_id=slot.id,
        date=slot.date,
        start_time=slot.start_time,
        end_time=slot.end_time,
        doctor_name=doctor.name,
        total_capacity=slot.max_capacity,
        allocated_tokens=slot.current_count,
        available_capacity=slot.available_capacity,
        utilization_percentage=round(utilization, 2),
        tokens_by_source=tokens_by_source
    )


@router.get("/analytics/doctors/{doctor_id}/day/{date}", response_model=DoctorDayAnalytics)
async def get_doctor_day_analytics(
    doctor_id: int,
    date: str,
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a doctor's entire day."""
    # Get doctor
    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Get slots for the day
    result = await db.execute(
        select(func.count(TimeSlot.id), func.sum(TimeSlot.max_capacity))
        .where(and_(TimeSlot.doctor_id == doctor_id, TimeSlot.date == date))
    )
    total_slots, total_capacity = result.one()
    total_capacity = total_capacity or 0
    
    # Get token statistics
    result = await db.execute(
        select(Token.status, func.count(Token.id))
        .join(TimeSlot)
        .where(
            and_(
                Token.doctor_id == doctor_id,
                TimeSlot.date == date
            )
        )
        .group_by(Token.status)
    )
    
    status_counts = {status: count for status, count in result.all()}
    
    total_allocated = sum(status_counts.values())
    avg_utilization = (total_allocated / total_capacity * 100) if total_capacity > 0 else 0
    
    return DoctorDayAnalytics(
        doctor_id=int(doctor.id),  # type: ignore[arg-type]
        doctor_name=str(doctor.name),  # type: ignore[arg-type]
        date=date,
        total_slots=total_slots or 0,
        total_capacity=total_capacity,
        total_allocated=total_allocated,
        total_completed=status_counts.get(TokenStatus.COMPLETED, 0),
        total_cancelled=status_counts.get(TokenStatus.CANCELLED, 0),
        total_no_shows=status_counts.get(TokenStatus.NO_SHOW, 0),
        average_utilization=round(avg_utilization, 2)
    )


@router.get("/analytics/system/status", response_model=SystemStatus)
async def get_system_status(db: AsyncSession = Depends(get_db)):
    """Get overall system status and statistics."""
    from sqlalchemy import or_
    
    # Total and active doctors
    result = await db.execute(select(func.count(Doctor.id)).where(Doctor.is_active == True))
    active_doctors = result.scalar()
    
    result = await db.execute(select(func.count(Doctor.id)))
    total_doctors = result.scalar()
    
    # Today's date
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Slots today
    result = await db.execute(
        select(func.count(TimeSlot.id))
        .where(TimeSlot.date == today)
    )
    total_slots_today = result.scalar()
    
    # Tokens today
    result = await db.execute(
        select(func.count(Token.id))
        .join(TimeSlot)
        .where(TimeSlot.date == today)
    )
    total_tokens_today = result.scalar()
    
    # Tokens by status
    result = await db.execute(
        select(Token.status, func.count(Token.id))
        .join(TimeSlot)
        .where(TimeSlot.date == today)
        .group_by(Token.status)
    )
    tokens_by_status = {str(status): count for status, count in result.all()}
    
    # Tokens by source
    result = await db.execute(
        select(Token.source, func.count(Token.id))
        .join(TimeSlot)
        .where(TimeSlot.date == today)
        .group_by(Token.source)
    )
    tokens_by_source = {str(source): count for source, count in result.all()}
    
    return SystemStatus(
        total_doctors=total_doctors or 0,
        active_doctors=active_doctors or 0,
        total_slots_today=total_slots_today or 0,
        total_tokens_today=total_tokens_today or 0,
        tokens_by_status=tokens_by_status,
        tokens_by_source=tokens_by_source
    )
