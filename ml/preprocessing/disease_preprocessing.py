import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

def load_and_preprocess_disease_dataset(dataset_path: str = 'ml/datasets/disease.csv'):
    """
    Loads Disease Symptom Dataset, cleans feature column names, encodes target prognosis labels,
    and performs a stratified train/test split.
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found at {dataset_path}")

    df = pd.read_csv(dataset_path)

    # Clean any trailing spaces in column names
    df.columns = [col.strip() for col in df.columns]

    # Clean target column if needed
    if 'Unnamed: 133' in df.columns:
        df = df.drop(columns=['Unnamed: 133'])

    feature_cols = [c for c in df.columns if c != 'prognosis']
    target_col = 'prognosis'

    print("=" * 60)
    print("DISEASE PREDICTION DATASET INSPECTION")
    print("=" * 60)
    print(f"Dataset Shape: {df.shape}")
    print(f"Symptom Feature Count: {len(feature_cols)}")
    print(f"Unique Diseases (Target Classes): {df[target_col].nunique()}")
    print(f"Missing Values (NaNs): {df.isnull().sum().sum()}")
    print(f"Duplicate Rows: {df.duplicated().sum()}")

    X = df[feature_cols]
    y_raw = df[target_col]

    # Encode disease string names to integer IDs
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)
    class_names = list(label_encoder.classes_)

    # Stratified Train/Test Split (80% Train, 20% Test, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print("\nTrain/Test Split Completed:")
    print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
    print(f"X_test shape:  {X_test.shape}, y_test shape:  {y_test.shape}")

    return X_train, X_test, y_train, y_test, feature_cols, class_names, label_encoder, df

if __name__ == "__main__":
    load_and_preprocess_disease_dataset()
