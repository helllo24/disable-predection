import json
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.exercise import ExerciseRecommendation
from app.schemas.exercise import ExerciseRecommendationRequest, ExerciseRecommendationResponse
from app.services.auth_service import get_current_user
from app.services.exercise_service import generate_exercise_recommendation

router = APIRouter(prefix="/api/recommendations/exercise", tags=["Personalized Exercise Recommendations"])

@router.post("", response_model=ExerciseRecommendationResponse, status_code=status.HTTP_201_CREATED)
def create_exercise_recommendation(
    data: ExerciseRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates a personalized, rule-based informational exercise guidance plan
    for the authenticated patient, persists history, and returns structured guidance.
    """
    rec_dict = generate_exercise_recommendation(
        user=current_user,
        fitness_level=data.fitness_level,
        goal=data.goal,
        db=db
    )

    db_record = ExerciseRecommendation(
        user_id=current_user.id,
        fitness_level=data.fitness_level,
        goal=data.goal,
        recommendations=json.dumps(rec_dict)
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return {
        "id": db_record.id,
        "fitness_level": db_record.fitness_level,
        "goal": db_record.goal,
        "recommendations": json.loads(db_record.recommendations),
        "created_at": db_record.created_at
    }

@router.get("/latest", response_model=Optional[ExerciseRecommendationResponse])
def get_latest_exercise_recommendation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the patient's latest exercise recommendation for the dashboard."""
    record = (
        db.query(ExerciseRecommendation)
        .filter(ExerciseRecommendation.user_id == current_user.id)
        .order_by(ExerciseRecommendation.id.desc())
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
        "fitness_level": record.fitness_level,
        "goal": record.goal,
        "recommendations": recs,
        "created_at": record.created_at
    }

@router.get("/history", response_model=List[ExerciseRecommendationResponse])
def get_exercise_recommendation_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the patient's exercise recommendation history strictly isolated to their account."""
    records = (
        db.query(ExerciseRecommendation)
        .filter(ExerciseRecommendation.user_id == current_user.id)
        .order_by(ExerciseRecommendation.id.desc())
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
            "fitness_level": r.fitness_level,
            "goal": r.goal,
            "recommendations": recs,
            "created_at": r.created_at
        })
    return out
