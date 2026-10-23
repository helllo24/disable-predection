# PROBABILITY CALIBRATION AND STATISTICAL UNCERTAINTY REPORT

**Model Algorithm**: **HistGradientBoosting**  
**Selected Calibration Method**: **Isotonic** (Fitted ONCE on VALIDATION set)  
**Test Set Policy**: **Evaluated ONCE on untouched TEST set ($N=15,000$, $B=1,000$ bootstraps)**  

---

## 1. Scientific Distinction: Discrimination vs Calibration

- **Discrimination**: The capacity of the model to rank and separate diabetic patients from non-diabetic patients (quantified by **ROC-AUC**, **PR-AUC**, **Sensitivity**, and **Specificity**).
- **Calibration**: The agreement between model-estimated risk probabilities and true observed disease prevalence (quantified by **Brier Score**, **Calibration Slope**, and **Reliability Curves**).

---

## 2. Statistical Uncertainty: 95% Bootstrap Confidence Intervals (TEST Set, $N=15,000$)

All empirical confidence intervals were computed via non-parametric bootstrapping ($B=1,000$ resamples) on the holdout test set.

| Performance Metric | Point Estimate & 95% Empirical Confidence Interval |
| :--- | :--- |
| **ROC-AUC** | **0.9985 (95% CI: 0.9968 – 0.9997)** |
| **Sensitivity (Recall)** | **0.9817 (95% CI: 0.9738 – 0.9888)** |
| **Specificity** | **0.9958 (95% CI: 0.9948 – 0.9969)** |
| **Precision (PPV)** | **0.9554 (95% CI: 0.9437 – 0.9662)** |
| **F1-Score** | **0.9683 (95% CI: 0.9612 – 0.9753)** |
| **Accuracy** | **0.9947 (95% CI: 0.9935 – 0.9958)** |

---

## 3. Probability Calibration Assessment (TEST Set)

Evaluating probability calibration accuracy on the test set before and after calibration:

| Calibration Metric | Base Uncalibrated Model | Calibrated Model (Isotonic) | Optimal Clinical Target |
| :--- | :--- | :--- | :--- |
| **Brier Score (MSE)** | 0.0033 | **0.0034** | 0.0 (Lower is better) |
| **Calibration Slope** | 0.9067 | **0.9822** | 1.0 (Ideal calibration slope) |
| **Calibration Intercept** | 0.0333 | **-0.0321** | 0.0 (Zero systematic bias) |

---

## 4. Pipeline Artifacts Created

1. **Calibrated Model Artifact**: `C:\Users\Admin\.gemini\antigravity\scratch\smart-healthcare-assistant\ml\models\diabetes_calibrated_model.joblib`
2. **Calibration Configuration**: `C:\Users\Admin\.gemini\antigravity\scratch\smart-healthcare-assistant\ml\models\calibration_config.json`
3. **Statistical Results & CIs JSON**: `C:\Users\Admin\.gemini\antigravity\scratch\smart-healthcare-assistant\ml\evaluation\calibration_and_ci_results.json`
4. **Markdown Report**: `C:\Users\Admin\.gemini\antigravity\scratch\smart-healthcare-assistant\data\processed\CALIBRATION_AND_UNCERTAINTY_REPORT.md`
