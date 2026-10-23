import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score, average_precision_score, accuracy_score,
    precision_score, recall_score, f1_score, confusion_matrix,
    brier_score_loss, roc_curve, precision_recall_curve
)

class CalibratedProbabilityModel:
    """
    Wrapper class combining base classifier with a probability calibrator (Platt / Isotonic).
    """
    def __init__(self, base_model, calibrator, method_name):
        self.base_model = base_model
        self.calibrator = calibrator
        self.method_name = method_name

    def predict_proba(self, X):
        base_probs = self.base_model.predict_proba(X)[:, 1]
        if self.method_name == "Sigmoid (Platt)":
            calib_probs = self.calibrator.predict_proba(base_probs.reshape(-1, 1))[:, 1]
        elif self.method_name == "Isotonic":
            calib_probs = self.calibrator.transform(base_probs)
        else:
            calib_probs = base_probs
        
        return np.vstack([1.0 - calib_probs, calib_probs]).T

    def predict(self, X, threshold=0.30):
        probs = self.predict_proba(X)[:, 1]
        return (probs >= threshold).astype(int)

def compute_calibration_curve(y_true, y_prob, n_bins=10):
    y_true = np.array(y_true)
    y_prob = np.array(y_prob)

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_centers = []
    prob_true = []
    prob_pred = []
    
    for i in range(n_bins):
        idx = (y_prob >= bin_edges[i]) & (y_prob < bin_edges[i+1])
        if np.sum(idx) > 0:
            bin_centers.append(float(np.mean(bin_edges[i:i+2])))
            prob_true.append(float(np.mean(y_true[idx])))
            prob_pred.append(float(np.mean(y_prob[idx])))

    if len(prob_pred) > 1:
        slope, intercept = np.polyfit(prob_pred, prob_true, 1)
    else:
        slope, intercept = 1.0, 0.0

    return {
        "bin_centers": np.round(bin_centers, 4).tolist(),
        "prob_true": np.round(prob_true, 4).tolist(),
        "prob_pred": np.round(prob_pred, 4).tolist(),
        "calibration_slope": round(float(slope), 4),
        "calibration_intercept": round(float(intercept), 4)
    }

def evaluate_clinical_model(y_true, y_prob, threshold=0.50):
    y_true = np.array(y_true)
    y_prob = np.array(y_prob)
    y_pred = (y_prob >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    roc_auc = float(roc_auc_score(y_true, y_prob))
    pr_auc = float(average_precision_score(y_true, y_prob))
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    npv = float(tn / (tn + fn)) if (tn + fn) > 0 else 0.0
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    brier = float(brier_score_loss(y_true, y_prob))

    fpr_arr, tpr_arr, _ = roc_curve(y_true, y_prob)
    sub_sample_idx = np.linspace(0, len(fpr_arr) - 1, min(50, len(fpr_arr)), dtype=int)
    roc_curve_data = {
        "fpr": np.round(fpr_arr[sub_sample_idx], 4).tolist(),
        "tpr": np.round(tpr_arr[sub_sample_idx], 4).tolist()
    }

    p_arr, r_arr, _ = precision_recall_curve(y_true, y_prob)
    sub_sample_pr_idx = np.linspace(0, len(p_arr) - 1, min(50, len(p_arr)), dtype=int)
    pr_curve_data = {
        "precision": np.round(p_arr[sub_sample_pr_idx], 4).tolist(),
        "recall": np.round(r_arr[sub_sample_pr_idx], 4).tolist()
    }

    calibration_data = compute_calibration_curve(y_true, y_prob)

    return {
        "threshold": round(float(threshold), 2),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "accuracy": round(acc, 4),
        "precision_ppv": round(prec, 4),
        "sensitivity_recall": round(rec, 4),
        "specificity": round(spec, 4),
        "npv": round(npv, 4),
        "f1_score": round(f1, 4),
        "brier_score": round(brier, 4),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp)
        },
        "roc_curve": roc_curve_data,
        "pr_curve": pr_curve_data,
        "calibration": calibration_data
    }

def analyze_threshold_grid(y_true, y_prob, thresholds=None):
    if thresholds is None:
        thresholds = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60, 0.70]

    y_true = np.array(y_true)
    y_prob = np.array(y_prob)

    rows = []
    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

        acc = float(accuracy_score(y_true, y_pred))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
        npv = float(tn / (tn + fn)) if (tn + fn) > 0 else 0.0
        f1 = float(f1_score(y_true, y_pred, zero_division=0))

        rows.append({
            "Threshold": round(t, 2),
            "Sensitivity": round(rec, 4),
            "Specificity": round(spec, 4),
            "Precision_PPV": round(prec, 4),
            "NPV": round(npv, 4),
            "F1_Score": round(f1, 4),
            "Accuracy": round(acc, 4),
            "False_Negatives": int(fn),
            "False_Positives": int(fp)
        })

    return pd.DataFrame(rows)
