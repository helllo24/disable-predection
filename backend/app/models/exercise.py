from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class ExerciseRecommendation(Base):
    __tablename__ = "exercise_recommendations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    fitness_level = Column(String(50), nullable=False)  # "Beginner", "Intermediate", "Advanced"
    goal = Column(String(100), nullable=False)  # "General Fitness", "Weight Management", "Mobility", "Strength"
    recommendations = Column(Text, nullable=False)  # JSON serialized recommendation dictionary
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="exercise_recommendations")
