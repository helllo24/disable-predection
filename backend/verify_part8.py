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
        "age": 28,
        "gender": "Male"
    }
    status, _ = make_request(f"{BASE_URL}/api/auth/register", method="POST", data=reg_data)
    assert status == 201, f"Failed to register patient {email}"
    
    login_data = {"email": email, "password": pwd}
    status, res = make_request(f"{BASE_URL}/api/auth/login", method="POST", data=login_data)
    assert status == 200 and "access_token" in res, "Failed to login"
    return res["access_token"]

def run_tests():
    print("--- Registering Patients A and B ---")
    token_a = register_and_login("exePatientA")
    token_b = register_and_login("exePatientB")
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    print("\n--- Test 1: Generate Valid Exercise Recommendation for Patient A ---")
    payload_a = {
        "fitness_level": "Beginner",
        "goal": "Weight Management"
    }
    status, res_a = make_request(f"{BASE_URL}/api/recommendations/exercise", method="POST", data=payload_a, headers=headers_a)
    print(f"Status: {status}, Response: {res_a}")
    assert status == 201, f"Expected 201 Created, got {status}"
    assert "recommendations" in res_a, "Missing recommendations dict"
    recs_a = res_a["recommendations"]
    assert "recommended_activities" in recs_a and len(recs_a["recommended_activities"]) > 0, "Activities missing"
    assert "frequency_guidance" in recs_a, "Frequency guidance missing"
    assert "duration_guidance" in recs_a, "Duration guidance missing"
    assert "intensity_guidance" in recs_a, "Intensity guidance missing"
    assert "safety_notes" in recs_a and len(recs_a["safety_notes"]) > 0, "Safety notes missing"
    assert any("Consult a healthcare professional" in note for note in recs_a["safety_notes"]), "Mandated safety note missing"
    print("[PASS] Test 1 Passed: Valid exercise recommendation generated successfully.")

    print("\n--- Test 2: Fitness Level Prescription Differentiation Test ---")
    payload_adv = {
        "fitness_level": "Advanced",
        "goal": "Strength"
    }
    status, res_adv = make_request(f"{BASE_URL}/api/recommendations/exercise", method="POST", data=payload_adv, headers=headers_a)
    recs_adv = res_adv["recommendations"]
    print(f"Beginner Duration: {recs_a['duration_guidance']}")
    print(f"Advanced Duration: {recs_adv['duration_guidance']}")
    assert recs_a["duration_guidance"] != recs_adv["duration_guidance"], "Prescription duration should differ by level!"
    print("[PASS] Test 2 Passed: Level prescription parameters differentiated.")

    print("\n--- Test 3: Unauthenticated Request Rejection ---")
    status, res = make_request(f"{BASE_URL}/api/recommendations/exercise", method="POST", data=payload_a)
    print(f"Status: {status}, Response: {res}")
    assert status == 401, f"Expected 401 Unauthorized, got {status}"
    print("[PASS] Test 3 Passed: Unauthenticated request rejected.")

    print("\n--- Test 4 & 5: History Persistence & Multi-Tenant Patient Isolation ---")
    status, history_a = make_request(f"{BASE_URL}/api/recommendations/exercise/history", method="GET", headers=headers_a)
    print(f"Patient A Exercise History Count: {len(history_a)}")
    assert status == 200 and len(history_a) == 2, "Expected 2 history records for Patient A"

    status, history_b = make_request(f"{BASE_URL}/api/recommendations/exercise/history", method="GET", headers=headers_b)
    print(f"Patient B Exercise History Count: {len(history_b)}")
    assert status == 200 and len(history_b) == 0, "Patient B should have 0 records!"
    print("[PASS] Test 4 & 5 Passed: History persisted & patient isolation verified.")

    print("\n--- Test 6: Dashboard Latest Exercise Endpoint ---")
    status, latest_a = make_request(f"{BASE_URL}/api/recommendations/exercise/latest", method="GET", headers=headers_a)
    print(f"Patient A Latest Exercise Plan: {latest_a['fitness_level']} - Goal: {latest_a['goal']}")
    assert status == 200 and latest_a is not None and latest_a["fitness_level"] == "Advanced", "Latest exercise fetch failed"
    print("[PASS] Test 6 Passed: Dashboard latest exercise endpoint verified.")

    print("\n[SUCCESS] ALL PART 8 EXERCISE RECOMMENDATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
