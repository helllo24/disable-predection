import json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.bmi import BMIRecord
from app.models.exercise import ExerciseRecommendation

def generate_exercise_recommendation(
    user: User,
    fitness_level: str,
    goal: str,
    db: Session
) -> Dict[str, Any]:
    """
    Rule-based, personalized informational exercise recommendation engine.
    Computes activity recommendations, frequency, duration, intensity, and safety guidance.
    """
    level_clean = fitness_level.strip().title()
    if level_clean not in ["Beginner", "Intermediate", "Advanced"]:
        level_clean = "Beginner"

    goal_clean = goal.strip().title()

    # 1. Level-Based Prescription Metrics
    if level_clean == "Beginner":
        frequency = "2 - 3 days per week (allow rest days between sessions)"
        duration = "20 - 30 minutes per session"
        intensity = "Light to Moderate intensity (RPE 3-5 out of 10; able to maintain a conversation comfortably)"
    elif level_clean == "Intermediate":
        frequency = "3 - 4 days per week"
        duration = "30 - 45 minutes per session"
        intensity = "Moderate intensity (RPE 5-7 out of 10; slightly breathless, able to speak in short sentences)"
    else:  # Advanced
        frequency = "4 - 5 days per week"
        duration = "45 - 60 minutes per session"
        intensity = "Moderate to Vigorous intensity (RPE 7-8 out of 10; challenging structured training)"

    # 2. Fetch Latest BMI Record for Joint-Impact Considerations
    latest_bmi = (
        db.query(BMIRecord)
        .filter(BMIRecord.user_id == user.id)
        .order_by(BMIRecord.id.desc())
        .first()
    )
    is_high_impact_sensitive = (user.age >= 60) or (latest_bmi and latest_bmi.bmi_value >= 30.0)

    # 3. Goal-Specific Activities
    activities = []
    if goal_clean == "Weight Management":
        if is_high_impact_sensitive:
            activities = ["Brisk Walking", "Stationary Cycling", "Water Aerobics", "Gentle Bodyweight Squats", "Seated Resistance Exercises"]
        else:
            activities = ["Brisk Walking / Light Jogging", "Cycling", "Low-Impact HIIT Circuits", "Bodyweight Squats & Lunges", "Swimming"]
    elif goal_clean == "Mobility":
        activities = ["Gentle Hatha / Chair Yoga", "Dynamic Joint Mobility Drills", "Standing Hamstring & Quadriceps Stretches", "Pilates Core Stability", "Walking"]
    elif goal_clean == "Strength":
        if level_clean == "Beginner":
            activities = ["Knee Push-ups", "Bodyweight Chair Squats", "Glute Bridges", "Resistance Band Rows", "Plank Holds (20-30s)"]
        else:
            activities = ["Standard Push-ups", "Dumbbell Squats & Lunges", "Dumbbell Overhead Press", "Bodyweight Pull-ups / Rows", "Core Planks"]
    else:  # General Fitness
        if is_high_impact_sensitive:
            activities = ["Brisk Walking", "Stationary Bike Cycling", "Water Aerobics", "Gentle Yoga & Stretching"]
        else:
            activities = ["Brisk Walking / Cycling", "Full-Body Bodyweight Circuit", "Light Swimming", "Yoga & Dynamic Stretching"]

    # 4. Mandatory Safety Guidance Notes
    safety_notes = [
        "Always perform a 5-10 minute light warm-up (e.g. slow walking, arm circles) before starting.",
        "Maintain adequate hydration by drinking water before, during, and after exercise.",
        "Listen to your body — stop immediately if you experience chest pain, dizziness, nausea, or acute joint pain.",
        "Consult a healthcare professional before starting a new exercise program, especially if you have a medical condition."
    ]

    if is_high_impact_sensitive:
        safety_notes.insert(1, "Focus on low-impact, joint-friendly movements to avoid excessive mechanical stress on knees and ankles.")

    return {
        "fitness_level": level_clean,
        "goal": goal_clean,
        "recommended_activities": activities,
        "frequency_guidance": frequency,
        "duration_guidance": duration,
        "intensity_guidance": intensity,
        "safety_notes": safety_notes
    }
