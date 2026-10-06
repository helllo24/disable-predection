import json
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.diet import DietRecommendation
from app.schemas.diet import DietRecommendationRequest, DietRecommendationResponse
from app.services.auth_service import get_current_user
from app.services.diet_service import generate_diet_recommendation

router = APIRouter(prefix="/api/recommendations/diet", tags=["Personalized Diet Recommendations"])

@router.post("", response_model=DietRecommendationResponse, status_code=status.HTTP_201_CREATED)
def create_diet_recommendation(
    data: DietRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates a personalized, rule-based informational diet guidance plan
    for the authenticated patient, persists history, and returns structured guidance.
    """
    rec_dict = generate_diet_recommendation(
        user=current_user,
        dietary_preference=data.dietary_preference,
        goal=data.goal,
        custom_allergies=data.custom_allergies or "",
        db=db
    )

    db_record = DietRecommendation(
        user_id=current_user.id,
        dietary_preference=data.dietary_preference,
        goal=data.goal,
        allergies=data.custom_allergies or current_user.allergies or "",
        recommendations=json.dumps(rec_dict)
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return {
        "id": db_record.id,
        "dietary_preference": db_record.dietary_preference,
        "goal": db_record.goal,
        "allergies": db_record.allergies,
        "recommendations": json.loads(db_record.recommendations),
        "created_at": db_record.created_at
    }

@router.get("/latest", response_model=Optional[DietRecommendationResponse])
def get_latest_diet_recommendation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the patient's latest diet recommendation for the dashboard."""
    record = (
        db.query(DietRecommendation)
        .filter(DietRecommendation.user_id == current_user.id)
        .order_by(DietRecommendation.id.desc())
        .first()
    )

    if not record:
        return None

    try:
        recs = json.loads(record.recommendations)
    except Exception:
        recs = {}

    return {
        "id": record.id,
        "dietary_preference": record.dietary_preference,
        "goal": record.goal,
        "allergies": record.allergies,
        "recommendations": recs,
        "created_at": record.created_at
    }

@router.get("/history", response_model=List[DietRecommendationResponse])
def get_diet_recommendation_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the patient's diet recommendation history strictly isolated to their account."""
    records = (
        db.query(DietRecommendation)
        .filter(DietRecommendation.user_id == current_user.id)
        .order_by(DietRecommendation.id.desc())
        .all()
    )

    out = []
    for r in records:
        try:
            recs = json.loads(r.recommendations)
        except Exception:
            recs = {}
        out.append({
            "id": r.id,
            "dietary_preference": r.dietary_preference,
            "goal": r.goal,
            "allergies": r.allergies,
            "recommendations": recs,
            "created_at": r.created_at
        })
    return out
