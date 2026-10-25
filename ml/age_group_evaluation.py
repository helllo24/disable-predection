
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

# 1. Load dataset
df = pd.read_csv("datasets/diabetes.csv")

target = "Outcome"

X = df.drop(columns=[target])
y = df[target]

# 2. Split data before evaluating age groups
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# 3. Train model using training data only
model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("model", HistGradientBoostingClassifier(random_state=42))
])

model.fit(X_train, y_train)

# 4. Predict on held-out test data
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

# 5. Create age groups for test records
results = X_test[["Age"]].copy()
results["Actual"] = y_test
results["Predicted"] = y_pred
results["Probability"] = y_prob

results["Age_Group"] = pd.cut(
    results["Age"],
    bins=[20, 30, 40, 50, 100],
    labels=["21-30", "31-40", "41-50", "51+"],
    right=True
)

# 6. Evaluate each age group
evaluation = []

for age_group, group in results.groupby(
    "Age_Group", observed=True
):
    if len(group) == 0:
        continue

    row = {
        "Age_Group": str(age_group),
        "Samples": len(group),
        "Actual_Positive": int(group["Actual"].sum()),
        "Accuracy": accuracy_score(
            group["Actual"], group["Predicted"]
        ),
        "Precision": precision_score(
            group["Actual"], group["Predicted"],
            zero_division=0
        ),
        "Recall": recall_score(
            group["Actual"], group["Predicted"],
            zero_division=0
        ),
        "F1_Score": f1_score(
            group["Actual"], group["Predicted"],
            zero_division=0
        )
    }

    # ROC-AUC requires both classes in the group
    if group["Actual"].nunique() == 2:
        row["ROC_AUC"] = roc_auc_score(
            group["Actual"], group["Probability"]
        )
    else:
        row["ROC_AUC"] = np.nan

    evaluation.append(row)

evaluation_df = pd.DataFrame(evaluation)

# 7. Save results
output_file = "age_group_evaluation.csv"
evaluation_df.to_csv(output_file, index=False)

print("\nAGE-GROUP EVALUATION RESULTS")
print(evaluation_df.to_string(index=False))
print(f"\nResults saved to: {output_file}")
