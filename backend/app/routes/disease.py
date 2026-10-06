import json
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.disease_prediction import DiseasePrediction
from app.schemas.disease_prediction import DiseasePredictionRequest, DiseasePredictionResponse
from app.services.auth_service import get_current_user
from app.services.disease_ml_service import disease_ml_service

router = APIRouter(prefix="/api/predictions/disease", tags=["Multi-Class Disease Prediction ML"])

@router.get("/symptoms", response_model=List[str])
def get_supported_symptoms(current_user: User = Depends(get_current_user)):
    """Returns the list of supported symptom identifiers for frontend selection controls."""
    return disease_ml_service.get_all_symptoms()

@router.post("", response_model=DiseasePredictionResponse, status_code=status.HTTP_201_CREATED)
def predict_disease(
    data: DiseasePredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accepts patient selected symptoms, runs multi-class disease ML inference,
    persists history for the patient, and returns predicted condition and probability.
    """
    # Run ML prediction pipeline
    ml_result = disease_ml_service.predict(data.symptoms)

    # Save to database for current patient
    db_record = DiseasePrediction(
        user_id=current_user.id,
        symptoms=json.dumps(ml_result["symptoms"]),
        predicted_disease=ml_result["predicted_disease"],
        probability=ml_result["probability"],
        model_name=ml_result["model"]
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return {
        "id": db_record.id,
        "predicted_disease": db_record.predicted_disease,
        "probability": db_record.probability,
        "model": db_record.model_name,
        "symptoms": json.loads(db_record.symptoms),
        "created_at": db_record.created_at
    }

@router.get("/history", response_model=List[DiseasePredictionResponse])
def get_disease_prediction_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the authenticated patient's disease prediction history strictly isolated to their account."""
    records = (
        db.query(DiseasePrediction)
        .filter(DiseasePrediction.user_id == current_user.id)
        .order_by(DiseasePrediction.id.desc())
        .all()
    )
    
    out = []
    for r in records:
        try:
            syms = json.loads(r.symptoms)
        except Exception:
            syms = [s.strip() for s in r.symptoms.split(",") if s.strip()]
        out.append({
            "id": r.id,
            "predicted_disease": r.predicted_disease,
            "probability": r.probability,
            "model": r.model_name,
            "symptoms": syms,
            "created_at": r.created_at
        })
    return out

@router.get("/latest", response_model=Optional[DiseasePredictionResponse])
def get_latest_disease_prediction(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the latest disease prediction record for the patient dashboard."""
    record = (
        db.query(DiseasePrediction)
        .filter(DiseasePrediction.user_id == current_user.id)
        .order_by(DiseasePrediction.id.desc())
        .first()
    )
    if not record:
        return None

    try:
        syms = json.loads(record.symptoms)
    except Exception:
        syms = [s.strip() for s in record.symptoms.split(",") if s.strip()]

    return {
        "id": record.id,
        "predicted_disease": record.predicted_disease,
        "probability": record.probability,
        "model": record.model_name,
        "symptoms": syms,
        "created_at": record.created_at
    }
