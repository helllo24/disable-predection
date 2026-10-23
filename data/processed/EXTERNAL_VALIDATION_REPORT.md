# TRUE EXTERNAL VALIDATION AUDIT REPORT

**Status**: **External validation pending verified independent dataset.**  
**Model Name**: `HistGradientBoosting`  
**Internal Baseline**: 100K Test Set ($N=15,000$, ROC-AUC = `0.9984`)  

---

## 1. Provenance Audit Notice

The 1,168-row dataset previously labeled as "Mendeley External Validation" was identified as **locally generated synthetic data** (`np.random.normal`) and unlinked from scientific validation.

In accordance with strict research rules:
- **No synthetic data** was used for validation.
- **No fake replacement metrics** were generated.
- Execution stopped before calculating external validation metrics.

---

## 2. Internal Test Baseline Metrics (Calibrated Model, Threshold = `0.3`)

| Metric | Internal Test Performance |
| :--- | :--- |
| **ROC-AUC** | **0.9984** |
| **PR-AUC** | **0.9921** |
| **Sensitivity (Recall)** | **0.9816 (98.16%)** |
| **Specificity** | **0.9959 (99.60%)** |
| **Precision (PPV)** | **0.9556 (95.71%)** |
| **NPV** | **0.9983 (99.83%)** |
| **Brier Score** | **0.0034** |

---

## 3. Integration Path for Verified Independent Cohort

To complete zero-shot external validation:
1. Download the authentic Mendeley dataset (DOI: `10.17632/nxnty5g7y6.2`).
2. Place the CSV at `data/external/mendeley_diabetes_real.csv`.
3. Re-run `python ml/evaluation/run_true_external_validation.py`.
