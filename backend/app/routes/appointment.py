from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse
)
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/appointments", tags=["Doctor Appointments"])

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Books a consultation appointment with validation:
    - Date cannot be in the past.
    - Doctor must exist and be active.
    - Double booking / conflicting appointments on the same doctor/date/time are prevented.
    """
    if data.appointment_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book an appointment for a past date."
        )

    doctor = db.query(Doctor).filter(Doctor.id == data.doctor_id, Doctor.active == True).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Selected doctor does not exist or is unavailable."
        )

    # Check for conflicting appointments on the same doctor, date, and time slot
    conflict = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == data.doctor_id,
            Appointment.appointment_date == data.appointment_date,
            Appointment.appointment_time == data.appointment_time.strip(),
            Appointment.status != "Cancelled"
        )
        .first()
    )

    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Dr. {doctor.name} is already booked for {data.appointment_date} at {data.appointment_time}. Please select another time slot."
        )

    appointment = Appointment(
        user_id=current_user.id,
        doctor_id=data.doctor_id,
        appointment_date=data.appointment_date,
        appointment_time=data.appointment_time.strip(),
        reason=data.reason.strip(),
        status="Scheduled",
        notes=data.notes.strip() if data.notes else None
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment

@router.get("", response_model=List[AppointmentResponse])
def get_user_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns all appointments booked by the authenticated patient."""
    return (
        db.query(Appointment)
        .filter(Appointment.user_id == current_user.id)
        .order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc())
        .all()
    )

@router.get("/upcoming", response_model=Optional[AppointmentResponse])
def get_next_upcoming_appointment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the patient's next upcoming scheduled appointment for the dashboard."""
    today = date.today()
    return (
        db.query(Appointment)
        .filter(
            Appointment.user_id == current_user.id,
            Appointment.status == "Scheduled",
            Appointment.appointment_date >= today
        )
        .order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc())
        .first()
    )

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment_by_id(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns appointment details strictly for the owner."""
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id, Appointment.user_id == current_user.id)
        .first()
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found or access denied"
        )
    return appointment

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates appointment status or details for the owner."""
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id, Appointment.user_id == current_user.id)
        .first()
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found or access denied"
        )

    if data.appointment_date:
        if data.appointment_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment date cannot be in the past."
            )
        appointment.appointment_date = data.appointment_date

    if data.appointment_time:
        appointment.appointment_time = data.appointment_time.strip()
    if data.reason:
        appointment.reason = data.reason.strip()
    if data.status:
        valid_statuses = ["Scheduled", "Completed", "Cancelled"]
        if data.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        appointment.status = data.status
    if data.notes is not None:
        appointment.notes = data.notes.strip() if data.notes else None

    db.commit()
    db.refresh(appointment)
    return appointment

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancels/Deletes an appointment owned by the patient."""
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id, Appointment.user_id == current_user.id)
        .first()
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found or access denied"
        )

    # Soft cancel or delete
    appointment.status = "Cancelled"
    db.commit()
    return None
