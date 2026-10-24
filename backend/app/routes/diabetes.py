
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.diabetes import DiabetesPrediction
from app.schemas.diabetes import (
    DiabetesPredictResponse,
    DiabetesPredictionRequest,
    DiabetesPredictionResponse,
)
from app.services.auth_service import get_current_user
from app.services.diabetes_ml_service import diabetes_ml_service

logger = logging.getLogger(__name__)

# Legacy PIMA prediction history and latest routes
router = APIRouter(
    prefix="/api/predictions/diabetes",
    tags=["Diabetes Risk Prediction ML"],
)

# Production PIMA prediction route
dedicated_router = APIRouter(
    prefix="/api/diabetes",
    tags=["PIMA Diabetes Risk Prediction"],
)


def normalize_contributing_features(features):
    """
    Ensure each SHAP feature contains all fields required by the
    DiabetesPredictResponse schema.

    Expected input fields:
      feature_name or feature
      actual_value
      shap_contribution

    direction assumes a positive SHAP value increases the model output
    being explained. Verify this against your model's positive class.
    """
    if not features:
        return []

    valid_features = []

    for item in features:
        if not isinstance(item, dict):
            logger.warning("Skipping invalid SHAP feature: %r", item)
            continue

        feature_name = item.get("feature_name") or item.get("feature")

        if not feature_name:
            logger.warning("Skipping SHAP feature without a name: %r", item)
            continue

        try:
            contribution = float(item.get("shap_contribution", 0.0))
            actual_value = float(item.get("actual_value", 0.0))
        except (TypeError, ValueError):
            logger.warning("Skipping SHAP feature with invalid values: %r", item)
            continue

        direction = item.get("direction")

        if direction not in ("increases risk", "decreases risk", "no effect"):
            if contribution > 0:
                direction = "increases risk"
            elif contribution < 0:
                direction = "decreases risk"
            else:
                direction = "no effect"

        valid_features.append({
            "feature_name": str(feature_name),
            "feature": str(item.get("feature") or feature_name),
            "actual_value": actual_value,
            "shap_contribution": contribution,
            "direction": direction,
        })

    # Percentage is based on the absolute SHAP contributions.
    total_absolute_contribution = sum(
        abs(item["shap_contribution"]) for item in valid_features
    )

    for item in valid_features:
        if total_absolute_contribution > 0:
            percentage = (
                abs(item["shap_contribution"])
                / total_absolute_contribution
                * 100
            )
        else:
            percentage = 0.0

        item["relative_contribution_pct"] = round(percentage, 2)

    valid_features.sort(
        key=lambda item: abs(item["shap_contribution"]),
        reverse=True,
    )

    return valid_features[:8]


@dedicated_router.post(
    "/predict",
    response_model=DiabetesPredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict Diabetes Risk using PIMA model",
)
def predict_diabetes_risk_production(
    data: DiabetesPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run the PIMA model, save the prediction, and return SHAP details."""

    try:
        input_dict = data.model_dump()

        # Run existing ML service.
        ml_result = diabetes_ml_service.predict(input_dict)

        # Fix the response validation issue by normalizing SHAP fields.
        contributing_features = normalize_contributing_features(
            ml_result.get("top_contributing_features", [])
        )

        prediction = int(ml_result["prediction"])
        probability = float(ml_result["probability"])
        risk = ml_result.get("risk", ml_result.get("risk_category", "Unknown"))
        risk_category = ml_result.get("risk_category", risk)
        model_name = ml_result.get("model", ml_result.get("model_version", "unknown"))

        # Save to the existing PIMA-compatible database table.
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
            prediction=prediction,
            risk=risk,
            probability=probability,
            model_name=model_name,
        )

        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        logger.info(
            "PIMA prediction successful: probability=%.4f, risk=%s, features=%d",
            probability,
            risk_category,
            len(contributing_features),
        )

        return {
            "prediction": prediction,
            "probability": probability,
            "risk_category": risk_category,
            "threshold": ml_result.get("threshold", 0.30),
            "model_version": ml_result.get(
                "model_version",
                model_name,
            ),
            "top_contributing_features": contributing_features,
            "disclaimer": ml_result.get(
                "disclaimer",
                "This model provides an estimated risk probability for "
                "clinical decision support. It does not provide an "
                "automated medical diagnosis.",
            ),
        }

    except ValueError as exc:
        db.rollback()
        logger.warning("PIMA validation error: %s", str(exc))

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Clinical feature validation failed: {exc}",
        ) from exc

    except Exception as exc:
        db.rollback()
        logger.error(
            "PIMA prediction failed: %s",
            str(exc),
            exc_info=True,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Diabetes prediction failed. Check backend logs.",
        ) from exc


@router.post(
    "",
    response_model=DiabetesPredictionResponse,
    status_code=status.HTTP_201_CREATED,
)
def predict_diabetes_risk_legacy(
    data: DiabetesPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run a PIMA prediction and save it to the user's history."""

    try:
        ml_result = diabetes_ml_service.predict(data.model_dump())

        prediction = int(ml_result["prediction"])
        probability = float(ml_result["probability"])
        risk = ml_result.get("risk", ml_result.get("risk_category", "Unknown"))
        model_name = ml_result.get("model", ml_result.get("model_version", "unknown"))

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
            prediction=prediction,
            risk=risk,
            probability=probability,
            model_name=model_name,
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
            "created_at": db_record.created_at,
        }

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()
        logger.error("Legacy PIMA prediction failed: %s", str(exc), exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction failed. Check backend logs.",
        ) from exc


@router.get("/history")
def get_diabetes_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return prediction history belonging only to the current user."""

    records = (
        db.query(DiabetesPrediction)
        .filter(DiabetesPrediction.user_id == current_user.id)
        .order_by(DiabetesPrediction.created_at.desc())
        .all()
    )

    return [
        {
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
            "created_at": record.created_at,
        }
        for record in records
    ]


@router.get(
    "/latest",
    response_model=Optional[DiabetesPredictionResponse],
)
def get_latest_diabetes_prediction(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the latest PIMA prediction for the current user."""

    record = (
        db.query(DiabetesPrediction)
        .filter(DiabetesPrediction.user_id == current_user.id)
        .order_by(DiabetesPrediction.created_at.desc())
        .first()
    )

    if record is None:
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
        "created_at": record.created_at,
    }
