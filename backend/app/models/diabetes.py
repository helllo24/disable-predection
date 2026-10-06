from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class DiabetesPrediction(Base):
    __tablename__ = "diabetes_predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pregnancies = Column(Integer, nullable=False)
    glucose = Column(Float, nullable=False)
    blood_pressure = Column(Float, nullable=False)
    skin_thickness = Column(Float, nullable=False)
    insulin = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)
    diabetes_pedigree_function = Column(Float, nullable=False)
    age = Column(Integer, nullable=False)
    prediction = Column(Integer, nullable=False)  # 0 or 1
    risk = Column(String(50), nullable=False)     # "Lower predicted risk" / "Higher predicted risk"
    probability = Column(Float, nullable=False)  # 0.0 to 1.0
    model_name = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="diabetes_predictions")
