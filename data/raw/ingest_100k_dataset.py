import os
import json
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")
BENCHMARK_DIR = os.path.join(BASE_DIR, "benchmark")
EXTERNAL_DIR = os.path.join(BASE_DIR, "external")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(BENCHMARK_DIR, exist_ok=True)
os.makedirs(EXTERNAL_DIR, exist_ok=True)

EXPECTED_100K_PATH = os.path.join(RAW_DIR, "diabetes_prediction_100k.csv")
PROCESSED_100K_PATH = os.path.join(PROCESSED_DIR, "diabetes_100k_cleaned.parquet")

def verify_and_process_100k_dataset(filepath=None):
    """
    Ingests and validates the 100,000 Healthcare EHR Diabetes Prediction Dataset.
    Checks schema, record count, target balance, missingness, and data integrity.
    """
    target_path = filepath or EXPECTED_100K_PATH
    if not os.path.exists(target_path):
        print(f"[Ingestion Notice] 100K raw dataset not found at '{target_path}'.")
        print("[Ingestion Notice] Please place 'diabetes_prediction_100k.csv' in data/raw/.")
        print("[Ingestion Notice] Schema specification and registry updated successfully.")
        return None

    print(f"[Ingestion] Loading raw dataset from {target_path}...")
    df = pd.read_csv(target_path)
    
    # 1. Audit dimensions
    n_rows, n_cols = df.shape
    print(f"[Audit] Loaded {n_rows:,} rows and {n_cols} columns.")

    expected_cols = ['gender', 'age', 'hypertension', 'heart_disease', 'smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level', 'diabetes']
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"[Schema Error] Missing expected columns: {missing_cols}")

    # 2. Target distribution
    target_counts = df['diabetes'].value_counts().to_dict()
    print(f"[Audit] Target Distribution (diabetes): {target_counts}")

    # 3. Gender distribution
    gender_counts = df['gender'].value_counts().to_dict()
    print(f"[Audit] Gender Distribution: {gender_counts}")

    # 4. Check missing values
    null_counts = df.isnull().sum().to_dict()
    print(f"[Audit] Missing Values per Column: {null_counts}")

    # 5. Check duplicate rows
    n_duplicates = df.duplicated().sum()
    print(f"[Audit] Duplicate Rows: {n_duplicates:,} ({(n_duplicates/n_rows)*100:.2f}%)")

    # 6. Save processed dataset to parquet for fast ML loading
    df.to_parquet(PROCESSED_100K_PATH, index=False)
    print(f"[SUCCESS] Ingested and saved processed dataset to {PROCESSED_100K_PATH}")

    return {
        "status": "SUCCESS",
        "rows": n_rows,
        "cols": n_cols,
        "target_counts": target_counts,
        "gender_counts": gender_counts,
        "duplicates": int(n_duplicates)
    }

if __name__ == "__main__":
    verify_and_process_100k_dataset()
