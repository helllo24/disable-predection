from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(String(50), nullable=False)  # e.g., "10:00 AM"
    reason = Column(Text, nullable=False)
    status = Column(String(50), default="Scheduled", nullable=False)  # "Scheduled", "Completed", "Cancelled"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
