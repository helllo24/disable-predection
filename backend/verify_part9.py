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
        "age": 35,
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
    token_a = register_and_login("medPatientA")
    token_b = register_and_login("medPatientB")
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    today_str = time.strftime("%Y-%m-%d")

    print("\n--- Test 1: Create Medicine Reminder for Patient A ---")
    payload_a = {
        "medicine_name": "Metformin",
        "dosage": "500 mg",
        "frequency": "Twice Daily",
        "start_date": today_str,
        "reminder_time": "08:00 AM",
        "notes": "Take after meals",
        "active": True
    }
    status, res_a = make_request(f"{BASE_URL}/api/medicines", method="POST", data=payload_a, headers=headers_a)
    print(f"Status: {status}, Response: {res_a}")
    assert status == 201, f"Expected 201 Created, got {status}"
    assert res_a["medicine_name"] == "Metformin", "Medicine name mismatch"
    med_id_a = res_a["id"]
    print("[PASS] Test 1 Passed: Medicine reminder created successfully.")

    print("\n--- Test 2: Read All Reminders & Today's Reminders for Patient A ---")
    status, all_a = make_request(f"{BASE_URL}/api/medicines", method="GET", headers=headers_a)
    assert status == 200 and len(all_a) == 1, "Expected 1 reminder for Patient A"

    status, today_a = make_request(f"{BASE_URL}/api/medicines/today", method="GET", headers=headers_a)
    assert status == 200 and len(today_a) == 1, "Expected 1 active reminder today for Patient A"
    assert today_a[0]["id"] == med_id_a, "Today reminder ID mismatch"
    print("[PASS] Test 2 Passed: Read reminders list & today's schedule verified.")

    print("\n--- Test 3: Update Medicine Reminder (Toggle Active / Change Dosage) ---")
    update_payload = {"dosage": "850 mg", "notes": "Updated dosage instructions"}
    status, updated_a = make_request(f"{BASE_URL}/api/medicines/{med_id_a}", method="PUT", data=update_payload, headers=headers_a)
    print(f"Status: {status}, Response: {updated_a}")
    assert status == 200 and updated_a["dosage"] == "850 mg", "Update dosage failed"
    print("[PASS] Test 3 Passed: Medicine reminder updated successfully.")

    print("\n--- Test 4: Unauthenticated Request Rejection ---")
    status, res = make_request(f"{BASE_URL}/api/medicines", method="GET")
    assert status == 401, f"Expected 401 Unauthorized, got {status}"
    print("[PASS] Test 4 Passed: Unauthenticated request rejected.")

    print("\n--- Test 5: Multi-Tenant Patient Data Isolation & Unauthorized Access Rejection ---")
    # Patient B attempts to read Patient A's reminder
    status, _ = make_request(f"{BASE_URL}/api/medicines/{med_id_a}", method="GET", headers=headers_b)
    assert status == 404, f"Patient B should be denied access to Patient A's reminder (404/403), got {status}"

    # Patient B attempts to update Patient A's reminder
    status, _ = make_request(f"{BASE_URL}/api/medicines/{med_id_a}", method="PUT", data={"dosage": "999mg"}, headers=headers_b)
    assert status == 404, f"Patient B should be denied updating Patient A's reminder, got {status}"

    # Patient B attempts to delete Patient A's reminder
    status, _ = make_request(f"{BASE_URL}/api/medicines/{med_id_a}", method="DELETE", headers=headers_b)
    assert status == 404, f"Patient B should be denied deleting Patient A's reminder, got {status}"

    # Verify Patient B has 0 reminders
    status, list_b = make_request(f"{BASE_URL}/api/medicines", method="GET", headers=headers_b)
    assert status == 200 and len(list_b) == 0, "Patient B should have 0 reminders"
    print("[PASS] Test 5 Passed: Multi-tenant patient isolation strictly enforced.")

    print("\n--- Test 6: Delete Medicine Reminder ---")
    status, _ = make_request(f"{BASE_URL}/api/medicines/{med_id_a}", method="DELETE", headers=headers_a)
    assert status == 204, f"Expected 204 No Content, got {status}"

    status, list_after_del = make_request(f"{BASE_URL}/api/medicines", method="GET", headers=headers_a)
    assert status == 200 and len(list_after_del) == 0, "Reminder should be deleted"
    print("[PASS] Test 6 Passed: Medicine reminder deleted successfully.")

    print("\n[SUCCESS] ALL PART 9 MEDICINE REMINDER TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
