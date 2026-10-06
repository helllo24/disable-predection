import os
import pandas as pd
import numpy as np

COMP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "datasets", "complications"))

dataset_files = {
    "Cardiovascular / Heart": "heart_disease.csv",
    "Kidney / Nephropathy": "kidney_disease.csv",
    "Nerve / Neuropathy": "neuropathy.csv",
    "Eye / Retinopathy": "retinopathy.csv",
    "Diabetic Foot Ulcer": "diabetic_foot.csv",
    "Peripheral Vascular": "vascular_disease.csv"
}

def analyze_all():
    print("==================================================================")
    print("PART 14.2 - DIABETES COMPLICATION DATASETS DETAILED ANALYSIS")
    print("==================================================================")

    for category, filename in dataset_files.items():
        filepath = os.path.join(COMP_DIR, filename)
        if not os.path.exists(filepath):
            print(f"\n[ERROR] File missing: {filepath}")
            continue

        df = pd.read_csv(filepath)
        target_col = df.columns[-1]
        feature_cols = list(df.columns[:-1])

        print(f"\n------------------------------------------------------------------")
        print(f"Dataset Category: {category} ({filename})")
        print(f"------------------------------------------------------------------")
        print(f" File Path: {filepath}")
        print(f" Shape: {df.shape[0]} Rows x {df.shape[1]} Columns ({len(feature_cols)} Features, 1 Target)")
        print(f" Target Column: '{target_col}'")
        
        # Missing values
        missing_total = df.isnull().sum().sum()
        missing_pct = (missing_total / (df.shape[0] * df.shape[1])) * 100
        print(f" Missing Values: {missing_total} ({missing_pct:.2f}%)")

        # Duplicate rows
        duplicates = df.duplicated().sum()
        print(f" Exact Duplicate Rows: {duplicates}")

        # Feature types
        num_cols = df[feature_cols].select_dtypes(include=[np.number]).columns.tolist()
        print(f" Feature Types: {len(num_cols)} Numeric/Categorical Clinical Features")

        # Target distribution
        target_counts = df[target_col].value_counts().sort_index()
        target_pcts = (df[target_col].value_counts(normalize=True).sort_index() * 100).round(2)
        dist_str = ", ".join([f"Class {cls}: {count} ({pct}%)" for cls, count, pct in zip(target_counts.index, target_counts.values, target_pcts.values)])
        print(f" Target Class Distribution: {dist_str}")

        # Basic Stats Summary
        stats = df[feature_cols].agg(['min', 'max', 'mean', 'std']).T
        print(f" Sample Feature Ranges:")
        for col in feature_cols[:4]:
            print(f"   - {col}: min={stats.loc[col, 'min']:.1f}, max={stats.loc[col, 'max']:.1f}, mean={stats.loc[col, 'mean']:.1f}, std={stats.loc[col, 'std']:.1f}")

if __name__ == "__main__":
    analyze_all()
