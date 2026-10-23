# 100K EHR Diabetes Prediction Dataset Ingestion Guide

## Overview
This document describes how to ingest, validate, and preprocess the **Healthcare EHR 100,000 Diabetes Prediction Dataset** (`data/raw/diabetes_prediction_100k.csv`).

---

## Dataset Acquisition

1. Download `diabetes_prediction_dataset.csv` from the official Kaggle repository:
   `https://www.kaggle.com/datasets/iammustafatz/diabetes-prediction-dataset`
2. Save the CSV file to `data/raw/diabetes_prediction_100k.csv`.

---

## Verification & Ingestion

Run the ingestion script to validate the dataset schema, confirm the 100,000 record count, audit class distribution ($8.5\%$ diabetic prevalence), check missing values, and export the processed dataset:

```powershell
backend\.venv\Scripts\python.exe data/raw/ingest_100k_dataset.py
```

---

## Data Quality & Leakage Audit Summary

- **Records**: Exactly 100,000 rows. Zero rows generated or synthetic.
- **Gender Balance**: 58,552 Female ($58.55\%$), 41,430 Male ($41.43\%$), 18 Other ($0.02\%$). Dual-gender representation.
- **Age Range**: Continuous span from pediatric ($0.08$ yrs) to older adults ($80.0$ yrs).
- **No Target Leakage**: `HbA1c_level` and `blood_glucose_level` are standard clinical screening biomarkers measured prior to diagnostic categorization.
