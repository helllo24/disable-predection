import json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.bmi import BMIRecord
from app.models.diabetes import DiabetesPrediction
from app.models.disease_prediction import DiseasePrediction
from app.models.diet import DietRecommendation

def generate_diet_recommendation(
    user: User,
    dietary_preference: str,
    goal: str,
    custom_allergies: str,
    db: Session
) -> Dict[str, Any]:
    """
    Rule-based, personalized informational diet recommendation engine.
    Applies strict dietary preference filters, allergy exclusions, and health-metric adjustments.
    """
    pref_clean = dietary_preference.strip().title()
    if pref_clean not in ["Vegetarian", "Non-Vegetarian", "Vegan"]:
        pref_clean = "Vegetarian"

    goal_clean = goal.strip().title()

    # Combine profile allergies with custom input allergies
    allergy_list = []
    if user.allergies:
        allergy_list.extend([a.strip().lower() for a in user.allergies.split(",") if a.strip()])
    if custom_allergies:
        allergy_list.extend([a.strip().lower() for a in custom_allergies.split(",") if a.strip()])

    allergy_set = set(allergy_list)

    # 1. Base Food Pools
    food_groups = ["Whole Grains", "Fresh Vegetables", "Healthy Fats", "Hydration Essentials"]

    if pref_clean == "Vegan":
        food_groups.insert(1, "Plant-Based Proteins")
        raw_proteins = ["Lentils", "Chickpeas", "Black Beans", "Tofu", "Tempeh", "Edamame", "Quinoa", "Pumpkin Seeds"]
    elif pref_clean == "Vegetarian":
        food_groups.insert(1, "Dairy & Plant Proteins")
        raw_proteins = ["Lentils", "Chickpeas", "Paneer / Cottage Cheese", "Greek Yogurt", "Eggs", "Tofu", "Quinoa"]
    else:  # Non-Vegetarian
        food_groups.insert(1, "Lean Proteins")
        raw_proteins = ["Skinless Chicken Breast", "Salmon", "Tuna", "Eggs", "Turkey", "Lentils", "Greek Yogurt"]

    raw_carbs = ["Brown Rice", "Quinoa", "Steel-Cut Oats", "Sweet Potatoes", "Whole Wheat Bread", "Barley"]
    raw_veggies = ["Spinach", "Broccoli", "Kale", "Carrots", "Bell Peppers", "Cucumbers", "Tomatoes", "Zucchini"]
    raw_fats = ["Avocado", "Extra Virgin Olive Oil", "Chia Seeds", "Flaxseeds", "Almonds", "Walnuts", "Sunflower Seeds"]

    # 2. Apply Allergy Exclusions
    def filter_allergens(food_items: List[str]) -> List[str]:
        filtered = []
        for item in food_items:
            item_lower = item.lower()
            excluded = False
            for alg in allergy_set:
                if alg in item_lower:
                    excluded = True
                    break
                if alg == "dairy" and any(d in item_lower for d in ["milk", "cheese", "yogurt", "paneer", "butter"]):
                    excluded = True
                    break
                if alg == "nuts" and any(n in item_lower for n in ["almond", "walnut", "peanut", "cashew", "nut"]):
                    excluded = True
                    break
                if alg == "eggs" and "egg" in item_lower:
                    excluded = True
                    break
                if alg == "soy" and any(s in item_lower for s in ["tofu", "edamame", "tempeh", "soy"]):
                    excluded = True
                    break
            if not excluded:
                filtered.append(item)
        return filtered

    clean_proteins = filter_allergens(raw_proteins)
    clean_carbs = filter_allergens(raw_carbs)
    clean_veggies = filter_allergens(raw_veggies)
    clean_fats = filter_allergens(raw_fats)

    # Combine into recommended list
    foods_to_consider = clean_proteins[:3] + clean_carbs[:2] + clean_veggies[:3] + clean_fats[:2]

    # 3. Base Foods to Limit
    foods_to_limit = ["Refined Sugars & Sodas", "Deep Fried Foods", "Highly Processed Fast Food", "Excessive Salt & Sodium"]

    # 4. Check Health Conditions / Predictions for Adjustments
    latest_diabetes = (
        db.query(DiabetesPrediction)
        .filter(DiabetesPrediction.user_id == user.id)
        .order_by(DiabetesPrediction.id.desc())
        .first()
    )

    if latest_diabetes and (latest_diabetes.prediction == 1 or latest_diabetes.probability > 0.5):
        foods_to_limit.insert(0, "High-Glycemic Simple Sugars & Processed Juices")
        if "Low-GI Complex Carbs" not in food_groups:
            food_groups.append("Low-GI Complex Carbs")

    latest_bmi = (
        db.query(BMIRecord)
        .filter(BMIRecord.user_id == user.id)
        .order_by(BMIRecord.id.desc())
        .first()
    )

    if latest_bmi and latest_bmi.bmi_value >= 25.0:
        foods_to_limit.append("Calorie-Dense Sugary Confectionery")

    # 5. Meal Plan Recommendations based on Dietary Preference
    if pref_clean == "Vegan":
        meal_ideas = {
            "breakfast": "Steel-cut oatmeal topped with chia seeds, berries, and cinnamon",
            "lunch": "Quinoa bowl with grilled tofu, roasted chickpeas, mixed greens, and olive oil dressing",
            "dinner": "Lentil vegetable curry served with steamed broccoli and brown rice",
            "snacks": "Sliced apple with sunflower seed butter or roasted edamame"
        }
    elif pref_clean == "Vegetarian":
        meal_ideas = {
            "breakfast": "Scrambled eggs or Greek yogurt with berries and crushed flaxseeds",
            "lunch": "Paneer or tofu salad bowl with quinoa, avocado, tomatoes, and pumpkin seeds",
            "dinner": "Moong dal soup with sauteed spinach, carrots, and sweet potato",
            "snacks": "Fresh fruit with a handful of seeds or low-fat cottage cheese"
        }
    else:  # Non-Vegetarian
        meal_ideas = {
            "breakfast": "Poached eggs on whole-grain toast with avocado slices and spinach",
            "lunch": "Grilled chicken breast or salmon with brown rice and steamed broccoli",
            "dinner": "Pan-seared fish or turkey with roasted vegetables and quinoa",
            "snacks": "Greek yogurt or boiled eggs with cucumber sticks"
        }

    # 6. Hydration Guidance based on body weight
    weight_kg = user.weight if user.weight and user.weight > 0 else 65.0
    liters = round(weight_kg * 0.035, 1)
    hydration_guidance = f"Aim for approximately {liters} - {round(liters + 0.5, 1)} Liters (8-10 glasses) of fresh water daily to support metabolic function."

    return {
        "dietary_preference": pref_clean,
        "goal": goal_clean,
        "allergies_excluded": list(allergy_set),
        "recommended_food_groups": food_groups,
        "foods_to_consider": foods_to_consider,
        "foods_to_limit": foods_to_limit,
        "general_meal_ideas": meal_ideas,
        "hydration_guidance": hydration_guidance
    }
