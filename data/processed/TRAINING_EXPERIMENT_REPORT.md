# DIABETES MACHINE LEARNING MODEL TRAINING EXPERIMENT REPORT

**Training Set (`X_train`)**: 70,000 records (5-Fold Stratified CV)  
**Validation Set (`X_val`)**: 15,000 records (Unseen Selection Set)  
**Selected Production Model**: **HistGradientBoosting**  
**Selected Screening Threshold**: `0.3`  
**Test Set Policy**: **UNTOUCHED (Preserved for final holdout testing)**  

---

## 1. Algorithm Comparison Table (Evaluated on Validation Set at Default 0.50 Threshold)

| Model Algorithm | 5-Fold CV ROC-AUC | Val ROC-AUC | Val PR-AUC | Val Sensitivity (Recall) | Val Specificity | Val Precision (PPV) | Val NPV | Val F1-Score | Val Brier Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **LogisticRegression** | 0.999 \pm 0.0001 | **0.999** | 0.9905 | **0.9297** | 0.9968 | 0.9635 | 0.9936 | 0.9463 | 0.0064 |
| **DecisionTree** | 0.997 \pm 0.001 | **0.9976** | 0.991 | **0.972** | 0.9979 | 0.9767 | 0.9975 | 0.9744 | 0.0034 |
| **RandomForest** | 0.9996 \pm 0.0 | **0.9997** | 0.9971 | **0.94** | 0.9995 | 0.9941 | 0.9946 | 0.9663 | 0.0044 |
| **HistGradientBoosting** | 0.9997 \pm 0.0 | **0.9998** | 0.9982 | **0.9712** | 0.9984 | 0.9822 | 0.9974 | 0.9767 | 0.0028 |
| **XGBoost** | 0.9997 \pm 0.0 | **0.9998** | 0.9982 | **0.9704** | 0.9986 | 0.9846 | 0.9973 | 0.9775 | 0.0028 |

---

## 2. Threshold Performance Analysis (Validation Set, HistGradientBoosting)

Evaluating multiple decision thresholds to select an optimal screening threshold:

| Threshold | Sensitivity | Specificity | Precision (PPV) | NPV | F1-Score | Accuracy | False Negatives | False Positives |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 0.1 | 0.9928 | 0.9943 | 0.9409 | 0.9993 | 0.9662 | 0.9942 | 9 | 78 |
| 0.15 | 0.9896 | 0.9953 | 0.9501 | 0.9991 | 0.9695 | 0.9948 | 13 | 65 |
| 0.2 | 0.988 | 0.996 | 0.9574 | 0.9989 | 0.9725 | 0.9953 | 15 | 55 |
| 0.25 | 0.9864 | 0.9965 | 0.9626 | 0.9988 | 0.9743 | 0.9957 | 17 | 48 |
| 0.3 | 0.9848 | 0.997 | 0.9678 | 0.9986 | 0.9762 | 0.996 | 19 | 41 |
| 0.35 | 0.98 | 0.9977 | 0.9746 | 0.9982 | 0.9773 | 0.9962 | 25 | 32 |
| 0.4 | 0.9784 | 0.9979 | 0.9769 | 0.998 | 0.9776 | 0.9963 | 27 | 29 |
| 0.5 | 0.9712 | 0.9984 | 0.9822 | 0.9974 | 0.9767 | 0.9961 | 36 | 22 |
| 0.6 | 0.9672 | 0.999 | 0.9886 | 0.997 | 0.9778 | 0.9963 | 41 | 14 |
| 0.7 | 0.96 | 0.9991 | 0.9893 | 0.9964 | 0.9744 | 0.9958 | 50 | 13 |


---

## 3. Selected Production Screening Configuration

- **Model**: `HistGradientBoosting`
- **Configured Threshold**: `0.3`
- **Sensitivity at `0.3`**: `0.9848`
- **Specificity at `0.3`**: `0.997`
- **Negative Predictive Value (NPV)**: `0.9986`
- **Clinical Rationale**: For a diabetes risk screening tool, maximizing **Sensitivity** and **NPV** minimizes dangerous false negatives (diabetic patients erroneously told they are low risk).
