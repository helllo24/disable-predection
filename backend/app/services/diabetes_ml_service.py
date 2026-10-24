
# import os
# import traceback
# from typing import Any, Dict

# import joblib
# import numpy as np
# import pandas as pd


# BASE_DIR = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), "..", "..", "..")
# )

# MODEL_PATH = os.path.join(
#     BASE_DIR,
#     "ml",
#     "models",
#     "pima",
#     "pima_diabetes_model.joblib",
# )

# DATASET_PATH = os.path.join(
#     BASE_DIR,
#     "ml",
#     "datasets",
#     "diabetes.csv",
# )

# PIMA_FEATURES = [
#     "Pregnancies",
#     "Glucose",
#     "BloodPressure",
#     "SkinThickness",
#     "Insulin",
#     "BMI",
#     "DiabetesPedigreeFunction",
#     "Age",
# ]

# FEATURE_LABELS = {
#     "Pregnancies": "Pregnancies",
#     "Glucose": "Glucose",
#     "BloodPressure": "Blood Pressure",
#     "SkinThickness": "Skin Thickness",
#     "Insulin": "Insulin",
#     "BMI": "BMI",
#     "DiabetesPedigreeFunction": "Diabetes Pedigree Function",
#     "Age": "Age",
# }


# class DiabetesMLService:
#     _instance = None

#     def __init__(self):
#         self._artifact = None
#         self._model = None
#         self._threshold = 0.5
#         self._features = PIMA_FEATURES.copy()
#         self._shap_background = None

#     @classmethod
#     def get_instance(cls):
#         if cls._instance is None:
#             instance = cls()
#             instance.load_model()
#             cls._instance = instance
#         return cls._instance

#     def load_model(self):
#         """Load the trained PIMA model artifact."""
#         if self._model is not None:
#             return

#         if not os.path.isfile(MODEL_PATH):
#             raise FileNotFoundError(
#                 f"PIMA model artifact not found: {MODEL_PATH}"
#             )

#         try:
#             artifact = joblib.load(MODEL_PATH)

#             if not isinstance(artifact, dict) or "model" not in artifact:
#                 raise ValueError(
#                     "Expected a model artifact containing the 'model' key."
#                 )

#             model = artifact["model"]
#             features = artifact.get("features", PIMA_FEATURES)

#             if list(features) != PIMA_FEATURES:
#                 raise ValueError(
#                     f"Unexpected PIMA feature order: {features}"
#                 )

#             if not hasattr(model, "predict_proba"):
#                 raise ValueError(
#                     "Loaded model does not support predict_proba()."
#                 )

#             classes = list(model.classes_)
#             if 1 not in classes:
#                 raise ValueError(
#                     "Model does not contain positive class 1."
#                 )

#             self._artifact = artifact
#             self._model = model
#             self._features = list(features)
#             self._threshold = float(
#                 artifact.get("decision_threshold", 0.5)
#             )

#             print("PIMA diabetes model loaded successfully.")
#             print(f"Model path: {MODEL_PATH}")
#             print(f"Decision threshold: {self._threshold}")

#         except Exception:
#             print("Failed to load PIMA model.")
#             traceback.print_exc()
#             self._artifact = None
#             self._model = None
#             raise

#     def _positive_probability(self, data):
#         """Return calibrated probability for diabetes-positive class."""
#         if isinstance(data, pd.DataFrame):
#             frame = data.loc[:, self._features]
#         else:
#             frame = pd.DataFrame(data, columns=self._features)

#         probabilities = self._model.predict_proba(frame)
#         positive_index = list(self._model.classes_).index(1)

#         return probabilities[:, positive_index]

#     def _load_shap_background(self):
#         """Load representative feature rows for SHAP explanations."""
#         if self._shap_background is not None:
#             return self._shap_background

#         if not os.path.isfile(DATASET_PATH):
#             print(f"SHAP dataset not found: {DATASET_PATH}")
#             return None

