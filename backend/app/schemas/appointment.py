from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator

from app.schemas.doctor import DoctorResponse

class AppointmentCreate(BaseModel):
    doctor_id: int = Field(..., description="ID of the doctor")
    appointment_date: date = Field(..., description="Desired appointment date")
    appointment_time: str = Field(..., min_length=1, max_length=50, description="Selected time slot")
    reason: str = Field(..., min_length=3, description="Reason for consultation")
    notes: Optional[str] = Field(None, description="Optional patient notes")

    @field_validator("appointment_date")
    @classmethod
    def validate_date_not_in_past(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Appointment date cannot be in the past.")
        return v

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[str] = Field(None, min_length=1, max_length=50)
    reason: Optional[str] = Field(None, min_length=3)
    status: Optional[str] = Field(None, description="Scheduled, Completed, or Cancelled")
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    user_id: int
    doctor_id: int
    doctor: DoctorResponse
    appointment_date: date
    appointment_time: str
    reason: str
    status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
