from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class DoctorResponse(BaseModel):
    id: int
    name: str
    specialization: str
    qualification: str
    clinic_hospital: str
    phone: str
    email: str
    available_days: str
    available_times: str
    active: bool

    class Config:
        from_attributes = True
