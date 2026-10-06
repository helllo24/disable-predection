from app.services.auth_service import (
    register_patient,
    authenticate_patient,
    get_current_user,
    get_current_admin_user,
    update_patient_profile
)
from app.services.bmi_service import compute_and_save_bmi, get_user_bmi_history, get_user_latest_bmi
from app.services.diabetes_ml_service import diabetes_ml_service
from app.services.disease_ml_service import disease_ml_service
from app.services.health_risk_service import calculate_health_risk_for_user
from app.services.diet_service import generate_diet_recommendation
from app.services.exercise_service import generate_exercise_recommendation
from app.services.pdf_report_service import generate_patient_health_pdf
from app.services.complications_ml_service import complications_ml_service

__all__ = [
    "register_patient",
    "authenticate_patient",
    "get_current_user",
    "get_current_admin_user",
    "update_patient_profile",
    "compute_and_save_bmi",
    "get_user_bmi_history",
    "get_user_latest_bmi",
    "diabetes_ml_service",
    "disease_ml_service",
    "calculate_health_risk_for_user",
    "generate_diet_recommendation",
    "generate_exercise_recommendation",
    "generate_patient_health_pdf",
    "complications_ml_service"
]
