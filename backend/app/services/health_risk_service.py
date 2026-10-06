import json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.bmi import BMIRecord
from app.models.diabetes import DiabetesPrediction
from app.models.disease_prediction import DiseasePrediction
from app.models.health_risk import HealthRiskScore

def calculate_health_risk_for_user(user: User, db: Session) -> Tuple[int, str, List[Dict[str, Any]]]:
    """
    Computes a transparent, explainable 0-100 composite Health Risk Score based on
    the patient's age, BMI profile, latest diabetes ML prediction, and latest disease ML prediction.
    """
    total_points = 0.0
    factors = []

    # 1. Age Factor
    age = user.age
    age_pts = 0
    if age >= 60:
        age_pts = 20
        detail_msg = f"Age {age} yrs (Senior demographic risk factor)"
    elif age >= 45:
        age_pts = 10
        detail_msg = f"Age {age} yrs (Middle-age demographic risk factor)"
    else:
        age_pts = 0
        detail_msg = f"Age {age} yrs (Low demographic age risk)"

    total_points += age_pts
    factors.append({
        "factor": "Age Demographics",
        "detail": detail_msg,
        "points": age_pts
    })

    # 2. BMI Factor (Fetch latest BMI record or calculate from height/weight profile)
    latest_bmi_rec = (
        db.query(BMIRecord)
        .filter(BMIRecord.user_id == user.id)
        .order_by(BMIRecord.id.desc())
        .first()
    )

    bmi_val = None
    bmi_cat = None
    if latest_bmi_rec:
        bmi_val = latest_bmi_rec.bmi_value
        bmi_cat = latest_bmi_rec.bmi_category
    elif user.height and user.weight and user.height > 0:
        height_m = user.height / 100.0
        bmi_val = user.weight / (height_m * height_m)

    bmi_pts = 0
    if bmi_val is not None:
        if bmi_val >= 30.0:
            bmi_pts = 25
            bmi_detail = f"BMI {bmi_val:.1f} (Obesity weight category)"
        elif bmi_val >= 25.0:
            bmi_pts = 15
            bmi_detail = f"BMI {bmi_val:.1f} (Overweight category)"
        elif bmi_val < 18.5:
            bmi_pts = 10
            bmi_detail = f"BMI {bmi_val:.1f} (Underweight category)"
        else:
            bmi_pts = 0
            bmi_detail = f"BMI {bmi_val:.1f} (Normal healthy weight range)"
    else:
        bmi_pts = 0
        bmi_detail = "BMI data not recorded yet in patient profile"

    total_points += bmi_pts
    factors.append({
        "factor": "Body Mass Index (BMI)",
        "detail": bmi_detail,
        "points": bmi_pts
    })

    # 3. Diabetes ML Prediction Factor
    latest_diabetes_rec = (
        db.query(DiabetesPrediction)
        .filter(DiabetesPrediction.user_id == user.id)
        .order_by(DiabetesPrediction.id.desc())
        .first()
    )

    diab_pts = 0.0
    if latest_diabetes_rec:
        prob = latest_diabetes_rec.probability
        diab_pts = round(prob * 35.0, 1)
        diab_detail = f"Diabetes ML Assessment: {latest_diabetes_rec.risk} ({prob * 100:.1f}% risk probability)"
    else:
        diab_pts = 0.0
        diab_detail = "No ML diabetes assessment recorded yet"

    total_points += diab_pts
    factors.append({
        "factor": "Diabetes Risk Assessment",
        "detail": diab_detail,
        "points": round(diab_pts, 1)
    })

    # 4. Multi-Class Disease ML Prediction Factor
    latest_disease_rec = (
        db.query(DiseasePrediction)
        .filter(DiseasePrediction.user_id == user.id)
        .order_by(DiseasePrediction.id.desc())
        .first()
    )

    dis_pts = 0.0
    if latest_disease_rec:
        prob = latest_disease_rec.probability
        dis_pts = round(prob * 20.0, 1)
        dis_detail = f"Disease ML Assessment: {latest_disease_rec.predicted_disease} ({prob * 100:.1f}% confidence)"
    else:
        dis_pts = 0.0
        dis_detail = "No ML multi-class disease assessment recorded yet"

    total_points += dis_pts
    factors.append({
        "factor": "Disease Assessment",
        "detail": dis_detail,
        "points": round(dis_pts, 1)
    })

    # Normalize score to 0–100 cap
    final_score = int(min(100, round(total_points)))

    # Determine risk category
    if final_score <= 33:
        category = "Low Risk"
    elif final_score <= 66:
        category = "Moderate Risk"
    else:
        category = "High Risk"

    return final_score, category, factors
