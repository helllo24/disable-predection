import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score, average_precision_score, accuracy_score,
    precision_score, recall_score, f1_score, confusion_matrix,
    brier_score_loss, roc_curve, precision_recall_curve
)


class CalibratedProbabilityModel:
    """Wrap a binary classifier with a fitted sigmoid or isotonic calibrator.

    The calibrator must be fitted on held-out or out-of-fold predictions, not
    predictions from the same rows used to fit the base estimator.
    """

    def __init__(self, base_model, calibrator, method_name):
        self.base_model = base_model
        self.calibrator = calibrator
        self.method_name = method_name
        # Explicit binary class order for sklearn-like consumers.
        self.classes_ = np.array([0, 1])

    def predict_proba(self, X):
        if not hasattr(self.base_model, "predict_proba"):
            raise TypeError("base_model must implement predict_proba().")

        base_matrix = np.asarray(self.base_model.predict_proba(X), dtype=float)
        if base_matrix.ndim != 2 or base_matrix.shape[0] != len(X):
            raise ValueError(
                "base_model.predict_proba() returned an unexpected shape: "
                f"{base_matrix.shape}"
            )

        base_classes = getattr(self.base_model, "classes_", None)
        if base_classes is not None:
            base_classes = list(base_classes)
            if 1 not in base_classes:
                raise ValueError(f"Positive class label 1 not found in {base_classes}.")
            positive_index = base_classes.index(1)
        else:
            if base_matrix.shape[1] != 2:
                raise ValueError("Cannot identify positive-class column in base model output.")
            positive_index = 1

        base_probs = base_matrix[:, positive_index]
        if not np.all(np.isfinite(base_probs)) or np.any((base_probs < 0) | (base_probs > 1)):
            raise ValueError("Base model returned invalid probabilities.")

        if self.method_name == "Sigmoid (Platt)":
            calibrated = self.calibrator.predict_proba(base_probs.reshape(-1, 1))
            calibrated = np.asarray(calibrated, dtype=float)
            calibrator_classes = getattr(self.calibrator, "classes_", None)
            if calibrator_classes is not None and 1 in list(calibrator_classes):
                calibrated_positive_index = list(calibrator_classes).index(1)
            else:
                if calibrated.ndim != 2 or calibrated.shape[1] != 2:
                    raise ValueError("Sigmoid calibrator returned an unexpected probability shape.")
                calibrated_positive_index = 1
            calibrated_probs = calibrated[:, calibrated_positive_index]

        elif self.method_name == "Isotonic":
            if not hasattr(self.calibrator, "transform"):
                raise TypeError("Isotonic calibrator must implement transform().")
            calibrated_probs = np.asarray(self.calibrator.transform(base_probs), dtype=float)

        elif self.method_name in (None, "None", "Uncalibrated"):
            calibrated_probs = base_probs

        else:
            raise ValueError(f"Unsupported calibration method: {self.method_name!r}")

        calibrated_probs = np.asarray(calibrated_probs, dtype=float).reshape(-1)
        if calibrated_probs.shape[0] != base_probs.shape[0]:
            raise ValueError("Calibrator output length does not match input length.")
        if not np.all(np.isfinite(calibrated_probs)):
            raise ValueError("Calibrator returned NaN or infinite probabilities.")

        # Numerical safety only; this does not prevent legitimate exact 0/1
        # outputs from an isotonic calibrator.
        calibrated_probs = np.clip(calibrated_probs, 0.0, 1.0)
        return np.column_stack((1.0 - calibrated_probs, calibrated_probs))

    def predict(self, X, threshold=0.30):
        if not 0.0 <= float(threshold) <= 1.0:
            raise ValueError("threshold must be between 0 and 1.")
        probs = self.predict_proba(X)[:, 1]
        return (probs >= float(threshold)).astype(int)


