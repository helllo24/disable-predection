import os
import json
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/research", tags=["Research & External Validation"])

# Path to pre-calculated ML research evaluation results
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RESULTS_PATH = os.path.join(PROJECT_ROOT, "ml", "evaluation", "external_validation_results.json")

def load_research_results():
    if not os.path.exists(RESULTS_PATH):
        raise HTTPException(
            status_code=500,
            detail="External validation results not found. Please run ml/training/train_external_validation.py first."
        )
    try:
        with open(RESULTS_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load research results: {str(e)}")

@router.get("/external-validation")
def get_external_validation_summary():
    """
    Returns internal Pima vs external Mendeley dataset validation metrics,
    optimism bias quantification, and ROC curve plot data.
    """
    data = load_research_results()
    return {
        "metadata": data.get("metadata", {}),
        "models": data.get("models", {})
    }

@router.get("/fairness-analysis")
def get_fairness_analysis():
    """
    Returns demographic subgroup fairness analysis stratified by Age (<40, 40-60, >60) and Sex,
    quantifying the Age Fairness Crisis and Systematic Arbitrariness Index.
    """
    data = load_research_results()
    models_data = data.get("models", {})
    
    fairness_by_model = {}
    for model_name, details in models_data.items():
        fairness_by_model[model_name] = details.get("subgroup_fairness", {})

    return {
        "title": "Demographic Subgroup Fairness & Age Bias Analysis",
        "subgroup_fairness": fairness_by_model
    }

@router.get("/calibration")
def get_calibration_metrics():
    """
    Returns Brier scores, calibration slopes, and reliability curve coordinates for internal vs external transfer.
    """
    data = load_research_results()
    models_data = data.get("models", {})
    
    calibration_by_model = {}
    for model_name, details in models_data.items():
        calibration_by_model[model_name] = details.get("calibration", {})

    return {
        "title": "Model Calibration & Brier Score Assessment",
        "calibration": calibration_by_model
    }

@router.get("/shap-stability")
def get_shap_stability():
    """
    Returns SHAP feature ranking stability across dataset transfer.
    """
    data = load_research_results()
    return data.get("shap_stability", {})

@router.get("/tripod-ai-report")
def get_tripod_ai_report():
    """
    Returns structured TRIPOD-AI reporting compliance items.
    """
    data = load_research_results()
    return {
        "framework": "TRIPOD-AI Checklist (Transparent Reporting of a Multivariable Prediction Model for Individual Prognosis or Diagnosis - AI)",
        "compliance_items": data.get("tripod_compliance", {})
    }
