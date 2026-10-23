import os
import sys
import json
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, "ml", "evaluation"))
from research_evaluation_metrics import CalibratedProbabilityModel

MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")
PACKAGE_DIR = os.path.join(MODELS_DIR, "production_package")
os.makedirs(PACKAGE_DIR, exist_ok=True)

# Source paths
SRC_PREPROCESSOR = os.path.join(MODELS_DIR, "diabetes_100k_preprocessor.joblib")
SRC_BASE_MODEL = os.path.join(MODELS_DIR, "histgradientboosting_100k.joblib")
SRC_CALIB_MODEL = os.path.join(MODELS_DIR, "diabetes_calibrated_model.joblib")
SRC_METADATA = os.path.join(MODELS_DIR, "diabetes_production_metadata.json")
SRC_CALIB_JSON = os.path.join(BASE_DIR, "ml", "evaluation", "calibration_and_ci_results.json")
SRC_SHAP_JSON = os.path.join(BASE_DIR, "ml", "evaluation", "shap_analysis_results.json")

# Target paths in package
TGT_PREPROCESSOR = os.path.join(PACKAGE_DIR, "preprocessor.joblib")
TGT_BASE_MODEL = os.path.join(PACKAGE_DIR, "model.joblib")
TGT_CALIB_MODEL = os.path.join(PACKAGE_DIR, "calibrated_model.joblib")
MANIFEST_JSON_PATH = os.path.join(PACKAGE_DIR, "model_manifest.json")

