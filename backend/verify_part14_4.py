import json
import urllib.request
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def make_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    
    req_data = None
    if data:
        req_data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            body_str = resp.read().decode("utf-8")
            return resp.status, json.loads(body_str) if body_str.strip() else {}
    except urllib.error.HTTPError as e:
        body_str = e.read().decode("utf-8")
        try:
            parsed = json.loads(body_str) if body_str.strip() else {"detail": str(e)}
        except Exception:
            parsed = {"detail": str(e)}
        return e.code, parsed

def register_and_login(prefix):
    ts = int(time.time() * 1000)
    email = f"{prefix}.comp.{ts}@example.com"
    pwd = "Password123"
    
    reg_data = {
        "full_name": f"{prefix.capitalize()} Complications Patient",
        "email": email, "phone": "+1999888111",
        "password": pwd, "confirm_password": pwd, "age": 52, "gender": "Male"
    }
    status, res_reg = make_request(f"{BASE_URL}/api/auth/register", method="POST", data=reg_data)
    assert status == 201, f"Failed to register {email}: {res_reg}"
    
    login_data = {"email": email, "password": pwd}
    status, res_log = make_request(f"{BASE_URL}/api/auth/login", method="POST", data=login_data)
    assert status == 200 and "access_token" in res_log, f"Failed to login: {res_log}"
    return email, res_log["access_token"]

def run_tests():
    print("==================================================================")
    print("PART 14.4 — DIABETES COMPLICATION BACKEND INTEGRATION TEST")
    print("==================================================================")

    # 1. Setup Auth Users
    print("\n[1/4] Authenticating Patient A and Patient B...")
    email_a, token_a = register_and_login("patA")
    email_b, token_b = register_and_login("patB")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print("   - Authenticated Patient A and Patient B.")

    # 2. POST /api/predictions/diabetes-complications
    print("\n[2/4] Testing POST /api/predictions/diabetes-complications...")
    payload_a = {
        "age": 55, "systolic_bp": 145.0, "diastolic_bp": 92.0,
        "hba1c": 8.5, "fasting_glucose": 165.0, "diabetes_duration_years": 12,
        "bmi": 29.5, "serum_creatinine": 1.8, "albumin_urine": 2,
        "tingling_feet": 1, "vibration_loss": 1, "ankle_reflex": 1,
        "loss_of_sensory_perception": 1, "history_of_ulcer": 0,
        "ankle_brachial_index": 0.82, "intermittent_claudication": 1
    }
    status, res_comp = make_request(f"{BASE_URL}/api/predictions/diabetes-complications", method="POST", data=payload_a, headers=headers_a)
    print(f"   - Status: {status}")
    print(f"   - Heart Risk: {res_comp.get('heart_risk')} (Prob: {res_comp.get('heart_probability')})")
    print(f"   - Kidney Risk: {res_comp.get('kidney_risk')} (Prob: {res_comp.get('kidney_probability')})")
    print(f"   - Neuropathy Risk: {res_comp.get('neuropathy_risk')} (Prob: {res_comp.get('neuropathy_probability')})")
    print(f"   - Retinopathy Risk: {res_comp.get('retinopathy_risk')} (Prob: {res_comp.get('retinopathy_probability')})")
    print(f"   - Foot Ulcer Risk: {res_comp.get('foot_risk')} (Prob: {res_comp.get('foot_probability')})")
    print(f"   - Vascular Risk: {res_comp.get('vascular_risk')} (Prob: {res_comp.get('vascular_probability')})")
    print(f"   - Overall Risk Summary: {res_comp.get('overall_risk_summary')}")
    assert status == 201 and "id" in res_comp, "POST prediction failed"

    # 3. GET /api/predictions/diabetes-complications/latest & /history
    print("\n[3/4] Testing GET /latest and GET /history...")
    status, res_latest = make_request(f"{BASE_URL}/api/predictions/diabetes-complications/latest", method="GET", headers=headers_a)
    assert status == 200 and res_latest["id"] == res_comp["id"], "GET latest failed"
    print("   - GET /latest returned latest record matching ID.")

    status, res_hist = make_request(f"{BASE_URL}/api/predictions/diabetes-complications/history", method="GET", headers=headers_a)
    assert status == 200 and len(res_hist) >= 1, "GET history failed"
    print(f"   - GET /history returned {len(res_hist)} record(s).")

    # 4. Patient Data Isolation Check
    print("\n[4/4] Testing Patient Data Isolation (Patient B vs Patient A)...")
    status, res_b_latest = make_request(f"{BASE_URL}/api/predictions/diabetes-complications/latest", method="GET", headers=headers_b)
    assert status == 404, f"Patient B should NOT see Patient A's complication records! Got {status}"
    print("[PASS] Patient Data Isolation Verified: Patient B cannot access Patient A's complication records.")

    print("\n==================================================================")
    print("ALL PART 14.4 BACKEND INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================================")

if __name__ == "__main__":
    run_tests()
