
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import (
    train_test_split,
    RandomizedSearchCV,
    StratifiedKFold,
)
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    brier_score_loss,
    confusion_matrix,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    HistGradientBoostingClassifier,
)
from xgboost import XGBClassifier


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------
DATA_PATH = Path("datasets/diabetes.csv")
TARGET = "Outcome"
RANDOM_STATE = 42


# --------------------------------------------------
# 2. Load and validate dataset
# --------------------------------------------------
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()
df = df.dropna(subset=[TARGET]).copy()

X = df.drop(columns=[TARGET])
y = df[TARGET].astype(int)

if set(y.unique()) != {0, 1}:
    raise ValueError("Target column must contain 0 and 1.")

# Pima dataset: zero often means missing measurement
for col in [
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
]:
    if col in X.columns:
        X[col] = X[col].replace(0, np.nan)

# Keep one fixed test set for every model
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y,
)


# --------------------------------------------------
# 3. Models and search spaces
# --------------------------------------------------
models = {
    "Logistic Regression": (
        Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(
                max_iter=3000,
                random_state=RANDOM_STATE,
            )),
        ]),
        {
            "model__C": [0.01, 0.1, 0.5, 1, 2, 5, 10],
            "model__class_weight": [None, "balanced"],
            "model__solver": ["lbfgs"],
        },
    ),

    "Random Forest": (
        Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestClassifier(
                random_state=RANDOM_STATE,
                n_jobs=1,
            )),
        ]),
        {
            "model__n_estimators": [200, 400, 600],
            "model__max_depth": [None, 3, 5, 8, 12],
            "model__min_samples_split": [2, 5, 10, 15],
            "model__min_samples_leaf": [1, 2, 4, 6],
            "model__max_features": ["sqrt", 0.8],
            "model__class_weight": [None, "balanced"],
        },
    ),

    "HistGradientBoosting": (
        Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", HistGradientBoostingClassifier(
                random_state=RANDOM_STATE,
            )),
        ]),
        {
            "model__learning_rate": [0.03, 0.05, 0.08, 0.1],
            "model__max_iter": [100, 200, 300],
            "model__max_leaf_nodes": [7, 15, 31],
            "model__l2_regularization": [0, 0.1, 1, 5],
            "model__min_samples_leaf": [10, 20, 30],
        },
    ),

    "XGBoost": (
        Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", XGBClassifier(
                objective="binary:logistic",
                eval_metric="logloss",
                random_state=RANDOM_STATE,
                n_jobs=1,
            )),
        ]),
        {
            "model__n_estimators": [100, 200, 300, 500],
            "model__max_depth": [2, 3, 4, 5],
            "model__learning_rate": [0.01, 0.03, 0.05, 0.1],
            "model__subsample": [0.7, 0.8, 0.9, 1.0],
            "model__colsample_bytree": [0.7, 0.8, 0.9, 1.0],
            "model__min_child_weight": [1, 3, 5],
            "model__reg_alpha": [0, 0.01, 0.1, 1],
            "model__reg_lambda": [1, 2, 5, 10],
        },
    ),
}


# --------------------------------------------------
# 4. Cross-validation setup
# --------------------------------------------------
cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=RANDOM_STATE,
)

results = []
best_cv_score = -1
best_model_name = None
best_model = None

# Tune each model using training data only
for name, (pipeline, parameters) in models.items():
    print(f"\n{'=' * 55}")
    print(f"Tuning: {name}")

    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=parameters,
        n_iter=25,
        scoring="accuracy",
        cv=cv,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=1,
        refit=True,
        error_score="raise",
    )

    search.fit(X_train, y_train)

    print("Best CV accuracy:", round(search.best_score_, 4))
    print("Best parameters:", search.best_params_)

    # Evaluate only after model selection on training folds
    candidate = search.best_estimator_
    probabilities = candidate.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test, predictions, labels=[0, 1]
    ).ravel()

    results.append({
        "Model": name,
        "CV_Accuracy": search.best_score_,
        "Test_Accuracy": accuracy_score(y_test, predictions),
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

    # Select using CV score, not test accuracy
    if search.best_score_ > best_cv_score:
        best_cv_score = search.best_score_
        best_model_name = name
        best_model = candidate


# --------------------------------------------------
# 5. Show and save results
# --------------------------------------------------
results_df = pd.DataFrame(results).sort_values(
    "CV_Accuracy", ascending=False
)

results_df.to_csv("improved_model_results.csv", index=False)

print("\n\nFINAL MODEL COMPARISON")
print(results_df.round(4).to_string(index=False))

print(f"\nSelected using training CV: {best_model_name}")
print(f"Best CV accuracy: {best_cv_score:.4f}")

# Save the selected pipeline
joblib.dump(best_model, "best_diabetes_model.joblib")

print("\nSaved:")
print("- improved_model_results.csv")
print("- best_diabetes_model.joblib")
