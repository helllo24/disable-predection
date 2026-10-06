import os
import json
import joblib
import pandas as pd
from typing import Dict, Any

# Resolve absolute paths to project root ml/ directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MODEL_FILE = os.path.join(BASE_DIR, "ml", "models", "diabetes_model.pkl")
METADATA_FILE = os.path.join(BASE_DIR, "ml", "models", "diabetes_model_metadata.json")

class DiabetesMLService:
    _instance = None
    _model = None
    _metadata = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DiabetesMLService()
            cls._instance.load_model()
        return cls._instance

    def load_model(self):
        """Loads trained model pipeline and metadata into memory once."""
        if not os.path.exists(MODEL_FILE) or not os.path.exists(METADATA_FILE):
            raise FileNotFoundError(f"Trained model files not found at {MODEL_FILE}. Please run ml/training/train_diabetes.py first.")

        print(f"Loading trained ML model from {MODEL_FILE}...")
        self._model = joblib.load(MODEL_FILE)

        with open(METADATA_FILE, 'r') as f:
            self._metadata = json.load(f)

        print(f"Loaded {self._metadata.get('selected_model', 'ML')} Model successfully.")

    def predict(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs prediction on feature input dictionary without retraining."""
        if self._model is None:
            self.load_model()

        features = [
            'Pregnancies',
            'Glucose',
            'BloodPressure',
            'SkinThickness',
            'Insulin',
            'BMI',
            'DiabetesPedigreeFunction',
            'Age'
        ]

        row_vals = [
            float(feature_data['pregnancies']),
            float(feature_data['glucose']),
            float(feature_data['blood_pressure']),
            float(feature_data['skin_thickness']),
            float(feature_data['insulin']),
            float(feature_data['bmi']),
            float(feature_data['diabetes_pedigree_function']),
            float(feature_data['age'])
        ]

        X_df = pd.DataFrame([row_vals], columns=features)

        # Handle medically implausible 0 values during inference (replace 0 with NaN for pipeline imputer)
        for col in ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']:
            if X_df[col].iloc[0] == 0:
                X_df[col] = float('nan')

        prediction = int(self._model.predict(X_df)[0])
        
        probability = 0.5
        if hasattr(self._model, "predict_proba"):
            probas = self._model.predict_proba(X_df)
            probability = float(probas[0][1])

        risk_label = "Higher predicted risk" if prediction == 1 else "Lower predicted risk"
        model_name = self._metadata.get("selected_model", "XGBoost")

        return {
            "prediction": prediction,
            "risk": risk_label,
            "probability": round(probability, 4),
            "model": model_name
        }

diabetes_ml_service = DiabetesMLService.get_instance()
