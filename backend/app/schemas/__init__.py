from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse, UserProfileUpdate
from app.schemas.bmi import BMICalculateRequest, BMIResponse
from app.schemas.diabetes import DiabetesPredictionRequest, DiabetesPredictionResponse
from app.schemas.disease_prediction import DiseasePredictionRequest, DiseasePredictionResponse
from app.schemas.health_risk import ContributingFactor, HealthRiskResponse
from app.schemas.diet import DietRecommendationRequest, DietRecommendationResponse
from app.schemas.exercise import ExerciseRecommendationRequest, ExerciseRecommendationResponse
from app.schemas.medicine import MedicineReminderCreate, MedicineReminderUpdate, MedicineReminderResponse
from app.schemas.doctor import DoctorResponse
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse

__all__ = [
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "UserProfileUpdate",
    "BMICalculateRequest",
    "BMIResponse",
    "DiabetesPredictionRequest",
    "DiabetesPredictionResponse",
    "DiseasePredictionRequest",
    "DiseasePredictionResponse",
    "ContributingFactor",
    "HealthRiskResponse",
    "DietRecommendationRequest",
    "DietRecommendationResponse",
    "ExerciseRecommendationRequest",
    "ExerciseRecommendationResponse",
    "MedicineReminderCreate",
    "MedicineReminderUpdate",
    "MedicineReminderResponse",
    "DoctorResponse",
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentResponse"
]
