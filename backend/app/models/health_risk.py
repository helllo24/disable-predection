from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class HealthRiskScore(Base):
    __tablename__ = "health_risk_scores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Integer, nullable=False)  # 0 to 100
    category = Column(String(50), nullable=False)  # "Low Risk", "Moderate Risk", "High Risk"
    contributing_factors = Column(Text, nullable=False)  # JSON serialized list of factors
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="health_risk_scores")
