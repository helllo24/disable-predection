from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

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
