# FAIRNESS AND SUBGROUP PERFORMANCE ANALYSIS REPORT

**Evaluation Set**: Untouched Holdout TEST Set ($N=15,000$)  
**Production Screening Threshold**: `0.3`  
**Fairness Policy**: **Transparent Reporting** (No artificial metric equalization or suppression of unfavorable subgroup findings).  

---

## 1. Demographic & Clinical Subgroup Performance Table

| Subgroup Category | Records ($N$) | Prevalence (%) | ROC-AUC (95% CI) | Sensitivity (95% CI) | Specificity | FPR | FNR | Precision | Brier Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Overall Cohort (All Patients)** | 15,000 | 8.33% | **0.9984** | **0.9816** | 0.9959 | 0.0041 | 0.0184 | 0.9556 | 0.0034 |
| **Female Cohort** | 8,711 | 8.23% | **0.9983** | **0.9819** | 0.9956 | 0.0044 | 0.0181 | 0.9526 | 0.0033 |
| **Male Cohort** | 6,274 | 8.5% | **0.9987** | **0.9812** | 0.9962 | 0.0038 | 0.0188 | 0.9596 | 0.0035 |
| **Age < 30 (Younger Adults)** | 3,957 | 0.15% | **1.0** | **1.0** | 1.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| **Age 30–49 (Middle-Aged Adults)** | 6,056 | 3.57% | **0.9974** | **0.9444** | 0.9983 | 0.0017 | 0.0556 | 0.9533 | 0.0025 |
| **Age >= 50 (Older Adults / High Risk)** | 4,987 | 20.61% | **0.9981** | **0.9893** | 0.9881 | 0.0119 | 0.0107 | 0.9558 | 0.0072 |
| **Hypertension Present** | 1,103 | 26.84% | **0.996** | **0.9865** | 0.9888 | 0.0112 | 0.0135 | 0.9701 | 0.0101 |
| **Hypertension Absent** | 13,897 | 6.86% | **0.9987** | **0.9801** | 0.9963 | 0.0037 | 0.0199 | 0.9512 | 0.0029 |
| **Heart Disease Present** | 622 | 32.64% | **0.9997** | **0.9852** | 0.9881 | 0.0119 | 0.0148 | 0.9756 | 0.0086 |
| **Heart Disease Absent** | 14,378 | 7.28% | **0.9982** | **0.9809** | 0.9961 | 0.0039 | 0.0191 | 0.9518 | 0.0032 |

---

## 2. Demographic Disparity Audit Findings

- **Sex Subgroup Disparity**:
  - Female Cohort ROC-AUC: `0.9983` (95% CI: `0.9983 (0.9958 – 0.9998)`)
  - Male Cohort ROC-AUC: `0.9987` (95% CI: `0.9987 (0.9966 – 0.9998)`)
  - **Sex ROC-AUC Gap**: `0.0004` (Equitable discrimination across biological sexes).

- **Age Subgroup Disparity**:
  - Age < 30 ROC-AUC: `1.0`
  - Age $\ge$ 50 ROC-AUC: `0.9981`
  - **Age ROC-AUC Gap**: `0.0019`.

---

## 3. Methodological Discussion & Limitations

1. **Prevalence Differences**: Older adults ($\ge 50$ yrs) have higher positive prevalence compared to pediatric/younger cohorts ($< 30$ yrs).
2. **Small Subgroup Sample Guidance**: Subgroup performance is reported transparently without artificial metric equalization to preserve empirical integrity.

---

## 4. Pipeline Artifacts Created

1. **Subgroup Fairness JSON**: `C:\Users\Admin\.gemini\antigravity\scratch\smart-healthcare-assistant\ml\evaluation\fairness_analysis_results.json`
2. **Subgroup Fairness CSV**: `C:\Users\Admin\.gemini\antigravity\scratch\smart-healthcare-assistant\data\processed\subgroup_fairness_table.csv`
3. **Subgroup ROC-AUC Chart**: `C:\Users\Admin\.gemini\antigravity\scratch\smart-healthcare-assistant\data\processed\subgroup_roc_auc_chart.png`
4. **Subgroup Sensitivity Chart**: `C:\Users\Admin\.gemini\antigravity\scratch\smart-healthcare-assistant\data\processed\subgroup_sensitivity_chart.png`
5. **Markdown Report**: `C:\Users\Admin\.gemini\antigravity\scratch\smart-healthcare-assistant\data\processed\FAIRNESS_AND_SUBGROUP_REPORT.md`
