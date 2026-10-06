from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class DiabetesComplicationsRequest(BaseModel):
    age: int = Field(..., ge=18, le=100, description="Patient age in years")
    systolic_bp: float = Field(..., ge=80.0, le=220.0, description="Systolic Blood Pressure (mmHg)")
    diastolic_bp: float = Field(..., ge=50.0, le=140.0, description="Diastolic Blood Pressure (mmHg)")
    hba1c: float = Field(..., ge=4.0, le=16.0, description="HbA1c level (%)")
    fasting_glucose: float = Field(..., ge=70.0, le=350.0, description="Fasting Blood Glucose (mg/dL)")
    diabetes_duration_years: int = Field(..., ge=0, le=60, description="Duration of Diabetes (years)")
    bmi: float = Field(..., ge=15.0, le=55.0, description="Body Mass Index (BMI)")
    serum_creatinine: float = Field(1.0, ge=0.3, le=15.0, description="Serum Creatinine (mg/dL)")
    albumin_urine: int = Field(0, ge=0, le=4, description="Urine Albumin Level (0-4)")
    tingling_feet: int = Field(0, ge=0, le=1, description="Foot Tingling/Numbness (0: No, 1: Yes)")
    vibration_loss: int = Field(0, ge=0, le=1, description="Reduced Foot Vibration Perception (0: No, 1: Yes)")
    ankle_reflex: int = Field(0, ge=0, le=2, description="Ankle Reflex (0: Normal, 1: Reduced, 2: Absent)")
    loss_of_sensory_perception: int = Field(0, ge=0, le=1, description="Loss of Protective Sensation (0: No, 1: Yes)")
    history_of_ulcer: int = Field(0, ge=0, le=1, description="History of Foot Ulcer (0: No, 1: Yes)")
    ankle_brachial_index: float = Field(0.9, ge=0.3, le=1.5, description="Ankle-Brachial Index (ABI)")
    intermittent_claudication: int = Field(0, ge=0, le=1, description="Leg Pain While Walking (0: No, 1: Yes)")

class DiabetesComplicationResponse(BaseModel):
    id: int
    user_id: int
    heart_risk: str
    heart_probability: float
    kidney_risk: str
    kidney_probability: float
    neuropathy_risk: str
    neuropathy_probability: float
    retinopathy_risk: str
    retinopathy_probability: float
    foot_risk: str
    foot_probability: float
    vascular_risk: str
    vascular_probability: float
    overall_risk_summary: str
    created_at: datetime

    class Config:
        from_attributes = True
