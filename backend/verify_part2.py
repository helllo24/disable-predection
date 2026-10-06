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

def run_tests():
    print("--- 1. Registering Patient ---")
    test_email = f"patient.part2.{int(time.time())}@example.com"
    patient_data = {
        "full_name": "Bob Patient",
        "email": test_email,
        "phone": "+1987654321",
        "password": "Password123",
        "confirm_password": "Password123",
        "age": 35,
        "gender": "Male"
    }
    status, res = make_request(f"{BASE_URL}/api/auth/register", method="POST", data=patient_data)
    print(f"Registration status: {status}")
    assert status == 201, "Registration failed"

    print("\n--- 2. Logging In ---")
    status, res = make_request(f"{BASE_URL}/api/auth/login", method="POST", data={"email": test_email, "password": "Password123"})
    print(f"Login status: {status}")
    assert status == 200 and "access_token" in res, "Login failed"
    token = res["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- 3. Checking Initial Profile via GET /api/auth/me ---")
    status, res = make_request(f"{BASE_URL}/api/auth/me", method="GET", headers=headers)
    print(f"Status: {status}, Initial Profile: {res}")
    assert status == 200, "Fetch profile failed"
    assert res.get("height") is None, "Height should be None initially"
    assert res.get("weight") is None, "Weight should be None initially"

    print("\n--- 4. Updating Profile via PUT /api/auth/profile ---")
    profile_update = {
        "full_name": "Bob Patient Jr.",
        "phone": "+1999888777",
        "age": 36,
        "gender": "Male",
        "height": 180.5,
        "weight": 78.2,
        "blood_group": "O+",
        "allergies": "Peanuts, Penicillin",
        "existing_conditions": "Seasonal Asthma"
    }
    status, res = make_request(f"{BASE_URL}/api/auth/profile", method="PUT", data=profile_update, headers=headers)
    print(f"Profile Update Status: {status}, Updated Profile: {res}")
    assert status == 200, "Update profile failed"
    assert res.get("full_name") == "Bob Patient Jr.", "Name update failed"
    assert res.get("height") == 180.5, "Height update failed"
    assert res.get("weight") == 78.2, "Weight update failed"
    assert res.get("blood_group") == "O+", "Blood group update failed"
    assert res.get("allergies") == "Peanuts, Penicillin", "Allergies update failed"

    print("\n--- 5. Confirming Persisted Profile via GET /api/auth/me ---")
    status, res = make_request(f"{BASE_URL}/api/auth/me", method="GET", headers=headers)
    print(f"Persisted Profile: {res}")
    assert status == 200 and res.get("blood_group") == "O+", "Persistence check failed"

    print("\n[SUCCESS] ALL PART 2 BACKEND PROFILE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
