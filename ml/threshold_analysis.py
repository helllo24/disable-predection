
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "datasets" / "diabetes.csv"
MODEL_PATH = BASE_DIR / "final_evaluation_results" / "final_diabetes_model.joblib"
OUTPUT_DIR = BASE_DIR / "threshold_analysis_results"
OUTPUT_DIR.mkdir(exist_ok=True)

# 1. Load data and recreate the same split
df = pd.read_csv(DATA_PATH)
X = df.drop(columns=["Outcome"])
y = df["Outcome"].astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

# 2. Define the selected model pipeline
pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("model", LogisticRegression(max_iter=2000, random_state=42)),
])

# 3. Get out-of-fold probabilities using TRAINING data only
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

oof_probabilities = cross_val_predict(
    pipeline,
    X_train,
    y_train,
    cv=cv,
    method="predict_proba",
)[:, 1]

# 4. Compare candidate thresholds on training OOF predictions
thresholds = np.arange(0.20, 0.701, 0.05)
rows = []

for threshold in thresholds:
    predictions = (oof_probabilities >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(
        y_train, predictions, labels=[0, 1]
    ).ravel()

    rows.append({
        "threshold": round(float(threshold), 2),
        "accuracy": accuracy_score(y_train, predictions),
        "precision": precision_score(
            y_train, predictions, zero_division=0
        ),
        "recall": recall_score(
            y_train, predictions, zero_division=0
        ),
        "f1": f1_score(
            y_train, predictions, zero_division=0
        ),
        "specificity": tn / (tn + fp) if (tn + fp) else 0,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "TP": tp,
    })

threshold_df = pd.DataFrame(rows)
threshold_df.to_csv(
    OUTPUT_DIR / "training_threshold_comparison.csv",
    index=False,
)

# Choose threshold using TRAINING data only.
# This is a research criterion, not a clinical recommendation.
best_row = threshold_df.loc[threshold_df["f1"].idxmax()]
best_threshold = float(best_row["threshold"])

print("\n=== TRAINING OOF THRESHOLD COMPARISON ===")
print(threshold_df.round(3).to_string(index=False))
print(f"\nSelected threshold by training OOF F1: {best_threshold:.2f}")

# 5. Evaluate the chosen threshold on the held-out test set
# Load the model already fitted by the final evaluation script.
if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Saved model not found: {MODEL_PATH}. "
        "Run final_model_evaluation.py first."
    )

final_model = joblib.load(MODEL_PATH)
test_probabilities = final_model.predict_proba(X_test)[:, 1]
test_predictions = (test_probabilities >= best_threshold).astype(int)

tn, fp, fn, tp = confusion_matrix(
    y_test, test_predictions, labels=[0, 1]
).ravel()

test_results = {
    "selected_threshold": best_threshold,
    "threshold_selection": "maximum F1 on training out-of-fold predictions",
    "test_samples": int(len(y_test)),
    "accuracy": float(accuracy_score(y_test, test_predictions)),
    "precision": float(precision_score(
        y_test, test_predictions, zero_division=0
    )),
    "recall": float(recall_score(
        y_test, test_predictions, zero_division=0
    )),
    "f1": float(f1_score(
        y_test, test_predictions, zero_division=0
    )),
    "roc_auc": float(roc_auc_score(y_test, test_probabilities)),
    "specificity": float(tn / (tn + fp)) if (tn + fp) else 0.0,
    "TN": int(tn),
    "FP": int(fp),
    "FN": int(fn),
    "TP": int(tp),
}

pd.DataFrame([test_results]).to_csv(
    OUTPUT_DIR / "selected_threshold_test_results.csv",
    index=False,
)

print("\n=== HELD-OUT TEST RESULTS AT SELECTED THRESHOLD ===")
for key, value in test_results.items():
    print(f"{key}: {value}")

print(f"\nResults saved to: {OUTPUT_DIR}")