def create_production_model_package():
    print("==================================================")
    print("PACKAGING PRODUCTION-READY DIABETES ML PACKAGE")
    print("==================================================")

    # 1. Load and copy preprocessor and models
    if not os.path.exists(SRC_PREPROCESSOR) or not os.path.exists(SRC_CALIB_MODEL):
        raise FileNotFoundError("Source preprocessor or calibrated model missing in ml/models/.")

    preprocessor = joblib.load(SRC_PREPROCESSOR)
    calibrated_model = joblib.load(SRC_CALIB_MODEL)
    base_model = joblib.load(SRC_BASE_MODEL) if os.path.exists(SRC_BASE_MODEL) else calibrated_model.base_model

    joblib.dump(preprocessor, TGT_PREPROCESSOR)
    joblib.dump(base_model, TGT_BASE_MODEL)
    joblib.dump(calibrated_model, TGT_CALIB_MODEL)

    print(f"[Package] Saved preprocessor to {TGT_PREPROCESSOR}")
    print(f"[Package] Saved base model to   {TGT_BASE_MODEL}")
    print(f"[Package] Saved calibrated model to {TGT_CALIB_MODEL}")

    # 2. Load evaluation and SHAP results for manifest
    with open(SRC_METADATA, "r") as f:
        meta = json.load(f)

    with open(SRC_CALIB_JSON, "r") as f:
        calib_data = json.load(f)

    with open(SRC_SHAP_JSON, "r") as f:
        shap_data = json.load(f)

    raw_features = ['gender', 'age', 'hypertension', 'heart_disease', 'smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level']
    cat_feature_names = preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out(['gender', 'smoking_history']).tolist()
    transformed_features = ['age', 'bmi', 'HbA1c_level', 'blood_glucose_level'] + cat_feature_names + ['hypertension', 'heart_disease']

    test_metrics = calib_data["test_evaluation"]["calibrated_model"]["confidence_intervals_95"]
    test_calib_stats = calib_data["test_evaluation"]["calibrated_model"]["calibration_stats"]

    # 3. Build Model Manifest JSON matching production requirements
    manifest = {
        "model_version": "1.0.0",
        "dataset_name": "Healthcare EHR 100K Diabetes Prediction Dataset",
        "dataset_version": "1.0.0",
        "preprocessing_version": "1.0.0",
        "algorithm": meta["model_name"],
        "target": "diabetes",
        "threshold": meta["production_threshold"],
        "selected_threshold": meta["production_threshold"],
        "threshold_rationale": meta["threshold_rationale"],
        "training_configuration": {
            "training_date": "2026-10-07",
            "random_seed": 42,
            "train_val_test_split": "70/15/15",
            "train_rows": 70000,
            "val_rows": 15000,
            "test_rows": 15000,
            "cross_validation_folds": 5,
            "cross_validation_strategy": "StratifiedKFold",
            "calibration_method": calib_data["calibration_configuration"]["selected_calibration_method"]
        },
        "features": {
            "raw_feature_order": raw_features,
            "transformed_feature_order": transformed_features,
            "schema": {
                "gender": {"type": "string", "allowed_values": ["Female", "Male", "Other"], "description": "Patient biological sex"},
                "age": {"type": "float", "range": [0.08, 80.0], "description": "Patient age in years"},
                "hypertension": {"type": "int", "allowed_values": [0, 1], "description": "Hypertension diagnosis indicator"},
                "heart_disease": {"type": "int", "allowed_values": [0, 1], "description": "Heart disease diagnosis indicator"},
                "smoking_history": {"type": "string", "allowed_values": ["never", "No Info", "current", "former", "ever", "not current"], "description": "Smoking history category"},
                "bmi": {"type": "float", "range": [10.0, 95.0], "description": "Body Mass Index (kg/m^2)"},
                "HbA1c_level": {"type": "float", "range": [3.5, 9.0], "description": "Glycated hemoglobin percentage (%)"},
                "blood_glucose_level": {"type": "int", "range": [80, 300], "description": "Blood glucose concentration (mg/dL)"}
            }
        },
        "raw_feature_schema": {
            "gender": {"type": "string", "allowed_values": ["Female", "Male", "Other"], "description": "Patient biological sex"},
            "age": {"type": "float", "range": [0.08, 80.0], "description": "Patient age in years"},
            "hypertension": {"type": "int", "allowed_values": [0, 1], "description": "Hypertension diagnosis indicator"},
            "heart_disease": {"type": "int", "allowed_values": [0, 1], "description": "Heart disease diagnosis indicator"},
            "smoking_history": {"type": "string", "allowed_values": ["never", "No Info", "current", "former", "ever", "not current"], "description": "Smoking history category"},
            "bmi": {"type": "float", "range": [10.0, 95.0], "description": "Body Mass Index (kg/m^2)"},
            "HbA1c_level": {"type": "float", "range": [3.5, 9.0], "description": "Glycated hemoglobin percentage (%)"},
            "blood_glucose_level": {"type": "int", "range": [80, 300], "description": "Blood glucose concentration (mg/dL)"}
        },
        "raw_feature_order": raw_features,
        "transformed_feature_order": transformed_features,
        "feature_metadata": {
            "num_raw_features": len(raw_features),
            "num_transformed_features": len(transformed_features),
            "categorical_encoding": "OneHotEncoder(drop=None, handle_unknown='ignore')",
            "numerical_imputation": "SimpleImputer(strategy='median')",
            "numerical_scaling": "StandardScaler()"
        },
        "metrics": {
            "roc_auc": test_metrics["roc_auc"]["ci_formatted"],
            "sensitivity_recall": test_metrics["recall_sensitivity"]["ci_formatted"],
            "specificity": test_metrics["specificity"]["ci_formatted"],
            "precision_ppv": test_metrics["precision_ppv"]["ci_formatted"],
            "f1_score": test_metrics["f1_score"]["ci_formatted"],
            "accuracy": test_metrics["accuracy"]["ci_formatted"]
        },
        "performance_metrics_test_set": {
            "roc_auc": test_metrics["roc_auc"]["ci_formatted"],
            "sensitivity_recall": test_metrics["recall_sensitivity"]["ci_formatted"],
            "specificity": test_metrics["specificity"]["ci_formatted"],
            "precision_ppv": test_metrics["precision_ppv"]["ci_formatted"],
            "f1_score": test_metrics["f1_score"]["ci_formatted"],
            "accuracy": test_metrics["accuracy"]["ci_formatted"]
        },
        "calibration": {
            "calibration_method": calib_data["calibration_configuration"]["selected_calibration_method"],
            "brier_score": test_calib_stats["brier_score"],
            "calibration_slope": test_calib_stats["calibration_slope"],
            "calibration_intercept": test_calib_stats["calibration_intercept"]
        },
        "calibration_metrics_test_set": {
            "brier_score": test_calib_stats["brier_score"],
            "calibration_slope": test_calib_stats["calibration_slope"],
            "calibration_intercept": test_calib_stats["calibration_intercept"]
        },
        "shap_metadata": {
            "base_expected_value": shap_data["base_expected_value"],
            "global_rankings": shap_data["global_feature_rankings"]
        },
        "artifacts": {
            "preprocessor": "preprocessor.joblib",
            "model": "model.joblib",
            "calibrated_model": "calibrated_model.joblib",
            "manifest": "model_manifest.json"
        },
        "clinical_disclaimer": "This model outputs an estimated risk probability for clinical decision-support and does NOT provide an automated medical diagnosis."
    }

    with open(MANIFEST_JSON_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"[Manifest] Production model manifest written to {MANIFEST_JSON_PATH}")
    print("==================================================")
    return manifest

if __name__ == "__main__":
    create_production_model_package()
