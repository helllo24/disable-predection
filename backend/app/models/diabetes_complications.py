from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class DiabetesComplicationPrediction(Base):
    __tablename__ = "diabetes_complication_predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # 6 Complication Risk Outputs
    heart_risk = Column(String(50), nullable=False)
    heart_probability = Column(Float, nullable=False)

    kidney_risk = Column(String(50), nullable=False)
    kidney_probability = Column(Float, nullable=False)

    neuropathy_risk = Column(String(50), nullable=False)
    neuropathy_probability = Column(Float, nullable=False)

    retinopathy_risk = Column(String(50), nullable=False)
    retinopathy_probability = Column(Float, nullable=False)

    foot_risk = Column(String(50), nullable=False)
    foot_probability = Column(Float, nullable=False)

    vascular_risk = Column(String(50), nullable=False)
    vascular_probability = Column(Float, nullable=False)

    overall_risk_summary = Column(String(100), nullable=False)
    input_parameters = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="diabetes_complication_predictions")

    def __repr__(self):
        return f"<DiabetesComplicationPrediction(id={self.id}, user_id={self.user_id}, overall='{self.overall_risk_summary}')>"
