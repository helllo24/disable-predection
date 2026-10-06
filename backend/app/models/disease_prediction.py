from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class DiseasePrediction(Base):
    __tablename__ = "disease_predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    symptoms = Column(Text, nullable=False)  # JSON or comma-separated string of selected symptoms
    predicted_disease = Column(String(100), nullable=False)
    probability = Column(Float, nullable=False)  # Confidence score (0.0 to 1.0)
    model_name = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="disease_prediction_records")
