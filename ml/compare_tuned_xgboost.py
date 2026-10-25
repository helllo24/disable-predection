
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.model_selection import (
    train_test_split,
    RandomizedSearchCV,
    StratifiedKFold,
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
)

from xgboost import XGBClassifier
import joblib


# 1. Configuration
DATA_PATH = Path("datasets/diabetes.csv")
TARGET = "Outcome"
RANDOM_STATE = 42


# 2. Load and prepare data
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()
df = df.dropna(subset=[TARGET]).copy()

X = df.drop(columns=[TARGET])
y = df[TARGET].astype(int)

if set(y.unique()) != {0, 1}:
    raise ValueError("Expected binary target values 0 and 1.")

# In this dataset, zero can indicate a missing measurement
for col in [
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
]:
    if col in X.columns:
        X[col] = X[col].replace(0, np.nan)

# One fixed split for both models
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y,
)


# 3. Baseline model
baseline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("model", XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        n_estimators=300,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=RANDOM_STATE,
        n_jobs=1,
    )),
])


# 4. Hyperparameter search
search_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("model", XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        n_jobs=1,
    )),
])

param_distributions = {
    "model__n_estimators": [100, 200, 300, 500],
    "model__max_depth": [2, 3, 4, 5],
    "model__learning_rate": [0.01, 0.03, 0.05, 0.1],
    "model__subsample": [0.7, 0.8, 0.9, 1.0],
    "model__colsample_bytree": [0.7, 0.8, 0.9, 1.0],
    "model__min_child_weight": [1, 3, 5, 7],
    "model__reg_alpha": [0, 0.01, 0.1, 1.0],
    "model__reg_lambda": [1, 2, 5, 10],
}

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=RANDOM_STATE,
)

search = RandomizedSearchCV(
    estimator=search_pipeline,
    param_distributions=param_distributions,
    n_iter=40,
    scoring="accuracy",
    cv=cv,
    random_state=RANDOM_STATE,
    n_jobs=-1,
    verbose=1,
    refit=True,
)


# 5. Train both models
print("Training baseline XGBoost...")
baseline.fit(X_train, y_train)

print("\nTuning XGBoost using training data only...")
search.fit(X_train, y_train)

tuned = search.best_estimator_

print("\nBest CV accuracy:", round(search.best_score_, 4))
print("Best parameters:")
print(search.best_params_)


# 6. Evaluate both on the SAME test set
def evaluate_model(name, model):
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test, predictions, labels=[0, 1]
    ).ravel()

    return {
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
    }


results = pd.DataFrame([
    evaluate_model("Baseline XGBoost", baseline),
    evaluate_model("Tuned XGBoost", tuned),
])

print("\nSAME-TEST-SET COMPARISON")
print(results.round(4).to_string(index=False))

baseline_acc = results.loc[
    results["Model"] == "Baseline XGBoost", "Accuracy"
].iloc[0]

tuned_acc = results.loc[
    results["Model"] == "Tuned XGBoost", "Accuracy"
].iloc[0]

print(f"\nAccuracy change: {(tuned_acc - baseline_acc) * 100:+.2f} percentage points")

# Save comparison and search parameters
results.to_csv("xgboost_fair_comparison.csv", index=False)
pd.DataFrame([search.best_params_]).to_csv(
    "xgboost_best_parameters.csv", index=False
)

# Save tuned model for later testing/deployment
joblib.dump(tuned, "tuned_xgboost_model.joblib")

print("\nSaved:")
print("- xgboost_fair_comparison.csv")
print("- xgboost_best_parameters.csv")
print("- tuned_xgboost_model.joblib")
