from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=False)
    password_hash = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    role = Column(String(20), nullable=False, default="PATIENT")
    is_active = Column(Boolean, nullable=False, default=True)

    # Patient Health Profile Fields
    height = Column(Float, nullable=True)  # in cm
    weight = Column(Float, nullable=True)  # in kg
    blood_group = Column(String(10), nullable=True)  # e.g., A+, O-
    allergies = Column(Text, nullable=True)
    existing_conditions = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    bmi_records = relationship("BMIRecord", back_populates="user", cascade="all, delete-orphan")
    diabetes_predictions = relationship("DiabetesPrediction", back_populates="user", cascade="all, delete-orphan")
    disease_prediction_records = relationship("DiseasePrediction", back_populates="user", cascade="all, delete-orphan")
    health_risk_scores = relationship("HealthRiskScore", back_populates="user", cascade="all, delete-orphan")
    diet_recommendations = relationship("DietRecommendation", back_populates="user", cascade="all, delete-orphan")
    exercise_recommendations = relationship("ExerciseRecommendation", back_populates="user", cascade="all, delete-orphan")
    medicine_reminders = relationship("MedicineReminder", back_populates="user", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")
    diabetes_complication_predictions = relationship("DiabetesComplicationPrediction", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}', active={self.is_active})>"
