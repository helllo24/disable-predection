import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.diabetes_complications import DiabetesComplicationPrediction
from app.schemas.diabetes_complications import DiabetesComplicationsRequest, DiabetesComplicationResponse
from app.services.auth_service import get_current_user
from app.services.complications_ml_service import complications_ml_service

router = APIRouter(prefix="/api/predictions/diabetes-complications", tags=["Diabetes Complications ML"])

@router.post("", response_model=DiabetesComplicationResponse, status_code=status.HTTP_201_CREATED)
def predict_and_save_complications(
    payload: DiabetesComplicationsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Runs multi-model ML inference across 6 diabetes complication categories
    (Heart, Kidney, Neuropathy, Retinopathy, Foot, Vascular) and saves result to DB.
    Enforces JWT authentication and patient data isolation.
    """
    input_dict = payload.model_dump()
    input_dict['gender'] = current_user.gender

    # Run ML Inference
    results = complications_ml_service.predict_all_complications(input_dict)

    # Save to Database
    record = DiabetesComplicationPrediction(
        user_id=current_user.id,
        heart_risk=results["heart_risk"],
        heart_probability=results["heart_probability"],
        kidney_risk=results["kidney_risk"],
        kidney_probability=results["kidney_probability"],
        neuropathy_risk=results["neuropathy_risk"],
        neuropathy_probability=results["neuropathy_probability"],
        retinopathy_risk=results["retinopathy_risk"],
        retinopathy_probability=results["retinopathy_probability"],
        foot_risk=results["foot_risk"],
        foot_probability=results["foot_probability"],
        vascular_risk=results["vascular_risk"],
        vascular_probability=results["vascular_probability"],
        overall_risk_summary=results["overall_risk_summary"],
        input_parameters=json.dumps(input_dict)
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record

@router.get("/latest", response_model=DiabetesComplicationResponse)
def get_latest_complications_prediction(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the authenticated patient's most recent complication risk assessment.
    Strictly isolated to current_user.id.
    """
    record = (
        db.query(DiabetesComplicationPrediction)
        .filter(DiabetesComplicationPrediction.user_id == current_user.id)
        .order_by(DiabetesComplicationPrediction.created_at.desc())
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No diabetes complication predictions found for this patient."
        )

    return record

@router.get("/history", response_model=List[DiabetesComplicationResponse])
def get_complications_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves history logs of complication risk assessments for authenticated patient.
    Strictly isolated to current_user.id.
    """
    records = (
        db.query(DiabetesComplicationPrediction)
        .filter(DiabetesComplicationPrediction.user_id == current_user.id)
        .order_by(DiabetesComplicationPrediction.created_at.desc())
        .all()
    )

    return records
