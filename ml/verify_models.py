
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.model_selection import (
    RepeatedStratifiedKFold,
    cross_validate,
)
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from xgboost import XGBClassifier


# 1. Configuration
DATA_PATH = Path("datasets/diabetes.csv")
TARGET = "Outcome"
RANDOM_STATE = 42


# 2. Load dataset
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()
df = df.dropna(subset=[TARGET]).copy()

X = df.drop(columns=[TARGET])
y = df[TARGET].astype(int)

if set(y.unique()) != {0, 1}:
    raise ValueError("Target must contain binary values 0 and 1.")

# Treat impossible zero measurements as missing in Pima data
for col in [
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
]:
    if col in X.columns:
        X[col] = X[col].replace(0, np.nan)


# 3. Models using configurations found in previous experiments
models = {
    "Logistic Regression": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            C=5,
            max_iter=3000,
            random_state=RANDOM_STATE,
        )),
    ]),

    "Random Forest": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestClassifier(
            n_estimators=400,
            min_samples_split=15,
            min_samples_leaf=6,
            max_features="sqrt",
            max_depth=8,
            random_state=RANDOM_STATE,
            n_jobs=1,
        )),
    ]),

    "HistGradientBoosting": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", HistGradientBoostingClassifier(
            min_samples_leaf=20,
            max_leaf_nodes=7,
            max_iter=100,
            learning_rate=0.03,
            l2_regularization=5,
            random_state=RANDOM_STATE,
        )),
    ]),

    "XGBoost": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", XGBClassifier(
            objective="binary:logistic",
            eval_metric="logloss",
            subsample=0.8,
            reg_lambda=5,
            reg_alpha=1,
            n_estimators=100,
            min_child_weight=5,
            max_depth=3,
            learning_rate=0.05,
            colsample_bytree=0.8,
            random_state=RANDOM_STATE,
            n_jobs=1,
        )),
    ]),
}


# 4. Repeated stratified 5-fold CV: 5 folds x 3 repeats
cv = RepeatedStratifiedKFold(
    n_splits=5,
    n_repeats=3,
    random_state=RANDOM_STATE,
)

scoring = {
    "accuracy": "accuracy",
    "precision": "precision",
    "recall": "recall",
    "f1": "f1",
    "roc_auc": "roc_auc",
}

rows = []

# 5. Evaluate each model on the same repeated folds
for name, model in models.items():
    print(f"\nEvaluating {name}...")

    scores = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring=scoring,
        n_jobs=-1,
        error_score="raise",
        return_train_score=False,
    )

    row = {"Model": name}

    for metric in scoring:
        values = scores[f"test_{metric}"]
        row[f"{metric}_mean"] = values.mean()
        row[f"{metric}_std"] = values.std(ddof=1)

    rows.append(row)

results = pd.DataFrame(rows).sort_values(
    "accuracy_mean", ascending=False
)

results.to_csv("repeated_cv_results.csv", index=False)

print("\nREPEATED STRATIFIED CROSS-VALIDATION RESULTS")
print("Each model: 5 folds x 3 repeats = 15 evaluations\n")
print(results.round(4).to_string(index=False))

print("\nSaved results to repeated_cv_results.csv")
