from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class DiseasePredictionRequest(BaseModel):
    symptoms: List[str] = Field(..., description="List of user-selected symptom identifiers")

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms_not_empty(cls, v: List[str]) -> List[str]:
        clean = [s.strip() for s in v if isinstance(s, str) and s.strip()]
        if not clean:
            raise ValueError("Please select at least one symptom to run disease prediction")
        return clean

class DiseasePredictionResponse(BaseModel):
    id: Optional[int] = None
    predicted_disease: str
    probability: float
    model: str
    symptoms: List[str]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
