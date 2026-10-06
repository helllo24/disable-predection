from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ContributingFactor(BaseModel):
    factor: str
    detail: str
    points: float

class HealthRiskResponse(BaseModel):
    id: Optional[int] = None
    score: int = Field(..., ge=0, le=100)
    category: str
    contributing_factors: List[ContributingFactor]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
