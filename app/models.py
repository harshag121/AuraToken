from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class TokenSource(str, enum.Enum):
    """Token source types with priority ordering."""
    PRIORITY = "priority"  # Paid priority patients (highest)
    FOLLOW_UP = "follow_up"  # Follow-up patients
    ONLINE = "online"  # Online booking
    WALK_IN = "walk_in"  # Walk-in (OPD desk)


class TokenStatus(str, enum.Enum):
    """Token lifecycle states."""
    ALLOCATED = "allocated"
    CHECKED_IN = "checked_in"
    CONSULTING = "consulting"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Doctor(Base):
    """Doctor entity with slot configuration."""
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    slots = relationship("TimeSlot", back_populates="doctor", cascade="all, delete-orphan")
    tokens = relationship("Token", back_populates="doctor")


class TimeSlot(Base):
    """Time slot with capacity management."""
    __tablename__ = "time_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    date = Column(String, nullable=False)  # Format: YYYY-MM-DD
    start_time = Column(String, nullable=False)  # Format: HH:MM
    end_time = Column(String, nullable=False)  # Format: HH:MM
    max_capacity = Column(Integer, nullable=False)
    current_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    doctor = relationship("Doctor", back_populates="slots")
    tokens = relationship("Token", back_populates="slot")
    
    @property
    def available_capacity(self):
        """Calculate remaining capacity."""
        return max(0, self.max_capacity - self.current_count)
    
    @property
    def is_full(self):
        """Check if slot is at capacity."""
        return self.current_count >= self.max_capacity


class Token(Base):
    """Token entity with allocation details."""
    __tablename__ = "tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token_number = Column(String, unique=True, nullable=False, index=True)
    patient_name = Column(String, nullable=False)
    patient_phone = Column(String, nullable=False)
    
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=False)
    
    source = Column(SQLEnum(TokenSource), nullable=False)
    status = Column(SQLEnum(TokenStatus), default=TokenStatus.ALLOCATED)
    
    priority_score = Column(Integer, default=0)
    sequence_number = Column(Integer, nullable=False)
    
    allocated_at = Column(DateTime, default=datetime.utcnow)
    checked_in_at = Column(DateTime, nullable=True)
    consultation_started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    notes = Column(String, nullable=True)
    
    # Relationships
    doctor = relationship("Doctor", back_populates="tokens")
    slot = relationship("TimeSlot", back_populates="tokens")
