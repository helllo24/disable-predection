import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "diabetes_prediction_100k.csv")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

PREPROCESSOR_SAVE_PATH = os.path.join(MODELS_DIR, "diabetes_100k_preprocessor.joblib")
CONFIG_SAVE_PATH = os.path.join(PROCESSED_DIR, "preprocessing_config.json")
SPLIT_METADATA_PATH = os.path.join(PROCESSED_DIR, "split_metadata.json")
REPORT_SAVE_PATH = os.path.join(PROCESSED_DIR, "PREPROCESSING_REPORT.md")

TRAIN_SAVE_PATH = os.path.join(PROCESSED_DIR, "train_100k.csv")
VAL_SAVE_PATH = os.path.join(PROCESSED_DIR, "val_100k.csv")
TEST_SAVE_PATH = os.path.join(PROCESSED_DIR, "test_100k.csv")

RANDOM_SEED = 42

def execute_70_15_15_split_pipeline():
    print("==================================================")
    print("EXECUTING RIGOROUS 70 / 15 / 15 DATASET SPLITTING PIPELINE")
    print("==================================================")

    # 1. Load raw data without modifying original file
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw dataset not found at {RAW_DATA_PATH}. Please run data/raw/generate_100k_raw.py first.")

    df_raw = pd.read_csv(RAW_DATA_PATH)
    n_rows_initial, n_cols_initial = df_raw.shape
    print(f"[Step 1] Loaded raw dataset ({n_rows_initial:,} rows, {n_cols_initial} columns)")

    # 2. Schema Validation
    expected_columns = ['gender', 'age', 'hypertension', 'heart_disease', 'smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level', 'diabetes']
    missing_columns = [col for col in expected_columns if col not in df_raw.columns]
    if missing_columns:
        raise ValueError(f"Schema Validation Failed! Missing columns: {missing_columns}")

    # 3. Duplicate Detection & Removal
    duplicates_count = int(df_raw.duplicated().sum())
    df_clean = df_raw.drop_duplicates().reset_index(drop=True)
    n_rows_deduped = len(df_clean)
    print(f"[Step 3] Deduplicated dataset: {n_rows_deduped:,} records ({duplicates_count:,} duplicates removed)")

    # 4. Implausible Value Audit & Cleaning (replace <= 0 with NaN for numerical features)
    impossible_cases = {
        "age_le_0": int((df_clean['age'] <= 0).sum()),
        "bmi_le_0": int((df_clean['bmi'] <= 0).sum()),
        "hba1c_le_0": int((df_clean['HbA1c_level'] <= 0).sum()),
        "glucose_le_0": int((df_clean['blood_glucose_level'] <= 0).sum())
    }
    df_clean.loc[df_clean['bmi'] <= 0, 'bmi'] = np.nan
    df_clean.loc[df_clean['HbA1c_level'] <= 0, 'HbA1c_level'] = np.nan
    df_clean.loc[df_clean['blood_glucose_level'] <= 0, 'blood_glucose_level'] = np.nan

    missing_report = df_clean.isnull().sum().to_dict()

    # 5. Target Leakage Audit
    df_corr = df_clean.copy()
    df_corr['gender_code'] = df_corr['gender'].astype('category').cat.codes
    df_corr['smoke_code'] = df_corr['smoking_history'].astype('category').cat.codes
    correlations = df_corr.corr(numeric_only=True)['diabetes'].drop('diabetes').to_dict()
    max_corr = max([abs(val) for val in correlations.values()])
    print(f"[Step 5] Target leakage audit: Max correlation = {max_corr:.4f}")

    # 6. Two-Stage Stratified Train / Validation / Test Splitting
    X = df_clean.drop(columns=['diabetes'])
    y = df_clean['diabetes']

    # Stage 1: Split 70% Train, 30% Temp (Val + Test)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=RANDOM_SEED, stratify=y
    )

    # Stage 2: Split 30% Temp into 15% Val and 15% Test (50/50 ratio of 30%)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=RANDOM_SEED, stratify=y_temp
    )

    print(f"[Step 6] 70 / 15 / 15 Stratified Split completed (Random Seed = {RANDOM_SEED}):")
    print(f"         - TRAIN:      {len(X_train):,} rows ({len(X_train)/n_rows_deduped*100:.1f}%)")
    print(f"         - VALIDATION: {len(X_val):,} rows ({len(X_val)/n_rows_deduped*100:.1f}%)")
    print(f"         - TEST:       {len(X_test):,} rows ({len(X_test)/n_rows_deduped*100:.1f}%) [UNTOUCHED]")

    # 7. Build Scikit-Learn ColumnTransformer
    num_cols = ['age', 'bmi', 'HbA1c_level', 'blood_glucose_level']
    categorical_cols = ['gender', 'smoking_history']
    binary_cols = ['hypertension', 'heart_disease']

    num_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    binary_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_pipeline, num_cols),
            ('cat', cat_pipeline, categorical_cols),
            ('bin', binary_pipeline, binary_cols)
        ],
        remainder='drop'
    )

    # 8. Fit Preprocessor STRICTLY ON TRAIN
    print("[Step 8] Fitting ColumnTransformer STRICTLY ON TRAIN (X_train)...")
    preprocessor.fit(X_train)

    X_train_trans = preprocessor.transform(X_train)
    X_val_trans = preprocessor.transform(X_val)
    X_test_trans = preprocessor.transform(X_test)

    cat_feature_names = preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out(categorical_cols).tolist()
    feature_names = num_cols + cat_feature_names + binary_cols

    # 9. Save Fitted Preprocessor Pipeline
    joblib.dump(preprocessor, PREPROCESSOR_SAVE_PATH)
    print(f"[Step 9] Saved fitted preprocessor to {PREPROCESSOR_SAVE_PATH}")

    # 10. Save Transformed Data CSVs
    df_train_proc = pd.DataFrame(X_train_trans, columns=feature_names)
    df_train_proc['diabetes'] = y_train.values

    df_val_proc = pd.DataFrame(X_val_trans, columns=feature_names)
    df_val_proc['diabetes'] = y_val.values

    df_test_proc = pd.DataFrame(X_test_trans, columns=feature_names)
    df_test_proc['diabetes'] = y_test.values

    df_train_proc.to_csv(TRAIN_SAVE_PATH, index=False)
    df_val_proc.to_csv(VAL_SAVE_PATH, index=False)
    df_test_proc.to_csv(TEST_SAVE_PATH, index=False)

    print(f"[Step 10] Saved preprocessed datasets:")
    print(f"          - Train: {TRAIN_SAVE_PATH}")
    print(f"          - Val:   {VAL_SAVE_PATH}")
    print(f"          - Test:  {TEST_SAVE_PATH}")

    # 11. Save Reproducibility Metadata
    train_dist = y_train.value_counts().to_dict()
    val_dist = y_val.value_counts().to_dict()
    test_dist = y_test.value_counts().to_dict()

    split_metadata = {
        "dataset_version": "1.0.0",
        "preprocessing_version": "1.0.0",
        "random_seed": RANDOM_SEED,
        "split_strategy": "Stratified 70/15/15 Split",
        "isolation_rule": "Final TEST set remains untouched until final model evaluation. Preprocessing fitted strictly on TRAIN.",
        "counts": {
            "train": {
                "rows": len(df_train_proc),
                "pct": 70.0,
                "negative_count": int(train_dist.get(0, 0)),
                "positive_count": int(train_dist.get(1, 0)),
                "positive_pct": round(float(train_dist.get(1, 0) / len(df_train_proc) * 100), 2)
            },
            "validation": {
                "rows": len(df_val_proc),
                "pct": 15.0,
                "negative_count": int(val_dist.get(0, 0)),
                "positive_count": int(val_dist.get(1, 0)),
                "positive_pct": round(float(val_dist.get(1, 0) / len(df_val_proc) * 100), 2)
            },
            "test": {
                "rows": len(df_test_proc),
                "pct": 15.0,
                "negative_count": int(test_dist.get(0, 0)),
                "positive_count": int(test_dist.get(1, 0)),
                "positive_pct": round(float(test_dist.get(1, 0) / len(df_test_proc) * 100), 2)
            }
        },
        "feature_list": feature_names,
        "benchmark_isolation": {
            "pima_dataset_path": "data/benchmark/pima_indians_diabetes.csv",
            "pima_isolation_note": "Pima Indians dataset (n=768) retained as a separate benchmark experiment. Zero mixing with 100K main dataset."
        }
    }

    with open(SPLIT_METADATA_PATH, "w") as f:
        json.dump(split_metadata, f, indent=2)

    with open(CONFIG_SAVE_PATH, "w") as f:
        json.dump(split_metadata, f, indent=2)

    # 12. Generate Preprocessing & Split Report Markdown
    markdown_report = f"""# REPRODUCIBLE DATASET SPLITTING & PREPROCESSING REPORT

**Dataset**: Healthcare EHR 100K Diabetes Prediction Dataset  
**Random Seed**: `{RANDOM_SEED}`  
**Fit Scope**: **Strictly Training Set (`TRAIN`) Only**  
**Test Set Policy**: **UNTOUCHED until final evaluation**  

---

## 1. Stratified Dataset Splitting Summary

| Split Name | Row Count ($N$) | Percentage (%) | Negative Count (0) | Positive Count (1) | Positive Ratio (%) | Isolation Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TRAIN** | **{len(df_train_proc):,}** | 70.0% | {train_dist.get(0, 0):,} | {train_dist.get(1, 0):,} | {train_dist.get(1, 0)/len(df_train_proc)*100:.2f}% | Model Training & Transformer Fitting |
| **VALIDATION** | **{len(df_val_proc):,}** | 15.0% | {val_dist.get(0, 0):,} | {val_dist.get(1, 0):,} | {val_dist.get(1, 0)/len(df_val_proc)*100:.2f}% | Hyperparameter Tuning & Selection |
| **TEST** | **{len(df_test_proc):,}** | 15.0% | {test_dist.get(0, 0):,} | {test_dist.get(1, 0):,} | {test_dist.get(1, 0)/len(df_test_proc)*100:.2f}% | **UNTOUCHED (Final Evaluation Only)** |

---

## 2. Reproducibility & Pipeline Configuration

- **Dataset Version**: `1.0.0`
- **Preprocessing Version**: `1.0.0`
- **Random Seed**: `{RANDOM_SEED}`
- **Fitted Pipeline Artifact**: `{PREPROCESSOR_SAVE_PATH}`
- **Feature Count**: `{len(feature_names)}` transformed features
- **Benchmark Experiment**: Pima Indians dataset ($N=768$) kept strictly separate in `data/benchmark/pima_indians_diabetes.csv`.

---

## 3. Transformed Features

```json
{json.dumps(feature_names, indent=2)}
```
"""

    with open(REPORT_SAVE_PATH, "w") as f:
        f.write(markdown_report)

    print("\n==================================================")
    print("DATASET SPLITTING & PREPROCESSING PIPELINE COMPLETED")
    print("==================================================")
    print(f"TRAIN rows:      {len(df_train_proc):,} | Neg: {train_dist.get(0, 0):,}, Pos: {train_dist.get(1, 0):,}")
    print(f"VALIDATION rows: {len(df_val_proc):,} | Neg: {val_dist.get(0, 0):,}, Pos: {val_dist.get(1, 0):,}")
    print(f"TEST rows:       {len(df_test_proc):,} | Neg: {test_dist.get(0, 0):,}, Pos: {test_dist.get(1, 0):,}")
    print("==================================================")

    return split_metadata

if __name__ == "__main__":
    execute_70_15_15_split_pipeline()
