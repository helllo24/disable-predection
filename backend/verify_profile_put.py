import json
import urllib.request
import time

BASE_URL = "http://127.0.0.1:8000"

def test_profile_update():
    ts = int(time.time() * 1000)
    email = f"prof.{ts}@example.com"
    pwd = "Password123"
    
    # 1. Register
    reg_data = {
        "full_name": "Test Profile User", "email": email, "phone": "+1999000111",
        "password": pwd, "confirm_password": pwd, "age": 30, "gender": "Male"
    }
    req = urllib.request.Request(f"{BASE_URL}/api/auth/register", data=json.dumps(reg_data).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    urllib.request.urlopen(req)
    
    # 2. Login
    login_data = {"email": email, "password": pwd}
    req = urllib.request.Request(f"{BASE_URL}/api/auth/login", data=json.dumps(login_data).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        token = res["access_token"]
        
    # 3. PUT /api/auth/profile
    profile_update = {
        "full_name": "Updated Profile User",
        "age": 32,
        "height": 180.0,
        "weight": 75.0,
        "blood_group": "O+"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    req = urllib.request.Request(f"{BASE_URL}/api/auth/profile", data=json.dumps(profile_update).encode("utf-8"), headers=headers, method="PUT")
    with urllib.request.urlopen(req) as resp:
        print(f"Status: {resp.status}")
        body = json.loads(resp.read().decode("utf-8"))
        print(f"Response: {body}")
        assert resp.status == 200 and body["full_name"] == "Updated Profile User"
        print("[SUCCESS] PUT /api/auth/profile works cleanly with HTTP 200 OK!")

if __name__ == "__main__":
    test_profile_update()
