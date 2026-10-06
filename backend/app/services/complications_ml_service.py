import os
import json
import joblib
import pandas as pd
from typing import Dict, Any

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models", "complications")

class ComplicationsMLService:
    _instance = None
    _models = {}
    _metadata = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ComplicationsMLService()
            cls._instance.load_all_models()
        return cls._instance

    def load_all_models(self):
        """Loads all 6 trained complication ML models into memory."""
        complications = ["heart", "kidney", "neuropathy", "retinopathy", "foot", "vascular"]

        for comp in complications:
            model_file = os.path.join(MODELS_DIR, f"{comp}_model.pkl")
            meta_file = os.path.join(MODELS_DIR, f"{comp}_metadata.json")

            if not os.path.exists(model_file) or not os.path.exists(meta_file):
                print(f"Complication ML files missing for {comp}. Running training script...")
                from ml.training.train_complications import train_all_complication_models
                train_all_complication_models()

            self._models[comp] = joblib.load(model_file)
            with open(meta_file, 'r') as f:
                self._metadata[comp] = json.load(f)

        print("Loaded all 6 Diabetes Complication ML Models successfully.")

    def predict_all_complications(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs predictions across all 6 complication risk categories."""
        if not self._models:
            self.load_all_models()

        # 1. Heart Model Inference
        df_heart = pd.DataFrame([{
            'age': float(input_data['age']),
            'gender': 1 if str(input_data.get('gender', '')).lower() == 'male' else 0,
            'bmi': float(input_data['bmi']),
            'systolic_bp': float(input_data['systolic_bp']),
            'diastolic_bp': float(input_data['diastolic_bp']),
            'cholesterol': 3 if float(input_data.get('hba1c', 7.0)) > 9.0 else 2 if float(input_data.get('hba1c', 7.0)) > 7.0 else 1,
            'glucose': 3 if float(input_data['fasting_glucose']) > 180 else 2 if float(input_data['fasting_glucose']) > 120 else 1,
            'smoking': 0, 'alcohol': 0, 'physical_activity': 1,
            'diabetes_duration_years': int(input_data['diabetes_duration_years'])
        }])[self._metadata['heart']['feature_columns']]

        pred_h = int(self._models['heart'].predict(df_heart)[0])
        prob_h = float(self._models['heart'].predict_proba(df_heart)[0][1]) if hasattr(self._models['heart'], 'predict_proba') else 0.5
        risk_h = "High Risk" if pred_h == 1 else "Low Risk"

        # 2. Kidney Model Inference
        df_kidney = pd.DataFrame([{
            'age': float(input_data['age']),
            'blood_pressure': float(input_data['diastolic_bp']),
            'specific_gravity': 1.015,
            'albumin': int(input_data['albumin_urine']),
            'sugar': 2 if float(input_data['fasting_glucose']) > 150 else 0,
            'serum_creatinine': float(input_data['serum_creatinine']),
            'sodium': 138, 'hemoglobin': 13.5,
            'hypertension': 1 if float(input_data['systolic_bp']) >= 140 else 0,
            'diabetes_mellitus': 1, 'pedal_edema': 1 if int(input_data['albumin_urine']) >= 2 else 0,
            'anemia': 0
        }])[self._metadata['kidney']['feature_columns']]

        pred_k = int(self._models['kidney'].predict(df_kidney)[0])
        prob_k = float(self._models['kidney'].predict_proba(df_kidney)[0][1]) if hasattr(self._models['kidney'], 'predict_proba') else 0.5
        risk_k = "Elevated Risk (Nephropathy)" if pred_k == 1 else "Low Risk"

        # 3. Neuropathy Model Inference
        df_neuro = pd.DataFrame([{
            'age': float(input_data['age']),
            'diabetes_duration_years': int(input_data['diabetes_duration_years']),
            'hba1c': float(input_data['hba1c']),
            'fasting_glucose': float(input_data['fasting_glucose']),
            'systolic_bp': float(input_data['systolic_bp']),
            'bmi': float(input_data['bmi']),
            'tingling_feet': int(input_data['tingling_feet']),
            'burning_pain': 1 if int(input_data['tingling_feet']) == 1 else 0,
            'vibration_loss': int(input_data['vibration_loss']),
            'ankle_reflex': int(input_data['ankle_reflex'])
        }])[self._metadata['neuropathy']['feature_columns']]

        pred_n = int(self._models['neuropathy'].predict(df_neuro)[0])
        probas_n = self._models['neuropathy'].predict_proba(df_neuro)[0] if hasattr(self._models['neuropathy'], 'predict_proba') else [0.3, 0.4, 0.3]
        prob_n = float(probas_n[pred_n])
        risk_n = "High Risk (Severe Neuropathy)" if pred_n == 2 else "Moderate Risk" if pred_n == 1 else "Low Risk"

        # 4. Retinopathy Model Inference
        df_retino = pd.DataFrame([{
            'quality_assessment': 1, 'prescreen_result': 1,
            'microaneurysm_count_lvl1': int(input_data['diabetes_duration_years']) * 3,
            'microaneurysm_count_lvl2': int(input_data['diabetes_duration_years']) * 2,
            'microaneurysm_count_lvl3': int(input_data['diabetes_duration_years']),
            'exudate_count_lvl1': float(input_data['hba1c']) * 0.5,
            'exudate_count_lvl2': float(input_data['hba1c']) * 0.8,
            'macula_center_distance': 0.35, 'optic_disc_diameter': 0.15
        }])[self._metadata['retinopathy']['feature_columns']]

        pred_r = int(self._models['retinopathy'].predict(df_retino)[0])
        prob_r = float(self._models['retinopathy'].predict_proba(df_retino)[0][1]) if hasattr(self._models['retinopathy'], 'predict_proba') else 0.5
        risk_r = "Signs of Retinopathy Detected" if pred_r == 1 else "Low Risk"

        # 5. Foot Ulcer Model Inference
        df_foot = pd.DataFrame([{
            'age': float(input_data['age']),
            'diabetes_duration_years': int(input_data['diabetes_duration_years']),
            'hba1c': float(input_data['hba1c']),
            'loss_of_sensory_perception': int(input_data['loss_of_sensory_perception']),
            'peripheral_arterial_disease': 1 if float(input_data['ankle_brachial_index']) < 0.9 else 0,
            'foot_deformity': 0,
            'history_of_ulcer': int(input_data['history_of_ulcer']),
            'callus_present': 1 if int(input_data['loss_of_sensory_perception']) == 1 else 0,
            'dry_cracked_skin': 1 if int(input_data['history_of_ulcer']) == 1 else 0
        }])[self._metadata['foot']['feature_columns']]

        pred_f = int(self._models['foot'].predict(df_foot)[0])
        probas_f = self._models['foot'].predict_proba(df_foot)[0] if hasattr(self._models['foot'], 'predict_proba') else [0.3, 0.4, 0.3]
        prob_f = float(probas_f[pred_f])
        risk_f = "High Risk (Ulcer/Amputation)" if pred_f == 2 else "Moderate Risk (Category 1)" if pred_f == 1 else "Low Risk"

        # 6. Vascular Disease Model Inference
        df_vasc = pd.DataFrame([{
            'age': float(input_data['age']),
            'ankle_brachial_index': float(input_data['ankle_brachial_index']),
            'systolic_bp': float(input_data['systolic_bp']),
            'diastolic_bp': float(input_data['diastolic_bp']),
            'fasting_glucose': float(input_data['fasting_glucose']),
            'total_cholesterol': 210.0, 'triglycerides': 180.0,
            'smoking_pack_years': 0,
            'intermittent_claudication': int(input_data['intermittent_claudication'])
        }])[self._metadata['vascular']['feature_columns']]

        pred_v = int(self._models['vascular'].predict(df_vasc)[0])
        probas_v = self._models['vascular'].predict_proba(df_vasc)[0] if hasattr(self._models['vascular'], 'predict_proba') else [0.3, 0.4, 0.3]
        prob_v = float(probas_v[pred_v])
        risk_v = "Severe Peripheral Vascular Disease" if pred_v == 2 else "Moderate Risk" if pred_v == 1 else "Low Risk"

        # Overall Complication Risk Assessment Summary
        high_count = sum(1 for r in [risk_h, risk_k, risk_n, risk_r, risk_f, risk_v] if "High" in r or "Elevated" in r or "Severe" in r or "Signs" in r)
        if high_count >= 3:
            overall_summary = "High Overall Complication Risk"
        elif high_count >= 1:
            overall_summary = "Moderate Overall Complication Risk"
        else:
            overall_summary = "Low Overall Complication Risk"

        return {
            "heart_risk": risk_h, "heart_probability": round(prob_h, 4),
            "kidney_risk": risk_k, "kidney_probability": round(prob_k, 4),
            "neuropathy_risk": risk_n, "neuropathy_probability": round(prob_n, 4),
            "retinopathy_risk": risk_r, "retinopathy_probability": round(prob_r, 4),
            "foot_risk": risk_f, "foot_probability": round(prob_f, 4),
            "vascular_risk": risk_v, "vascular_probability": round(prob_v, 4),
            "overall_risk_summary": overall_summary
        }

complications_ml_service = ComplicationsMLService.get_instance()
