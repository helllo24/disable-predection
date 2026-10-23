# Genuine External Dataset Integration Guide

This directory (`ml/datasets/external/`) is designated for storing verified, real-world external validation datasets for independent model testing.

## Preferred Cohort: Mendeley Diabetes Dataset

- **Official Title**: Predicting Diabetes From Tracking Medical Records
- **Source**: Mendeley Data (Rashid, 2021) / DOI: `10.17632/nxnty5g7y6.2`
- **Expected Filename**: `mendeley_diabetes_real.csv`
- **Expected Target Path**: `ml/datasets/external/mendeley_diabetes_real.csv`

---

## Required Data Schema

To execute zero-shot external validation using `ml/training/train_external_validation.py`, the CSV file must conform to the following schema:

| Column Name | Data Type | Units / Range | Description |
| :--- | :--- | :--- | :--- |
| `Pregnancies` | `int` | `0 – 17` | Number of times pregnant (0 for male patients) |
| `Glucose` | `float` / `int` | `0 – 300 mg/dL` | Plasma glucose concentration (2-hour oral glucose tolerance test) |
| `BloodPressure` | `float` / `int` | `0 – 140 mmHg` | Diastolic blood pressure |
| `SkinThickness` | `float` / `int` | `0 – 99 mm` | Triceps skin fold thickness |
| `Insulin` | `float` / `int` | `0 – 846 mu U/ml` | 2-Hour serum insulin |
| `BMI` | `float` | `0 – 70.0 kg/m²` | Body Mass Index |
| `DiabetesPedigreeFunction` | `float` | `0.078 – 2.42` | Diabetes pedigree function |
| `Age` | `int` | `21 – 81 years` | Age in years |
| `Sex` | `int` / `str` | `0` (Female) / `1` (Male) | Biological sex demographic |
| `Outcome` | `int` | `0` (Non-Diabetic) / `1` (Diabetic) | Diagnostic target variable |

---

## How to Integrate

1. Download the verified dataset from the official DOI repository (`10.17632/nxnty5g7y6.2`).
2. Verify feature names match the schema above.
3. Save the file to `ml/datasets/external/mendeley_diabetes_real.csv`.
4. Re-run `python ml/training/train_external_validation.py` to calculate genuine, un-biased external validation metrics.
