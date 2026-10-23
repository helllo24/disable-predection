# REAL SHAP FEATURE IMPORTANCE & EXPLAINABILITY REPORT

**Model Evaluated**: **HistGradientBoosting**  
**Evaluation Cohort**: 1,000 preprocessed patient records  
**Base Expected Value ($E[f(x)]$)**: `-8.5780`  
**Top Calculated Feature**: **HbA1c_level** (Mean $|\text{SHAP}| = 2.6765$)  

---

## 1. Empirical SHAP Global Feature Importance Ranking

*Note: All feature rankings are calculated directly from empirical SHAP value magnitude averages.*

| Rank | Feature Name | Mean $|\text{SHAP}|$ Contribution | Clinical Interpretation in Model |
| :--- | :--- | :--- | :--- |
| **#1** | `HbA1c_level` | **2.6765** | Feature magnitude contribution to risk prediction |
| **#2** | `blood_glucose_level` | **0.3289** | Feature magnitude contribution to risk prediction |
| **#3** | `age` | **0.1369** | Feature magnitude contribution to risk prediction |
| **#4** | `bmi` | **0.0788** | Feature magnitude contribution to risk prediction |
| **#5** | `hypertension` | **0.0117** | Feature magnitude contribution to risk prediction |
| **#6** | `heart_disease` | **0.0069** | Feature magnitude contribution to risk prediction |
| **#7** | `smoking_history_current` | **0.0028** | Feature magnitude contribution to risk prediction |
| **#8** | `smoking_history_No Info` | **0.002** | Feature magnitude contribution to risk prediction |
| **#9** | `smoking_history_never` | **0.0013** | Feature magnitude contribution to risk prediction |
| **#10** | `gender_Female` | **0.0011** | Feature magnitude contribution to risk prediction |
| **#11** | `smoking_history_ever` | **0.0011** | Feature magnitude contribution to risk prediction |
| **#12** | `smoking_history_not current` | **0.0009** | Feature magnitude contribution to risk prediction |
| **#13** | `gender_Male` | **0.0008** | Feature magnitude contribution to risk prediction |
| **#14** | `smoking_history_former` | **0.0004** | Feature magnitude contribution to risk prediction |
| **#15** | `gender_Other` | **0.0** | Feature magnitude contribution to risk prediction |

---

## 2. Empirical Findings

- Empirical SHAP analysis confirms that **`HbA1c_level`** and **`blood_glucose_level`** are the top 2 mathematical predictors in the `HistGradientBoosting` model.
- Features with positive SHAP values push the patient's predicted diabetes probability higher, whereas negative SHAP values shift the risk score lower.

---

## 3. Sample Individual Patient Risk Explanation

- **Patient Risk Score**: `100.0%`
- **Model Base Expected Value**: `-857.8%`

### Top Factors Increasing Risk Contribution:
- **`HbA1c_level`** (Value: `2.9321`): Contributed `+15.2072` to increasing risk score (91.85% relative shift).
- **`blood_glucose_level`** (Value: `2.374`): Contributed `+1.1728` to increasing risk score (7.08% relative shift).
- **`bmi`** (Value: `2.4777`): Contributed `+0.0865` to increasing risk score (0.52% relative shift).

### Top Factors Decreasing Risk Contribution:
- **`smoking_history_not current`** (Value: `1.0`): Contributed `-0.0031` to lowering risk score (0.02% relative shift).
- **`hypertension`** (Value: `0.0`): Contributed `-0.003` to lowering risk score (0.02% relative shift).
- **`smoking_history_No Info`** (Value: `0.0`): Contributed `-0.0027` to lowering risk score (0.02% relative shift).

### Non-Technical Patient Communication:
> "The model estimated a diabetes risk probability of 100.0%. Features such as HbA1c_level, blood_glucose_level, bmi contributed positively to increasing the risk score, while features like smoking_history_not current, hypertension, smoking_history_No Info contributed to lowering the risk score. Note: These contributions represent feature weights in the predictive model and do NOT imply direct medical causation."

---

## 4. Pipeline Artifacts Created

1. **SHAP Analysis JSON**: `C:\Users\Admin\.gemini\antigravity\scratch\smart-healthcare-assistant\ml\evaluation\shap_analysis_results.json`
2. **SHAP Feature Rankings CSV**: `C:\Users\Admin\.gemini\antigravity\scratch\smart-healthcare-assistant\data\processed\shap_feature_rankings.csv`
3. **SHAP Values CSV**: `C:\Users\Admin\.gemini\antigravity\scratch\smart-healthcare-assistant\data\processed\shap_values.csv`
4. **SHAP Summary Plot**: `C:\Users\Admin\.gemini\antigravity\scratch\smart-healthcare-assistant\data\processed\shap_summary_plot.png`
5. **SHAP Bar Plot**: `C:\Users\Admin\.gemini\antigravity\scratch\smart-healthcare-assistant\data\processed\shap_bar_plot.png`
