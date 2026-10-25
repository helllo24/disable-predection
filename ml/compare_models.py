
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    brier_score_loss,
    confusion_matrix,
)

# 1. Update this path to your actual dataset CSV file
DATA_PATH = Path("datasets/diabetes.csv")
TARGET = "Outcome"
RANDOM_STATE = 42

# 2. Load dataset
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()

if TARGET not in df.columns:
    raise ValueError(
        f"Target '{TARGET}' not found. Available columns: {list(df.columns)}"
    )

# Keep rows with a known target; features are imputed in the pipeline
df = df.dropna(subset=[TARGET]).copy()

X = df.drop(columns=[TARGET])
y = df[TARGET].astype(int)

# Pima dataset: zero in these measurements may indicate missing data
zero_as_missing = [
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
]

for col in zero_as_missing:
    if col in X.columns:
        X[col] = X[col].replace(0, np.nan)

# 3. One common, stratified train/test split for every model
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y,
)

# 4. Define models
models = {
    "Logistic Regression": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)),
    ]),

    "Random Forest": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestClassifier(
            n_estimators=300,
            random_state=RANDOM_STATE,
            class_weight="balanced",
        )),
    ]),

    "HistGradientBoosting": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", HistGradientBoostingClassifier(
            random_state=RANDOM_STATE,
        )),
    ]),
}

# XGBoost is optional
try:
    from xgboost import XGBClassifier

    models["XGBoost"] = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", XGBClassifier(
            n_estimators=300,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=RANDOM_STATE,
        )),
    ])
except ImportError:
    print("XGBoost is not installed; skipping that model.")

# 5. Train, calibrate and evaluate each model
results = []

for name, pipeline in models.items():
    calibrated_model = CalibratedClassifierCV(
        estimator=pipeline,
        method="sigmoid",
        cv=3,
    )

    calibrated_model.fit(X_train, y_train)

    probabilities = calibrated_model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test, predictions, labels=[0, 1]
    ).ravel()

    results.append({
        "Model": name,
        "Accuracy": accuracy_score(y_test, predictions),
        "Precision": precision_score(
            y_test, predictions, zero_division=0
        ),
        "Recall": recall_score(
            y_test, predictions, zero_division=0
        ),
        "F1": f1_score(y_test, predictions, zero_division=0),
        "ROC_AUC": roc_auc_score(y_test, probabilities),
        "Brier_Score": brier_score_loss(y_test, probabilities),
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "TP": tp,
    })

# 6. Save results
results_df = pd.DataFrame(results)
results_df = results_df.sort_values("ROC_AUC", ascending=False)

results_df.to_csv("model_comparison_results.csv", index=False)

print("\nMODEL COMPARISON RESULTS")
print(results_df.round(4).to_string(index=False))
print("\nSaved results to model_comparison_results.csv")