#         try:
#             dataset = pd.read_csv(DATASET_PATH)

#             missing = [
#                 feature
#                 for feature in self._features
#                 if feature not in dataset.columns
#             ]

#             if missing:
#                 print(f"SHAP dataset is missing columns: {missing}")
#                 return None

#             background = dataset[self._features].copy()

#             for feature in self._features:
#                 background[feature] = pd.to_numeric(
#                     background[feature], errors="coerce"
#                 )

#             background = background.replace(
#                 [np.inf, -np.inf], np.nan
#             ).dropna()

#             if background.empty:
#                 print("SHAP background dataset has no valid rows.")
#                 return None

#             # Deterministic sample to reduce explanation cost.
#             background = background.sample(
#                 n=min(50, len(background)),
#                 random_state=42,
#             ).reset_index(drop=True)

#             self._shap_background = background
#             return background

#         except Exception:
#             print("Unable to load SHAP background dataset.")
#             traceback.print_exc()
#             return None



#     def _get_shap_explanation(self, input_df):
#         """
#         Explain the positive-class probability.

#         SHAP contributions are on the probability scale because the
#         explained function returns calibrated positive-class probabilities.
#         """
#         try:
#             import shap

#             background = self._load_shap_background()
#             if background is None:
#                 return []

#             explainer = shap.PermutationExplainer(
#                 self._positive_probability,
#                 background,
#                 feature_names=self._features,
#                 seed=42,
#             )

#             explanation = explainer(
#                 input_df[self._features],
#                 max_evals=2 * len(self._features) + 1,
#                 silent=True,
#             )

#             values = np.asarray(explanation.values)

#             # A single patient and a single explained output are expected.
#             if values.ndim == 3:
#                 values = values[0, :, 0]
#             elif values.ndim == 2:
#                 values = values[0]

#             if values.ndim != 1 or len(values) != len(self._features):
#                 print(
#                     "Unexpected SHAP output shape:",
#                     values.shape,
#                 )
#                 return []

#             contributions = []

#             for feature, actual_value, shap_value in zip(
#                 self._features,
#                 input_df.iloc[0].tolist(),
#                 values,
#             ):
#                 shap_value = float(shap_value)

#                 if not np.isfinite(shap_value):
#                     continue

#                 contributions.append({
#                     "feature_name": FEATURE_LABELS.get(
#                         feature, feature
#                     ),
#                     "feature": feature,
#                     "actual_value": float(actual_value),
#                     "shap_contribution": shap_value,
#                 })

#             contributions.sort(
#                 key=lambda item: abs(item["shap_contribution"]),
#                 reverse=True,
#             )

#             return contributions

#         except Exception as exc:
#             # Never prevent the prediction itself if SHAP fails.
#             print(f"SHAP explanation failed: {exc}")
#             traceback.print_exc()
#             return []

#     def predict(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
#         """Predict diabetes probability and explain the model output."""
#         if self._model is None:
#             self.load_model()

#         if not isinstance(feature_data, dict):
#             raise TypeError("feature_data must be a dictionary.")

#         aliases = {
#             "Pregnancies": ["Pregnancies", "pregnancies"],
#             "Glucose": ["Glucose", "glucose"],
#             "BloodPressure": [
#                 "BloodPressure",
#                 "blood_pressure",
#                 "bloodPressure",
#             ],
#             "SkinThickness": [
#                 "SkinThickness",
#                 "skin_thickness",
#                 "skinThickness",
#             ],
#             "Insulin": ["Insulin", "insulin"],
#             "BMI": ["BMI", "bmi"],
#             "DiabetesPedigreeFunction": [
#                 "DiabetesPedigreeFunction",
#                 "diabetes_pedigree_function",
#                 "diabetesPedigreeFunction",
#             ],
#             "Age": ["Age", "age"],
#         }

#         patient_input = {}

