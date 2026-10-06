import os
import numpy as np
import pandas as pd

np.random.seed(42)

COMP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "complications"))
os.makedirs(COMP_DIR, exist_ok=True)

print(f"Generating clinical benchmark datasets in: {COMP_DIR}")

# -------------------------------------------------------------
# 1. ❤️ Heart / Cardiovascular Complication Dataset (heart_disease.csv)
# -------------------------------------------------------------
n_heart = 2000
age_h = np.random.randint(40, 80, n_heart)
gender_h = np.random.choice([0, 1], n_heart)  # 0: Female, 1: Male
bmi_h = np.round(np.random.uniform(18.5, 42.0, n_heart), 1)
sys_bp = np.random.randint(100, 185, n_heart)
dia_bp = np.random.randint(60, 115, n_heart)
chol_h = np.random.choice([1, 2, 3], n_heart, p=[0.5, 0.3, 0.2])  # 1: Normal, 2: Above Normal, 3: High
gluc_h = np.random.choice([1, 2, 3], n_heart, p=[0.4, 0.35, 0.25])
smoke_h = np.random.choice([0, 1], n_heart, p=[0.75, 0.25])
alco_h = np.random.choice([0, 1], n_heart, p=[0.85, 0.15])
active_h = np.random.choice([0, 1], n_heart, p=[0.3, 0.7])
diab_duration_h = np.random.randint(1, 30, n_heart)

# Risk score calculation for realistic target distribution
score_h = (sys_bp > 140)*2.0 + (dia_bp > 90)*1.5 + (chol_h == 3)*2.0 + (gluc_h == 3)*1.8 + (smoke_h == 1)*1.5 + (diab_duration_h > 10)*1.5 + (bmi_h > 30)*1.2 + np.random.normal(0, 1.2, n_heart)
target_h = (score_h > 4.5).astype(int)

df_heart = pd.DataFrame({
    'age': age_h, 'gender': gender_h, 'bmi': bmi_h,
    'systolic_bp': sys_bp, 'diastolic_bp': dia_bp,
    'cholesterol': chol_h, 'glucose': gluc_h,
    'smoking': smoke_h, 'alcohol': alco_h, 'physical_activity': active_h,
    'diabetes_duration_years': diab_duration_h,
    'cardio_risk': target_h
})
df_heart.to_csv(os.path.join(COMP_DIR, "heart_disease.csv"), index=False)
print("Created heart_disease.csv (2000 rows x 12 cols)")

# -------------------------------------------------------------
# 2. 🫘 Kidney / Diabetic Nephropathy Dataset (kidney_disease.csv)
# -------------------------------------------------------------
n_kidney = 1200
age_k = np.random.randint(35, 78, n_kidney)
bp_k = np.random.randint(70, 120, n_kidney)
sg_k = np.random.choice([1.005, 1.010, 1.015, 1.020, 1.025], n_kidney)
al_k = np.random.choice([0, 1, 2, 3, 4], n_kidney, p=[0.4, 0.25, 0.15, 0.1, 0.1]) # Albumin in urine
su_k = np.random.choice([0, 1, 2, 3, 4], n_kidney, p=[0.35, 0.3, 0.15, 0.12, 0.08]) # Sugar in urine
sc_k = np.round(np.random.uniform(0.5, 10.0, n_kidney), 2) # Serum Creatinine
sod_k = np.random.randint(120, 150, n_kidney)
hemo_k = np.round(np.random.uniform(8.0, 17.5, n_kidney), 1)
htn_k = np.random.choice([0, 1], n_kidney, p=[0.4, 0.6])
dm_k = np.random.choice([0, 1], n_kidney, p=[0.1, 0.9])
pe_k = np.random.choice([0, 1], n_kidney, p=[0.7, 0.3]) # Pedal edema
ane_k = np.random.choice([0, 1], n_kidney, p=[0.75, 0.25]) # Anemia

score_k = (al_k >= 2)*3.0 + (sc_k > 1.4)*3.5 + (hemo_k < 11)*2.0 + (htn_k == 1)*1.5 + (pe_k == 1)*1.5 + np.random.normal(0, 1.0, n_kidney)
target_k = (score_k > 4.0).astype(int)

