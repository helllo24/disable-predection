from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    specialization = Column(String(100), nullable=False)
    qualification = Column(String(100), nullable=False)
    clinic_hospital = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    available_days = Column(String(255), nullable=False)  # e.g., "Monday, Wednesday, Friday"
    available_times = Column(String(255), nullable=False)  # e.g., "09:00 AM - 01:00 PM"
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
