from app.routes.health import router as health_router
from app.routes.auth import router as auth_router
from app.routes.bmi import router as bmi_router
from app.routes.diabetes import router as diabetes_router
from app.routes.disease import router as disease_router
from app.routes.health_risk import router as health_risk_router
from app.routes.diet import router as diet_router
from app.routes.exercise import router as exercise_router
from app.routes.medicine import router as medicine_router
from app.routes.doctor import router as doctor_router
from app.routes.appointment import router as appointment_router
from app.routes.report import router as report_router
from app.routes.admin import router as admin_router
from app.routes.diabetes_complications import router as diabetes_complications_router
from app.routes.research import router as research_router

__all__ = [
    "health_router",
    "auth_router",
    "bmi_router",
    "diabetes_router",
    "disease_router",
    "health_risk_router",
    "diet_router",
    "exercise_router",
    "medicine_router",
    "doctor_router",
    "appointment_router",
    "report_router",
    "admin_router",
    "diabetes_complications_router",
    "research_router"
]
