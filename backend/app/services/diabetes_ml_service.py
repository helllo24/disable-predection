import os
import sys
import json
import joblib
import pandas as pd
from typing import Dict, Any

# Resolve absolute paths to project root ml/ directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(BASE_DIR, "ml", "models"))
sys.path.insert(0, os.path.join(BASE_DIR, "ml", "evaluation"))

try:
    from production_inference import get_production_engine, predict_patient_risk
except ImportError:
    get_production_engine = None
    predict_patient_risk = None

class DiabetesMLService:
    _instance = None
    _engine = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DiabetesMLService()
            cls._instance.load_model()
        return cls._instance

    def load_model(self):
        """Loads trained model pipeline and metadata from production package into memory."""
        print("Loading production-ready ML model package...")
        if get_production_engine is not None:
            self._engine = get_production_engine()
            print(f"Loaded {self._engine.manifest.get('algorithm', 'HistGradientBoosting')} Production Model successfully.")
        else:
            raise RuntimeError("Failed to import ProductionInferenceEngine from ml/models/production_inference.py")

    def predict(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs prediction on feature input dictionary using the loaded production package."""
        if self._engine is None:
            self.load_model()

        # Map input features to 100K EHR schema if legacy keys are passed
        patient_input = {}
        if "gender" in feature_data:
            patient_input = {
                "gender": feature_data["gender"],
                "age": feature_data["age"],
                "hypertension": feature_data["hypertension"],
                "heart_disease": feature_data["heart_disease"],
                "smoking_history": feature_data["smoking_history"],
                "bmi": feature_data["bmi"],
                "HbA1c_level": feature_data["HbA1c_level"],
                "blood_glucose_level": feature_data["blood_glucose_level"]
            }
        else:
            # Map legacy Pima fields to 100K schema defaults
            glucose = float(feature_data.get("glucose", 100.0))
            # Estimate HbA1c from plasma glucose using ADAG formula: HbA1c = (Glucose + 46.7) / 28.7
            estimated_hba1c = round((glucose + 46.7) / 28.7, 1)
            patient_input = {
                "gender": "Female",
                "age": float(feature_data.get("age", 50.0)),
                "hypertension": 1 if float(feature_data.get("blood_pressure", 80)) > 90 else 0,
                "heart_disease": 0,
                "smoking_history": "never",
                "bmi": float(feature_data.get("bmi", 28.0)),
                "HbA1c_level": estimated_hba1c,
                "blood_glucose_level": int(glucose)
            }

        # Run production inference engine
        result = self._engine.predict_risk(patient_input)

        pred_val = result.get("prediction", result.get("binary_classification", 0))
        risk_label = result.get("risk_category", result.get("classification_label", "Low Risk"))
        prob_val = result.get("probability", result.get("estimated_risk_probability", 0.0))
        model_name = result.get("algorithm", self._engine.manifest.get("algorithm", "HistGradientBoosting"))

        return {
            "prediction": pred_val,
            "risk": risk_label,
            "probability": prob_val,
            "risk_percentage": round(prob_val * 100, 1),
            "risk_category": risk_label,
            "threshold": result.get("threshold", 0.30),
            "model": model_name,
            "model_version": result.get("model_version", "1.0.0"),
            "top_contributing_features": result.get("top_contributing_features", []),
            "disclaimer": result.get("disclaimer", "This model outputs an estimated risk probability for clinical decision-support and does NOT provide an automated medical diagnosis.")
        }

diabetes_ml_service = DiabetesMLService.get_instance()

