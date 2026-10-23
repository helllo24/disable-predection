import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    roc_auc_score, average_precision_score, accuracy_score,
    precision_score, recall_score, f1_score, confusion_matrix,
    brier_score_loss
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")
EVAL_DIR = os.path.join(BASE_DIR, "ml", "evaluation")

VAL_PATH = os.path.join(PROCESSED_DIR, "val_100k.csv")
TEST_PATH = os.path.join(PROCESSED_DIR, "test_100k.csv")
UNPROD_MODEL_PATH = os.path.join(MODELS_DIR, "diabetes_production_model.joblib")
PROD_METADATA_PATH = os.path.join(MODELS_DIR, "diabetes_production_metadata.json")

CALIB_MODEL_PATH = os.path.join(MODELS_DIR, "diabetes_calibrated_model.joblib")
CALIB_CONFIG_PATH = os.path.join(MODELS_DIR, "calibration_config.json")
RESULTS_JSON_PATH = os.path.join(EVAL_DIR, "calibration_and_ci_results.json")
REPORT_MD_PATH = os.path.join(PROCESSED_DIR, "CALIBRATION_AND_UNCERTAINTY_REPORT.md")

RANDOM_SEED = 42

from research_evaluation_metrics import compute_calibration_curve, CalibratedProbabilityModel

def compute_calibration_stats(y_true, y_prob, n_bins=10):
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins, strategy='uniform')
    if len(prob_pred) > 1:
        slope, intercept = np.polyfit(prob_pred, prob_true, 1)
    else:
        slope, intercept = 1.0, 0.0

    brier = brier_score_loss(y_true, y_prob)

    return {
        "brier_score": round(float(brier), 4),
        "calibration_slope": round(float(slope), 4),
        "calibration_intercept": round(float(intercept), 4),
        "prob_true": np.round(prob_true, 4).tolist(),
        "prob_pred": np.round(prob_pred, 4).tolist()
    }

def compute_bootstrap_confidence_intervals(y_true, y_prob, threshold=0.30, n_bootstraps=1000, seed=42):
    np.random.seed(seed)
    y_true = np.array(y_true)
    y_prob = np.array(y_prob)
    n_samples = len(y_true)
    
    boot_metrics = {
        "roc_auc": [],
        "accuracy": [],
        "recall_sensitivity": [],
        "specificity": [],
        "precision_ppv": [],
        "f1_score": []
    }

    for _ in range(n_bootstraps):
        idx = np.random.choice(n_samples, size=n_samples, replace=True)
        y_b_true = y_true[idx]
        y_b_prob = y_prob[idx]
        
        if len(np.unique(y_b_true)) < 2:
            continue
            
        y_b_pred = (y_b_prob >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_b_true, y_b_pred).ravel()

        boot_metrics["roc_auc"].append(roc_auc_score(y_b_true, y_b_prob))
        boot_metrics["accuracy"].append(accuracy_score(y_b_true, y_b_pred))
        boot_metrics["recall_sensitivity"].append(recall_score(y_b_true, y_b_pred, zero_division=0))
        boot_metrics["specificity"].append(tn / (tn + fp) if (tn + fp) > 0 else 0.0)
        boot_metrics["precision_ppv"].append(precision_score(y_b_true, y_b_pred, zero_division=0))
        boot_metrics["f1_score"].append(f1_score(y_b_true, y_b_pred, zero_division=0))

    ci_results = {}
    for metric_name, values in boot_metrics.items():
        point_estimate = float(np.mean(values))
        lower_ci = float(np.percentile(values, 2.5))
        upper_ci = float(np.percentile(values, 97.5))
        ci_results[metric_name] = {
            "mean": round(point_estimate, 4),
            "ci_95_lower": round(lower_ci, 4),
            "ci_95_upper": round(upper_ci, 4),
            "ci_formatted": f"{round(point_estimate, 4)} (95% CI: {round(lower_ci, 4)} – {round(upper_ci, 4)})"
        }

    return ci_results

