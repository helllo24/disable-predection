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
            try:
                parsed = json.loads(body) if body and body.strip() else {}
            except Exception:
                parsed = {"raw": body}
            return resp.status, parsed
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body) if body and body.strip() else {"detail": str(e)}
        except Exception:
            parsed = {"detail": str(e), "raw": body}
        return e.code, parsed

def register_and_login_patient(name_prefix):
    ts = int(time.time() * 1000)
    email = f"{name_prefix}.{ts}@example.com"
    pwd = "Password123"
    
    reg_data = {
        "full_name": f"{name_prefix.capitalize()} Patient",
        "email": email,
        "phone": "+1234567890",
        "password": pwd,
        "confirm_password": pwd,
        "age": 29,
        "gender": "Female"
    }
    status, res_reg = make_request(f"{BASE_URL}/api/auth/register", method="POST", data=reg_data)
    assert status == 201, f"Failed to register patient {email}, got {status}: {res_reg}"
    
    login_data = {"email": email, "password": pwd}
    status, res = make_request(f"{BASE_URL}/api/auth/login", method="POST", data=login_data)
    assert status == 200 and "access_token" in res, f"Failed to login: {res}"
    return email, pwd, res["access_token"]

def login_admin():
    login_data = {"email": "admin@example.com", "password": "AdminPass123"}
    status, res = make_request(f"{BASE_URL}/api/auth/login", method="POST", data=login_data)
    assert status == 200 and "access_token" in res, f"Failed to login as default admin: {res}"
    return res["access_token"]

def run_tests():
    print("--- Authenticating Patient and Admin Users ---")
    pat_email, pat_pwd, token_patient = register_and_login_patient("regularPatient")
    token_admin = login_admin()
    
    headers_patient = {"Authorization": f"Bearer {token_patient}"}
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    print("\n--- Test 1: Patient Access Control Rejection (403 Forbidden) ---")
    status, res_pat = make_request(f"{BASE_URL}/api/admin/dashboard", method="GET", headers=headers_patient)
    print(f"Patient Admin Call Status: {status}, Detail: {res_pat}")
    assert status == 403, f"Expected 403 Forbidden for patient accessing admin API, got {status}"
    print("[PASS] Test 1 Passed: Patient denied admin API access (403 Forbidden).")

    print("\n--- Test 2: Admin Dashboard Real Statistics ---")
    status, stats = make_request(f"{BASE_URL}/api/admin/dashboard", method="GET", headers=headers_admin)
    print(f"Status: {status}, Stats Response: {stats}")
    assert status == 200, f"Expected 200 OK, got {status}"
    assert "total_patients" in stats and "total_diabetes_predictions" in stats, "Missing stat fields"
    assert stats["total_patients"] >= 1, "Total patients count should be >= 1"
    print("[PASS] Test 2 Passed: Admin dashboard statistics retrieved successfully.")

    print("\n--- Test 3: Patients Directory & Password Hash Exclusion ---")
    status, patients_list = make_request(f"{BASE_URL}/api/admin/patients", method="GET", headers=headers_admin)
    print(f"Status: {status}, Patients Count: {len(patients_list)}")
    assert status == 200 and len(patients_list) >= 1, "Patients list empty"
    target_patient = patients_list[0]
    # VERIFY ABSOLUTE SECURITY: Password hash MUST NEVER be in response!
    assert "password_hash" not in target_patient and "password" not in target_patient, "SECURITY VIOLATION: Password field exposed in admin patients API!"
    target_id = target_patient["id"]
    print("[PASS] Test 3 Passed: Patients list retrieved and password hashes verified excluded.")

    print("\n--- Test 4: Admin Toggle Patient Active Status & Account Deactivation Check ---")
    status, toggle_res = make_request(f"{BASE_URL}/api/admin/patients/{target_id}/toggle-status", method="PUT", headers=headers_admin)
    print(f"Status: {status}, Toggle Response: {toggle_res}")
    assert status == 200, f"Toggle status failed with {status}"
    
    # If target was deactivated, verify login is rejected
    if not toggle_res["is_active"]:
        status_login, res_login = make_request(f"{BASE_URL}/api/auth/login", method="POST", data={"email": pat_email, "password": pat_pwd})
        assert status_login == 403, f"Deactivated patient should be denied login (403), got {status_login}"
        # Toggle back to active
        make_request(f"{BASE_URL}/api/admin/patients/{target_id}/toggle-status", method="PUT", headers=headers_admin)
    print("[PASS] Test 4 Passed: Patient account status toggle & login blocking verified.")

    print("\n--- Test 5: Prediction Logs & Appointments Monitoring ---")
    status, preds = make_request(f"{BASE_URL}/api/admin/predictions", method="GET", headers=headers_admin)
    assert status == 200 and "recent_diabetes_predictions" in preds, "Predictions endpoint failed"

    status, appts = make_request(f"{BASE_URL}/api/admin/appointments", method="GET", headers=headers_admin)
    assert status == 200 and isinstance(appts, list), "Appointments endpoint failed"
    print("[PASS] Test 5 Passed: Prediction logs and system appointments fetched by admin.")

    print("\n[SUCCESS] ALL PART 12 ADMIN DASHBOARD TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
