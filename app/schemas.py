from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models import TokenSource, TokenStatus


# Doctor Schemas
class DoctorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    specialization: str = Field(..., min_length=1, max_length=100)


class DoctorCreate(DoctorBase):
    pass


class DoctorResponse(DoctorBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Time Slot Schemas
class TimeSlotBase(BaseModel):
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    start_time: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    end_time: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    max_capacity: int = Field(..., ge=1, le=100)


class TimeSlotCreate(TimeSlotBase):
    doctor_id: int


class TimeSlotResponse(TimeSlotBase):
    id: int
    doctor_id: int
    current_count: int
    is_active: bool
    available_capacity: int
    is_full: bool
    
    class Config:
        from_attributes = True


# Token Schemas
class TokenRequest(BaseModel):
    patient_name: str = Field(..., min_length=1, max_length=100)
    patient_phone: str = Field(..., pattern=r'^\+?[\d\s-]{10,15}$')
    doctor_id: int
    slot_id: int
    source: TokenSource
    notes: Optional[str] = None


class TokenResponse(BaseModel):
    id: int
    token_number: str
    patient_name: str
    patient_phone: str
    doctor_id: int
    slot_id: int
    source: TokenSource
    status: TokenStatus
    priority_score: int
    sequence_number: int
    allocated_at: datetime
    checked_in_at: Optional[datetime]
    consultation_started_at: Optional[datetime]
    completed_at: Optional[datetime]
    notes: Optional[str]
    
    class Config:
        from_attributes = True


class TokenUpdateStatus(BaseModel):
    status: TokenStatus


class TokenReallocation(BaseModel):
    new_slot_id: int
    reason: Optional[str] = None


# Analytics Schemas
class SlotAnalytics(BaseModel):
    slot_id: int
    date: str
    start_time: str
    end_time: str
    doctor_name: str
    total_capacity: int
    allocated_tokens: int
    available_capacity: int
    utilization_percentage: float
    tokens_by_source: dict


class DoctorDayAnalytics(BaseModel):
    doctor_id: int
    doctor_name: str
    date: str
    total_slots: int
    total_capacity: int
    total_allocated: int
    total_completed: int
    total_cancelled: int
    total_no_shows: int
    average_utilization: float


class SystemStatus(BaseModel):
    total_doctors: int
    active_doctors: int
    total_slots_today: int
    total_tokens_today: int
    tokens_by_status: dict
    tokens_by_source: dict
