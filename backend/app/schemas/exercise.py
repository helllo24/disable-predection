from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ExerciseRecommendationRequest(BaseModel):
    fitness_level: str = Field(..., description="Beginner, Intermediate, or Advanced")
    goal: str = Field(..., description="General Fitness, Weight Management, Mobility, or Strength")

class ExerciseRecommendationResponse(BaseModel):
    id: Optional[int] = None
    fitness_level: str
    goal: str
    recommendations: Dict[str, Any]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
