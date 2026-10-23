import os
import numpy as np
import pandas as pd

RAW_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diabetes_prediction_100k.csv")

def generate_100k_raw_dataset_if_missing():
    if os.path.exists(RAW_PATH):
        print(f"[Dataset] Raw 100K dataset already exists at {RAW_PATH}")
        return

    print(f"[Dataset Generator] Generating 100,000-record dataset matching Healthcare EHR specifications at {RAW_PATH}...")
    np.random.seed(42)
    n = 100000

    # Target: 91.5% Negative (0), 8.5% Positive (1)
    y = np.random.choice([0, 1], size=n, p=[0.915, 0.085])
    n_neg = int(np.sum(y == 0))
    n_pos = int(np.sum(y == 1))

    # Demographics
    gender_choices = ['Female', 'Male', 'Other']
    gender_probs = [0.585, 0.414, 0.001]
    gender = np.random.choice(gender_choices, size=n, p=gender_probs)

    # Age (0.08 to 80.0)
    age_neg = np.clip(np.random.normal(40, 18, n_neg), 0.08, 80.0)
    age_pos = np.clip(np.random.normal(61, 12, n_pos), 18.0, 80.0)
    age = np.zeros(n)
    age[y == 0] = age_neg
    age[y == 1] = age_pos

    # Hypertension
    hyp_neg = np.random.choice([0, 1], size=n_neg, p=[0.94, 0.06])
    hyp_pos = np.random.choice([0, 1], size=n_pos, p=[0.75, 0.25])
    hypertension = np.zeros(n, dtype=int)
    hypertension[y == 0] = hyp_neg
    hypertension[y == 1] = hyp_pos

    # Heart Disease
    hd_neg = np.random.choice([0, 1], size=n_neg, p=[0.97, 0.03])
    hd_pos = np.random.choice([0, 1], size=n_pos, p=[0.85, 0.15])
    heart_disease = np.zeros(n, dtype=int)
    heart_disease[y == 0] = hd_neg
    heart_disease[y == 1] = hd_pos

    # Smoking History
    smoke_choices = ['never', 'No Info', 'former', 'current', 'not current', 'ever']
    smoke_probs = [0.35, 0.35, 0.09, 0.09, 0.06, 0.06]
    smoking_history = np.random.choice(smoke_choices, size=n, p=smoke_probs)

    # BMI
    bmi_neg = np.clip(np.random.normal(26.8, 5.8, n_neg), 10.01, 80.0)
    bmi_pos = np.clip(np.random.normal(36.0, 7.5, n_pos), 18.0, 95.69)
    bmi = np.zeros(n)
    bmi[y == 0] = bmi_neg
    bmi[y == 1] = bmi_pos

    # HbA1c Level
    hba1c_neg = np.clip(np.random.normal(5.4, 0.7, n_neg), 3.5, 6.6)
    hba1c_pos = np.clip(np.random.normal(6.9, 0.8, n_pos), 6.5, 9.0)
    hba1c = np.zeros(n)
    hba1c[y == 0] = hba1c_neg
    hba1c[y == 1] = hba1c_pos

    # Blood Glucose Level
    glu_neg = np.clip(np.random.normal(132, 28, n_neg), 80, 200)
    glu_pos = np.clip(np.random.normal(194, 38, n_pos), 126, 300)
    glu = np.zeros(n, dtype=int)
    glu[y == 0] = glu_neg.astype(int)
    glu[y == 1] = glu_pos.astype(int)

    # Inject 10 duplicate rows to test duplicate detection
    df = pd.DataFrame({
        'gender': gender,
        'age': np.round(age, 2),
        'hypertension': hypertension,
        'heart_disease': heart_disease,
        'smoking_history': smoking_history,
        'bmi': np.round(bmi, 2),
        'HbA1c_level': np.round(hba1c, 1),
        'blood_glucose_level': glu,
        'diabetes': y
    })

    # Duplicate first 15 rows to test duplicate detection
    duplicates = df.iloc[:15].copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    df.to_csv(RAW_PATH, index=False)
    print(f"[SUCCESS] Created 100,015 record raw dataset at {RAW_PATH}")

if __name__ == "__main__":
    generate_100k_raw_dataset_if_missing()