df_kidney = pd.DataFrame({
    'age': age_k, 'blood_pressure': bp_k, 'specific_gravity': sg_k,
    'albumin': al_k, 'sugar': su_k, 'serum_creatinine': sc_k,
    'sodium': sod_k, 'hemoglobin': hemo_k, 'hypertension': htn_k,
    'diabetes_mellitus': dm_k, 'pedal_edema': pe_k, 'anemia': ane_k,
    'kidney_disease_risk': target_k
})
df_kidney.to_csv(os.path.join(COMP_DIR, "kidney_disease.csv"), index=False)
print("Created kidney_disease.csv (1200 rows x 13 cols)")

# -------------------------------------------------------------
# 3. 🧠 Nerve / Diabetic Neuropathy Dataset (neuropathy.csv)
# -------------------------------------------------------------
n_nerve = 1500
age_n = np.random.randint(30, 80, n_nerve)
diab_dur_n = np.random.randint(1, 35, n_nerve)
hba1c_n = np.round(np.random.uniform(5.5, 14.0, n_nerve), 1)
fbg_n = np.random.randint(90, 300, n_nerve) # Fasting blood glucose
sys_n = np.random.randint(110, 180, n_nerve)
bmi_n = np.round(np.random.uniform(19.0, 45.0, n_nerve), 1)
tingling_n = np.random.choice([0, 1], n_nerve, p=[0.55, 0.45]) # Numbness/Tingling in feet
burning_n = np.random.choice([0, 1], n_nerve, p=[0.65, 0.35])  # Burning sensation
vibration_loss_n = np.random.choice([0, 1], n_nerve, p=[0.7, 0.3]) # Reduced vibration perception
reflex_n = np.random.choice([0, 1, 2], n_nerve, p=[0.5, 0.35, 0.15]) # 0: Normal, 1: Reduced, 2: Absent

score_n = (diab_dur_n > 8)*2.0 + (hba1c_n > 8.0)*2.5 + (tingling_n == 1)*2.0 + (vibration_loss_n == 1)*3.0 + (reflex_n == 2)*3.0 + np.random.normal(0, 1.2, n_nerve)
target_n = np.zeros(n_nerve, dtype=int)
target_n[score_n >= 4.0] = 1 # Moderate Risk
target_n[score_n >= 7.5] = 2 # High Risk

df_nerve = pd.DataFrame({
    'age': age_n, 'diabetes_duration_years': diab_dur_n,
    'hba1c': hba1c_n, 'fasting_glucose': fbg_n,
    'systolic_bp': sys_n, 'bmi': bmi_n,
    'tingling_feet': tingling_n, 'burning_pain': burning_n,
    'vibration_loss': vibration_loss_n, 'ankle_reflex': reflex_n,
    'neuropathy_risk': target_n
})
df_nerve.to_csv(os.path.join(COMP_DIR, "neuropathy.csv"), index=False)
print("Created neuropathy.csv (1500 rows x 11 cols)")

# -------------------------------------------------------------
# 4. 👁️ Eye / Diabetic Retinopathy Dataset (retinopathy.csv)
# -------------------------------------------------------------
n_eye = 1151
quality_e = np.random.choice([0, 1], n_eye, p=[0.05, 0.95])
prescreen_e = np.random.choice([0, 1], n_eye, p=[0.1, 0.9])
ma_count1 = np.random.randint(0, 100, n_eye)
ma_count2 = np.random.randint(0, 80, n_eye)
ma_count3 = np.random.randint(0, 60, n_eye)
exudate1 = np.round(np.random.exponential(5.0, n_eye), 2)
exudate2 = np.round(np.random.exponential(10.0, n_eye), 2)
macula_dist = np.round(np.random.uniform(0.2, 0.6, n_eye), 3)
disc_diam = np.round(np.random.uniform(0.1, 0.25, n_eye), 3)

score_e = (ma_count1 > 30)*2.0 + (exudate2 > 8.0)*2.5 + (macula_dist < 0.35)*2.0 + np.random.normal(0, 1.0, n_eye)
target_e = (score_e > 2.5).astype(int)

df_eye = pd.DataFrame({
    'quality_assessment': quality_e, 'prescreen_result': prescreen_e,
    'microaneurysm_count_lvl1': ma_count1, 'microaneurysm_count_lvl2': ma_count2,
    'microaneurysm_count_lvl3': ma_count3, 'exudate_count_lvl1': exudate1,
    'exudate_count_lvl2': exudate2, 'macula_center_distance': macula_dist,
    'optic_disc_diameter': disc_diam, 'retinopathy_risk': target_e
})
df_eye.to_csv(os.path.join(COMP_DIR, "retinopathy.csv"), index=False)
print("Created retinopathy.csv (1151 rows x 10 cols)")

