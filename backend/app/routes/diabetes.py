from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.diabetes import DiabetesPrediction
from app.schemas.diabetes import DiabetesPredictionRequest, DiabetesPredictionResponse
from app.services.auth_service import get_current_user
from app.services.diabetes_ml_service import diabetes_ml_service

router = APIRouter(prefix="/api/predictions/diabetes", tags=["Diabetes Risk Prediction ML"])

@router.post("", response_model=DiabetesPredictionResponse, status_code=status.HTTP_201_CREATED)
def predict_diabetes_risk(
    data: DiabetesPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accepts patient physiological metrics, runs trained ML inference (XGBoost/RF),
    persists history for the patient, and returns predicted risk score and probability.
    """
    input_dict = data.model_dump()
    
    # Run ML prediction pipeline
    ml_result = diabetes_ml_service.predict(input_dict)

    # Save to database for current patient
    db_record = DiabetesPrediction(
        user_id=current_user.id,
        pregnancies=data.pregnancies,
        glucose=data.glucose,
        blood_pressure=data.blood_pressure,
        skin_thickness=data.skin_thickness,
        insulin=data.insulin,
        bmi=data.bmi,
        diabetes_pedigree_function=data.diabetes_pedigree_function,
        age=data.age,
        prediction=ml_result["prediction"],
        risk=ml_result["risk"],
        probability=ml_result["probability"],
        model_name=ml_result["model"]
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return {
        "id": db_record.id,
        "prediction": db_record.prediction,
        "risk": db_record.risk,
        "probability": db_record.probability,
        "model": db_record.model_name,
        "pregnancies": db_record.pregnancies,
        "glucose": db_record.glucose,
        "blood_pressure": db_record.blood_pressure,
        "skin_thickness": db_record.skin_thickness,
        "insulin": db_record.insulin,
        "bmi": db_record.bmi,
        "diabetes_pedigree_function": db_record.diabetes_pedigree_function,
        "age": db_record.age,
        "created_at": db_record.created_at
    }

@router.get("/history", response_model=List[DiabetesPredictionResponse])
def get_diabetes_prediction_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the authenticated patient's prediction history strictly isolated to their account."""
    records = (
        db.query(DiabetesPrediction)
        .filter(DiabetesPrediction.user_id == current_user.id)
        .order_by(DiabetesPrediction.id.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "prediction": r.prediction,
            "risk": r.risk,
            "probability": r.probability,
            "model": r.model_name,
            "pregnancies": r.pregnancies,
            "glucose": r.glucose,
            "blood_pressure": r.blood_pressure,
            "skin_thickness": r.skin_thickness,
            "insulin": r.insulin,
            "bmi": r.bmi,
            "diabetes_pedigree_function": r.diabetes_pedigree_function,
            "age": r.age,
            "created_at": r.created_at
        }
        for r in records
    ]

@router.get("/latest", response_model=Optional[DiabetesPredictionResponse])
def get_latest_diabetes_prediction(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the latest diabetes risk prediction record for the patient dashboard."""
    record = (
        db.query(DiabetesPrediction)
        .filter(DiabetesPrediction.user_id == current_user.id)
        .order_by(DiabetesPrediction.id.desc())
        .first()
    )
    if not record:
        return None

    return {
        "id": record.id,
        "prediction": record.prediction,
        "risk": record.risk,
        "probability": record.probability,
        "model": record.model_name,
        "pregnancies": record.pregnancies,
        "glucose": record.glucose,
        "blood_pressure": record.blood_pressure,
        "skin_thickness": record.skin_thickness,
        "insulin": record.insulin,
        "bmi": record.bmi,
        "diabetes_pedigree_function": record.diabetes_pedigree_function,
        "age": record.age,
        "created_at": record.created_at
    }
