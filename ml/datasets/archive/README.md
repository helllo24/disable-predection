# Legacy & Archived Datasets

This directory contains archived datasets and legacy script outputs preserved strictly for scientific transparency and reproducibility auditing.

## Archived Files

1. **`legacy_synthetic_mendeley_diabetes.csv`**
   - **Rows**: 1,168
   - **Features**: 9 (`Pregnancies`, `Glucose`, `BloodPressure`, `SkinThickness`, `Insulin`, `BMI`, `DiabetesPedigreeFunction`, `Age`, `Sex`) + `Outcome`
   - **Provenance**: **SYNTHETIC / GENERATED** locally using Gaussian/Poisson/Exponential random distributions (`np.random.normal`, `np.random.poisson`, `np.random.exponential`) in `ml/training/train_external_validation.py`.
   - **Reason for Archiving**: This dataset was previously mislabeled as the "Mendeley Diabetes Dataset" ($n=1,168$) in code comments, validation reports, and papers.
   - **Usage Restriction**: **INVALID FOR SCIENTIFIC RESEARCH VALIDATION**. This dataset MUST NOT be passed off as an external, independent clinical cohort.

2. **`../training/archive/legacy_train_synthetic_validation.py`**
   - **Description**: Legacy training script that generated `legacy_synthetic_mendeley_diabetes.csv` on the fly and computed zero-shot validation metrics.
   - **Status**: Archived for auditability. Superceded by `ml/training/train_external_validation.py`.
