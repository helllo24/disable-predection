import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "datasets", "complications"))
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "complications"))
os.makedirs(MODELS_DIR, exist_ok=True)

complication_configs = {
    "heart": {
        "file": "heart_disease.csv",
        "target": "cardio_risk",
        "model_name": "heart_model.pkl",
        "meta_name": "heart_metadata.json",
        "type": "binary"
    },
    "kidney": {
        "file": "kidney_disease.csv",
        "target": "kidney_disease_risk",
        "model_name": "kidney_model.pkl",
        "meta_name": "kidney_metadata.json",
        "type": "binary"
    },
    "neuropathy": {
        "file": "neuropathy.csv",
        "target": "neuropathy_risk",
        "model_name": "neuropathy_model.pkl",
        "meta_name": "neuropathy_metadata.json",
        "type": "multiclass"
    },
    "retinopathy": {
        "file": "retinopathy.csv",
        "target": "retinopathy_risk",
        "model_name": "retinopathy_model.pkl",
        "meta_name": "retinopathy_metadata.json",
        "type": "binary"
    },
    "foot": {
        "file": "diabetic_foot.csv",
        "target": "foot_ulcer_risk_category",
        "model_name": "foot_model.pkl",
        "meta_name": "foot_metadata.json",
        "type": "multiclass"
    },
    "vascular": {
        "file": "vascular_disease.csv",
        "target": "vascular_disease_risk",
        "model_name": "vascular_model.pkl",
        "meta_name": "vascular_metadata.json",
        "type": "multiclass"
    }
}

def train_all_complication_models():
    print("==================================================================")
    print("TRAINING DIABETES COMPLICATION RISK ML MODELS")
    print("==================================================================")

    results_summary = {}

    for comp_key, cfg in complication_configs.items():
        csv_path = os.path.join(DATA_DIR, cfg["file"])
        if not os.path.exists(csv_path):
            print(f"[ERROR] Missing dataset file: {csv_path}")
            continue

        df = pd.read_csv(csv_path)
        target_col = cfg["target"]
        feature_cols = [c for c in df.columns if c != target_col]

        X = df[feature_cols]
        y = df[target_col]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        # Build Machine Learning Pipeline
        if cfg["type"] == "binary":
            model = Pipeline([
                ('scaler', StandardScaler()),
                ('classifier', XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.05, random_state=42, eval_metric='logloss'))
            ])
        else:
            model = Pipeline([
                ('scaler', StandardScaler()),
                ('classifier', RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42))
            ])

        model.fit(X_train, y_train)

        # Evaluation
        y_pred = model.predict(X_test)
        acc = float(accuracy_score(y_test, y_pred))
        f1 = float(f1_score(y_test, y_pred, average='weighted'))

        # Save Model Pipeline
        model_path = os.path.join(MODELS_DIR, cfg["model_name"])
        joblib.dump(model, model_path)

        # Save Metadata JSON
        meta = {
            "complication": comp_key,
            "target_column": target_col,
            "feature_columns": feature_cols,
            "accuracy": round(acc, 4),
            "f1_score": round(f1, 4),
            "model_type": "XGBoost" if cfg["type"] == "binary" else "RandomForest"
        }
        meta_path = os.path.join(MODELS_DIR, cfg["meta_name"])
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2)

        results_summary[comp_key] = meta
        print(f"[SUCCESS] Trained {comp_key.upper()} Model -> Accuracy: {acc*100:.2f}%, F1: {f1*100:.2f}% | Saved to {model_path}")

    print("\n[COMPLETE] All 6 Diabetes Complication ML Models trained successfully!")
    return results_summary

if __name__ == "__main__":
    train_all_complication_models()
