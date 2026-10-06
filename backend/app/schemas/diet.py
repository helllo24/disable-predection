from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class DietRecommendationRequest(BaseModel):
    dietary_preference: str = Field(..., description="Vegetarian, Non-Vegetarian, or Vegan")
    goal: str = Field(..., description="Health goal (e.g. Weight Management, Weight Loss, General Healthy Eating)")
    custom_allergies: Optional[str] = Field("", description="Comma-separated food allergies")

class DietRecommendationResponse(BaseModel):
    id: Optional[int] = None
    dietary_preference: str
    goal: str
    allergies: Optional[str] = ""
    recommendations: Dict[str, Any]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
