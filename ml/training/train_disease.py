import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from ml.preprocessing.disease_preprocessing import load_and_preprocess_disease_dataset

def train_and_evaluate_disease_models():
    """
    Trains Logistic Regression, Random Forest, and XGBoost multi-class disease classifiers,
    evaluates them on the unseen test set, selects the best model, and saves models & metadata.
    """
    X_train, X_test, y_train, y_test, feature_cols, class_names, label_encoder, raw_df = load_and_preprocess_disease_dataset('ml/datasets/disease.csv')

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42),
        "XGBoost": XGBClassifier(n_estimators=100, learning_rate=0.05, max_depth=6, random_state=42, eval_metric='mlogloss')
    }

    model_files = {
        "Logistic Regression": "ml/models/disease_logistic_regression.pkl",
        "Random Forest": "ml/models/disease_random_forest.pkl",
        "XGBoost": "ml/models/disease_xgboost.pkl"
    }

    results = {}
    fitted_models = {}

    print("\n" + "=" * 60)
    print("TRAINING & EVALUATING MULTI-CLASS DISEASE MODELS")
    print("=" * 60)

    for name, clf in models.items():
        # Fit model on training dataset
        clf.fit(X_train, y_train)
        fitted_models[name] = clf

        # Save individual model
        joblib.dump(clf, model_files[name])

        # Evaluate on unseen test data
        y_pred = clf.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        cm = confusion_matrix(y_test, y_pred).tolist()

        results[name] = {
            "accuracy": float(acc),
            "precision": float(prec),
            "recall": float(rec),
            "f1": float(f1),
            "confusion_matrix_shape": f"{len(cm)}x{len(cm[0])}"
        }

        print(f"\nModel: {name}")
        print(f"  Accuracy:  {acc:.4f}")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall:    {rec:.4f}")
        print(f"  F1-Score:  {f1:.4f}")

    # Select optimal model based on composite F1 and Accuracy on unseen test data
    best_name = max(results.keys(), key=lambda k: (results[k]["f1"], results[k]["accuracy"]))
    best_clf = fitted_models[best_name]

    print("\n" + "=" * 60)
    print(f"SELECTED OPTIMAL DISEASE MODEL: {best_name}")
    print(f"Reason: Highest multi-class F1-Score ({results[best_name]['f1']:.4f}) and Accuracy ({results[best_name]['accuracy']:.4f})")
    print("=" * 60)

    # Save optimal model to ml/models/disease_model.pkl
    selected_model_path = "ml/models/disease_model.pkl"
    joblib.dump(best_clf, selected_model_path)

    # Save Label Encoder
    encoder_path = "ml/models/disease_label_encoder.pkl"
    joblib.dump(label_encoder, encoder_path)

    # Extract Feature Importances or Coefficients if available
    feature_importances = {}
    if hasattr(best_clf, 'feature_importances_'):
        importances = best_clf.feature_importances_
        feature_importances = {feat: float(imp) for feat, imp in zip(feature_cols, importances)}

    # Save comprehensive metadata JSON
    metadata = {
        "selected_model": best_name,
        "selected_model_file": selected_model_path,
        "label_encoder_file": encoder_path,
        "training_timestamp": datetime.now().isoformat(),
        "dataset": {
            "name": "Disease Symptom Prediction Dataset",
            "total_samples": int(len(raw_df)),
            "symptom_features_count": len(feature_cols),
            "symptoms_list": feature_cols,
            "disease_classes_count": len(class_names),
            "disease_classes": class_names
        },
        "all_model_evaluations": results,
        "feature_importances_top10": dict(sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)[:10]) if feature_importances else {}
    }

    metadata_path = "ml/models/disease_model_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved selected disease model to {selected_model_path}")
    print(f"Saved metadata to {metadata_path}")

    return results, best_name, metadata

if __name__ == "__main__":
    train_and_evaluate_disease_models()
