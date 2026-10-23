from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

import math

ALLOWED_GENDERS = {"Female", "Male", "Other"}
ALLOWED_SMOKING = {"never", "No Info", "current", "former", "ever", "not current"}

class DiabetesClinicalFeaturesRequest(BaseModel):
    gender: str = Field(..., description="Patient biological sex (Female, Male, Other)")
    age: float = Field(..., ge=0.08, le=120.0, description="Patient age in years (0.08 to 120.0)")
    hypertension: int = Field(..., ge=0, le=1, description="Hypertension indicator (0 = No, 1 = Yes)")
    heart_disease: int = Field(..., ge=0, le=1, description="Heart disease indicator (0 = No, 1 = Yes)")
    smoking_history: str = Field(..., description="Smoking history category (never, No Info, current, former, ever, not current)")
    bmi: float = Field(..., ge=10.0, le=120.0, description="Body Mass Index (10.0 to 120.0 kg/m^2)")
    HbA1c_level: float = Field(..., ge=3.5, le=15.0, description="Glycated hemoglobin percentage (3.5% to 15.0%)")
    blood_glucose_level: float = Field(..., ge=50.0, le=600.0, description="Blood glucose concentration (50 to 600 mg/dL)")

    @field_validator("age", "bmi", "HbA1c_level", "blood_glucose_level")
    @classmethod
    def validate_finite_numeric(cls, v: float, info) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError(f"Feature '{info.field_name}' must be a finite numerical value. Received: {v}")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if not isinstance(v, str) or v.strip() not in ALLOWED_GENDERS:
            raise ValueError(f"Invalid gender '{v}'. Allowed biological sex categories: {sorted(list(ALLOWED_GENDERS))}")
        return v.strip()

    @field_validator("smoking_history")
    @classmethod
    def validate_smoking(cls, v: str) -> str:
        if not isinstance(v, str) or v.strip() not in ALLOWED_SMOKING:
            raise ValueError(f"Invalid smoking history '{v}'. Allowed categories: {sorted(list(ALLOWED_SMOKING))}")
        return v.strip()

class FeatureContributionItem(BaseModel):
    feature: str
    actual_value: Optional[float] = None
    shap_contribution: float
    direction: str
    relative_contribution_pct: float

class DiabetesPredictResponse(BaseModel):
    prediction: int = Field(..., description="Binary classification (0 = Low Risk, 1 = High Risk at threshold)")
    probability: float = Field(..., description="Calibrated risk probability (0.0 to 1.0)")
    risk_category: str = Field(..., description="Categorical risk stratification (Low Risk, Moderate Risk, High Risk)")
    threshold: float = Field(..., description="Selected decision threshold (e.g. 0.30)")
    model_version: str = Field(..., description="Production model package version")
    top_contributing_features: List[FeatureContributionItem] = Field(default_factory=list, description="Instance SHAP feature contributions")
    disclaimer: str = Field(..., description="Clinical non-diagnostic decision-support disclaimer")

# Legacy Pima Schemas (Preserved for Backward Compatibility)
class DiabetesPredictionRequest(BaseModel):
    pregnancies: int = Field(..., ge=0, le=25, description="Number of pregnancies")
    glucose: float = Field(..., ge=0, le=500, description="Plasma glucose concentration")
    blood_pressure: float = Field(..., ge=0, le=250, description="Diastolic blood pressure (mm Hg)")
    skin_thickness: float = Field(..., ge=0, le=150, description="Triceps skin fold thickness (mm)")
    insulin: float = Field(..., ge=0, le=1200, description="2-Hour serum insulin (mu U/ml)")
    bmi: float = Field(..., ge=0, le=120, description="Body mass index (weight in kg/(height in m)^2)")
    diabetes_pedigree_function: float = Field(..., ge=0.0, le=5.0, description="Diabetes pedigree function score")
    age: int = Field(..., ge=1, le=120, description="Age in years")

    @field_validator("pregnancies", "age")
    @classmethod
    def validate_non_negative_ints(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Value cannot be negative")
        return v

    @field_validator("glucose", "blood_pressure", "skin_thickness", "insulin", "bmi", "diabetes_pedigree_function")
    @classmethod
    def validate_non_negative_floats(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Value cannot be negative")
        return v

class DiabetesPredictionResponse(BaseModel):
    id: Optional[int] = None
    prediction: int
    risk: str
    probability: float
    model: str
    pregnancies: Optional[int] = None
    glucose: Optional[float] = None
    blood_pressure: Optional[float] = None
    skin_thickness: Optional[float] = None
    insulin: Optional[float] = None
    bmi: Optional[float] = None
    diabetes_pedigree_function: Optional[float] = None
    age: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