#         for feature in self._features:
#             matching_key = next(
#                 (
#                     key for key in aliases[feature]
#                     if key in feature_data
#                 ),
#                 None,
#             )

#             if matching_key is None:
#                 raise ValueError(
#                     f"Missing required feature: {feature}"
#                 )

#             try:
#                 value = float(feature_data[matching_key])
#             except (TypeError, ValueError):
#                 raise ValueError(
#                     f"Feature '{feature}' must be numeric."
#                 ) from None

#             if not np.isfinite(value):
#                 raise ValueError(
#                     f"Feature '{feature}' must be finite."
#                 )

#             if value < 0:
#                 raise ValueError(
#                     f"Feature '{feature}' cannot be negative."
#                 )

#             patient_input[feature] = value

#         input_df = pd.DataFrame(
#             [patient_input],
#             columns=self._features,
#         )

#         probability = float(self._positive_probability(input_df)[0])

#         if not np.isfinite(probability) or not 0 <= probability <= 1:
#             raise ValueError(
#                 f"Invalid probability returned by model: {probability}"
#             )

#         prediction = int(probability >= self._threshold)

#         if probability < 0.30:
#             risk_category = "Low"
#         elif probability < 0.60:
#             risk_category = "Moderate"
#         else:
#             risk_category = "High"

#         # Explanation failures return [] without breaking the prediction.
#         shap_features = self._get_shap_explanation(input_df)

#         return {
#             "prediction": prediction,
#             "risk": risk_category,
#             "probability": probability,
#             "risk_percentage": round(probability * 100, 1),
#             "risk_category": risk_category,
#             "threshold": self._threshold,
#             "model": "PIMA Calibrated Classifier",
#             "model_version": "pima-1.0.0",
#             "top_contributing_features": shap_features,
#             "disclaimer": (
#                 "This model provides an estimated diabetes risk, "
#                 "not a medical diagnosis. It was trained on the PIMA "
#                 "dataset and may not generalize to every population. "
#                 "SHAP values explain the model output and do not prove "
#                 "causation. Consult a qualified healthcare professional."
#             ),
#         }


# # Initialize the service when this module is imported.
# diabetes_ml_service = DiabetesMLService.get_instance()

import os
import traceback
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "models",
    "pima",
    "pima_diabetes_model.joblib",
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "datasets",
    "diabetes.csv",
)

PIMA_FEATURES = [
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age",
]

FEATURE_LABELS = {
    "Pregnancies": "Pregnancies",
    "Glucose": "Glucose",
    "BloodPressure": "Blood Pressure",
    "SkinThickness": "Skin Thickness",
    "Insulin": "Insulin",
    "BMI": "BMI",
    "DiabetesPedigreeFunction": "Diabetes Pedigree Function",
    "Age": "Age",
}


