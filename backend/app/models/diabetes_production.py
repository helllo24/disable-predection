from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


class DiabetesProductionPrediction(Base):
    __tablename__ = "diabetes_production_predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    gender = Column(String(20), nullable=False)
    age = Column(Float, nullable=False)
    hypertension = Column(Integer, nullable=False)
    heart_disease = Column(Integer, nullable=False)
    smoking_history = Column(String(30), nullable=False)
    bmi = Column(Float, nullable=False)
    HbA1c_level = Column(Float, nullable=False)
    blood_glucose_level = Column(Float, nullable=False)
    prediction = Column(Integer, nullable=False)
    probability = Column(Float, nullable=False)
    risk_category = Column(String(50), nullable=False)
    threshold = Column(Float, nullable=False, default=0.30)
    model_version = Column(String(20), nullable=False, default="1.0.0")
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="diabetes_production_predictions")
