import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

# Add evaluation directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, "ml", "evaluation"))
from research_evaluation_metrics import CalibratedProbabilityModel

PACKAGE_DIR = os.path.join(BASE_DIR, "ml", "models", "production_package")
MANIFEST_PATH = os.path.join(PACKAGE_DIR, "model_manifest.json")
PREPROCESSOR_PATH = os.path.join(PACKAGE_DIR, "preprocessor.joblib")
MODEL_PATH = os.path.join(PACKAGE_DIR, "calibrated_model.joblib")

class ProductionInferenceEngine:
    def __init__(self):
        if not os.path.exists(MANIFEST_PATH) or not os.path.exists(MODEL_PATH) or not os.path.exists(PREPROCESSOR_PATH):
            raise FileNotFoundError("Production package artifacts missing. Run ml/models/package_production_model.py first.")

        with open(MANIFEST_PATH, "r") as f:
            self.manifest = json.load(f)

        self.preprocessor = joblib.load(PREPROCESSOR_PATH)
        self.calibrated_model = joblib.load(MODEL_PATH)
        self.raw_feature_order = self.manifest["raw_feature_order"]
        self.schema = self.manifest["raw_feature_schema"]
        self.threshold = self.manifest["selected_threshold"]

    def validate_input(self, patient_data):
        """
        Enforces strict feature schema and ordering validation.
        Prevents incorrect feature order or missing fields from silently producing predictions.
        """
        if isinstance(patient_data, dict):
            df_input = pd.DataFrame([patient_data])
        elif isinstance(patient_data, pd.DataFrame):
            df_input = patient_data.copy()
        else:
            raise TypeError("Patient input must be a dict or pandas DataFrame.")

        # Check for missing required features
        missing_features = [f for f in self.raw_feature_order if f not in df_input.columns]
        if missing_features:
            raise ValueError(f"Input validation error! Missing required features: {missing_features}")

        # Enforce exact raw feature column ordering
        df_ordered = df_input[self.raw_feature_order].copy()

        # Validate feature types & value bounds
        for feat in self.raw_feature_order:
            feat_meta = self.schema[feat]
            val = df_ordered[feat].iloc[0]

            if feat_meta["type"] == "string" and "allowed_values" in feat_meta:
                if val not in feat_meta["allowed_values"]:
                    raise ValueError(f"Invalid value '{val}' for feature '{feat}'. Allowed values: {feat_meta['allowed_values']}")
            elif feat_meta["type"] in ["int", "float"]:
                try:
                    num_val = float(val)
                    if np.isnan(num_val) or np.isinf(num_val):
                        raise ValueError(f"Feature '{feat}' must be a finite numerical value. Received: {val}")
                    if "range" in feat_meta:
                        min_v, max_v = feat_meta["range"]
                        if num_val < min_v or num_val > max_v:
                            raise ValueError(f"Feature '{feat}' value {num_val} is outside valid physiological range [{min_v}, {max_v}].")
                except Exception as e:
                    raise ValueError(f"Feature '{feat}' validation error: {str(e)}")

        return df_ordered

    def predict_risk(self, patient_data):
        """
        Executes production prediction pipeline:
        1. Validate schema & enforce feature ordering.
        2. Transform raw features using loaded preprocessor artifact.
        3. Predict calibrated risk probability.
        """
        df_valid = self.validate_input(patient_data)

        # Transform raw features using loaded preprocessor (No manual code duplication)
        X_trans = self.preprocessor.transform(df_valid)

        # Predict probability using loaded calibrated model
        probs = self.calibrated_model.predict_proba(X_trans)[0]
        risk_prob = float(probs[1])

        # Classification at configured threshold (0.30)
        is_high_risk = bool(risk_prob >= self.threshold)
        
        if risk_prob < 0.30:
            category = "Low Risk"
        elif risk_prob < 0.60:
            category = "Moderate Risk"
        else:
            category = "High Risk"

        # 4. Generate SHAP Explanation for individual patient prediction
        top_contributing_features = []
        try:
            import shap
            if not hasattr(self, "_explainer") or self._explainer is None:
                self._explainer = shap.TreeExplainer(self.calibrated_model.base_model)
            
            shap_vals = self._explainer.shap_values(X_trans)
            if isinstance(shap_vals, list):
                inst_shap = shap_vals[1][0] if len(shap_vals) > 1 else shap_vals[0][0]
            elif isinstance(shap_vals, np.ndarray) and len(shap_vals.shape) == 3:
                inst_shap = shap_vals[0, :, 1]
            elif isinstance(shap_vals, np.ndarray) and len(shap_vals.shape) == 2:
                inst_shap = shap_vals[0]
            else:
                inst_shap = shap_vals

            transformed_features = self.manifest["transformed_feature_order"]
            total_abs_shap = float(np.sum(np.abs(inst_shap)))

            all_contributions = []
            for i, feat_name in enumerate(transformed_features):
                s_val = float(inst_shap[i])
                val_raw = X_trans[0, i] if isinstance(X_trans, np.ndarray) else X_trans.iloc[0, i]
                rel_pct = (abs(s_val) / total_abs_shap * 100) if total_abs_shap > 0 else 0.0

                all_contributions.append({
                    "feature": feat_name,
                    "actual_value": round(float(val_raw), 4),
                    "shap_contribution": round(s_val, 4),
                    "direction": "increased risk contribution" if s_val > 0 else "decreased risk contribution",
                    "relative_contribution_pct": round(rel_pct, 2)
                })

            all_contributions.sort(key=lambda x: abs(x["shap_contribution"]), reverse=True)
            top_contributing_features = all_contributions[:5]
        except Exception as e:
            print(f"[SHAP Warning] Live instance SHAP calculation fallback to manifest global rankings: {e}")
            global_rankings = self.manifest.get("shap_metadata", {}).get("global_rankings", [])
            for r in global_rankings[:5]:
                top_contributing_features.append({
                    "feature": r["feature"],
                    "shap_contribution": r["mean_abs_shap"],
                    "direction": "increased risk contribution",
                    "relative_contribution_pct": 0.0
                })

        return {
            "prediction": 1 if is_high_risk else 0,
            "probability": round(risk_prob, 4),
            "risk_category": category,
            "threshold": self.threshold,
            "model_version": self.manifest["model_version"],
            "top_contributing_features": top_contributing_features,
            "disclaimer": self.manifest["clinical_disclaimer"]
        }

# Global singleton instance for fast backend API import
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
        "blood_glucose_level": 160
    }
    
    result = predict_patient_risk(test_patient)
    print("Prediction Result:")
    print(json.dumps(result, indent=2))
