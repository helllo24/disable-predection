
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

# Mark impossible zero measurements as missing
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

# Keep the final test set untouched during tuning
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y,
)


# 3. Preprocessing + XGBoost pipeline
pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("model", XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        n_jobs=1,
    )),
])


# 4. Hyperparameter search space
param_distributions = {
    "model__n_estimators": [100, 200, 300, 500, 700],
    "model__max_depth": [2, 3, 4, 5, 6],
    "model__learning_rate": [0.01, 0.03, 0.05, 0.1, 0.15],
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
    estimator=pipeline,
    param_distributions=param_distributions,
    n_iter=40,
    scoring="accuracy",
    cv=cv,
    random_state=RANDOM_STATE,
    n_jobs=-1,
    verbose=1,
    refit=True,
)

# 5. Tune using training data only
print("Starting XGBoost hyperparameter tuning...")
search.fit(X_train, y_train)

print("\nBest cross-validation accuracy:")
print(round(search.best_score_, 4))

print("\nBest hyperparameters:")
print(search.best_params_)


# 6. Evaluate the selected model on the held-out test set
best_model = search.best_estimator_
probabilities = best_model.predict_proba(X_test)[:, 1]
predictions = (probabilities >= 0.5).astype(int)

tn, fp, fn, tp = confusion_matrix(
    y_test, predictions, labels=[0, 1]
).ravel()

results = {
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

print("\nTUNED XGBOOST TEST RESULTS")
for metric, value in results.items():
    print(f"{metric}: {value:.4f}" if isinstance(value, (float, np.floating)) else f"{metric}: {value}")

# 7. Save results and best parameters
pd.DataFrame([results]).to_csv(
    "tuned_xgboost_results.csv", index=False
)

pd.DataFrame([search.best_params_]).to_csv(
    "tuned_xgboost_parameters.csv", index=False
)

print("\nSaved:")
print("- tuned_xgboost_results.csv")
print("- tuned_xgboost_parameters.csv")
