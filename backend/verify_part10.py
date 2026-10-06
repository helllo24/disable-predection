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
        "age": 40,
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
    token_a = register_and_login("apptPatientA")
    token_b = register_and_login("apptPatientB")
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    print("\n--- Test 1: Fetch Doctors Directory ---")
    status, docs = make_request(f"{BASE_URL}/api/doctors", method="GET")
    print(f"Status: {status}, Total Doctors Found: {len(docs)}")
    assert status == 200 and len(docs) >= 5, "Expected at least 5 demo doctors"
    doctor_id = docs[0]["id"]
    print(f"Using Doctor ID #{doctor_id} ({docs[0]['name']}) for booking tests.")
    print("[PASS] Test 1 Passed: Doctors directory fetched successfully.")

    today_str = time.strftime("%Y-%m-%d")

    print("\n--- Test 2: Book Valid Appointment for Patient A ---")
    payload_a = {
        "doctor_id": doctor_id,
        "appointment_date": today_str,
        "appointment_time": "10:00 AM",
        "reason": "Routine Cardiology Consultation"
    }
    status, res_a = make_request(f"{BASE_URL}/api/appointments", method="POST", data=payload_a, headers=headers_a)
    print(f"Status: {status}, Response: {res_a}")
    assert status == 201, f"Expected 201 Created, got {status}"
    appt_id_a = res_a["id"]
    assert res_a["status"] == "Scheduled", "Status mismatch"
    print("[PASS] Test 2 Passed: Appointment booked successfully.")

    print("\n--- Test 3: Past Date Appointment Validation Rejection ---")
    payload_past = {
        "doctor_id": doctor_id,
        "appointment_date": "2020-01-01",
        "appointment_time": "10:00 AM",
        "reason": "Past date test"
    }
    status, res_past = make_request(f"{BASE_URL}/api/appointments", method="POST", data=payload_past, headers=headers_a)
    print(f"Status: {status}, Response: {res_past}")
    assert status in [400, 422], f"Expected 400 or 422 for past date, got {status}"
    print("[PASS] Test 3 Passed: Past appointment date rejected.")

    print("\n--- Test 4: Conflicting Double-Booking Rejection ---")
    # Patient B attempts to book the exact same doctor, date, and time slot
    payload_conflict = {
        "doctor_id": doctor_id,
        "appointment_date": today_str,
        "appointment_time": "10:00 AM",
        "reason": "Conflicting slot test"
    }
    status, res_conflict = make_request(f"{BASE_URL}/api/appointments", method="POST", data=payload_conflict, headers=headers_b)
    print(f"Status: {status}, Response: {res_conflict}")
    assert status == 409, f"Expected 409 Conflict for double booking, got {status}"
    print("[PASS] Test 4 Passed: Double-booking conflicting slot rejected.")

    print("\n--- Test 5: Read Patient Appointments & Upcoming Appointment ---")
    status, appts_a = make_request(f"{BASE_URL}/api/appointments", method="GET", headers=headers_a)
    assert status == 200 and len(appts_a) == 1, "Patient A should have 1 appointment"

    status, upcoming_a = make_request(f"{BASE_URL}/api/appointments/upcoming", method="GET", headers=headers_a)
    assert status == 200 and upcoming_a is not None and upcoming_a["id"] == appt_id_a, "Upcoming appointment mismatch"
    print("[PASS] Test 5 Passed: Patient appointments & upcoming endpoint verified.")

    print("\n--- Test 6: Multi-Tenant Patient Isolation & Unauthorized Access ---")
    # Patient B attempts to view Patient A's appointment
    status, _ = make_request(f"{BASE_URL}/api/appointments/{appt_id_a}", method="GET", headers=headers_b)
    assert status == 404, f"Patient B should be denied access to Patient A's appointment, got {status}"

    # Patient B attempts to cancel Patient A's appointment
    status, _ = make_request(f"{BASE_URL}/api/appointments/{appt_id_a}", method="DELETE", headers=headers_b)
    assert status == 404, f"Patient B should be denied cancelling Patient A's appointment, got {status}"

    status, appts_b = make_request(f"{BASE_URL}/api/appointments", method="GET", headers=headers_b)
    assert status == 200 and len(appts_b) == 0, "Patient B should have 0 appointments"
    print("[PASS] Test 6 Passed: Multi-tenant patient isolation strictly enforced.")

    print("\n--- Test 7: Cancel Appointment ---")
    status, _ = make_request(f"{BASE_URL}/api/appointments/{appt_id_a}", method="DELETE", headers=headers_a)
    assert status == 204, f"Expected 204 No Content, got {status}"

    status, appts_after_del = make_request(f"{BASE_URL}/api/appointments", method="GET", headers=headers_a)
    assert appts_after_del[0]["status"] == "Cancelled", "Status should now be Cancelled"
    print("[PASS] Test 7 Passed: Appointment cancelled successfully.")

    print("\n[SUCCESS] ALL PART 10 DOCTOR APPOINTMENT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