def run_calibration_and_uncertainty_pipeline():
    print("==================================================")
    print("RUNNING PROBABILITY CALIBRATION & BOOTSTRAP UNCERTAINTY PIPELINE")
    print("==================================================")

    # 1. Load Validation & Test Datasets
    val_df = pd.read_csv(VAL_PATH)
    test_df = pd.read_csv(TEST_PATH)

    X_val = val_df.drop(columns=['diabetes']).values
    y_val = val_df['diabetes'].values

    X_test = test_df.drop(columns=['diabetes']).values
    y_test = test_df['diabetes'].values

    # 2. Load Base Production Model
    base_model = joblib.load(UNPROD_MODEL_PATH)
    with open(PROD_METADATA_PATH, "r") as f:
        meta = json.load(f)

    threshold = meta.get("production_threshold", 0.30)
    print(f"[Model] Base Model: {meta['model_name']} | Target Threshold = {threshold}")

    # 3. Evaluate Base Model Calibration on VALIDATION Set
    val_probs_base = base_model.predict_proba(X_val)[:, 1]
    base_val_calib = compute_calibration_stats(y_val, val_probs_base)
    print(f"[Validation Calib - Base] Brier = {base_val_calib['brier_score']} | Slope = {base_val_calib['calibration_slope']}")

    # 4. Investigate & Fit Calibration Methods ON VALIDATION DATA ONLY
    print("[Calibration] Fitting Platt Scaling (Sigmoid Logistic Regression) on VALIDATION set...")
    platt_scaler = LogisticRegression(C=1.0, max_iter=1000, random_state=RANDOM_SEED)
    platt_scaler.fit(val_probs_base.reshape(-1, 1), y_val)
    val_probs_sig = platt_scaler.predict_proba(val_probs_base.reshape(-1, 1))[:, 1]
    sig_val_calib = compute_calibration_stats(y_val, val_probs_sig)
    print(f"              -> Sigmoid (Platt): Brier = {sig_val_calib['brier_score']} | Slope = {sig_val_calib['calibration_slope']}")

    print("[Calibration] Fitting Isotonic Regression on VALIDATION set...")
    isotonic_scaler = IsotonicRegression(out_of_bounds='clip')
    isotonic_scaler.fit(val_probs_base, y_val)
    val_probs_iso = isotonic_scaler.transform(val_probs_base)
    iso_val_calib = compute_calibration_stats(y_val, val_probs_iso)
    print(f"              -> Isotonic:        Brier = {iso_val_calib['brier_score']} | Slope = {iso_val_calib['calibration_slope']}")

    # Select Best Calibrator (Lowest Validation Brier Score)
    calib_options = {
        "Uncalibrated": (None, base_val_calib["brier_score"]),
        "Sigmoid (Platt)": (platt_scaler, sig_val_calib["brier_score"]),
        "Isotonic": (isotonic_scaler, iso_val_calib["brier_score"])
    }
    best_calib_name = min(calib_options, key=lambda k: calib_options[k][1])
    best_scaler = calib_options[best_calib_name][0]

    print(f"\n[Selection] Selected Optimal Calibrator: '{best_calib_name}'")

    # Wrap into Calibrated Model
    calibrated_wrapper = CalibratedProbabilityModel(base_model, best_scaler, best_calib_name)

    # 5. Save Calibrated Model Artifact & Config
    joblib.dump(calibrated_wrapper, CALIB_MODEL_PATH)
    
    calib_config = {
        "base_model": meta['model_name'],
        "selected_calibration_method": best_calib_name,
        "fit_scope": "VALIDATION_DATA_ONLY (X_val)",
        "validation_brier_scores": {
            "Uncalibrated": base_val_calib["brier_score"],
            "Sigmoid (Platt)": sig_val_calib["brier_score"],
            "Isotonic": iso_val_calib["brier_score"]
        },
        "saved_calibrated_model_path": CALIB_MODEL_PATH
    }
    with open(CALIB_CONFIG_PATH, "w") as f:
        json.dump(calib_config, f, indent=2)

    # 6. Evaluate Calibrated Model ONCE on UNTOUCHED TEST Set
    test_probs_base = base_model.predict_proba(X_test)[:, 1]
    test_probs_calib = calibrated_wrapper.predict_proba(X_test)[:, 1]

    test_calib_stats_base = compute_calibration_stats(y_test, test_probs_base)
    test_calib_stats_calib = compute_calibration_stats(y_test, test_probs_calib)

    print("\n--- TEST SET EVALUATION: BASE VS CALIBRATED MODEL ---")
    print(f"Base Test Brier:       {test_calib_stats_base['brier_score']} | Slope = {test_calib_stats_base['calibration_slope']}")
    print(f"Calibrated Test Brier: {test_calib_stats_calib['brier_score']} | Slope = {test_calib_stats_calib['calibration_slope']}")

    # 7. Compute 95% Bootstrap Confidence Intervals (B = 1000) on TEST Set
    print("\n[Uncertainty] Computing 95% Bootstrap Confidence Intervals (B=1,000) on TEST set...")
    ci_base = compute_bootstrap_confidence_intervals(y_test, test_probs_base, threshold=threshold, n_bootstraps=1000)
    ci_calib = compute_bootstrap_confidence_intervals(y_test, test_probs_calib, threshold=threshold, n_bootstraps=1000)

    # 8. Save Complete Results JSON
    full_results = {
        "calibration_configuration": calib_config,
        "test_evaluation": {
            "uncalibrated_base": {
                "calibration_stats": test_calib_stats_base,
                "confidence_intervals_95": ci_base
            },
            "calibrated_model": {
                "calibration_stats": test_calib_stats_calib,
                "confidence_intervals_95": ci_calib
            }
        }
    }

    with open(RESULTS_JSON_PATH, "w") as f:
        json.dump(full_results, f, indent=2)

    # 9. Generate Markdown Report
    markdown_report = f"""# PROBABILITY CALIBRATION AND STATISTICAL UNCERTAINTY REPORT

**Model Algorithm**: **{meta['model_name']}**  
**Selected Calibration Method**: **{best_calib_name}** (Fitted ONCE on VALIDATION set)  
**Test Set Policy**: **Evaluated ONCE on untouched TEST set ($N={len(X_test):,}$, $B=1,000$ bootstraps)**  

---

## 1. Scientific Distinction: Discrimination vs Calibration

- **Discrimination**: The capacity of the model to rank and separate diabetic patients from non-diabetic patients (quantified by **ROC-AUC**, **PR-AUC**, **Sensitivity**, and **Specificity**).
- **Calibration**: The agreement between model-estimated risk probabilities and true observed disease prevalence (quantified by **Brier Score**, **Calibration Slope**, and **Reliability Curves**).

---

## 2. Statistical Uncertainty: 95% Bootstrap Confidence Intervals (TEST Set, $N=15,000$)

All empirical confidence intervals were computed via non-parametric bootstrapping ($B=1,000$ resamples) on the holdout test set.

| Performance Metric | Point Estimate & 95% Empirical Confidence Interval |
| :--- | :--- |
| **ROC-AUC** | **{ci_calib['roc_auc']['ci_formatted']}** |
| **Sensitivity (Recall)** | **{ci_calib['recall_sensitivity']['ci_formatted']}** |
| **Specificity** | **{ci_calib['specificity']['ci_formatted']}** |
| **Precision (PPV)** | **{ci_calib['precision_ppv']['ci_formatted']}** |
| **F1-Score** | **{ci_calib['f1_score']['ci_formatted']}** |
| **Accuracy** | **{ci_calib['accuracy']['ci_formatted']}** |

---

## 3. Probability Calibration Assessment (TEST Set)

Evaluating probability calibration accuracy on the test set before and after calibration:

| Calibration Metric | Base Uncalibrated Model | Calibrated Model ({best_calib_name}) | Optimal Clinical Target |
| :--- | :--- | :--- | :--- |
| **Brier Score (MSE)** | {test_calib_stats_base['brier_score']} | **{test_calib_stats_calib['brier_score']}** | 0.0 (Lower is better) |
| **Calibration Slope** | {test_calib_stats_base['calibration_slope']} | **{test_calib_stats_calib['calibration_slope']}** | 1.0 (Ideal calibration slope) |
| **Calibration Intercept** | {test_calib_stats_base['calibration_intercept']} | **{test_calib_stats_calib['calibration_intercept']}** | 0.0 (Zero systematic bias) |

---

## 4. Pipeline Artifacts Created

1. **Calibrated Model Artifact**: `{CALIB_MODEL_PATH}`
2. **Calibration Configuration**: `{CALIB_CONFIG_PATH}`
3. **Statistical Results & CIs JSON**: `{RESULTS_JSON_PATH}`
4. **Markdown Report**: `{REPORT_MD_PATH}`
"""

    with open(REPORT_MD_PATH, "w") as f:
        f.write(markdown_report)

    print(f"[SUCCESS] Calibration & CI Pipeline completed! Report written to {REPORT_MD_PATH}")
    print("==================================================")
    return full_results

if __name__ == "__main__":
    run_calibration_and_uncertainty_pipeline()