# -------------------------------------------------------------
# 5. 🦶 Diabetic Foot Ulcer Dataset (diabetic_foot.csv)
# -------------------------------------------------------------
n_foot = 1500
age_f = np.random.randint(35, 82, n_foot)
dur_f = np.random.randint(1, 40, n_foot)
hba1c_f = np.round(np.random.uniform(5.5, 14.5, n_foot), 1)
lops_f = np.random.choice([0, 1], n_foot, p=[0.6, 0.4]) # Loss of Protective Sensation
pad_f = np.random.choice([0, 1], n_foot, p=[0.75, 0.25]) # Peripheral Arterial Disease
deformity_f = np.random.choice([0, 1], n_foot, p=[0.7, 0.3]) # Foot Deformity
ulcer_hist_f = np.random.choice([0, 1], n_foot, p=[0.85, 0.15]) # History of Ulcer
callus_f = np.random.choice([0, 1], n_foot, p=[0.55, 0.45]) # Callus present
dry_skin_f = np.random.choice([0, 1], n_foot, p=[0.4, 0.6])

score_f = (lops_f == 1)*2.5 + (pad_f == 1)*2.5 + (deformity_f == 1)*1.5 + (ulcer_hist_f == 1)*3.5 + np.random.normal(0, 1.0, n_foot)
target_f = np.zeros(n_foot, dtype=int)
target_f[score_f >= 3.0] = 1 # Moderate Risk (Category 1)
target_f[score_f >= 6.0] = 2 # High Risk (Category 2/3)

df_foot = pd.DataFrame({
    'age': age_f, 'diabetes_duration_years': dur_f, 'hba1c': hba1c_f,
    'loss_of_sensory_perception': lops_f, 'peripheral_arterial_disease': pad_f,
    'foot_deformity': deformity_f, 'history_of_ulcer': ulcer_hist_f,
    'callus_present': callus_f, 'dry_cracked_skin': dry_skin_f,
    'foot_ulcer_risk_category': target_f
})
df_foot.to_csv(os.path.join(COMP_DIR, "diabetic_foot.csv"), index=False)
print("Created diabetic_foot.csv (1500 rows x 10 cols)")

# -------------------------------------------------------------
# 6. 🩸 Peripheral Vascular Disease Dataset (vascular_disease.csv)
# -------------------------------------------------------------
n_vasc = 1800
age_v = np.random.randint(40, 85, n_vasc)
abi_v = np.round(np.random.uniform(0.4, 1.3, n_vasc), 2) # Ankle-Brachial Index (<0.9 indicates PAD)
sys_v = np.random.randint(105, 190, n_vasc)
dia_v = np.random.randint(65, 115, n_vasc)
glucose_v = np.random.randint(90, 290, n_vasc)
chol_v = np.random.randint(130, 320, n_vasc)
trig_v = np.random.randint(80, 400, n_vasc)
smoke_pk = np.random.randint(0, 45, n_vasc)
claudication_v = np.random.choice([0, 1], n_vasc, p=[0.7, 0.3]) # Leg pain while walking

score_v = (abi_v < 0.9)*3.5 + (abi_v < 0.7)*2.5 + (claudication_v == 1)*3.0 + (sys_v > 140)*1.5 + (smoke_pk > 15)*1.5 + np.random.normal(0, 1.0, n_vasc)
target_v = np.zeros(n_vasc, dtype=int)
target_v[score_v >= 3.5] = 1 # Moderate Risk
target_v[score_v >= 7.0] = 2 # Severe Vascular Risk

df_vasc = pd.DataFrame({
    'age': age_v, 'ankle_brachial_index': abi_v,
    'systolic_bp': sys_v, 'diastolic_bp': dia_v,
    'fasting_glucose': glucose_v, 'total_cholesterol': chol_v,
    'triglycerides': trig_v, 'smoking_pack_years': smoke_pk,
    'intermittent_claudication': claudication_v,
    'vascular_disease_risk': target_v
})
df_vasc.to_csv(os.path.join(COMP_DIR, "vascular_disease.csv"), index=False)
print("Created vascular_disease.csv (1800 rows x 10 cols)")

print("[SUCCESS] All 6 Diabetes Complication Datasets generated successfully!")
