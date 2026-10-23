# REPRODUCIBLE DATASET SPLITTING & PREPROCESSING REPORT

**Dataset**: Healthcare EHR 100K Diabetes Prediction Dataset  
**Random Seed**: `42`  
**Fit Scope**: **Strictly Training Set (`TRAIN`) Only**  
**Test Set Policy**: **UNTOUCHED until final evaluation**  

---

## 1. Stratified Dataset Splitting Summary

| Split Name | Row Count ($N$) | Percentage (%) | Negative Count (0) | Positive Count (1) | Positive Ratio (%) | Isolation Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TRAIN** | **70,000** | 70.0% | 64,164 | 5,836 | 8.34% | Model Training & Transformer Fitting |
| **VALIDATION** | **15,000** | 15.0% | 13,749 | 1,251 | 8.34% | Hyperparameter Tuning & Selection |
| **TEST** | **15,000** | 15.0% | 13,750 | 1,250 | 8.33% | **UNTOUCHED (Final Evaluation Only)** |

---

## 2. Reproducibility & Pipeline Configuration

- **Dataset Version**: `1.0.0`
- **Preprocessing Version**: `1.0.0`
- **Random Seed**: `42`
- **Fitted Pipeline Artifact**: `C:\Users\Admin\.gemini\antigravity\scratch\smart-healthcare-assistant\ml\models\diabetes_100k_preprocessor.joblib`
- **Feature Count**: `15` transformed features
- **Benchmark Experiment**: Pima Indians dataset ($N=768$) kept strictly separate in `data/benchmark/pima_indians_diabetes.csv`.

---

## 3. Transformed Features

```json
[
  "age",
  "bmi",
  "HbA1c_level",
  "blood_glucose_level",
  "gender_Female",
  "gender_Male",
  "gender_Other",
  "smoking_history_No Info",
  "smoking_history_current",
  "smoking_history_ever",
  "smoking_history_former",
  "smoking_history_never",
  "smoking_history_not current",
  "hypertension",
  "heart_disease"
]
```
