import urllib.request
import json
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
        "gender": "Male"
    }
    status, _ = make_request(f"{BASE_URL}/api/auth/register", method="POST", data=reg_data)
    assert status == 201, f"Failed to register patient {email}"
    
    login_data = {"email": email, "password": pwd}
    status, res = make_request(f"{BASE_URL}/api/auth/login", method="POST", data=login_data)
    assert status == 200 and "access_token" in res, "Failed to login"
    return res["access_token"]

def run_tests():
    print("--- Registering Test Patients A and B ---")
    token_a = register_and_login("patientA")
    token_b = register_and_login("patientB")
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    print("\n--- Test 1: Height 170 cm, Weight 68 kg ---")
    req1 = {"height": 170, "height_unit": "cm", "weight": 68, "weight_unit": "kg"}
    status, res = make_request(f"{BASE_URL}/api/bmi/calculate", method="POST", data=req1, headers=headers_a)
    print(f"Status: {status}, Response: {res}")
    assert status == 201, "Test 1 calculation failed"
    assert round(res["bmi"], 1) == 23.5, f"Expected 23.5, got {res['bmi']}"
    assert res["category"] == "Normal weight", f"Expected Normal weight, got {res['category']}"
    print("[PASS] Test 1 Passed: BMI = 23.5 (Normal weight)")

    print("\n--- Test 2: Height 170 cm, Weight 85 kg ---")
    req2 = {"height": 170, "height_unit": "cm", "weight": 85, "weight_unit": "kg"}
    status, res = make_request(f"{BASE_URL}/api/bmi/calculate", method="POST", data=req2, headers=headers_a)
    print(f"Status: {status}, Response: {res}")
    assert status == 201, "Test 2 calculation failed"
    assert res["category"] == "Overweight", f"Expected Overweight, got {res['category']}"
    print("[PASS] Test 2 Passed: Category = Overweight")

    print("\n--- Test 3: Invalid Height = -170 ---")
    req3 = {"height": -170, "height_unit": "cm", "weight": 68, "weight_unit": "kg"}
    status, res = make_request(f"{BASE_URL}/api/bmi/calculate", method="POST", data=req3, headers=headers_a)
    print(f"Status: {status}, Response: {res}")
    assert status in [400, 422], "Expected 400 or 422 for negative height"
    print("[PASS] Test 3 Passed: Invalid negative height correctly rejected")

    print("\n--- Test 4: Invalid Weight = 0 ---")
    req4 = {"height": 170, "height_unit": "cm", "weight": 0, "weight_unit": "kg"}
    status, res = make_request(f"{BASE_URL}/api/bmi/calculate", method="POST", data=req4, headers=headers_a)
    print(f"Status: {status}, Response: {res}")
    assert status in [400, 422], "Expected 400 or 422 for weight 0"
    print("[PASS] Test 4 Passed: Weight 0 correctly rejected")

    print("\n--- Test 5: Verify BMI History Persistence for Patient A ---")
    status, history_a = make_request(f"{BASE_URL}/api/bmi/history", method="GET", headers=headers_a)
    print(f"Status: {status}, History count: {len(history_a)}")
    assert status == 200 and len(history_a) == 2, f"Expected 2 history records, got {len(history_a)}"
    assert history_a[0]["category"] == "Overweight", "Newest record should be first"
    print("[PASS] Test 5 Passed: BMI history stored and ordered newest first")

    print("\n--- Test 6: Multi-tenant Privacy Isolation (Patient B cannot access Patient A's records) ---")
    status, history_b = make_request(f"{BASE_URL}/api/bmi/history", method="GET", headers=headers_b)
    print(f"Patient B History Count: {len(history_b)}")
    assert status == 200 and len(history_b) == 0, "Patient B should see 0 records!"
    print("[PASS] Test 6 Passed: Patient B cannot access Patient A's history")

    print("\n--- Test 7: Unauthenticated Request Rejection ---")
    status, res = make_request(f"{BASE_URL}/api/bmi/history", method="GET")
    print(f"Status: {status}, Response: {res}")
    assert status == 401, "Unauthenticated request should return 401"
    print("[PASS] Test 7 Passed: Unauthenticated request rejected")

    print("\n--- Test 8: Dashboard Latest Real BMI Record Integration Endpoint ---")
    status, latest_a = make_request(f"{BASE_URL}/api/bmi/latest", method="GET", headers=headers_a)
    print(f"Patient A Latest BMI: {latest_a}")
    assert status == 200 and latest_a["category"] == "Overweight", "Latest record fetch failed"
    
    status, latest_b = make_request(f"{BASE_URL}/api/bmi/latest", method="GET", headers=headers_b)
    print(f"Patient B Latest BMI: {latest_b}")
    assert status == 200 and latest_b is None, "Patient B should have null latest record"
    print("[PASS] Test 8 Passed: Dashboard latest BMI endpoint returns real latest record")

    print("\n[SUCCESS] ALL PART 3 BMI CALCULATOR TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
