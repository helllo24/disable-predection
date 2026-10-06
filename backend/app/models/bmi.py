from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class BMIRecord(Base):
    __tablename__ = "bmi_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    height = Column(Float, nullable=False)
    height_unit = Column(String(10), nullable=False, default="cm")
    weight = Column(Float, nullable=False)
    weight_unit = Column(String(10), nullable=False, default="kg")
    height_m = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    bmi_value = Column(Float, nullable=False)
    bmi_category = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="bmi_records")
