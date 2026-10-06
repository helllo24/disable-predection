from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.medicine import MedicineReminder
from app.schemas.medicine import (
    MedicineReminderCreate,
    MedicineReminderUpdate,
    MedicineReminderResponse
)
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/medicines", tags=["Medication Reminders"])

@router.post("", response_model=MedicineReminderResponse, status_code=status.HTTP_201_CREATED)
def create_medicine_reminder(
    data: MedicineReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a new patient-configured medication reminder."""
    reminder = MedicineReminder(
        user_id=current_user.id,
        medicine_name=data.medicine_name.strip(),
        dosage=data.dosage.strip(),
        frequency=data.frequency.strip(),
        start_date=data.start_date,
        end_date=data.end_date,
        reminder_time=data.reminder_time.strip(),
        notes=data.notes.strip() if data.notes else None,
        active=data.active
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder

@router.get("", response_model=List[MedicineReminderResponse])
def get_user_medicine_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns all medicine reminders configured by the authenticated patient."""
    return (
        db.query(MedicineReminder)
        .filter(MedicineReminder.user_id == current_user.id)
        .order_by(MedicineReminder.id.desc())
        .all()
    )

@router.get("/today", response_model=List[MedicineReminderResponse])
def get_today_medicine_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns active medicine reminders scheduled for today's date."""
    today = date.today()
    reminders = (
        db.query(MedicineReminder)
        .filter(
            MedicineReminder.user_id == current_user.id,
            MedicineReminder.active == True,
            MedicineReminder.start_date <= today
        )
        .all()
    )

    # Filter out ended prescriptions
    valid_today = [
        r for r in reminders
        if r.end_date is None or r.end_date >= today
    ]
    return valid_today

@router.get("/{reminder_id}", response_model=MedicineReminderResponse)
def get_medicine_reminder_by_id(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns a specific medicine reminder by ID strictly for the owner."""
    reminder = (
        db.query(MedicineReminder)
        .filter(MedicineReminder.id == reminder_id, MedicineReminder.user_id == current_user.id)
        .first()
    )

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine reminder not found or access denied"
        )
    return reminder

@router.put("/{reminder_id}", response_model=MedicineReminderResponse)
def update_medicine_reminder(
    reminder_id: int,
    data: MedicineReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates an existing medicine reminder for the owner."""
    reminder = (
        db.query(MedicineReminder)
        .filter(MedicineReminder.id == reminder_id, MedicineReminder.user_id == current_user.id)
        .first()
    )

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine reminder not found or access denied"
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if isinstance(value, str):
                setattr(reminder, field, value.strip())
            else:
                setattr(reminder, field, value)

    db.commit()
    db.refresh(reminder)
    return reminder

@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medicine_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a medicine reminder owned by the patient."""
    reminder = (
        db.query(MedicineReminder)
        .filter(MedicineReminder.id == reminder_id, MedicineReminder.user_id == current_user.id)
        .first()
    )

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine reminder not found or access denied"
        )

    db.delete(reminder)
    db.commit()
    return None
