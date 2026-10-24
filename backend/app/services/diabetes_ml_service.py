
import os
import sys
import traceback
from typing import Any, Dict

# Project root: smart-healthcare-assistant/
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

ML_MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")
ML_EVALUATION_DIR = os.path.join(BASE_DIR, "ml", "evaluation")

# Add project directories to Python's import path
for directory in (ML_MODELS_DIR, ML_EVALUATION_DIR):
    if directory not in sys.path:
        sys.path.insert(0, directory)

# Import the production inference engine and preserve the real error
_IMPORT_ERROR = None

try:
    from production_inference import (
        get_production_engine,
        predict_patient_risk,
    )
except Exception as exc:
    get_production_engine = None
    predict_patient_risk = None
    _IMPORT_ERROR = exc

    print("ERROR: Could not import production_inference.")
    traceback.print_exc()


class DiabetesMLService:
    _instance = None
    _engine = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            instance = cls()
            instance.load_model()
            cls._instance = instance

        return cls._instance

    def load_model(self):
        """Load the production inference engine into memory."""
        if self._engine is not None:
            return

        print("Loading production-ready ML model package...")

        if get_production_engine is None:
            raise RuntimeError(
                "Failed to import ProductionInferenceEngine. "
                "Check the original traceback printed above."
            ) from _IMPORT_ERROR

        try:
            self._engine = get_production_engine()

            if self._engine is None:
                raise RuntimeError(
                    "get_production_engine() returned None."
                )

            manifest = getattr(self._engine, "manifest", {}) or {}
            algorithm = manifest.get(
                "algorithm", "Unknown model algorithm"
            )

            print(
                f"Loaded {algorithm} production model successfully."
            )

        except Exception:
            print("ERROR: Failed to initialize the production model.")
            traceback.print_exc()
            self._engine = None
            raise

    def predict(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict estimated diabetes risk for a patient."""
        if self._engine is None:
            self.load_model()

        # Validate and normalize incoming data.
        if not isinstance(feature_data, dict):
            raise TypeError("feature_data must be a dictionary.")

        # New 100K EHR input schema
        required_fields = {
            "gender",
            "age",
            "hypertension",
            "heart_disease",
            "smoking_history",
            "bmi",
            "HbA1c_level",
            "blood_glucose_level",
        }

        if required_fields.issubset(feature_data.keys()):
            patient_input = {
                "gender": str(feature_data["gender"]),
                "age": float(feature_data["age"]),
                "hypertension": int(feature_data["hypertension"]),
                "heart_disease": int(feature_data["heart_disease"]),
                "smoking_history": str(feature_data["smoking_history"]),
                "bmi": float(feature_data["bmi"]),
                "HbA1c_level": float(feature_data["HbA1c_level"]),
                "blood_glucose_level": int(
                    feature_data["blood_glucose_level"]
                ),
            }

        else:
            # Legacy Pima-style input compatibility.
            glucose = float(feature_data.get("glucose", 100.0))
            age = float(feature_data.get("age", 50.0))
            bmi = float(feature_data.get("bmi", 28.0))
            blood_pressure = float(
                feature_data.get("blood_pressure", 80.0)
            )

            # Approximate HbA1c from glucose. This is only an estimate,
            # not a substitute for a measured HbA1c result.
            estimated_hba1c = round((glucose + 46.7) / 28.7, 1)

            patient_input = {
                "gender": "Female",
                "age": age,
                "hypertension": int(blood_pressure > 90),
                "heart_disease": 0,
                "smoking_history": "never",
                "bmi": bmi,
                "HbA1c_level": estimated_hba1c,
                "blood_glucose_level": int(glucose),
            }

        # Run the production inference engine.
        result = self._engine.predict_risk(patient_input)

        if not isinstance(result, dict):
            raise RuntimeError(
                "The inference engine returned an unexpected result."
            )

        pred_val = result.get(
            "prediction",
            result.get("binary_classification", 0),
        )

        risk_label = result.get(
            "risk_category",
            result.get("classification_label", "Unknown"),
        )

        prob_val = result.get(
            "probability",
            result.get("estimated_risk_probability"),
        )

        if prob_val is None:
            raise KeyError(
                "The inference result contains no probability field."
            )

        prob_val = float(prob_val)

        if not 0.0 <= prob_val <= 1.0:
            raise ValueError(
                f"Invalid risk probability returned by model: {prob_val}"
            )

        manifest = getattr(self._engine, "manifest", {}) or {}

        model_name = result.get(
            "algorithm",
            manifest.get("algorithm", "Unknown model algorithm"),
        )

        return {
            "prediction": pred_val,
            "risk": risk_label,
            "probability": prob_val,
            "risk_percentage": round(prob_val * 100, 1),
            "risk_category": risk_label,
            "threshold": result.get("threshold", 0.30),
            "model": model_name,
            "model_version": result.get(
                "model_version",
                manifest.get("model_version", "1.0.0"),
            ),
            "top_contributing_features": result.get(
                "top_contributing_features", []
            ),
            "disclaimer": result.get(
                "disclaimer",
                "This model provides an estimated risk probability "
                "for clinical decision support and does not provide "
                "an automated medical diagnosis.",
            ),
        }


# Initialize the service when this module is imported.
diabetes_ml_service = DiabetesMLService.get_instance()
