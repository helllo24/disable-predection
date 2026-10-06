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
        "age": 32,
        "gender": "Female"
    }
    status, _ = make_request(f"{BASE_URL}/api/auth/register", method="POST", data=reg_data)
    assert status == 201, f"Failed to register patient {email}"
    
    login_data = {"email": email, "password": pwd}
    status, res = make_request(f"{BASE_URL}/api/auth/login", method="POST", data=login_data)
    assert status == 200 and "access_token" in res, "Failed to login"
    return res["access_token"]

def run_tests():
    print("--- Registering Patients A and B ---")
    token_a = register_and_login("dietPatientA")
    token_b = register_and_login("dietPatientB")
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    print("\n--- Test 1: Generate Valid Diet Recommendation for Patient A ---")
    payload_a = {
        "dietary_preference": "Vegetarian",
        "goal": "Weight Loss",
        "custom_allergies": "Dairy"
    }
    status, res_a = make_request(f"{BASE_URL}/api/recommendations/diet", method="POST", data=payload_a, headers=headers_a)
    print(f"Status: {status}, Response: {res_a}")
    assert status == 201, f"Expected 201 Created, got {status}"
    assert "recommendations" in res_a, "Missing recommendations dict"
    recs_a = res_a["recommendations"]
    assert "recommended_food_groups" in recs_a and len(recs_a["recommended_food_groups"]) > 0, "Food groups missing"
    assert "foods_to_consider" in recs_a and len(recs_a["foods_to_consider"]) > 0, "Foods to consider missing"
    assert "foods_to_limit" in recs_a, "Foods to limit missing"
    assert "hydration_guidance" in recs_a, "Hydration guidance missing"
    print("[PASS] Test 1 Passed: Valid diet recommendation generated successfully.")

    print("\n--- Test 2: Vegan Preference Filtering Test ---")
    payload_vegan = {
        "dietary_preference": "Vegan",
        "goal": "Healthy Eating",
        "custom_allergies": ""
    }
    status, res_v = make_request(f"{BASE_URL}/api/recommendations/diet", method="POST", data=payload_vegan, headers=headers_a)
    recs_v = res_v["recommendations"]
    print(f"Vegan Foods to Consider: {recs_v['foods_to_consider']}")
    # Verify no meat or poultry present
    meat_keywords = ["chicken", "beef", "pork", "turkey", "fish", "salmon", "tuna"]
    for food in recs_v["foods_to_consider"]:
        assert not any(m in food.lower() for m in meat_keywords), f"Meat item found in Vegan diet: {food}"
    print("[PASS] Test 2 Passed: Vegan preference filtered out all meat products.")

    print("\n--- Test 3: Allergy Exclusions Test (Dairy Allergy) ---")
    for food in recs_a["foods_to_consider"]:
        assert not any(d in food.lower() for d in ["milk", "cheese", "paneer", "yogurt"]), f"Dairy allergen found: {food}"
    print("[PASS] Test 3 Passed: Dairy allergy excluded dairy products.")

    print("\n--- Test 4: Unauthenticated Request Rejection ---")
    status, res = make_request(f"{BASE_URL}/api/recommendations/diet", method="POST", data=payload_a)
    print(f"Status: {status}, Response: {res}")
    assert status == 401, f"Expected 401 Unauthorized, got {status}"
    print("[PASS] Test 4 Passed: Unauthenticated request rejected.")

    print("\n--- Test 5 & 6: History Persistence & Multi-Tenant Patient Isolation ---")
    status, history_a = make_request(f"{BASE_URL}/api/recommendations/diet/history", method="GET", headers=headers_a)
    print(f"Patient A Diet History Count: {len(history_a)}")
    assert status == 200 and len(history_a) == 2, "Expected 2 history records for Patient A"

    status, history_b = make_request(f"{BASE_URL}/api/recommendations/diet/history", method="GET", headers=headers_b)
    print(f"Patient B Diet History Count: {len(history_b)}")
    assert status == 200 and len(history_b) == 0, "Patient B should have 0 records!"
    print("[PASS] Test 5 & 6 Passed: History persisted & patient isolation verified.")

    print("\n--- Test 7: Dashboard Latest Diet Endpoint ---")
    status, latest_a = make_request(f"{BASE_URL}/api/recommendations/diet/latest", method="GET", headers=headers_a)
    print(f"Patient A Latest Diet: {latest_a['dietary_preference']} - Goal: {latest_a['goal']}")
    assert status == 200 and latest_a is not None and latest_a["dietary_preference"] == "Vegan", "Latest diet fetch failed"
    print("[PASS] Test 7 Passed: Dashboard latest diet endpoint verified.")

    print("\n[SUCCESS] ALL PART 7 DIET RECOMMENDATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
