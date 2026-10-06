import os
import json
import joblib
import pandas as pd
from typing import List, Dict, Any

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MODEL_FILE = os.path.join(BASE_DIR, "ml", "models", "disease_model.pkl")
ENCODER_FILE = os.path.join(BASE_DIR, "ml", "models", "disease_label_encoder.pkl")
METADATA_FILE = os.path.join(BASE_DIR, "ml", "models", "disease_model_metadata.json")

class DiseaseMLService:
    _instance = None
    _model = None
    _label_encoder = None
    _metadata = None
    _symptoms_list = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DiseaseMLService()
            cls._instance.load_model()
        return cls._instance

    def load_model(self):
        """Loads trained disease classification model, label encoder, and metadata into memory ONCE."""
        if not os.path.exists(MODEL_FILE) or not os.path.exists(METADATA_FILE):
            print("Disease ML files missing. Training models now...")
            from ml.training.train_disease import train_and_evaluate_disease_models
            train_and_evaluate_disease_models()

        print(f"Loading trained Disease ML model from {MODEL_FILE}...")
        self._model = joblib.load(MODEL_FILE)
        self._label_encoder = joblib.load(ENCODER_FILE)

        with open(METADATA_FILE, 'r') as f:
            self._metadata = json.load(f)

        self._symptoms_list = self._metadata.get("dataset", {}).get("symptoms_list", [])
        print(f"Loaded {self._metadata.get('selected_model', 'ML')} Model with {len(self._symptoms_list)} symptoms.")

    def get_all_symptoms(self) -> List[str]:
        """Returns the list of 132 supported symptom identifiers."""
        if not self._symptoms_list:
            self.load_model()
        return self._symptoms_list

    def predict(self, selected_symptoms: List[str]) -> Dict[str, Any]:
        """Performs multi-class disease prediction on user-selected symptoms."""
        if self._model is None:
            self.load_model()

        # Sanitize selected symptoms
        clean_selected = set(s.strip().lower() for s in selected_symptoms if s.strip())

        # Construct binary feature vector matching the 132 features
        feature_dict = {}
        for feature in self._symptoms_list:
            feature_dict[feature] = [1 if feature.lower() in clean_selected else 0]

        X_df = pd.DataFrame(feature_dict)[self._symptoms_list]

        # Model Inference
        pred_class_idx = int(self._model.predict(X_df)[0])
        predicted_disease = self._label_encoder.inverse_transform([pred_class_idx])[0]

        probability = 0.95
        if hasattr(self._model, "predict_proba"):
            probas = self._model.predict_proba(X_df)[0]
            probability = float(probas[pred_class_idx])

        model_name = self._metadata.get("selected_model", "Logistic Regression")

        return {
            "predicted_disease": str(predicted_disease),
            "probability": round(probability, 4),
            "model": model_name,
            "symptoms": list(clean_selected)
        }

disease_ml_service = DiseaseMLService.get_instance()
