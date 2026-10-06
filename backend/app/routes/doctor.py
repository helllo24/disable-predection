from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorResponse

router = APIRouter(prefix="/api/doctors", tags=["Doctors Directory"])

@router.get("", response_model=List[DoctorResponse])
def get_doctors(
    specialization: Optional[str] = Query(None, description="Filter by doctor specialization"),
    db: Session = Depends(get_db)
):
    """Returns directory of active sample/demo doctors."""
    query = db.query(Doctor).filter(Doctor.active == True)
    if specialization and specialization.strip():
        query = query.filter(Doctor.specialization.iloclike(f"%{specialization.strip()}%"))
    return query.all()

@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor_by_id(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """Returns doctor details by ID."""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id, Doctor.active == True).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    return doctor
