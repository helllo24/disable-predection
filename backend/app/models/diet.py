from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class DietRecommendation(Base):
    __tablename__ = "diet_recommendations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    dietary_preference = Column(String(50), nullable=False)  # "Vegetarian", "Non-Vegetarian", "Vegan"
    goal = Column(String(100), nullable=False)  # "Weight Management", "Healthy Eating", "Weight Loss"
    allergies = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=False)  # JSON serialized recommendation dictionary
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="diet_recommendations")
