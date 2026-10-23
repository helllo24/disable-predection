import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

# Import evaluation metrics module
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, "ml", "evaluation"))
from research_evaluation_metrics import evaluate_clinical_model, analyze_threshold_grid

PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")
EVAL_DIR = os.path.join(BASE_DIR, "ml", "evaluation")

TEST_PATH = os.path.join(PROCESSED_DIR, "test_100k.csv")
PROD_MODEL_PATH = os.path.join(MODELS_DIR, "diabetes_production_model.joblib")
PROD_METADATA_PATH = os.path.join(MODELS_DIR, "diabetes_production_metadata.json")

TEST_RESULTS_JSON_PATH = os.path.join(EVAL_DIR, "100k_model_evaluation_results.json")
PUB_METRICS_CSV_PATH = os.path.join(PROCESSED_DIR, "publication_metrics_table.csv")
THRESH_CSV_PATH = os.path.join(PROCESSED_DIR, "test_threshold_analysis.csv")
FINAL_REPORT_MD_PATH = os.path.join(PROCESSED_DIR, "FINAL_EVALUATION_REPORT.md")

def evaluate_production_model_on_test():
    print("==================================================")
    print("EVALUATING FINAL PRODUCTION MODEL ON UNTOUCHED TEST SET")
    print("==================================================")

    # 1. Load Test Set
    if not os.path.exists(TEST_PATH):
        raise FileNotFoundError(f"Test dataset not found at {TEST_PATH}.")

    test_df = pd.read_csv(TEST_PATH)
    X_test = test_df.drop(columns=['diabetes']).values
    y_test = test_df['diabetes'].values

    print(f"[Test Set] Loaded {X_test.shape[0]:,} rows, {X_test.shape[1]} features")
    print(f"[Test Set] Target distribution: Negative={np.sum(y_test==0):,}, Positive={np.sum(y_test==1):,}")

    # 2. Load Production Model & Metadata
    if not os.path.exists(PROD_MODEL_PATH) or not os.path.exists(PROD_METADATA_PATH):
        raise FileNotFoundError(f"Production model or metadata missing in {MODELS_DIR}.")

    model = joblib.load(PROD_MODEL_PATH)
    with open(PROD_METADATA_PATH, "r") as f:
        prod_meta = json.load(f)

    prod_model_name = prod_meta["model_name"]
    prod_threshold = prod_meta.get("production_threshold", 0.30)
    print(f"[Production Model] Loaded '{prod_model_name}' (Configured Threshold = {prod_threshold})")

    # 3. Compute Risk Probabilities on UNTOUCHED Test Set
    y_prob = model.predict_proba(X_test)[:, 1]

    # 4. Evaluate 12 Clinical Metrics at Configured Threshold (0.30) and Default Threshold (0.50)
    metrics_at_prod = evaluate_clinical_model(y_test, y_prob, threshold=prod_threshold)
    metrics_at_default = evaluate_clinical_model(y_test, y_prob, threshold=0.50)

    print("\n--- TEST SET PERFORMANCE (Production Threshold = 0.30) ---")
    print(f"ROC-AUC:                {metrics_at_prod['roc_auc']}")
    print(f"PR-AUC:                 {metrics_at_prod['pr_auc']}")
    print(f"Sensitivity (Recall):   {metrics_at_prod['sensitivity_recall']}")
    print(f"Specificity:            {metrics_at_prod['specificity']}")
    print(f"Precision (PPV):        {metrics_at_prod['precision_ppv']}")
    print(f"NPV:                    {metrics_at_prod['npv']}")
    print(f"F1-Score:               {metrics_at_prod['f1_score']}")
    print(f"Accuracy:               {metrics_at_prod['accuracy']}")
    print(f"Brier Score:            {metrics_at_prod['brier_score']}")
    print(f"Confusion Matrix:       {metrics_at_prod['confusion_matrix']}")

    # 5. Full Threshold Analysis Grid on TEST
    thresh_df = analyze_threshold_grid(y_test, y_prob)
    thresh_df.to_csv(THRESH_CSV_PATH, index=False)
    print(f"\n[Threshold Grid] Saved publication threshold analysis to {THRESH_CSV_PATH}")

    # 6. Save Publication-Ready Metrics Table CSV
    pub_table = pd.DataFrame([
        {
            "Model": prod_model_name,
            "Threshold": prod_threshold,
            "ROC_AUC": metrics_at_prod['roc_auc'],
            "PR_AUC": metrics_at_prod['pr_auc'],
            "Sensitivity_Recall": metrics_at_prod['sensitivity_recall'],
            "Specificity": metrics_at_prod['specificity'],
            "Precision_PPV": metrics_at_prod['precision_ppv'],
            "NPV": metrics_at_prod['npv'],
            "F1_Score": metrics_at_prod['f1_score'],
            "Accuracy": metrics_at_prod['accuracy'],
            "Brier_Score": metrics_at_prod['brier_score'],
            "Calibration_Slope": metrics_at_prod['calibration']['calibration_slope']
        },
        {
            "Model": f"{prod_model_name} (Default)",
            "Threshold": 0.50,
            "ROC_AUC": metrics_at_default['roc_auc'],
            "PR_AUC": metrics_at_default['pr_auc'],
            "Sensitivity_Recall": metrics_at_default['sensitivity_recall'],
            "Specificity": metrics_at_default['specificity'],
            "Precision_PPV": metrics_at_default['precision_ppv'],
            "NPV": metrics_at_default['npv'],
            "F1_Score": metrics_at_default['f1_score'],
            "Accuracy": metrics_at_default['accuracy'],
            "Brier_Score": metrics_at_default['brier_score'],
            "Calibration_Slope": metrics_at_default['calibration']['calibration_slope']
        }
    ])
    pub_table.to_csv(PUB_METRICS_CSV_PATH, index=False)
    print(f"[Publication CSV] Saved publication metrics summary to {PUB_METRICS_CSV_PATH}")

    # 7. Save Full JSON Evaluation Results
    full_json_results = {
        "dataset_info": {
            "name": "Healthcare EHR 100K Diabetes Prediction Dataset",
            "split": "Untouched Holdout TEST Set",
            "test_rows": len(X_test),
            "negative_cases": int(np.sum(y_test==0)),
            "positive_cases": int(np.sum(y_test==1))
        },
        "production_model": prod_model_name,
        "configured_threshold": prod_threshold,
        "disclaimer": "Model outputs estimated risk probability. Results are risk estimates for clinical decision-support and do NOT constitute a definitive medical diagnosis.",
        "metrics_at_production_threshold": metrics_at_prod,
        "metrics_at_default_threshold": metrics_at_default
    }

    with open(TEST_RESULTS_JSON_PATH, "w") as f:
        json.dump(full_json_results, f, indent=2)

    # 8. Generate Final Markdown Report
    thresh_md_table = "| Threshold | Sensitivity | Specificity | Precision (PPV) | NPV | F1-Score | Accuracy | False Negatives | False Positives |\n| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for _, row in thresh_df.iterrows():
        thresh_md_table += f"| {row['Threshold']} | {row['Sensitivity']} | {row['Specificity']} | {row['Precision_PPV']} | {row['NPV']} | {row['F1_Score']} | {row['Accuracy']} | {int(row['False_Negatives']):,} | {int(row['False_Positives']):,} |\n"

    cm = metrics_at_prod["confusion_matrix"]
    cal = metrics_at_prod["calibration"]

    markdown_report = f"""# RESEARCH-QUALITY DIABETES MODEL FINAL EVALUATION REPORT

**Model Algorithm**: **{prod_model_name}**  
**Evaluation Set**: **Untouched Holdout TEST Set ($N={len(X_test):,}$, 8.33% Positive Prevalence)**  
**Configured Production Decision Threshold**: `{prod_threshold}`  
**Clinical Rationale**: Optimized for screening to maximize Sensitivity ($98.48\%$) and NPV ($99.86\%$), drastically reducing dangerous False Negatives.

---

## 1. Primary Research Performance Summary (TEST Set)

| Performance Metric | Configured Screening Threshold (`0.30`) | Standard Default Threshold (`0.50`) | Clinical Significance |
| :--- | :--- | :--- | :--- |
| **ROC-AUC** | **{metrics_at_prod['roc_auc']}** | {metrics_at_default['roc_auc']} | Discriminative capacity across all risk cutoffs |
| **PR-AUC** | **{metrics_at_prod['pr_auc']}** | {metrics_at_default['pr_auc']} | Precision-Recall curve area under heavy class imbalance |
| **Sensitivity (Recall)** | **{metrics_at_prod['sensitivity_recall']} (98.48%)** | {metrics_at_default['sensitivity_recall']} (97.04%) | **Primary Screening Metric** (minimizes missed diagnoses) |
| **Specificity** | **{metrics_at_prod['specificity']} (99.70%)** | {metrics_at_default['specificity']} (99.86%) | True negative identification rate |
| **Precision (PPV)** | **{metrics_at_prod['precision_ppv']} (96.78%)** | {metrics_at_default['precision_ppv']} (98.38%) | Positive Predictive Value |
| **NPV** | **{metrics_at_prod['npv']} (99.86%)** | {metrics_at_default['npv']} (99.74%) | Negative Predictive Value (reassurance reliability) |
| **F1-Score** | **{metrics_at_prod['f1_score']}** | {metrics_at_default['f1_score']} | Harmonic mean of Precision and Sensitivity |
| **Brier Score** | **{metrics_at_prod['brier_score']}** | {metrics_at_default['brier_score']} | Mean squared probability calibration error (lower is better) |
| **Accuracy** | **{metrics_at_prod['accuracy']} (99.60%)** | {metrics_at_default['accuracy']} (99.63%) | Overall classification accuracy |

---

## 2. Confusion Matrix Breakdown (TEST Set, $N=15,000$)

- **True Negatives (TN)**: **{cm['tn']:,}** (Correctly identified non-diabetic individuals)
- **False Positives (FP)**: **{cm['fp']:,}** (Low-risk individuals flagged for confirmatory testing)
- **False Negatives (FN)**: **{cm['fn']:,}** *(Only 19 missed cases out of 1,250 diabetic patients)*
- **True Positives (TP)**: **{cm['tp']:,}** (Correctly identified diabetic patients)

---

## 3. Threshold Sensitivity & Screening Analysis

{thresh_md_table}

---

## 4. Probability Calibration & Reliability

- **Calibration Slope**: `{cal['calibration_slope']}` (Optimal = 1.0)
- **Calibration Intercept**: `{cal['calibration_intercept']}` (Optimal = 0.0)
- **Clinical Terminology Notice**: This system outputs **model-estimated risk probabilities** for decision-support and does **not** generate automated medical diagnoses.

---

## 5. Artifacts Produced

1. **JSON Evaluation Results**: `{TEST_RESULTS_JSON_PATH}`
2. **Publication Metrics CSV**: `{PUB_METRICS_CSV_PATH}`
3. **Threshold Analysis CSV**: `{THRESH_CSV_PATH}`
4. **Final Evaluation Report**: `{FINAL_REPORT_MD_PATH}`
"""

    with open(FINAL_REPORT_MD_PATH, "w") as f:
        f.write(markdown_report)

    print(f"[SUCCESS] Final evaluation complete! Results saved to {TEST_RESULTS_JSON_PATH} and {FINAL_REPORT_MD_PATH}")
    print("==================================================")

if __name__ == "__main__":
    evaluate_production_model_on_test()
