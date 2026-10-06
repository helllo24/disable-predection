import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.pipeline import Pipeline

from ml.preprocessing.diabetes_preprocessing import load_and_preprocess_dataset, FEATURE_COLUMNS

def train_and_evaluate_all_models():
    """
    Trains Logistic Regression, Random Forest, and XGBoost models, evaluates performance
    on the unseen test set, selects the optimal model, and saves models and metadata.
    """
    X_train, X_test, y_train, y_test, preprocessor, raw_df = load_and_preprocess_dataset('ml/datasets/diabetes.csv')

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
        "XGBoost": XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, random_state=42, eval_metric='logloss')
    }

    model_files = {
        "Logistic Regression": "ml/models/diabetes_logistic_regression.pkl",
        "Random Forest": "ml/models/diabetes_random_forest.pkl",
        "XGBoost": "ml/models/diabetes_xgboost.pkl"
    }

    results = {}
    fitted_pipelines = {}

    print("\n" + "=" * 60)
    print("TRAINING & EVALUATING ML MODELS")
    print("=" * 60)

    for name, clf in models.items():
        # Build complete Pipeline combining preprocessor + classifier
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', clf)
        ])

        # Fit ONLY on training data
        pipeline.fit(X_train, y_train)
        fitted_pipelines[name] = pipeline

        # Save individual model pipeline
        joblib.dump(pipeline, model_files[name])

        # Evaluate on unseen test data
        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1] if hasattr(pipeline, "predict_proba") else None

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_proba) if y_proba is not None else 0.0
        cm = confusion_matrix(y_test, y_pred).tolist()

        results[name] = {
            "accuracy": float(acc),
            "precision": float(prec),
            "recall": float(rec),
            "f1": float(f1),
            "roc_auc": float(roc_auc),
            "confusion_matrix": cm
        }

        print(f"\nModel: {name}")
        print(f"  Accuracy:  {acc:.4f}")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall:    {rec:.4f}")
        print(f"  F1-Score:  {f1:.4f}")
        print(f"  ROC-AUC:   {roc_auc:.4f}")
        print(f"  Confusion Matrix: {cm}")

    # Model Selection Logic:
    # In medical screening, high Recall (Sensitivity) and high ROC-AUC / F1 are vital to avoid missing high-risk patients.
    # We rank models primarily by ROC-AUC and F1 score.
    best_name = max(results.keys(), key=lambda k: (results[k]["roc_auc"], results[k]["f1"]))
    best_pipeline = fitted_pipelines[best_name]

    print("\n" + "=" * 60)
    print(f"SELECTED OPTIMAL MODEL: {best_name}")
    print(f"Reason: Highest composite ROC-AUC ({results[best_name]['roc_auc']:.4f}) and F1 ({results[best_name]['f1']:.4f})")
    print("=" * 60)

    # Save selected model as diabetes_model.pkl
    selected_model_path = "ml/models/diabetes_model.pkl"
    joblib.dump(best_pipeline, selected_model_path)

    # Extract Feature Importances or Coefficients for Explainability
    clf_step = best_pipeline.named_steps['classifier']
    feature_importances = {}
    if hasattr(clf_step, 'feature_importances_'):
        importances = clf_step.feature_importances_
        feature_importances = {feat: float(imp) for feat, imp in zip(FEATURE_COLUMNS, importances)}
    elif hasattr(clf_step, 'coef_'):
        coefs = clf_step.coef_[0]
        feature_importances = {feat: float(c) for feat, c in zip(FEATURE_COLUMNS, coefs)}

    # Save metadata JSON
    metadata = {
        "selected_model": best_name,
        "selected_model_file": "ml/models/diabetes_model.pkl",
        "training_timestamp": datetime.now().isoformat(),
        "dataset": {
            "name": "Pima Indians Diabetes Dataset",
            "total_samples": int(len(raw_df)),
            "features": FEATURE_COLUMNS,
            "target": "Outcome (0=No Diabetes, 1=Diabetes)"
        },
        "all_model_evaluations": results,
        "feature_importances": feature_importances,
        "preprocessing_info": {
            "imputation": "SimpleImputer (median)",
            "scaling": "StandardScaler",
            "handled_zero_features": ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
        }
    }

    metadata_path = "ml/models/diabetes_model_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved selected model to {selected_model_path}")
    print(f"Saved metadata to {metadata_path}")

    return results, best_name, metadata

if __name__ == "__main__":
    train_and_evaluate_all_models()