class DiabetesMLService:
    _instance = None

    def __init__(self):
        self._artifact = None
        self._model = None
        self._threshold = 0.5
        self._features = PIMA_FEATURES.copy()
        self._shap_background = None
        self._shap_explainer = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            instance = cls()
            instance.load_model()
            cls._instance = instance

        return cls._instance

    def load_model(self):
        """Load the trained PIMA model artifact."""
        if self._model is not None:
            return

        if not os.path.isfile(MODEL_PATH):
            raise FileNotFoundError(
                f"PIMA model artifact not found: {MODEL_PATH}"
            )

        try:
            artifact = joblib.load(MODEL_PATH)

            if not isinstance(artifact, dict):
                raise ValueError(
                    "Expected a dictionary model artifact."
                )

            if "model" not in artifact:
                raise ValueError(
                    "Model artifact must contain the 'model' key."
                )

            model = artifact["model"]
            features = artifact.get("features", PIMA_FEATURES)

            if list(features) != PIMA_FEATURES:
                raise ValueError(
                    f"Unexpected PIMA feature order: {features}"
                )

            if not hasattr(model, "predict_proba"):
                raise ValueError(
                    "Loaded model must support predict_proba()."
                )

            if not hasattr(model, "classes_"):
                raise ValueError(
                    "Loaded model must expose classes_."
                )

            classes = list(model.classes_)

            if 1 not in classes:
                raise ValueError(
                    "Model does not contain positive class 1."
                )

            threshold = float(
                artifact.get("decision_threshold", 0.5)
            )

            if not 0 < threshold < 1:
                raise ValueError(
                    "Decision threshold must be between 0 and 1."
                )

            self._artifact = artifact
            self._model = model
            self._features = list(features)
            self._threshold = threshold

            print("PIMA diabetes model loaded successfully.")
            print(f"Model path: {MODEL_PATH}")
            print(f"Decision threshold: {self._threshold}")

        except Exception:
            print("Failed to load PIMA model.")
            traceback.print_exc()
            self._artifact = None
            self._model = None
            raise

    def _positive_probability(self, data):
        """
        Return the model's probability for positive class 1.

        The explainer uses the same function as the prediction.
        """
        if isinstance(data, pd.DataFrame):
            frame = data.loc[:, self._features].copy()
        else:
            frame = pd.DataFrame(
                data,
                columns=self._features,
            )

        probabilities = self._model.predict_proba(frame)

        positive_index = list(
            self._model.classes_
        ).index(1)

        return probabilities[:, positive_index]

    def _load_shap_background(self):
        """Load representative rows for SHAP background data."""
        if self._shap_background is not None:
            return self._shap_background

        if not os.path.isfile(DATASET_PATH):
            print(
                f"SHAP dataset not found: {DATASET_PATH}"
            )
            return None

        try:
            dataset = pd.read_csv(DATASET_PATH)

            missing = [
                feature
                for feature in self._features
                if feature not in dataset.columns
            ]

            if missing:
                print(
                    f"SHAP dataset missing columns: {missing}"
                )
                return None

            background = dataset[self._features].copy()

            for feature in self._features:
                background[feature] = pd.to_numeric(
                    background[feature],
                    errors="coerce",
                )

            background = background.replace(
                [np.inf, -np.inf],
                np.nan,
            ).dropna()

            if background.empty:
                print(
                    "SHAP background dataset has no valid rows."
                )
                return None

            background = background.sample(
                n=min(50, len(background)),
                random_state=42,
            ).reset_index(drop=True)

            self._shap_background = background

            print(
                "SHAP background loaded:",
                len(background),
                "rows",
            )

            return background

        except Exception:
            print("Unable to load SHAP background dataset.")
            traceback.print_exc()
            return None

    def _get_shap_explainer(self):
        """Create the explainer once and reuse it."""
        if self._shap_explainer is not None:
            return self._shap_explainer

        try:
            import shap

            background = self._load_shap_background()

            if background is None:
                return None

            self._shap_explainer = shap.PermutationExplainer(
                self._positive_probability,
                background,
                feature_names=self._features,
                seed=42,
            )

            print("SHAP explainer initialized successfully.")

            return self._shap_explainer

        except Exception as exc:
            print(f"SHAP initialization failed: {exc}")
            traceback.print_exc()
            return None

    def _get_shap_explanation(self, input_df):
        """
        Explain the positive-class probability for one patient.

        Returned SHAP values are in probability-output units.
        """
        try:
            explainer = self._get_shap_explainer()

            if explainer is None:
                return []

            explanation = explainer(
                input_df[self._features],
                max_evals=2 * len(self._features) + 1,
                silent=True,
            )

            values = np.asarray(explanation.values)

            # Expected output: (1, number_of_features).
            if values.ndim == 3:
                values = values[0, :, 0]
            elif values.ndim == 2:
                values = values[0]

            if (
                values.ndim != 1
                or len(values) != len(self._features)
            ):
                print(
                    "Unexpected SHAP output shape:",
                    values.shape,
                )
                return []

            contributions = []

            for feature, actual_value, shap_value in zip(
                self._features,
                input_df.iloc[0].tolist(),
                values,
            ):
                shap_value = float(shap_value)

                if not np.isfinite(shap_value):
                    continue

                # Keep the original feature name for frontend mapping.
                contributions.append({
                    "feature_name": feature,
                    "feature": feature,
                    "actual_value": float(actual_value),
                    "shap_contribution": shap_value,
                })

            contributions.sort(
                key=lambda item: abs(
                    item["shap_contribution"]
                ),
                reverse=True,
            )

            return contributions

        except Exception as exc:
            print(f"SHAP explanation failed: {exc}")
            traceback.print_exc()
            return []

    def predict(
        self,
        feature_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Predict diabetes probability and explain model output."""
        if self._model is None:
            self.load_model()

        if not isinstance(feature_data, dict):
            raise TypeError(
                "feature_data must be a dictionary."
            )

        aliases = {
            "Pregnancies": [
                "Pregnancies",
                "pregnancies",
            ],
            "Glucose": [
                "Glucose",
                "glucose",
            ],
            "BloodPressure": [
                "BloodPressure",
                "blood_pressure",
                "bloodPressure",
            ],
            "SkinThickness": [
                "SkinThickness",
                "skin_thickness",
                "skinThickness",
            ],
            "Insulin": [
                "Insulin",
                "insulin",
            ],
            "BMI": [
                "BMI",
                "bmi",
            ],
            "DiabetesPedigreeFunction": [
                "DiabetesPedigreeFunction",
                "diabetes_pedigree_function",
                "diabetesPedigreeFunction",
            ],
            "Age": [
                "Age",
                "age",
            ],
        }

        patient_input = {}

        for feature in self._features:
            matching_key = next(
                (
                    key
                    for key in aliases[feature]
                    if key in feature_data
                ),
                None,
            )

            if matching_key is None:
                raise ValueError(
                    f"Missing required feature: {feature}"
                )

            try:
                value = float(feature_data[matching_key])
            except (TypeError, ValueError):
                raise ValueError(
                    f"Feature '{feature}' must be numeric."
                ) from None

            if not np.isfinite(value):
                raise ValueError(
                    f"Feature '{feature}' must be finite."
                )

            if value < 0:
                raise ValueError(
                    f"Feature '{feature}' cannot be negative."
                )

            patient_input[feature] = value

        input_df = pd.DataFrame(
            [patient_input],
            columns=self._features,
        )

        probability = float(
            self._positive_probability(input_df)[0]
        )

        if (
            not np.isfinite(probability)
            or not 0 <= probability <= 1
        ):
            raise ValueError(
                f"Invalid probability returned by model: {probability}"
            )

        prediction = int(
            probability >= self._threshold
        )

        if probability < 0.30:
            risk_category = "Low"
        elif probability < 0.60:
            risk_category = "Moderate"
        else:
            risk_category = "High"

        shap_features = self._get_shap_explanation(
            input_df
        )

        return {
            "prediction": prediction,
            "risk": risk_category,
            "probability": probability,
            "risk_percentage": round(
                probability * 100,
                1,
            ),
            "risk_category": risk_category,
            "threshold": self._threshold,
            "decision_threshold": self._threshold,
            "model": "PIMA Calibrated Classifier",
            "model_version": "pima-1.0.0",
            "top_contributing_features": shap_features,
            "shap_available": bool(shap_features),
            "disclaimer": (
                "This model provides an estimated diabetes risk, "
                "not a medical diagnosis. It was trained on the PIMA "
                "dataset and may not generalize to every population. "
                "SHAP values explain the model output and do not prove "
                "causation. Consult a qualified healthcare professional."
            ),
        }


diabetes_ml_service = DiabetesMLService.get_instance()

