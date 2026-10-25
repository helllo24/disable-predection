
from pathlib import Path
import json
import warnings

import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import (
    train_test_split,
    RepeatedStratifiedKFold,
    cross_validate,
)
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    brier_score_loss,
    confusion_matrix,
    classification_report,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier

warnings.filterwarnings("ignore")

# --------------------------------------------------
# 1. Paths and dataset
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "datasets" / "diabetes.csv"
OUTPUT_DIR = BASE_DIR / "final_evaluation_results"
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_PATH)

TARGET = "Outcome"

if TARGET not in df.columns:
    raise ValueError(
        f"Target column '{TARGET}' not found. "
        f"Available columns: {list(df.columns)}"
    )

X = df.drop(columns=[TARGET])
y = df[TARGET].astype(int)

if set(y.unique()) != {0, 1}:
    raise ValueError("Outcome must contain binary labels 0 and 1.")

# --------------------------------------------------
# 2. Split before model selection
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

# --------------------------------------------------
# 3. Define candidate models
# --------------------------------------------------

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=2000,
        random_state=42,
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    ),
    "HistGradientBoosting": HistGradientBoostingClassifier(
        random_state=42,
    ),
}

# Add XGBoost if it is installed.
try:
    from xgboost import XGBClassifier

    models["XGBoost"] = XGBClassifier(
        n_estimators=200,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
    )
except ImportError:
    print("XGBoost not installed; skipping that candidate.")

# --------------------------------------------------
# 4. Cross-validation on TRAINING data only
# --------------------------------------------------

cv = RepeatedStratifiedKFold(
    n_splits=5,
    n_repeats=3,
    random_state=42,
)

scoring = {
    "roc_auc": "roc_auc",
    "accuracy": "accuracy",
    "precision": "precision",
    "recall": "recall",
    "f1": "f1",
}

cv_results = []
fitted_candidates = {}

for name, estimator in models.items():
    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", estimator),
    ])

    scores = cross_validate(
        pipeline,
        X_train,
        y_train,
        cv=cv,
        scoring=scoring,
        n_jobs=1,
        error_score="raise",
    )

    row = {"Model": name}

    for metric in scoring:
        values = scores[f"test_{metric}"]
        row[f"{metric}_mean"] = values.mean()
        row[f"{metric}_std"] = values.std()

    cv_results.append(row)
    fitted_candidates[name] = pipeline

results_df = pd.DataFrame(cv_results)
results_df = results_df.sort_values(
    by="roc_auc_mean",
    ascending=False,
)

results_df.to_csv(
    OUTPUT_DIR / "training_cv_comparison.csv",
    index=False,
)

print("\n=== TRAINING-ONLY CROSS-VALIDATION ===")
print(results_df.round(4).to_string(index=False))

# --------------------------------------------------
# 5. Select model using CV only
# --------------------------------------------------

best_name = results_df.iloc[0]["Model"]
best_model = fitted_candidates[best_name]

print(f"\nSelected model by mean CV ROC-AUC: {best_name}")

# Fit the selected model on all training data.
best_model.fit(X_train, y_train)

# --------------------------------------------------
# 6. Evaluate ONCE on the held-out test set
# --------------------------------------------------

probabilities = best_model.predict_proba(X_test)[:, 1]
predictions = (probabilities >= 0.5).astype(int)

tn, fp, fn, tp = confusion_matrix(
    y_test,
    predictions,
    labels=[0, 1],
).ravel()

test_metrics = {
    "selected_model": best_name,
    "selection_metric": "mean ROC-AUC from training-only CV",
    "test_samples": int(len(y_test)),
    "test_accuracy": float(accuracy_score(y_test, predictions)),
    "test_precision": float(
        precision_score(y_test, predictions, zero_division=0)
    ),
    "test_recall": float(
        recall_score(y_test, predictions, zero_division=0)
    ),
    "test_f1": float(
        f1_score(y_test, predictions, zero_division=0)
    ),
    "test_roc_auc": float(
        roc_auc_score(y_test, probabilities)
    ),
    "test_brier_score": float(
        brier_score_loss(y_test, probabilities)
    ),
    "TN": int(tn),
    "FP": int(fp),
    "FN": int(fn),
    "TP": int(tp),
    "classification_threshold": 0.5,
}

with open(
    OUTPUT_DIR / "final_test_metrics.json",
    "w",
    encoding="utf-8",
) as file:
    json.dump(test_metrics, file, indent=4)

pd.DataFrame({
    "actual": y_test.to_numpy(),
    "predicted": predictions,
    "predicted_probability": probabilities,
}).to_csv(
    OUTPUT_DIR / "final_test_predictions.csv",
    index=False,
)

joblib.dump(
    best_model,
    OUTPUT_DIR / "final_diabetes_model.joblib",
)

print("\n=== FINAL HELD-OUT TEST RESULTS ===")
for key, value in test_metrics.items():
    print(f"{key}: {value}")

print("\n=== CLASSIFICATION REPORT ===")
print(classification_report(
    y_test,
    predictions,
    target_names=["No diabetes", "Diabetes"],
    zero_division=0,
))

print(f"\nFiles saved to: {OUTPUT_DIR}")
