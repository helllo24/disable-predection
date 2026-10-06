from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.bmi import BMICalculateRequest, BMIResponse
from app.services.auth_service import get_current_user
from app.services.bmi_service import compute_and_save_bmi, get_user_bmi_history, get_user_latest_bmi

router = APIRouter(prefix="/api/bmi", tags=["BMI Calculator"])

@router.post("/calculate", response_model=BMIResponse, status_code=status.HTTP_201_CREATED)
def calculate_bmi(
    data: BMICalculateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculates BMI from height and weight, categorizes it, and saves calculation history for patient."""
    record = compute_and_save_bmi(db, current_user, data)
    return {
        "id": record.id,
        "bmi": record.bmi_value,
        "category": record.bmi_category,
        "height": record.height,
        "height_unit": record.height_unit,
        "weight": record.weight,
        "weight_unit": record.weight_unit,
        "height_m": record.height_m,
        "weight_kg": record.weight_kg,
        "created_at": record.created_at
    }

@router.get("/history", response_model=List[BMIResponse])
def get_bmi_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the authenticated patient's BMI calculation history ordered newest first."""
    records = get_user_bmi_history(db, current_user)
    return [
        {
            "id": r.id,
            "bmi": r.bmi_value,
            "category": r.bmi_category,
            "height": r.height,
            "height_unit": r.height_unit,
            "weight": r.weight,
            "weight_unit": r.weight_unit,
            "height_m": r.height_m,
            "weight_kg": r.weight_kg,
            "created_at": r.created_at
        }
        for r in records
    ]

@router.get("/latest", response_model=Optional[BMIResponse])
def get_latest_bmi(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the latest calculated BMI record for the patient."""
    record = get_user_latest_bmi(db, current_user)
    if not record:
        return None
    return {
        "id": record.id,
        "bmi": record.bmi_value,
        "category": record.bmi_category,
        "height": record.height,
        "height_unit": record.height_unit,
        "weight": record.weight,
        "weight_unit": record.weight_unit,
        "height_m": record.height_m,
        "weight_kg": record.weight_kg,
        "created_at": record.created_at
    }
