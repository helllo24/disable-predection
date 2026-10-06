import os
import json
import urllib.request
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def make_raw_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    
    req_data = None
    if data:
        req_data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            content_type = resp.headers.get("Content-Type", "")
            content_disposition = resp.headers.get("Content-Disposition", "")
            body_bytes = resp.read()
            return resp.status, content_type, content_disposition, body_bytes
    except urllib.error.HTTPError as e:
        body_bytes = e.read()
        return e.code, e.headers.get("Content-Type", ""), "", body_bytes

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
        "age": 45,
        "gender": "Male"
    }
    req_bytes = json.dumps(reg_data).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/api/auth/register", data=req_bytes, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 201
    
    login_data = {"email": email, "password": pwd}
    req_bytes = json.dumps(login_data).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/api/auth/login", data=req_bytes, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["access_token"]

def run_tests():
    print("--- Registering Patients A and B ---")
    token_a = register_and_login("pdfPatientA")
    token_b = register_and_login("pdfPatientB")
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    print("\n--- Test 1: Populate Sample Assessment Data for Patient A ---")
    # Add BMI for A
    bmi_req = urllib.request.Request(f"{BASE_URL}/api/bmi/calculate", data=json.dumps({"height": 175, "weight": 70}).encode("utf-8"), headers={"Content-Type": "application/json", **headers_a}, method="POST")
    urllib.request.urlopen(bmi_req)
    
    # Add Diabetes prediction for A
    diab_payload = {
        "pregnancies": 1, "glucose": 110, "blood_pressure": 70,
        "skin_thickness": 20, "insulin": 80, "bmi": 22.8,
        "diabetes_pedigree_function": 0.45, "age": 30
    }
    diab_req = urllib.request.Request(f"{BASE_URL}/api/predictions/diabetes", data=json.dumps(diab_payload).encode("utf-8"), headers={"Content-Type": "application/json", **headers_a}, method="POST")
    urllib.request.urlopen(diab_req)

    print("\n--- Test 2: Generate PDF Report for Patient A ---")
    status, c_type, c_disp, body_bytes = make_raw_request(f"{BASE_URL}/api/reports/health", method="GET", headers=headers_a)
    print(f"Status: {status}, Content-Type: {c_type}, Disposition: {c_disp}, Size: {len(body_bytes)} bytes")
    assert status == 200, f"Expected 200 OK, got {status}"
    assert "application/pdf" in c_type, f"Expected application/pdf, got {c_type}"
    assert body_bytes.startswith(b"%PDF-"), "Magic header does not start with %PDF-"
    print("[PASS] Test 2 Passed: PDF report generated successfully for Patient A.")

    print("\n--- Test 3: Missing Data Handling (Patient B with 0 assessment records) ---")
    status_b, c_type_b, c_disp_b, body_bytes_b = make_raw_request(f"{BASE_URL}/api/reports/health", method="GET", headers=headers_b)
    print(f"Status B: {status_b}, Size: {len(body_bytes_b)} bytes")
    assert status_b == 200 and body_bytes_b.startswith(b"%PDF-"), "Missing data handling failed"
    print("[PASS] Test 3 Passed: PDF generated cleanly for patient with no data ('No data available.').")

    print("\n--- Test 4: Unauthenticated Request Rejection ---")
    status_unauth, _, _, _ = make_raw_request(f"{BASE_URL}/api/reports/health", method="GET")
    assert status_unauth == 401, f"Expected 401 Unauthorized, got {status_unauth}"
    print("[PASS] Test 4 Passed: Unauthenticated PDF request rejected.")

    print("\n[SUCCESS] ALL PART 11 HEALTH REPORT PDF TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
