
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import shap

from sklearn.impute import SimpleImputer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline


# 1. Load dataset
DATA_PATH = Path("datasets/diabetes.csv")
OUTPUT_DIR = Path("shap_results")
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()
df = df.dropna(subset=["Outcome"]).copy()

X = df.drop(columns=["Outcome"])
y = df["Outcome"].astype(int)

# 2. Treat zero measurements as missing
for col in [
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
]:
    if col in X.columns:
        X[col] = X[col].replace(0, np.nan)

# 3. Train the model
model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("model", HistGradientBoostingClassifier(
        min_samples_leaf=20,
        max_leaf_nodes=7,
        max_iter=100,
        learning_rate=0.03,
        l2_regularization=5,
        random_state=42,
    )),
])

model.fit(X, y)

# 4. Impute data for SHAP explanations
imputer = model.named_steps["imputer"]
X_imputed = pd.DataFrame(
    imputer.transform(X),
    columns=X.columns,
    index=X.index,
)

# Small background sample keeps model-agnostic SHAP manageable
background = X_imputed.sample(
    n=min(50, len(X_imputed)),
    random_state=42,
)

# Explain a sample of observations
explain_data = X_imputed.sample(
    n=min(100, len(X_imputed)),
    random_state=7,
)

# 5. Explain predicted probability for Outcome = 1
def predict_positive_probability(data):
    data_array = np.asarray(data)
    return model.named_steps["model"].predict_proba(data_array)[:, 1]

explainer = shap.Explainer(
    predict_positive_probability,
    background,
    algorithm="permutation",
)

shap_values = explainer(
    explain_data,
    max_evals=2 * X.shape[1] + 1,
)

# 6. Global feature importance (beeswarm)
plt.figure()
shap.plots.beeswarm(shap_values, max_display=10, show=False)
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "shap_summary.png",
    dpi=300,
    bbox_inches="tight",
)
plt.close()

# 7. Mean absolute SHAP feature importance
plt.figure()
shap.plots.bar(shap_values, max_display=10, show=False)
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "shap_feature_importance.png",
    dpi=300,
    bbox_inches="tight",
)
plt.close()

# 8. Explain one individual prediction
one_explanation = shap_values[0]

plt.figure()
shap.plots.waterfall(one_explanation, max_display=10, show=False)
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "shap_individual_prediction.png",
    dpi=300,
    bbox_inches="tight",
)
plt.close()

# 9. Export feature importance values
importance = pd.DataFrame({
    "Feature": X.columns,
    "Mean_Absolute_SHAP": np.abs(shap_values.values).mean(axis=0),
}).sort_values("Mean_Absolute_SHAP", ascending=False)

importance.to_csv(
    OUTPUT_DIR / "shap_importance.csv",
    index=False,
)

print("\nSHAP analysis completed.")
print("\nFeature importance:")
print(importance.to_string(index=False))
print(f"\nFiles saved in: {OUTPUT_DIR.resolve()}")
