from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator

class MedicineReminderCreate(BaseModel):
    medicine_name: str = Field(..., min_length=1, max_length=255, description="Name of the prescribed medicine")
    dosage: str = Field(..., min_length=1, max_length=100, description="Dosage (e.g., 500mg, 1 tablet)")
    frequency: str = Field(..., min_length=1, max_length=100, description="Frequency (e.g., Daily, Twice Daily)")
    start_date: date = Field(..., description="Start date for taking medication")
    end_date: Optional[date] = Field(None, description="End date for taking medication")
    reminder_time: str = Field(..., min_length=1, max_length=50, description="Reminder time (e.g., 08:00 AM)")
    notes: Optional[str] = Field(None, description="Optional prescription instructions or notes")
    active: bool = Field(True, description="Whether the reminder is currently active")

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: Optional[date], values) -> Optional[date]:
        if v and "start_date" in values.data and v < values.data["start_date"]:
            raise ValueError("End date cannot be earlier than start date")
        return v

class MedicineReminderUpdate(BaseModel):
    medicine_name: Optional[str] = Field(None, min_length=1, max_length=255)
    dosage: Optional[str] = Field(None, min_length=1, max_length=100)
    frequency: Optional[str] = Field(None, min_length=1, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reminder_time: Optional[str] = Field(None, min_length=1, max_length=50)
    notes: Optional[str] = None
    active: Optional[bool] = None

class MedicineReminderResponse(BaseModel):
    id: int
    medicine_name: str
    dosage: str
    frequency: str
    start_date: date
    end_date: Optional[date] = None
    reminder_time: str
    notes: Optional[str] = None
    active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
