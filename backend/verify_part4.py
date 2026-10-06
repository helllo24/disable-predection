import os
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
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return e.code, json.loads(body) if body else {"detail": str(e)}

def register_and_login(name_prefix):
    ts = int(time.time() * 1000)
    email = f"{name_prefix}.{ts}@example.com"
    pwd = "Password123"
    
    reg_data = {
        "full_name": f"{name_prefix.capitalize()} Patient",
        "email": email,
        "phone": "+1234567890",
        "password": pwd,
        "confirm_password": pwd,
        "age": 30,
        "gender": "Female"
    }
    status, _ = make_request(f"{BASE_URL}/api/auth/register", method="POST", data=reg_data)
    assert status == 201, f"Failed to register patient {email}"
    
    login_data = {"email": email, "password": pwd}
    status, res = make_request(f"{BASE_URL}/api/auth/login", method="POST", data=login_data)
    assert status == 200 and "access_token" in res, "Failed to login"
    return res["access_token"]

def run_tests():
    print("--- Test 7: Model files existence and metadata integrity ---")
    model_file = os.path.join("..", "ml", "models", "diabetes_model.pkl")
    metadata_file = os.path.join("..", "ml", "models", "diabetes_model_metadata.json")
    
    if not os.path.exists(model_file):
        model_file = os.path.join("ml", "models", "diabetes_model.pkl")
        metadata_file = os.path.join("ml", "models", "diabetes_model_metadata.json")

    assert os.path.exists(model_file), f"Model file missing at {model_file}"
    assert os.path.exists(metadata_file), f"Metadata file missing at {metadata_file}"
    
    with open(metadata_file, 'r') as f:
        meta = json.load(f)
    
    print(f"Loaded Selected Model: {meta.get('selected_model')}")
    print(f"Features in Model: {meta.get('dataset', {}).get('features')}")
    print(f"Evaluation Metrics Summary: {json.dumps(meta.get('all_model_evaluations'), indent=2)}")
    print("[PASS] Test 7 Passed: Model files and metadata verified.")

    print("\n--- Registering Patients A and B ---")
    token_a = register_and_login("diabPatientA")
    token_b = register_and_login("diabPatientB")
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    print("\n--- Test 1 & Test 8: Valid Diabetes Prediction Input & Output Validation ---")
    valid_payload = {
        "pregnancies": 2,
        "glucose": 148,
        "blood_pressure": 72,
        "skin_thickness": 35,
        "insulin": 0,
        "bmi": 33.6,
        "diabetes_pedigree_function": 0.627,
        "age": 50
    }
    status, res = make_request(f"{BASE_URL}/api/predictions/diabetes", method="POST", data=valid_payload, headers=headers_a)
    print(f"Status: {status}, Response: {res}")
    assert status == 201, f"Expected 201 Created, got {status}"
    assert "prediction" in res and res["prediction"] in [0, 1], "Prediction output invalid"
    assert "risk" in res and ("risk" in res["risk"].lower()), "Risk output wording invalid"
    assert "probability" in res and 0.0 <= res["probability"] <= 1.0, "Probability out of range"
    assert "model" in res and len(res["model"]) > 0, "Model name missing"
    print("[PASS] Test 1 & Test 8 Passed: Valid prediction generated accurately.")

    print("\n--- Test 2: Invalid Negative Input Values Rejection ---")
    invalid_neg = {
        "pregnancies": -2,
        "glucose": 120,
        "blood_pressure": 70,
        "skin_thickness": 20,
        "insulin": 79,
        "bmi": 25.5,
        "diabetes_pedigree_function": 0.35,
        "age": 30
    }
    status, res = make_request(f"{BASE_URL}/api/predictions/diabetes", method="POST", data=invalid_neg, headers=headers_a)
    print(f"Status: {status}, Response: {res}")
    assert status in [400, 422], f"Expected 400/422 for negative input, got {status}"
    print("[PASS] Test 2 Passed: Invalid negative values rejected.")

    print("\n--- Test 3: Missing Required Field Rejection ---")
    missing_field_payload = {
        "pregnancies": 2,
        "glucose": 120,
        # blood_pressure missing
        "skin_thickness": 20,
        "insulin": 79,
        "bmi": 25.5,
        "diabetes_pedigree_function": 0.35,
        "age": 30
    }
    status, res = make_request(f"{BASE_URL}/api/predictions/diabetes", method="POST", data=missing_field_payload, headers=headers_a)
    print(f"Status: {status}, Response: {res}")
    assert status == 422, f"Expected 422 Unprocessable Entity, got {status}"
    print("[PASS] Test 3 Passed: Missing required field rejected.")

    print("\n--- Test 4: Prediction API without JWT Authorization ---")
    status, res = make_request(f"{BASE_URL}/api/predictions/diabetes", method="POST", data=valid_payload)
    print(f"Status: {status}, Response: {res}")
    assert status == 401, f"Expected 401 Unauthorized, got {status}"
    print("[PASS] Test 4 Passed: Unauthenticated prediction attempt rejected.")

    print("\n--- Test 5: Verify Prediction History Persistence for Patient A ---")
    status, history_a = make_request(f"{BASE_URL}/api/predictions/diabetes/history", method="GET", headers=headers_a)
    print(f"Patient A History Count: {len(history_a)}")
    assert status == 200 and len(history_a) == 1, "Expected 1 history record for Patient A"
    assert history_a[0]["glucose"] == 148, "History payload mismatch"
    print("[PASS] Test 5 Passed: Prediction history persisted correctly.")

    print("\n--- Test 6: Multi-tenant Patient Data Isolation ---")
    status, history_b = make_request(f"{BASE_URL}/api/predictions/diabetes/history", method="GET", headers=headers_b)
    print(f"Patient B History Count: {len(history_b)}")
    assert status == 200 and len(history_b) == 0, "Patient B should have 0 records!"
    print("[PASS] Test 6 Passed: Patient B cannot access Patient A's predictions.")

    print("\n--- Test 9: Dashboard Latest Prediction Integration Endpoint ---")
    status, latest_a = make_request(f"{BASE_URL}/api/predictions/diabetes/latest", method="GET", headers=headers_a)
    print(f"Patient A Latest Prediction: {latest_a}")
    assert status == 200 and latest_a is not None and latest_a["glucose"] == 148, "Latest prediction fetch failed"

    status, latest_b = make_request(f"{BASE_URL}/api/predictions/diabetes/latest", method="GET", headers=headers_b)
    print(f"Patient B Latest Prediction: {latest_b}")
    assert status == 200 and latest_b is None, "Patient B should have None for latest prediction"
    print("[PASS] Test 9 Passed: Dashboard latest prediction endpoint verified.")

    print("\n[SUCCESS] ALL PART 4 DIABETES ML PREDICTION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
