import urllib.request
import json
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
    print("--- 1. Testing GET / ---")
    status, res = make_request(f"{BASE_URL}/")
    print(f"Status: {status}, Response: {res}")
    assert status == 200 and res.get("message") == "Smart Healthcare Assistant API is running", "GET / failed"

    print("\n--- 2. Testing GET /api/health ---")
    status, res = make_request(f"{BASE_URL}/api/health")
    print(f"Status: {status}, Response: {res}")
    assert status == 200 and res.get("status") == "healthy", "GET /api/health failed"

    print("\n--- 3. Testing POST /api/auth/register ---")
    import time
    test_email = f"alice.smith.{int(time.time())}@example.com"
    patient_data = {
        "full_name": "Alice Smith",
        "email": test_email,
        "phone": "+1234567890",
        "password": "SecretPassword123",
        "confirm_password": "SecretPassword123",
        "age": 29,
        "gender": "Female"
    }
    status, res = make_request(f"{BASE_URL}/api/auth/register", method="POST", data=patient_data)
    print(f"Status: {status}, Response: {res}")
    assert status == 201, f"Registration failed with status {status}"
    assert res.get("email") == test_email, "Email mismatch"
    assert res.get("role") == "PATIENT", "Role mismatch"
    assert "password_hash" not in res, "Password hash leaked in response!"

    print("\n--- 4. Testing Duplicate Email Registration Rejection ---")
    status, res = make_request(f"{BASE_URL}/api/auth/register", method="POST", data=patient_data)
    print(f"Status: {status}, Response: {res}")
    assert status == 400, "Duplicate registration was not rejected!"

    print("\n--- 5. Testing POST /api/auth/login ---")
    login_data = {
        "email": test_email,
        "password": "SecretPassword123"
    }
    status, res = make_request(f"{BASE_URL}/api/auth/login", method="POST", data=login_data)
    print(f"Status: {status}, Token received: {'access_token' in res}")
    assert status == 200 and "access_token" in res, "Login failed"
    token = res["access_token"]

    print("\n--- 6. Testing Invalid Login Credentials Rejection ---")
    bad_login = {
        "email": test_email,
        "password": "WrongPassword!"
    }
    status, res = make_request(f"{BASE_URL}/api/auth/login", method="POST", data=bad_login)
    print(f"Status: {status}, Response: {res}")
    assert status == 401, "Invalid login was not rejected!"

    print("\n--- 7. Testing Protected GET /api/auth/me ---")
    headers = {"Authorization": f"Bearer {token}"}
    status, res = make_request(f"{BASE_URL}/api/auth/me", method="GET", headers=headers)
    print(f"Status: {status}, User Profile: {res}")
    assert status == 200 and res.get("full_name") == "Alice Smith", "Protected /me failed"

    print("\n--- 8. Testing Unauthenticated Request Rejection ---")
    status, res = make_request(f"{BASE_URL}/api/auth/me", method="GET")
    print(f"Status: {status}, Response: {res}")
    assert status == 401, "Unauthenticated request was not rejected!"

    print("\n[SUCCESS] ALL BACKEND AUTHENTICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
