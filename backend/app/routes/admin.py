from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.database.connection import get_db
from app.models.user import User
from app.models.bmi import BMIRecord
from app.models.diabetes import DiabetesPrediction
from app.models.disease_prediction import DiseasePrediction
from app.models.medicine import MedicineReminder
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.services.auth_service import get_current_admin_user

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])

@router.get("/dashboard")
def get_admin_dashboard_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Returns real application statistics across all system modules.
    Only accessible by users with ADMIN role.
    """
    total_patients = db.query(User).filter(User.role == "PATIENT").count()
    total_diabetes_preds = db.query(DiabetesPrediction).count()
    total_disease_preds = db.query(DiseasePrediction).count()
    total_bmi_recs = db.query(BMIRecord).count()
    total_appts = db.query(Appointment).count()
    active_meds = db.query(MedicineReminder).filter(MedicineReminder.active == True).count()

    return {
        "total_patients": total_patients,
        "total_diabetes_predictions": total_diabetes_preds,
        "total_disease_predictions": total_disease_preds,
        "total_bmi_records": total_bmi_recs,
        "total_appointments": total_appts,
        "active_medicine_reminders": active_meds
    }

@router.get("/patients")
def get_all_patients(
    search: Optional[str] = Query(None, description="Search by name or email"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Returns directory of registered patients.
    Never exposes password_hash or unneeded sensitive credentials.
    """
    query = db.query(User).filter(User.role == "PATIENT")

    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query = query.filter(
            (User.full_name.ilike(term)) | (User.email.ilike(term))
        )

    patients = query.order_by(User.id.desc()).all()

    out = []
    for p in patients:
        out.append({
            "id": p.id,
            "full_name": p.full_name,
            "email": p.email,
            "phone": p.phone,
            "age": p.age,
            "gender": p.gender,
            "height": p.height,
            "weight": p.weight,
            "blood_group": p.blood_group,
            "role": p.role,
            "is_active": p.is_active,
            "created_at": p.created_at
        })
    return out

@router.put("/patients/{patient_id}/toggle-status")
def toggle_patient_active_status(
    patient_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Toggles active/inactive status of a patient account."""
    patient = db.query(User).filter(User.id == patient_id, User.role == "PATIENT").first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient account not found."
        )

    patient.is_active = not patient.is_active
    db.commit()
    db.refresh(patient)

    return {
        "id": patient.id,
        "full_name": patient.full_name,
        "email": patient.email,
        "is_active": patient.is_active,
        "message": f"Account for {patient.full_name} is now {'Active' if patient.is_active else 'Deactivated'}."
    }

@router.get("/predictions")
def get_prediction_statistics(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Returns prediction counts and recent prediction logs across all patients.
    """
    diab_list = (
        db.query(DiabetesPrediction)
        .options(joinedload(DiabetesPrediction.user))
        .order_by(DiabetesPrediction.id.desc())
        .limit(10)
        .all()
    )

    dis_list = (
        db.query(DiseasePrediction)
        .options(joinedload(DiseasePrediction.user))
        .order_by(DiseasePrediction.id.desc())
        .limit(10)
        .all()
    )

    recent_diab = []
    for d in diab_list:
        recent_diab.append({
            "id": d.id,
            "patient_name": d.user.full_name if d.user else "Unknown",
            "patient_email": d.user.email if d.user else "Unknown",
            "risk": d.risk,
            "probability": d.probability,
            "glucose": d.glucose,
            "bmi": d.bmi,
            "created_at": d.created_at
        })

    recent_dis = []
    for s in dis_list:
        recent_dis.append({
            "id": s.id,
            "patient_name": s.user.full_name if s.user else "Unknown",
            "patient_email": s.user.email if s.user else "Unknown",
            "predicted_disease": s.predicted_disease,
            "probability": s.probability,
            "model": s.model_name,
            "created_at": s.created_at
        })

    return {
        "total_diabetes_predictions": db.query(DiabetesPrediction).count(),
        "total_disease_predictions": db.query(DiseasePrediction).count(),
        "recent_diabetes_predictions": recent_diab,
        "recent_disease_predictions": recent_dis
    }

@router.get("/appointments")
def get_all_system_appointments(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Returns all appointments scheduled across the system.
    Only accessible by users with ADMIN role.
    """
    appts = (
        db.query(Appointment)
        .options(joinedload(Appointment.user), joinedload(Appointment.doctor))
        .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())
        .all()
    )

    out = []
    for a in appts:
        out.append({
            "id": a.id,
            "patient_name": a.user.full_name if a.user else f"Patient #{a.user_id}",
            "patient_email": a.user.email if a.user else "-",
            "doctor_name": a.doctor.name if a.doctor else f"Doctor #{a.doctor_id}",
            "specialization": a.doctor.specialization if a.doctor else "-",
            "clinic_hospital": a.doctor.clinic_hospital if a.doctor else "-",
            "appointment_date": a.appointment_date,
            "appointment_time": a.appointment_time,
            "reason": a.reason,
            "status": a.status,
            "created_at": a.created_at
        })
    return out
