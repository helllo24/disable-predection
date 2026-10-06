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

def register_and_login(name_prefix, age=30):
    ts = int(time.time() * 1000)
    email = f"{name_prefix}.{ts}@example.com"
    pwd = "Password123"
    
    reg_data = {
        "full_name": f"{name_prefix.capitalize()} Patient",
        "email": email,
        "phone": "+1234567890",
        "password": pwd,
        "confirm_password": pwd,
        "age": age,
        "gender": "Female"
    }
    status, _ = make_request(f"{BASE_URL}/api/auth/register", method="POST", data=reg_data)
    assert status == 201, f"Failed to register patient {email}"
    
    login_data = {"email": email, "password": pwd}
    status, res = make_request(f"{BASE_URL}/api/auth/login", method="POST", data=login_data)
    assert status == 200 and "access_token" in res, "Failed to login"
    return res["access_token"]

def run_tests():
    print("--- Registering Patients A (Age 50) and B (Age 25) ---")
    token_a = register_and_login("riskPatientA", age=50)
    token_b = register_and_login("riskPatientB", age=25)
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    print("\n--- Test 1: Calculate Valid Health Risk Score for Patient A ---")
    # First, let's create a BMI and Diabetes prediction record for Patient A
    bmi_payload = {"height": 165, "height_unit": "cm", "weight": 85, "weight_unit": "kg"}
    make_request(f"{BASE_URL}/api/bmi/calculate", method="POST", data=bmi_payload, headers=headers_a)

    diab_payload = {
        "pregnancies": 2, "glucose": 150, "blood_pressure": 75, "skin_thickness": 30,
        "insulin": 100, "bmi": 31.2, "diabetes_pedigree_function": 0.5, "age": 50
    }
    make_request(f"{BASE_URL}/api/predictions/diabetes", method="POST", data=diab_payload, headers=headers_a)

    status, res_a = make_request(f"{BASE_URL}/api/health-risk/calculate", method="POST", headers=headers_a)
    print(f"Status: {status}, Response: {res_a}")
    assert status == 201, f"Expected 201 Created, got {status}"
    assert "score" in res_a and 0 <= res_a["score"] <= 100, "Score out of 0-100 range"
    assert "category" in res_a and res_a["category"] in ["Low Risk", "Moderate Risk", "High Risk"], "Category invalid"
    assert "contributing_factors" in res_a and len(res_a["contributing_factors"]) == 4, "Contributing factors count mismatch"
    print("[PASS] Test 1 Passed: Valid composite score calculated successfully.")

    print("\n--- Test 2: Calculate Score with Partial/Missing ML Data for Patient B ---")
    status, res_b = make_request(f"{BASE_URL}/api/health-risk/calculate", method="POST", headers=headers_b)
    print(f"Status: {status}, Response: {res_b}")
    assert status == 201, f"Expected 201 Created, got {status}"
    assert "score" in res_b and res_b["score"] == 0, "Expected 0 score for young patient without health risks"
    assert res_b["category"] == "Low Risk", "Expected Low Risk category"
    print("[PASS] Test 2 Passed: Handled missing ML predictions gracefully.")

    print("\n--- Test 3: Unauthenticated Request Rejection ---")
    status, res = make_request(f"{BASE_URL}/api/health-risk/calculate", method="POST")
    print(f"Status: {status}, Response: {res}")
    assert status == 401, f"Expected 401 Unauthorized, got {status}"
    print("[PASS] Test 3 Passed: Unauthenticated calculation attempt rejected.")

    print("\n--- Test 4 & 5: History Persistence & Multi-Tenant Isolation ---")
    status, history_a = make_request(f"{BASE_URL}/api/health-risk/history", method="GET", headers=headers_a)
    print(f"Patient A History Count: {len(history_a)}")
    assert status == 200 and len(history_a) == 1, "Expected 1 history record for Patient A"
    assert history_a[0]["score"] == res_a["score"], "Score mismatch in history"

    status, history_b = make_request(f"{BASE_URL}/api/health-risk/history", method="GET", headers=headers_b)
    print(f"Patient B History Count: {len(history_b)}")
    assert status == 200 and len(history_b) == 1, "Expected 1 history record for Patient B"
    assert history_b[0]["score"] == res_b["score"], "Score mismatch for Patient B"
    assert history_a[0]["id"] != history_b[0]["id"], "Patient isolation failure!"
    print("[PASS] Test 4 & 5 Passed: History persisted & patient isolation verified.")

    print("\n--- Test 6: Dashboard Latest Health Risk Score Endpoint ---")
    status, latest_a = make_request(f"{BASE_URL}/api/health-risk/latest", method="GET", headers=headers_a)
    print(f"Patient A Latest Score: {latest_a}")
    assert status == 200 and latest_a is not None and latest_a["score"] == res_a["score"], "Latest score fetch failed"
    print("[PASS] Test 6 Passed: Dashboard latest risk score endpoint verified.")

    print("\n[SUCCESS] ALL PART 6 HEALTH RISK SCORE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
