
from pathlib import Path

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import (
    roc_auc_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
)

# --------------------------------------------------
# 1. Paths and configuration
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = ROOT / "ml" / "datasets" / "diabetes.csv"

MODEL_DIR = ROOT / "ml" / "models" / "pima"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "pima_diabetes_model.joblib"

FEATURES = [
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age",
]

TARGET = "Outcome"

# --------------------------------------------------
# 2. Load and validate dataset
# --------------------------------------------------

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"PIMA dataset not found: {DATA_PATH}"
    )

df = pd.read_csv(DATA_PATH)

required_columns = FEATURES + [TARGET]
missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

df = df[required_columns].copy()
df = df.drop_duplicates()
df = df.dropna(subset=[TARGET])

for column in required_columns:
    df[column] = pd.to_numeric(
        df[column], errors="coerce"
    )

df = df.dropna(subset=[TARGET])

if not df[TARGET].isin([0, 1]).all():
    raise ValueError("Outcome must contain only 0 and 1.")

X = df[FEATURES].copy()
y = df[TARGET].astype(int)

# In the conventional PIMA dataset, zero measurements
# in these fields are generally treated as missing.
zero_missing_columns = [
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
]

X[zero_missing_columns] = X[
    zero_missing_columns
].replace(0, float("nan"))

print("Dataset shape:", df.shape)
print("\nTarget distribution:")
print(y.value_counts())

# --------------------------------------------------
# 3. Split into train, calibration, and test sets
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

X_fit, X_cal, y_fit, y_cal = train_test_split(
    X_train,
    y_train,
    test_size=0.25,
    random_state=42,
    stratify=y_train,
)

print("\nTraining records:", len(X_fit))
print("Calibration records:", len(X_cal))
print("Test records:", len(X_test))

# --------------------------------------------------
# 4. Build and train the base model
# --------------------------------------------------

base_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="median"),
    ),
    (
        "model",
        HistGradientBoostingClassifier(
            learning_rate=0.05,
            max_iter=100,
            max_leaf_nodes=15,
            min_samples_leaf=15,
            l2_regularization=1.0,
            random_state=42,
        ),
    ),
])

print("\nTraining base model...")

base_pipeline.fit(X_fit, y_fit)

print("Base model training completed.")

# --------------------------------------------------
# 5. Calibrate without refitting the base model
# --------------------------------------------------

print("\nCalibrating model...")

calibrated_model = CalibratedClassifierCV(
    estimator=FrozenEstimator(base_pipeline),
    method="sigmoid",
)

calibrated_model.fit(X_cal, y_cal)

print("Calibration completed.")

# --------------------------------------------------
# 6. Evaluate on untouched test data
# --------------------------------------------------

probabilities = calibrated_model.predict_proba(
    X_test
)[:, 1]

threshold = 0.5
predictions = (
    probabilities >= threshold
).astype(int)

roc_auc = roc_auc_score(
    y_test, probabilities
)

brier = brier_score_loss(
    y_test, probabilities
)

print("\n========== PIMA TEST RESULTS ==========")
print("ROC-AUC:", round(roc_auc, 4))
print("Brier score:", round(brier, 4))

print("\nClassification report:")
print(
    classification_report(
        y_test,
        predictions,
        zero_division=0,
    )
)

print("Confusion matrix:")
print(confusion_matrix(y_test, predictions))

print("\nProbability distribution:")
print(
    pd.Series(probabilities).describe(
        percentiles=[0.1, 0.25, 0.5, 0.75, 0.9]
    )
)

print(
    "\nBelow 1%:",
    round((probabilities < 0.01).mean() * 100, 2),
    "%",
)

print(
    "Above 99%:",
    round((probabilities > 0.99).mean() * 100, 2),
    "%",
)

# --------------------------------------------------
# 7. Save model and feature schema
# --------------------------------------------------

artifact = {
    "model": calibrated_model,
    "features": FEATURES,
    "target": TARGET,
    "dataset": "PIMA Diabetes Dataset",
    "decision_threshold": threshold,
    "metrics": {
        "roc_auc": float(roc_auc),
        "brier_score": float(brier),
    },
}

joblib.dump(artifact, MODEL_PATH)

print("\nModel saved successfully:")
print(MODEL_PATH)
