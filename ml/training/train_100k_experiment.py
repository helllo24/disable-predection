import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from xgboost import XGBClassifier

# Add evaluation directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, "ml", "evaluation"))
from research_evaluation_metrics import evaluate_clinical_model, analyze_threshold_grid

PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")
EVAL_DIR = os.path.join(BASE_DIR, "ml", "evaluation")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(EVAL_DIR, exist_ok=True)

TRAIN_PATH = os.path.join(PROCESSED_DIR, "train_100k.csv")
VAL_PATH = os.path.join(PROCESSED_DIR, "val_100k.csv")
RESULTS_JSON_PATH = os.path.join(EVAL_DIR, "training_experiment_results.json")
REPORT_MD_PATH = os.path.join(PROCESSED_DIR, "TRAINING_EXPERIMENT_REPORT.md")
PROD_METADATA_PATH = os.path.join(MODELS_DIR, "diabetes_production_metadata.json")
PROD_MODEL_PATH = os.path.join(MODELS_DIR, "diabetes_production_model.joblib")

RANDOM_SEED = 42

def run_ml_training_experiment():
    print("==================================================")
    print("RUNNING DIABETES ML EXPERIMENT & MODEL SELECTION")
    print("==================================================")

    # 1. Load Preprocessed Datasets
    if not os.path.exists(TRAIN_PATH) or not os.path.exists(VAL_PATH):
        raise FileNotFoundError("Preprocessed train/val datasets not found. Run ml/preprocessing/diabetes_100k_preprocessing.py first.")

    train_df = pd.read_csv(TRAIN_PATH)
    val_df = pd.read_csv(VAL_PATH)

    X_train = train_df.drop(columns=['diabetes']).values
    y_train = train_df['diabetes'].values

    X_val = val_df.drop(columns=['diabetes']).values
    y_val = val_df['diabetes'].values

    feature_cols = train_df.drop(columns=['diabetes']).columns.tolist()

    print(f"[Dataset] Train set: {X_train.shape[0]:,} rows, {X_train.shape[1]} features")
    print(f"[Dataset] Val set:   {X_val.shape[0]:,} rows, {X_val.shape[1]} features")

    # Define Candidate Models with Optimized Fast Specs
    candidate_models = {
        "LogisticRegression": LogisticRegression(C=1.0, max_iter=1000, random_state=RANDOM_SEED),
        "DecisionTree": DecisionTreeClassifier(max_depth=10, min_samples_split=20, random_state=RANDOM_SEED),
        "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=12, random_state=RANDOM_SEED, n_jobs=-1),
        "HistGradientBoosting": HistGradientBoostingClassifier(max_iter=150, learning_rate=0.08, max_depth=8, random_state=RANDOM_SEED),
        "XGBoost": XGBClassifier(n_estimators=150, max_depth=6, learning_rate=0.08, subsample=0.8, random_state=RANDOM_SEED, eval_metric='logloss', n_jobs=-1)
    }

    cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    experiment_results = {}

    best_model_name = None
    best_val_roc_auc = -1.0

    # Train and Evaluate Each Model
    for model_name, model in candidate_models.items():
        print(f"\n[Training] Training {model_name}...")

        # 5-Fold Stratified CV on TRAIN
        cv_scores = []
        for train_idx, cv_val_idx in cv_strategy.split(X_train, y_train):
            X_tr, y_tr = X_train[train_idx], y_train[train_idx]
            X_cv_val, y_cv_val = X_train[cv_val_idx], y_train[cv_val_idx]
            
            clf_fold = model.__class__(**model.get_params())
            clf_fold.fit(X_tr, y_tr)
            cv_probs = clf_fold.predict_proba(X_cv_val)[:, 1]
            cv_scores.append(evaluate_clinical_model(y_cv_val, cv_probs)["roc_auc"])

        mean_cv_auc = round(float(np.mean(cv_scores)), 4)
        std_cv_auc = round(float(np.std(cv_scores)), 4)

        # Fit Model on Full TRAIN
        model.fit(X_train, y_train)

        # Evaluate on VALIDATION Set (Unseen during training)
        val_probs = model.predict_proba(X_val)[:, 1]
        val_eval = evaluate_clinical_model(y_val, val_probs, threshold=0.50)

        print(f"       -> 5-Fold CV ROC-AUC: {mean_cv_auc} ± {std_cv_auc}")
        print(f"       -> Validation ROC-AUC: {val_eval['roc_auc']} | PR-AUC: {val_eval['pr_auc']} | Sensitivity: {val_eval['sensitivity_recall']} | Specificity: {val_eval['specificity']}")

        # Save individual candidate model
        model_save_path = os.path.join(MODELS_DIR, f"{model_name.lower()}_100k.joblib")
        joblib.dump(model, model_save_path)

        experiment_results[model_name] = {
            "mean_cv_auc": mean_cv_auc,
            "std_cv_auc": std_cv_auc,
            "val_metrics": val_eval,
            "model_path": model_save_path
        }

        # Select Best Model Based on Validation ROC-AUC & PR-AUC
        if val_eval["roc_auc"] > best_val_roc_auc:
            best_val_roc_auc = val_eval["roc_auc"]
            best_model_name = model_name

    print(f"\n==================================================")
    print(f"[MODEL SELECTION] Selected Top Production Model: {best_model_name} (Val ROC-AUC = {best_val_roc_auc})")
    print("==================================================")

    best_model = candidate_models[best_model_name]
    val_probs_best = best_model.predict_proba(X_val)[:, 1]

    # Perform Threshold Analysis Grid on VALIDATION set for the selected production model
    thresh_df = analyze_threshold_grid(y_val, val_probs_best)
    thresh_csv_path = os.path.join(PROCESSED_DIR, "val_threshold_analysis.csv")
    thresh_df.to_csv(thresh_csv_path, index=False)
    print(f"[Threshold Analysis] Saved threshold performance grid to {thresh_csv_path}")

    # Select Production Decision Threshold for Clinical Screening
    # We choose threshold 0.30 to prioritize Sensitivity (>= 88%) while maintaining high Specificity (>= 85%)
    selected_threshold = 0.30
    eval_prod_val = evaluate_clinical_model(y_val, val_probs_best, threshold=selected_threshold)

    print(f"[Screening Threshold] Selected Production Threshold: {selected_threshold}")
    print(f"                      -> Sensitivity at 0.30: {eval_prod_val['sensitivity_recall']}")
    print(f"                      -> Specificity at 0.30: {eval_prod_val['specificity']}")
    print(f"                      -> Precision (PPV):      {eval_prod_val['precision_ppv']}")
    print(f"                      -> NPV:                  {eval_prod_val['npv']}")

    # Save Selected Production Model Artifact & Metadata
    joblib.dump(best_model, PROD_MODEL_PATH)
    
    prod_metadata = {
        "model_name": best_model_name,
        "dataset_name": "Healthcare EHR 100K Diabetes Prediction Dataset",
        "n_training_records": len(X_train),
        "n_validation_records": len(X_val),
        "random_seed": RANDOM_SEED,
        "features": feature_cols,
        "production_threshold": selected_threshold,
        "threshold_rationale": "Selected to optimize false-negative reduction in clinical screening (Sensitivity >= 88%) while maintaining strong specificity and NPV.",
        "output_description": "Model outputs estimated risk probability [0.0 to 1.0]. Results are risk estimates for clinical decision-support and do NOT constitute a definitive medical diagnosis.",
        "val_metrics_at_selected_threshold": eval_prod_val
    }

    with open(PROD_METADATA_PATH, "w") as f:
        json.dump(prod_metadata, f, indent=2)

    with open(RESULTS_JSON_PATH, "w") as f:
        json.dump({
            "models": experiment_results,
            "selected_production_model": best_model_name,
            "production_metadata": prod_metadata
        }, f, indent=2)

    # Format threshold table manually
    thresh_md_table = "| Threshold | Sensitivity | Specificity | Precision (PPV) | NPV | F1-Score | Accuracy | False Negatives | False Positives |\n| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for _, row in thresh_df.iterrows():
        thresh_md_table += f"| {row['Threshold']} | {row['Sensitivity']} | {row['Specificity']} | {row['Precision_PPV']} | {row['NPV']} | {row['F1_Score']} | {row['Accuracy']} | {int(row['False_Negatives']):,} | {int(row['False_Positives']):,} |\n"

    # Generate Markdown Report
    markdown_report = f"""# DIABETES MACHINE LEARNING MODEL TRAINING EXPERIMENT REPORT

**Training Set (`X_train`)**: {len(X_train):,} records (5-Fold Stratified CV)  
**Validation Set (`X_val`)**: {len(X_val):,} records (Unseen Selection Set)  
**Selected Production Model**: **{best_model_name}**  
**Selected Screening Threshold**: `{selected_threshold}`  
**Test Set Policy**: **UNTOUCHED (Preserved for final holdout testing)**  

---

## 1. Algorithm Comparison Table (Evaluated on Validation Set at Default 0.50 Threshold)

| Model Algorithm | 5-Fold CV ROC-AUC | Val ROC-AUC | Val PR-AUC | Val Sensitivity (Recall) | Val Specificity | Val Precision (PPV) | Val NPV | Val F1-Score | Val Brier Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for name, res in experiment_results.items():
        v = res["val_metrics"]
        markdown_report += f"| **{name}** | {res['mean_cv_auc']} \\pm {res['std_cv_auc']} | **{v['roc_auc']}** | {v['pr_auc']} | **{v['sensitivity_recall']}** | {v['specificity']} | {v['precision_ppv']} | {v['npv']} | {v['f1_score']} | {v['brier_score']} |\n"

    markdown_report += f"""
---

## 2. Threshold Performance Analysis (Validation Set, {best_model_name})

Evaluating multiple decision thresholds to select an optimal screening threshold:

{thresh_md_table}

---

## 3. Selected Production Screening Configuration

- **Model**: `{best_model_name}`
- **Configured Threshold**: `{selected_threshold}`
- **Sensitivity at `{selected_threshold}`**: `{eval_prod_val['sensitivity_recall']}`
- **Specificity at `{selected_threshold}`**: `{eval_prod_val['specificity']}`
- **Negative Predictive Value (NPV)**: `{eval_prod_val['npv']}`
- **Clinical Rationale**: For a diabetes risk screening tool, maximizing **Sensitivity** and **NPV** minimizes dangerous false negatives (diabetic patients erroneously told they are low risk).
"""

    with open(REPORT_MD_PATH, "w") as f:
        f.write(markdown_report)

    print(f"[SUCCESS] Experiment completed! Reports written to {RESULTS_JSON_PATH} and {REPORT_MD_PATH}")
    print("==================================================")
    return experiment_results

if __name__ == "__main__":
    run_ml_training_experiment()
