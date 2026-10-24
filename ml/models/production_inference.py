
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

EVALUATION_DIR = os.path.join(BASE_DIR, "ml", "evaluation")

if EVALUATION_DIR not in sys.path:
    sys.path.insert(0, EVALUATION_DIR)

# Keep this import if your project contains this module/class.
# If it is genuinely missing, resolve that dependency separately.
from research_evaluation_metrics import CalibratedProbabilityModel


PACKAGE_DIR = os.path.join(
    BASE_DIR, "ml", "models", "production_package"
)
MANIFEST_PATH = os.path.join(PACKAGE_DIR, "model_manifest.json")
PREPROCESSOR_PATH = os.path.join(PACKAGE_DIR, "preprocessor.joblib")
MODEL_PATH = os.path.join(PACKAGE_DIR, "calibrated_model.joblib")


class ProductionInferenceEngine:
    def __init__(self):
        required_files = [
            MANIFEST_PATH,
            MODEL_PATH,
            PREPROCESSOR_PATH,
        ]

        missing_files = [
            path for path in required_files
            if not os.path.exists(path)
        ]

        if missing_files:
            raise FileNotFoundError(
                "Production package artifacts missing: "
                + ", ".join(missing_files)
            )

        with open(MANIFEST_PATH, "r", encoding="utf-8") as file:
            self.manifest = json.load(file)

        self.preprocessor = joblib.load(PREPROCESSOR_PATH)
        self.calibrated_model = joblib.load(MODEL_PATH)

        self.raw_feature_order = self.manifest["raw_feature_order"]
        self.schema = self.manifest["raw_feature_schema"]
        self.threshold = float(self.manifest["selected_threshold"])

        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError(
                f"Invalid selected threshold: {self.threshold}"
            )

        self._explainer = None

    def validate_input(self, patient_data):
        """
        Validate raw patient features and enforce training-time order.
        """
        if isinstance(patient_data, dict):
            df_input = pd.DataFrame([patient_data])
        elif isinstance(patient_data, pd.DataFrame):
            df_input = patient_data.copy()
        else:
            raise TypeError(
                "Patient input must be a dict or pandas DataFrame."
            )

        if df_input.empty:
            raise ValueError("Patient input cannot be empty.")

        missing_features = [
            feature for feature in self.raw_feature_order
            if feature not in df_input.columns
        ]

        if missing_features:
            raise ValueError(
                "Input validation error! Missing required features: "
                f"{missing_features}"
            )

        # This endpoint handles one patient at a time.
        if len(df_input) != 1:
            raise ValueError(
                "Exactly one patient record must be supplied."
            )

        df_ordered = df_input[self.raw_feature_order].copy()

        for feature in self.raw_feature_order:
            metadata = self.schema[feature]
            value = df_ordered[feature].iloc[0]

            if pd.isna(value):
                raise ValueError(
                    f"Feature '{feature}' cannot be empty."
                )

            if metadata["type"] == "string":
                allowed_values = metadata.get("allowed_values")

                if allowed_values and value not in allowed_values:
                    raise ValueError(
                        f"Invalid value '{value}' for '{feature}'. "
                        f"Allowed values: {allowed_values}"
                    )

            elif metadata["type"] in ("int", "float"):
                try:
                    numeric_value = float(value)
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"Feature '{feature}' must be numeric. "
                        f"Received: {value}"
                    ) from exc

                if not np.isfinite(numeric_value):
                    raise ValueError(
                        f"Feature '{feature}' must be finite."
                    )

                if metadata["type"] == "int" and not numeric_value.is_integer():
                    raise ValueError(
                        f"Feature '{feature}' must be an integer."
                    )

                if "range" in metadata:
                    min_value, max_value = metadata["range"]

                    if not min_value <= numeric_value <= max_value:
                        raise ValueError(
                            f"Feature '{feature}' value {numeric_value} "
                            f"is outside the configured range "
                            f"[{min_value}, {max_value}]."
                        )

                df_ordered[feature] = numeric_value

        return df_ordered

    @staticmethod
    def _positive_class_probability(model, transformed_input):
        """
        Return the probability associated with class label 1.
        Do not assume class 1 is always the second column.
        """
        probabilities = np.asarray(
            model.predict_proba(transformed_input),
            dtype=float,
        )

        if probabilities.ndim != 2 or probabilities.shape[0] != 1:
            raise ValueError(
                "Expected predict_proba to return one row of probabilities; "
                f"received shape {probabilities.shape}."
            )

        classes = getattr(model, "classes_", None)

        # Some calibrated wrappers expose classes on their base model.
        if classes is None and hasattr(model, "base_model"):
            classes = getattr(model.base_model, "classes_", None)

        if classes is None:
            # Binary classifiers commonly return [class 0, class 1].
            # This fallback is only safe if the wrapper preserves that order.
            if probabilities.shape[1] != 2:
                raise ValueError(
                    "Cannot determine positive class probability: "
                    "model does not expose classes_ and is not binary."
                )
            positive_index = 1
        else:
            classes = list(classes)

            if 1 not in classes:
                raise ValueError(
                    f"Positive class 1 not found in model classes: {classes}"
                )

            positive_index = classes.index(1)

        if positive_index >= probabilities.shape[1]:
            raise ValueError(
                "Model class index does not match probability output."
            )

        probability = float(probabilities[0, positive_index])

        if not np.isfinite(probability) or not 0.0 <= probability <= 1.0:
            raise ValueError(
                f"Invalid predicted probability: {probability}"
            )

        return probability, probabilities

    @staticmethod
    def _get_base_model_probability(model, transformed_input):
        """
        Diagnostic only: get the uncalibrated base-model probability for class 1.
        This must NOT replace the calibrated probability used by the application.
        """
        base_model = getattr(model, "base_model", None)
        if base_model is None:
            return None

        try:
            probabilities = np.asarray(
                base_model.predict_proba(transformed_input), dtype=float
            )
            classes = getattr(base_model, "classes_", None)

            if probabilities.ndim != 2 or probabilities.shape[0] != 1:
                return None

            if classes is not None:
                classes = list(classes)
                if 1 not in classes:
                    return None
                positive_index = classes.index(1)
            else:
                if probabilities.shape[1] != 2:
                    return None
                positive_index = 1

            if positive_index >= probabilities.shape[1]:
                return None

            value = float(probabilities[0, positive_index])
            if not np.isfinite(value) or not 0.0 <= value <= 1.0:
                return None
            return value
        except Exception as exc:
            print(f"[DEBUG] Could not obtain base-model probability: {exc}")
            return None

    def _get_shap_values(self, transformed_input):
        """
        Calculate SHAP values for one patient.
        Returns None if a compatible explainer cannot be created.
        """
        try:
            import shap

            if self._explainer is None:
                base_model = getattr(
                    self.calibrated_model,
                    "base_model",
                    self.calibrated_model,
                )
                self._explainer = shap.TreeExplainer(base_model)

            explanation = self._explainer.shap_values(transformed_input)

            if isinstance(explanation, list):
                if len(explanation) > 1:
                    values = np.asarray(explanation[1])
                elif len(explanation) == 1:
                    values = np.asarray(explanation[0])
                else:
                    return None

            else:
                values = np.asarray(explanation)

                # Common SHAP format: (samples, features, classes).
                if values.ndim == 3:
                    if values.shape[2] > 1:
                        values = values[:, :, 1]
                    else:
                        values = values[:, :, 0]

            # Expected shape: (1, number_of_features).
            if values.ndim == 2:
                if values.shape[0] != 1:
                    return None
                values = values[0]

            if values.ndim != 1:
                print(
                    "[SHAP Warning] Unexpected SHAP shape:",
                    values.shape,
                )
                return None

            if not np.all(np.isfinite(values)):
                print("[SHAP Warning] Non-finite SHAP values.")
                return None

            return values.astype(float)

        except Exception as exc:
            print(f"[SHAP Warning] Could not calculate SHAP values: {exc}")
            return None

    def _build_contributions(
        self,
        df_valid,
        transformed_input,
        shap_values,
    ):
        """
        Build explanations using original values for matching raw features.
        Transformed/one-hot features retain their transformed values.
        """
        transformed_features = self.manifest.get(
            "transformed_feature_order", []
        )

        if len(transformed_features) != len(shap_values):
            print(
                "[SHAP Warning] Feature count mismatch: "
                f"{len(transformed_features)} names vs "
                f"{len(shap_values)} SHAP values."
            )
            return []

        if isinstance(transformed_input, pd.DataFrame):
            transformed_values = transformed_input.iloc[0].to_numpy()
        else:
            transformed_values = np.asarray(transformed_input)[0]

        total_abs_shap = float(np.sum(np.abs(shap_values)))
        contributions = []

        for index, feature_name in enumerate(transformed_features):
            shap_value = float(shap_values[index])

            # Numerical or categorical feature retained without transformation.
            if feature_name in df_valid.columns:
                actual_value = df_valid.iloc[0][feature_name]

                if hasattr(actual_value, "item"):
                    actual_value = actual_value.item()

            else:
                # Try to map one-hot columns back to a raw categorical field.
                matching_feature = next(
                    (
                        raw_feature
                        for raw_feature in self.raw_feature_order
                        if feature_name.startswith(raw_feature + "_")
                    ),
                    None,
                )

                if matching_feature is not None:
                    category = feature_name[
                        len(matching_feature) + 1:
                    ]
                    patient_category = str(
                        df_valid.iloc[0][matching_feature]
                    )
                    actual_value = int(patient_category == category)

                else:
                    # Scaled/encoded features cannot always be mapped
                    # to raw units by name alone.
                    actual_value = transformed_values[index]

                    if hasattr(actual_value, "item"):
                        actual_value = actual_value.item()

                    if isinstance(actual_value, (int, float, np.number)):
                        actual_value = float(actual_value)

            relative_percentage = (
                abs(shap_value) / total_abs_shap * 100.0
                if total_abs_shap > 0
                else 0.0
            )

            if shap_value > 0:
                direction = "increased risk contribution"
            elif shap_value < 0:
                direction = "decreased risk contribution"
            else:
                direction = "no contribution"

            contributions.append({
                "feature": feature_name,
                "actual_value": actual_value,
                "shap_contribution": round(shap_value, 4),
                "direction": direction,
                "relative_contribution_pct": round(
                    relative_percentage, 2
                ),
            })

        contributions.sort(
            key=lambda item: abs(item["shap_contribution"]),
            reverse=True,
        )

        return contributions[:5]

    def predict_risk(self, patient_data):
        """
        Validate one patient, transform inputs, calculate calibrated
        probability, classify using the configured threshold, and explain.
        """
        df_valid = self.validate_input(patient_data)
        transformed_input = self.preprocessor.transform(df_valid)

        risk_probability, probability_array = (
            self._positive_class_probability(
                self.calibrated_model,
                transformed_input,
            )
        )

        # Diagnostics: compare uncalibrated and calibrated probabilities.
        # The application must continue to use the calibrated probability.
        base_probability = self._get_base_model_probability(
            self.calibrated_model, transformed_input
        )
        print("\\n========== RISK DEBUG ==========")
        print("[DEBUG] Calibrated class probabilities:", probability_array)
        print("[DEBUG] Calibrated positive-class probability:", repr(risk_probability))
        print("[DEBUG] Calibrated risk percentage:", risk_probability * 100.0)
        print("[DEBUG] Base-model (uncalibrated) probability:", repr(base_probability))
        print("[DEBUG] Decision threshold:", self.threshold)
        print("================================\\n")

        is_high_risk = risk_probability >= self.threshold

        if risk_probability < 0.30:
            risk_category = "Low Risk"
        elif risk_probability < 0.60:
            risk_category = "Moderate Risk"
        else:
            risk_category = "High Risk"

        top_contributing_features = []
        shap_values = self._get_shap_values(transformed_input)

        if shap_values is not None:
            top_contributing_features = self._build_contributions(
                df_valid,
                transformed_input,
                shap_values,
            )

        if not top_contributing_features:
            global_rankings = (
                self.manifest.get("shap_metadata", {})
                .get("global_rankings", [])
            )

            # Global rankings are not patient-specific SHAP explanations.
            # Do not label them as individual contributions.
            if global_rankings:
                print(
                    "[SHAP Warning] Returning no individual explanation; "
                    "global rankings are available in the manifest."
                )

        return {
            "prediction": 1 if is_high_risk else 0,
            "probability": risk_probability,
            "risk_category": risk_category,
            "threshold": self.threshold,
            "model_version": self.manifest.get(
                "model_version", "unknown"
            ),
            "top_contributing_features": top_contributing_features,
            "disclaimer": self.manifest.get(
                "clinical_disclaimer", ""
            ),
        }


# Global singleton instance for fast backend API import.
_engine = None


def get_production_engine():
    global _engine

    if _engine is None:
        _engine = ProductionInferenceEngine()

    return _engine


def predict_patient_risk(patient_dict):
    engine = get_production_engine()
    return engine.predict_risk(patient_dict)


if __name__ == "__main__":
    print("Testing Production Inference Engine...")

    test_patient = {
        "gender": "Female",
        "age": 55.0,
        "hypertension": 1,
        "heart_disease": 0,
        "smoking_history": "former",
        "bmi": 32.5,
        "HbA1c_level": 6.8,
        "blood_glucose_level": 160,
    }

    result = predict_patient_risk(test_patient)

    print("Prediction Result:")
    print(json.dumps(result, indent=2, default=str))
