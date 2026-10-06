import sys
import os

# Ensure app can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.routes.research import (
    get_external_validation_summary,
    get_fairness_analysis,
    get_calibration_metrics,
    get_shap_stability,
    get_tripod_ai_report
)

def test_research_endpoints_direct():
    print("==================================================")
    print("VERIFYING DIABETES PREDICTION RESEARCH API FUNCTIONS")
    print("==================================================")

    # 1. External Validation Endpoint
    val_data = get_external_validation_summary()
    assert "models" in val_data, "Missing models in response"
    assert "XGBoost" in val_data["models"], "Missing XGBoost in models"
    print("[PASS] get_external_validation_summary()")

    xgb_metrics = val_data["models"]["XGBoost"]
    print(f"       -> Internal CV AUC: {xgb_metrics['internal_validation']['auc_mean']}")
    print(f"       -> External AUC (Mendeley n=1,168): {xgb_metrics['external_validation']['auc']}")
    print(f"       -> Optimism Bias Drop: -{xgb_metrics['optimism_bias']['relative_auc_drop_pct']}%")

    # 2. Subgroup Fairness Analysis Endpoint
    fair_data = get_fairness_analysis()
    assert "subgroup_fairness" in fair_data, "Missing subgroup_fairness"
    print("[PASS] get_fairness_analysis()")
    print(f"       -> Age Fairness Gap (Young vs Older): {fair_data['subgroup_fairness']['XGBoost']['age_fairness_gap']}")

    # 3. Calibration Metrics Endpoint
    cal_data = get_calibration_metrics()
    assert "calibration" in cal_data, "Missing calibration"
    print("[PASS] get_calibration_metrics()")

    # 4. SHAP Stability Endpoint
    shap_data = get_shap_stability()
    assert "rankings" in shap_data, "Missing rankings"
    print("[PASS] get_shap_stability()")
    print(f"       -> Top Predictor: {shap_data.get('top_predictor')}")

    # 5. TRIPOD-AI Compliance Endpoint
    tripod_data = get_tripod_ai_report()
    assert "compliance_items" in tripod_data, "Missing compliance items"
    print("[PASS] get_tripod_ai_report()")

    print("\n==================================================")
    print("ALL RESEARCH API FUNCTIONS VERIFIED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    test_research_endpoints_direct()
