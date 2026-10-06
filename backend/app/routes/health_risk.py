import json
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.health_risk import HealthRiskScore
from app.schemas.health_risk import HealthRiskResponse
from app.services.auth_service import get_current_user
from app.services.health_risk_service import calculate_health_risk_for_user

router = APIRouter(prefix="/api/health-risk", tags=["Composite Health Risk Score"])

@router.post("/calculate", response_model=HealthRiskResponse, status_code=status.HTTP_201_CREATED)
def compute_health_risk(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculates a 0-100 composite Health Risk Score for the authenticated patient,
    persists history with explainable contributing factors, and returns the result.
    """
    score, category, factors = calculate_health_risk_for_user(current_user, db)

    db_record = HealthRiskScore(
        user_id=current_user.id,
        score=score,
        category=category,
        contributing_factors=json.dumps(factors)
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return {
        "id": db_record.id,
        "score": db_record.score,
        "category": db_record.category,
        "contributing_factors": json.loads(db_record.contributing_factors),
        "created_at": db_record.created_at
    }

@router.get("/latest", response_model=Optional[HealthRiskResponse])
def get_latest_health_risk(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the patient's latest composite Health Risk Score for the dashboard."""
    record = (
        db.query(HealthRiskScore)
        .filter(HealthRiskScore.user_id == current_user.id)
        .order_by(HealthRiskScore.id.desc())
        .first()
    )

    if not record:
        return None

    try:
        factors = json.loads(record.contributing_factors)
    except Exception:
        factors = []

    return {
        "id": record.id,
        "score": record.score,
        "category": record.category,
        "contributing_factors": factors,
        "created_at": record.created_at
    }

@router.get("/history", response_model=List[HealthRiskResponse])
def get_health_risk_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the patient's historical Health Risk Scores strictly isolated to their account."""
    records = (
        db.query(HealthRiskScore)
        .filter(HealthRiskScore.user_id == current_user.id)
        .order_by(HealthRiskScore.id.desc())
        .all()
    )

    out = []
    for r in records:
        try:
            factors = json.loads(r.contributing_factors)
        except Exception:
            factors = []
        out.append({
            "id": r.id,
            "score": r.score,
            "category": r.category,
            "contributing_factors": factors,
            "created_at": r.created_at
        })
    return out
