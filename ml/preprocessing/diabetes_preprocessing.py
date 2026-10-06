import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    'Pregnancies',
    'Glucose',
    'BloodPressure',
    'SkinThickness',
    'Insulin',
    'BMI',
    'DiabetesPedigreeFunction',
    'Age'
]

ZERO_IMPLAUSIBLE_COLS = [
    'Glucose',
    'BloodPressure',
    'SkinThickness',
    'Insulin',
    'BMI'
]

def load_and_preprocess_dataset(dataset_path: str = 'ml/datasets/diabetes.csv'):
    """
    Loads Pima Indians Diabetes dataset, inspects features/classes, handles medically
    implausible zero values, and performs a reproducible stratified train/test split.
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found at {dataset_path}")

    df = pd.read_csv(dataset_path)
    print("=" * 60)
    print("DIABETES DATASET INSPECTION")
    print("=" * 60)
    print(f"Dataset Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Missing Values (Explicit NaNs):\n{df.isnull().sum()}")
    print(f"Duplicate Rows: {df.duplicated().sum()}")
    print(f"Data Types:\n{df.dtypes}")
    print(f"Class Distribution (Outcome):\n{df['Outcome'].value_counts(normalize=True)}")

    # Replace medically implausible 0 values with NaN for imputation
    df_clean = df.copy()
    for col in ZERO_IMPLAUSIBLE_COLS:
        zero_count = (df_clean[col] == 0).sum()
        print(f"Feature '{col}' has {zero_count} zero values (replaced with NaN for median imputation)")
        df_clean[col] = df_clean[col].replace(0, np.nan)

    X = df_clean[FEATURE_COLUMNS]
    y = df_clean['Outcome']

    # Stratified Train/Test Split (80% Train, 20% Test, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print("\nTrain/Test Split Completed:")
    print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
    print(f"X_test shape:  {X_test.shape}, y_test shape:  {y_test.shape}")

    # Build preprocessing pipeline (Imputer + Scaler) fitted ONLY on X_train to prevent data leakage
    preprocessor = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    return X_train, X_test, y_train, y_test, preprocessor, df

if __name__ == "__main__":
    load_and_preprocess_dataset()