def compute_calibration_curve(y_true, y_prob, n_bins=10):
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob, dtype=float)
    if y_true.shape[0] != y_prob.shape[0]:
        raise ValueError("y_true and y_prob must have the same length.")
    if n_bins < 1:
        raise ValueError("n_bins must be >= 1.")
    if not np.all(np.isfinite(y_prob)) or np.any((y_prob < 0) | (y_prob > 1)):
        raise ValueError("y_prob must contain finite probabilities in [0, 1].")

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_centers, prob_true, prob_pred = [], [], []

    for i in range(n_bins):
        # Include probability 1.0 in the final bin.
        if i == n_bins - 1:
            idx = (y_prob >= bin_edges[i]) & (y_prob <= bin_edges[i + 1])
        else:
            idx = (y_prob >= bin_edges[i]) & (y_prob < bin_edges[i + 1])
        if np.any(idx):
            bin_centers.append(float((bin_edges[i] + bin_edges[i + 1]) / 2.0))
            prob_true.append(float(np.mean(y_true[idx])))
            prob_pred.append(float(np.mean(y_prob[idx])))

    if len(prob_pred) > 1 and np.ptp(prob_pred) > 0:
        slope, intercept = np.polyfit(prob_pred, prob_true, 1)
    else:
        slope, intercept = 1.0, 0.0

    return {
        "bin_centers": np.round(bin_centers, 4).tolist(),
        "prob_true": np.round(prob_true, 4).tolist(),
        "prob_pred": np.round(prob_pred, 4).tolist(),
        "calibration_slope": round(float(slope), 4),
        "calibration_intercept": round(float(intercept), 4),
    }


def evaluate_clinical_model(y_true, y_prob, threshold=0.50):
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob, dtype=float)
    if y_true.shape[0] != y_prob.shape[0]:
        raise ValueError("y_true and y_prob must have the same length.")
    if not np.all(np.isfinite(y_prob)) or np.any((y_prob < 0) | (y_prob > 1)):
        raise ValueError("y_prob must contain finite probabilities in [0, 1].")
    if not 0.0 <= float(threshold) <= 1.0:
        raise ValueError("threshold must be between 0 and 1.")
    if len(np.unique(y_true)) != 2:
        raise ValueError("y_true must contain both binary classes 0 and 1.")

    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    roc_auc = float(roc_auc_score(y_true, y_prob))
    pr_auc = float(average_precision_score(y_true, y_prob))
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    spec = float(tn / (tn + fp)) if (tn + fp) else 0.0
    npv = float(tn / (tn + fn)) if (tn + fn) else 0.0
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    brier = float(brier_score_loss(y_true, y_prob))

    fpr_arr, tpr_arr, _ = roc_curve(y_true, y_prob)
    sub_sample_idx = np.linspace(0, len(fpr_arr) - 1, min(50, len(fpr_arr)), dtype=int)
    roc_curve_data = {
        "fpr": np.round(fpr_arr[sub_sample_idx], 4).tolist(),
        "tpr": np.round(tpr_arr[sub_sample_idx], 4).tolist(),
    }

    p_arr, r_arr, _ = precision_recall_curve(y_true, y_prob)
    sub_sample_pr_idx = np.linspace(0, len(p_arr) - 1, min(50, len(p_arr)), dtype=int)
    pr_curve_data = {
        "precision": np.round(p_arr[sub_sample_pr_idx], 4).tolist(),
        "recall": np.round(r_arr[sub_sample_pr_idx], 4).tolist(),
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
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "roc_curve": roc_curve_data,
        "pr_curve": pr_curve_data,
        "calibration": calibration_data,
    }


def analyze_threshold_grid(y_true, y_prob, thresholds=None):
    if thresholds is None:
        thresholds = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60, 0.70]
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob, dtype=float)
    if y_true.shape[0] != y_prob.shape[0]:
        raise ValueError("y_true and y_prob must have the same length.")
    if len(np.unique(y_true)) != 2:
        raise ValueError("y_true must contain both binary classes 0 and 1.")
    if not np.all(np.isfinite(y_prob)) or np.any((y_prob < 0) | (y_prob > 1)):
        raise ValueError("y_prob must contain finite probabilities in [0, 1].")

    rows = []
    for threshold in thresholds:
        threshold = float(threshold)
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Invalid threshold: {threshold}")
        y_pred = (y_prob >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        spec = float(tn / (tn + fp)) if (tn + fp) else 0.0
        npv = float(tn / (tn + fn)) if (tn + fn) else 0.0
        rows.append({
            "Threshold": round(threshold, 2),
            "Sensitivity": round(rec, 4),
            "Specificity": round(spec, 4),
            "Precision_PPV": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
            "NPV": round(npv, 4),
            "F1_Score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
            "Accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
            "False_Negatives": int(fn),
            "False_Positives": int(fp),
        })
    return pd.DataFrame(rows)
