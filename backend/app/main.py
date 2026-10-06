import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database.connection import engine, Base
from app.routes import (
    health_router,
    auth_router,
    bmi_router,
    diabetes_router,
    disease_router,
    health_risk_router,
    diet_router,
    exercise_router,
    medicine_router,
    doctor_router,
    appointment_router,
    report_router,
    admin_router,
    diabetes_complications_router,
    research_router
)
import app.models  # noqa: F401

load_dotenv()

# Initialize tables automatically on app startup
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[DB Warning] Could not auto-create tables: {e}")

app = FastAPI(
    title=os.getenv("APP_NAME", "Diabetes Prediction Using Machine Learning API"),
    version="1.0.0",
    description="FastAPI Backend for MCA Project: Diabetes prediction using machine learning (Multi-Dataset External Validation & Subgroup Fairness)"
)

# Configure CORS dynamically to allow any local frontend port (5173, 5174, etc.)
origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:5175,http://127.0.0.1:5175")
origins = [origin.strip() for origin in origins_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(bmi_router)
app.include_router(diabetes_router)
app.include_router(disease_router)
app.include_router(health_risk_router)
app.include_router(diet_router)
app.include_router(exercise_router)
app.include_router(medicine_router)
app.include_router(doctor_router)
app.include_router(appointment_router)
app.include_router(report_router)
app.include_router(admin_router)
app.include_router(diabetes_complications_router)
app.include_router(research_router)

@app.get("/")
def read_root():
    """Root API endpoint required by Part 0."""
    return {"message": "Diabetes Prediction Using Machine Learning API is running"}
