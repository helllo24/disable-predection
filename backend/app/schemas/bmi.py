from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class BMICalculateRequest(BaseModel):
    height: float = Field(..., gt=0, description="Height value must be greater than 0")
    height_unit: str = Field("cm", description="Height unit: cm or ft")
    weight: float = Field(..., gt=0, description="Weight value must be greater than 0")
    weight_unit: str = Field("kg", description="Weight unit: kg or lb")

    @field_validator("height_unit")
    @classmethod
    def validate_height_unit(cls, v: str) -> str:
        clean = v.lower().strip()
        if clean not in ["cm", "ft"]:
            raise ValueError("Height unit must be 'cm' or 'ft'")
        return clean

    @field_validator("weight_unit")
    @classmethod
    def validate_weight_unit(cls, v: str) -> str:
        clean = v.lower().strip()
        if clean not in ["kg", "lb"]:
            raise ValueError("Weight unit must be 'kg' or 'lb'")
        return clean

    @field_validator("height")
    @classmethod
    def validate_height_bounds(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Height must be a positive number greater than zero")
        if v > 300: # cm or ft safety upper bound check
            raise ValueError("Height value exceeds realistic limits (max 300 cm / 10 ft)")
        return v

    @field_validator("weight")
    @classmethod
    def validate_weight_bounds(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Weight must be a positive number greater than zero")
        if v > 500: # kg or lb safety upper bound check
            raise ValueError("Weight value exceeds realistic limits (max 500 kg / 1100 lb)")
        return v

class BMIResponse(BaseModel):
    id: int
    bmi: float
    category: str
    height: float
    height_unit: str
    weight: float
    weight_unit: str
    height_m: float
    weight_kg: float
    created_at: datetime

    class Config:
        from_attributes = True
