
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

# Configuration
N_BOOTSTRAPS = 2000
RANDOM_STATE = 42
TARGET = "Outcome"

# 1. Load the dataset
df = pd.read_csv("datasets/diabetes.csv")

X = df.drop(columns=[TARGET])
y = df[TARGET]

# 2. Recreate the same held-out test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y,
)

# 3. Train the model on training data only
model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("model", HistGradientBoostingClassifier(
        random_state=RANDOM_STATE
    )),
])

model.fit(X_train, y_train)

# 4. Prepare test predictions
test_results = X_test[["Age"]].copy()
test_results["Actual"] = y_test.to_numpy()
test_results["Predicted"] = model.predict(X_test)
test_results["Probability"] = model.predict_proba(X_test)[:, 1]

test_results["Age_Group"] = pd.cut(
    test_results["Age"],
    bins=[20, 30, 40, 50, 100],
    labels=["21-30", "31-40", "41-50", "51+"],
    right=True,
)

# 5. Define metrics
def calculate_metrics(actual, predicted, probability):
    metrics = {
        "Accuracy": accuracy_score(actual, predicted),
        "Precision": precision_score(
            actual, predicted, zero_division=0
        ),
        "Recall": recall_score(
            actual, predicted, zero_division=0
        ),
        "F1_Score": f1_score(
            actual, predicted, zero_division=0
        ),
    }

    if len(np.unique(actual)) == 2:
        metrics["ROC_AUC"] = roc_auc_score(
            actual, probability
        )
    else:
        metrics["ROC_AUC"] = np.nan

    return metrics


# 6. Bootstrap confidence intervals for each age group
rng = np.random.default_rng(RANDOM_STATE)
output_rows = []

metric_names = [
    "Accuracy", "Precision", "Recall", "F1_Score", "ROC_AUC"
]

for age_group in ["21-30", "31-40", "41-50", "51+"]:
    group = test_results[
        test_results["Age_Group"].astype(str) == age_group
    ].copy()

    if group.empty:
        continue

    actual = group["Actual"].to_numpy()
    predicted = group["Predicted"].to_numpy()
    probability = group["Probability"].to_numpy()

    observed = calculate_metrics(actual, predicted, probability)

    bootstrap_values = {name: [] for name in metric_names}
    n = len(group)

    for _ in range(N_BOOTSTRAPS):
        indices = rng.integers(0, n, size=n)

        boot_actual = actual[indices]
        boot_predicted = predicted[indices]
        boot_probability = probability[indices]

        values = calculate_metrics(
            boot_actual, boot_predicted, boot_probability
        )

        for name in metric_names:
            value = values[name]
            if np.isfinite(value):
                bootstrap_values[name].append(value)

    row = {
        "Age_Group": age_group,
        "Samples": n,
        "Actual_Positive": int(actual.sum()),
    }

    for name in metric_names:
        values = bootstrap_values[name]

        row[f"{name}_Observed"] = observed[name]

        if values:
            row[f"{name}_CI_Lower"] = np.percentile(values, 2.5)
            row[f"{name}_CI_Upper"] = np.percentile(values, 97.5)
        else:
            row[f"{name}_CI_Lower"] = np.nan
            row[f"{name}_CI_Upper"] = np.nan

    output_rows.append(row)

# 7. Save results
output = pd.DataFrame(output_rows)
output.to_csv("bootstrap_age_group_results.csv", index=False)

print("\nBOOTSTRAP AGE-GROUP RESULTS (95% CIs)")
for _, row in output.iterrows():
    print(f"\nAge group: {row['Age_Group']} | Samples: {row['Samples']}")

    for name in metric_names:
        observed = row[f"{name}_Observed"]
        lower = row[f"{name}_CI_Lower"]
        upper = row[f"{name}_CI_Upper"]

        if pd.notna(lower) and pd.notna(upper):
            print(
                f"  {name}: {observed:.3f} "
                f"(95% CI: {lower:.3f} to {upper:.3f})"
            )
        else:
            print(f"  {name}: CI unavailable")

print("\nSaved: bootstrap_age_group_results.csv")
