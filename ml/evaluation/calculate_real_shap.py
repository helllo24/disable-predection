import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import shap

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")
EVAL_DIR = os.path.join(BASE_DIR, "ml", "evaluation")

TEST_PATH = os.path.join(PROCESSED_DIR, "test_100k.csv")
PROD_MODEL_PATH = os.path.join(MODELS_DIR, "diabetes_production_model.joblib")
PROD_METADATA_PATH = os.path.join(MODELS_DIR, "diabetes_production_metadata.json")

SHAP_JSON_PATH = os.path.join(EVAL_DIR, "shap_analysis_results.json")
SHAP_RANKINGS_CSV_PATH = os.path.join(PROCESSED_DIR, "shap_feature_rankings.csv")
SHAP_VALUES_CSV_PATH = os.path.join(PROCESSED_DIR, "shap_values.csv")
SUMMARY_PLOT_PATH = os.path.join(PROCESSED_DIR, "shap_summary_plot.png")
BAR_PLOT_PATH = os.path.join(PROCESSED_DIR, "shap_bar_plot.png")
REPORT_MD_PATH = os.path.join(PROCESSED_DIR, "SHAP_EXPLAINABILITY_REPORT.md")

def compute_real_shap_explainability():
    print("==================================================")
    print("COMPUTING REAL SHAP EXPLAINABILITY & FEATURE RANKINGS")
    print("==================================================")

    # 1. Load Production Model & Metadata
    if not os.path.exists(PROD_MODEL_PATH) or not os.path.exists(PROD_METADATA_PATH):
        raise FileNotFoundError(f"Production model or metadata missing in {MODELS_DIR}.")

    model = joblib.load(PROD_MODEL_PATH)
    with open(PROD_METADATA_PATH, "r") as f:
        prod_meta = json.load(f)

    model_name = prod_meta["model_name"]
    print(f"[Model] Loaded production model '{model_name}'")

    # 2. Load Preprocessed Test Dataset
    test_df = pd.read_csv(TEST_PATH)
    X_test = test_df.drop(columns=['diabetes'])
    y_test = test_df['diabetes'].values
    feature_names = X_test.columns.tolist()

    print(f"[Test Data] Loaded {X_test.shape[0]:,} records with {len(feature_names)} features")

    # Sample 1,000 background test records for robust SHAP calculation
    np.random.seed(42)
    sample_idx = np.random.choice(len(X_test), size=min(1000, len(X_test)), replace=False)
    X_sample = X_test.iloc[sample_idx]
    y_sample = y_test[sample_idx]

    # 3. Create SHAP Explainer
    print(f"[SHAP Engine] Initializing SHAP Explainer for {model_name}...")
    try:
        explainer = shap.TreeExplainer(model)
        shap_values_raw = explainer.shap_values(X_sample)
    except Exception as e:
        print(f"[SHAP Engine] TreeExplainer fallback to generic Explainer ({e})")
        explainer = shap.Explainer(model.predict_proba, X_sample)
        shap_values_raw = explainer(X_sample).values

    # Normalize SHAP output format if 3D (multi-class or binary two-output)
    if isinstance(shap_values_raw, list):
        shap_vals = shap_values_raw[1] if len(shap_values_raw) > 1 else shap_values_raw[0]
    elif isinstance(shap_values_raw, np.ndarray) and len(shap_values_raw.shape) == 3:
        shap_vals = shap_values_raw[:, :, 1]
    else:
        shap_vals = shap_values_raw

    # Extract base value / expected value
    if hasattr(explainer, "expected_value"):
        base_val = explainer.expected_value
        if isinstance(base_val, (list, np.ndarray)):
            base_val = float(base_val[1]) if len(base_val) > 1 else float(base_val[0])
        else:
            base_val = float(base_val)
    else:
        base_val = float(np.mean(model.predict_proba(X_sample)[:, 1]))

    print(f"[SHAP Engine] Expected Base Value: {base_val:.4f}")

    # 4. Global Feature Importance Calculation (mean |SHAP|)
    mean_abs_shap = np.mean(np.abs(shap_vals), axis=0)
    sorted_indices = np.argsort(mean_abs_shap)[::-1]

    feature_rankings = []
    for rank, idx in enumerate(sorted_indices, 1):
        feature_rankings.append({
            "rank": rank,
            "feature": feature_names[idx],
            "mean_abs_shap": round(float(mean_abs_shap[idx]), 4)
        })

    df_rankings = pd.DataFrame(feature_rankings)
    df_rankings.to_csv(SHAP_RANKINGS_CSV_PATH, index=False)
    print(f"[Global Importance] Saved SHAP feature rankings to {SHAP_RANKINGS_CSV_PATH}")

    # Save full SHAP values CSV
    df_shap_values = pd.DataFrame(shap_vals, columns=feature_names)
    df_shap_values.to_csv(SHAP_VALUES_CSV_PATH, index=False)

    # 5. Generate SHAP Plots
    print("[Plots] Generating SHAP summary plot...")
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_vals, X_sample, feature_names=feature_names, show=False)
    plt.title(f"SHAP Summary Plot ({model_name} - 100K Cohort)", fontsize=12, pad=15)
    plt.tight_layout()
    plt.savefig(SUMMARY_PLOT_PATH, dpi=300, bbox_inches='tight')
    plt.close()

    print("[Plots] Generating SHAP bar plot...")
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_vals, X_sample, feature_names=feature_names, plot_type="bar", show=False)
    plt.title(f"SHAP Global Feature Importance ({model_name})", fontsize=12, pad=15)
    plt.tight_layout()
    plt.savefig(BAR_PLOT_PATH, dpi=300, bbox_inches='tight')
    plt.close()

    # 6. Individual Prediction Explanation Function
    def explain_patient_instance(patient_idx):
        patient_features = X_sample.iloc[patient_idx]
        patient_shap = shap_vals[patient_idx]
        pred_prob = float(model.predict_proba(patient_features.values.reshape(1, -1))[:, 1][0])

        total_abs_shap = np.sum(np.abs(patient_shap))
        
        feature_contributions = []
        for i, feat_name in enumerate(feature_names):
            val = float(patient_features.iloc[i])
            s_val = float(patient_shap[i])
            rel_pct = (abs(s_val) / total_abs_shap * 100) if total_abs_shap > 0 else 0.0

            feature_contributions.append({
                "feature": feat_name,
                "actual_value": round(val, 4),
                "shap_contribution": round(s_val, 4),
                "direction": "increased risk contribution" if s_val > 0 else "decreased risk contribution",
                "relative_contribution_pct": round(rel_pct, 2)
            })

        # Sort by magnitude of SHAP contribution
        feature_contributions.sort(key=lambda x: abs(x["shap_contribution"]), reverse=True)

        top_positive = [f for f in feature_contributions if f["shap_contribution"] > 0][:3]
        top_negative = [f for f in feature_contributions if f["shap_contribution"] < 0][:3]

        return {
            "patient_index": int(patient_idx),
            "predicted_risk_probability": round(pred_prob, 4),
            "base_expected_value": round(base_val, 4),
            "top_positive_contributors": top_positive,
            "top_negative_contributors": top_negative,
            "all_feature_contributions": feature_contributions,
            "non_technical_explanation": (
                f"The model estimated a diabetes risk probability of {round(pred_prob * 100, 1)}%. "
                f"Features such as {', '.join([p['feature'] for p in top_positive]) or 'none'} contributed positively to increasing the risk score, "
                f"while features like {', '.join([n['feature'] for n in top_negative]) or 'none'} contributed to lowering the risk score. "
                "Note: These contributions represent feature weights in the predictive model and do NOT imply direct medical causation."
            )
        }

    # Generate sample individual patient explanation (High Risk Patient)
    high_risk_idx = np.where(y_sample == 1)[0][0] if len(np.where(y_sample == 1)[0]) > 0 else 0
    sample_individual_explanation = explain_patient_instance(high_risk_idx)

    # 7. Save Summary JSON
    shap_results_json = {
        "model_name": model_name,
        "sample_size_evaluated": len(X_sample),
        "base_expected_value": round(base_val, 4),
        "global_feature_rankings": feature_rankings,
        "sample_individual_explanation": sample_individual_explanation,
        "plots": {
            "summary_plot": SUMMARY_PLOT_PATH,
            "bar_plot": BAR_PLOT_PATH
        },
        "disclaimer": "SHAP contributions quantify mathematical feature importance in the predictive model and do NOT describe biological or medical causation."
    }

    with open(SHAP_JSON_PATH, "w") as f:
        json.dump(shap_results_json, f, indent=2)

    # 8. Generate Markdown Report
    top_feat = feature_rankings[0]["feature"]
    second_feat = feature_rankings[1]["feature"]

    markdown_report = f"""# REAL SHAP FEATURE IMPORTANCE & EXPLAINABILITY REPORT

**Model Evaluated**: **{model_name}**  
**Evaluation Cohort**: {len(X_sample):,} preprocessed patient records  
**Base Expected Value ($E[f(x)]$)**: `{base_val:.4f}`  
**Top Calculated Feature**: **{top_feat}** (Mean $|\\text{{SHAP}}| = {feature_rankings[0]['mean_abs_shap']}$)  

---

## 1. Empirical SHAP Global Feature Importance Ranking

*Note: All feature rankings are calculated directly from empirical SHAP value magnitude averages.*

| Rank | Feature Name | Mean $|\\text{{SHAP}}|$ Contribution | Clinical Interpretation in Model |
| :--- | :--- | :--- | :--- |
"""
    for item in feature_rankings:
        markdown_report += f"| **#{item['rank']}** | `{item['feature']}` | **{item['mean_abs_shap']}** | Feature magnitude contribution to risk prediction |\n"

    markdown_report += f"""
---

## 2. Empirical Findings

- Empirical SHAP analysis confirms that **`{top_feat}`** and **`{second_feat}`** are the top 2 mathematical predictors in the `{model_name}` model.
- Features with positive SHAP values push the patient's predicted diabetes probability higher, whereas negative SHAP values shift the risk score lower.

---

## 3. Sample Individual Patient Risk Explanation

- **Patient Risk Score**: `{sample_individual_explanation['predicted_risk_probability'] * 100:.1f}%`
- **Model Base Expected Value**: `{sample_individual_explanation['base_expected_value'] * 100:.1f}%`

### Top Factors Increasing Risk Contribution:
"""
    for item in sample_individual_explanation["top_positive_contributors"]:
        markdown_report += f"- **`{item['feature']}`** (Value: `{item['actual_value']}`): Contributed `+{item['shap_contribution']}` to increasing risk score ({item['relative_contribution_pct']}% relative shift).\n"

    markdown_report += "\n### Top Factors Decreasing Risk Contribution:\n"
    for item in sample_individual_explanation["top_negative_contributors"]:
        markdown_report += f"- **`{item['feature']}`** (Value: `{item['actual_value']}`): Contributed `{item['shap_contribution']}` to lowering risk score ({item['relative_contribution_pct']}% relative shift).\n"

    markdown_report += f"""
### Non-Technical Patient Communication:
> "{sample_individual_explanation['non_technical_explanation']}"

---

## 4. Pipeline Artifacts Created

1. **SHAP Analysis JSON**: `{SHAP_JSON_PATH}`
2. **SHAP Feature Rankings CSV**: `{SHAP_RANKINGS_CSV_PATH}`
3. **SHAP Values CSV**: `{SHAP_VALUES_CSV_PATH}`
4. **SHAP Summary Plot**: `{SUMMARY_PLOT_PATH}`
5. **SHAP Bar Plot**: `{BAR_PLOT_PATH}`
"""

    with open(REPORT_MD_PATH, "w") as f:
        f.write(markdown_report)

    print(f"[SUCCESS] Real SHAP explainability completed! Reports written to {SHAP_JSON_PATH} and {REPORT_MD_PATH}")
    print("==================================================")
    return shap_results_json

if __name__ == "__main__":
    compute_real_shap_explainability()
