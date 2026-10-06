from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.bmi import BMIRecord
from app.models.user import User
from app.schemas.bmi import BMICalculateRequest

def calculate_bmi_category(bmi_val: float) -> str:
    """Determines standard adult BMI category."""
    if bmi_val < 18.5:
        return "Underweight"
    elif bmi_val < 25.0:
        return "Normal weight"
    elif bmi_val < 30.0:
        return "Overweight"
    else:
        return "Obesity"

def compute_and_save_bmi(db: Session, user: User, data: BMICalculateRequest) -> BMIRecord:
    """Validates, converts units, calculates BMI, and stores history for the patient."""
    if data.height <= 0 or data.weight <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Height and weight must be positive numeric values greater than zero."
        )

    # Unit Conversions to Standard M / KG
    if data.height_unit == "ft":
        height_m = data.height * 0.3048
    else:  # cm
        height_m = data.height / 100.0

    if data.weight_unit == "lb":
        weight_kg = data.weight * 0.45359237
    else:  # kg
        weight_kg = data.weight

    if height_m <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid height value after conversion."
        )

    # Standard BMI Formula: kg / m^2
    raw_bmi = weight_kg / (height_m ** 2)
    bmi_value = round(raw_bmi, 1)
    category = calculate_bmi_category(bmi_value)

    # Persist record
    record = BMIRecord(
        user_id=user.id,
        height=round(data.height, 2),
        height_unit=data.height_unit,
        weight=round(data.weight, 2),
        weight_unit=data.weight_unit,
        height_m=round(height_m, 3),
        weight_kg=round(weight_kg, 2),
        bmi_value=bmi_value,
        bmi_category=category
    )

    # Also update user's quick health profile attributes (in cm and kg)
    user.height = round(height_m * 100.0, 1)
    user.weight = round(weight_kg, 1)

    db.add(record)
    db.commit()
    db.refresh(record)

    return record

def get_user_bmi_history(db: Session, user: User) -> List[BMIRecord]:
    """Fetches history records belonging ONLY to the authenticated patient, newest first."""
    return (
        db.query(BMIRecord)
        .filter(BMIRecord.user_id == user.id)
        .order_by(BMIRecord.id.desc())
        .all()
    )

def get_user_latest_bmi(db: Session, user: User) -> Optional[BMIRecord]:
    """Fetches the latest BMI calculation record for the patient."""
    return (
        db.query(BMIRecord)
        .filter(BMIRecord.user_id == user.id)
        .order_by(BMIRecord.id.desc())
        .first()
    )
