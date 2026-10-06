import os
import json
import urllib.request
import time
import sys
import datetime
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

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
            content_type = resp.headers.get("Content-Type", "")
            body_bytes = resp.read()
            if "application/pdf" in content_type:
                return resp.status, content_type, body_bytes
            body_str = body_bytes.decode("utf-8")
            try:
                parsed = json.loads(body_str) if body_str and body_str.strip() else {}
            except Exception:
                parsed = {"raw": body_str}
            return resp.status, content_type, parsed
    except urllib.error.HTTPError as e:
        content_type = e.headers.get("Content-Type", "")
        body_bytes = e.read()
        body_str = body_bytes.decode("utf-8")
        try:
            parsed = json.loads(body_str) if body_str and body_str.strip() else {"detail": str(e)}
        except Exception:
            parsed = {"detail": str(e), "raw": body_str}
        return e.code, content_type, parsed

def register_and_login_patient(prefix):
    ts = int(time.time() * 1000)
    email = f"{prefix}.{ts}@example.com"
    pwd = "Password123"
    
    reg_data = {
        "full_name": f"{prefix.capitalize()} Patient",
        "email": email,
        "phone": "+1999888777",
        "password": pwd,
        "confirm_password": pwd,
        "age": 35,
        "gender": "Male"
    }
    status, _, res_reg = make_request(f"{BASE_URL}/api/auth/register", method="POST", data=reg_data)
    assert status == 201, f"Failed to register patient {email}: {res_reg}"
    
    login_data = {"email": email, "password": pwd}
    status, _, res_log = make_request(f"{BASE_URL}/api/auth/login", method="POST", data=login_data)
    assert status == 200 and "access_token" in res_log, f"Failed to login {email}: {res_log}"
    return email, pwd, res_log["access_token"]

def login_admin():
    login_data = {"email": "admin@example.com", "password": "AdminPass123"}
    status, _, res_log = make_request(f"{BASE_URL}/api/auth/login", method="POST", data=login_data)
    assert status == 200 and "access_token" in res_log, f"Failed to login admin: {res_log}"
    return res_log["access_token"]

def run_integration_tests():
    print("==================================================================")
    print("AI-POWERED SMART HEALTHCARE ASSISTANT — PART 13 FULL SYSTEM INTEGRATION TEST")
    print("==================================================================")

    # 1. Auth Setup: Patient A, Patient B, Admin
    print("\n[1/12] Registering & Authenticating Users...")
    email_a, pwd_a, token_a = register_and_login_patient("patientA")
    email_b, pwd_b, token_b = register_and_login_patient("patientB")
    token_admin = login_admin()
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    print("[PASS] Authenticated Patient A, Patient B, and Admin User.")

    # 2. Part 3 — BMI Calculator Module
    print("\n[2/12] Testing Part 3 — BMI Calculator...")
    bmi_payload = {"height": 178, "height_unit": "cm", "weight": 76, "weight_unit": "kg"}
    status, _, bmi_res = make_request(f"{BASE_URL}/api/bmi/calculate", method="POST", data=bmi_payload, headers=headers_a)
    assert status in (200, 201) and ("bmi" in bmi_res or "bmi_value" in bmi_res), f"BMI calculation failed: {bmi_res}"
    bmi_val = bmi_res.get("bmi") or bmi_res.get("bmi_value")
    bmi_cat = bmi_res.get("category") or bmi_res.get("bmi_category")
    print(f"   - Patient A BMI: {bmi_val} ({bmi_cat})")

    # 3. Part 4 — Diabetes ML Prediction
    print("\n[3/12] Testing Part 4 — Diabetes ML Prediction...")
    diab_payload = {
        "pregnancies": 2, "glucose": 135, "blood_pressure": 75,
        "skin_thickness": 22, "insulin": 90, "bmi": 24.0,
        "diabetes_pedigree_function": 0.52, "age": 35
    }
    status, _, diab_res = make_request(f"{BASE_URL}/api/predictions/diabetes", method="POST", data=diab_payload, headers=headers_a)
    assert status in (200, 201) and "prediction" in diab_res, f"Diabetes prediction failed: {diab_res}"
    print(f"   - Patient A Diabetes Outcome: {diab_res['risk']} (Prob: {diab_res['probability']*100:.1f}%)")

    # 4. Part 5 — Disease ML Prediction
    print("\n[4/12] Testing Part 5 — Disease ML Prediction...")
    dis_payload = {"symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"]}
    status, _, dis_res = make_request(f"{BASE_URL}/api/predictions/disease", method="POST", data=dis_payload, headers=headers_a)
    assert status in (200, 201) and "predicted_disease" in dis_res, f"Disease prediction failed: {dis_res}"
    print(f"   - Patient A Predicted Disease: {dis_res['predicted_disease']} (Prob: {dis_res['probability']*100:.1f}%)")

    # 5. Part 6 — Health Risk Score
    print("\n[5/12] Testing Part 6 — Health Risk Score...")
    status, _, risk_res = make_request(f"{BASE_URL}/api/health-risk/calculate", method="POST", headers=headers_a)
    assert status in (200, 201) and "score" in risk_res, f"Health risk calculation failed: {risk_res}"
    print(f"   - Patient A Composite Health Risk Score: {risk_res['score']}/100 ({risk_res['category']})")

    # 6. Part 7 — Diet Recommendation
    print("\n[6/12] Testing Part 7 — Diet Recommendation...")
    diet_payload = {"dietary_preference": "Vegetarian", "goal": "General Healthy Eating", "allergies": "Peanuts"}
    status, _, diet_res = make_request(f"{BASE_URL}/api/recommendations/diet", method="POST", data=diet_payload, headers=headers_a)
    assert status in (200, 201) and "recommendations" in diet_res, f"Diet recommendation failed: {diet_res}"
    print(f"   - Patient A Diet Guidance Generated.")

    # 7. Part 8 — Exercise Recommendation
    print("\n[7/12] Testing Part 8 — Exercise Recommendation...")
    ex_payload = {"fitness_level": "Beginner", "goal": "General Fitness"}
    status, _, ex_res = make_request(f"{BASE_URL}/api/recommendations/exercise", method="POST", data=ex_payload, headers=headers_a)
    assert status in (200, 201) and "recommendations" in ex_res, f"Exercise recommendation failed: {ex_res}"
    print(f"   - Patient A Exercise Guidance Generated.")

    # 8. Part 9 — Medicine Reminder
    print("\n[8/12] Testing Part 9 — Medicine Reminder...")
    med_payload = {
        "medicine_name": "Metformin", "dosage": "500 mg", "frequency": "Daily",
        "start_date": "2026-08-01", "end_date": "2026-08-30", "reminder_time": "08:00 AM"
    }
    status, _, med_res = make_request(f"{BASE_URL}/api/medicines", method="POST", data=med_payload, headers=headers_a)
    assert status in (200, 201) and "id" in med_res, f"Medicine creation failed: {med_res}"
    print(f"   - Medicine Reminder Created (ID: {med_res['id']})")

    # 9. Part 10 — Doctor Appointment
    print("\n[9/12] Testing Part 10 — Doctor Appointment...")
    future_date = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    appt_payload = {
        "doctor_id": 1, "appointment_date": future_date,
        "appointment_time": "10:00 AM", "reason": "General Checkup"
    }
    status, _, appt_res = make_request(f"{BASE_URL}/api/appointments", method="POST", data=appt_payload, headers=headers_a)
    assert status in (200, 201) and "id" in appt_res, f"Appointment booking failed: {appt_res}"
    print(f"   - Appointment Booked with Doctor #1.")

    # 10. Part 11 — Health Report PDF
    print("\n[10/12] Testing Part 11 — Health Report PDF Generation...")
    status, c_type, pdf_bytes = make_request(f"{BASE_URL}/api/reports/health", method="GET", headers=headers_a)
    assert status == 200 and "application/pdf" in c_type and pdf_bytes.startswith(b"%PDF-"), "PDF report failed"
    print(f"   - Health PDF Generated ({len(pdf_bytes)} bytes, %PDF- verified).")

    # 11. Part 12 — Admin Dashboard & Security RBAC
    print("\n[11/12] Testing Part 12 — Admin Dashboard & Security RBAC...")
    # Patient B attempts admin endpoint -> 403 Forbidden
    status, _, res_b_admin = make_request(f"{BASE_URL}/api/admin/dashboard", method="GET", headers=headers_b)
    assert status == 403, f"Patient should be denied admin endpoint (403), got {status}"
    print("   - RBAC Security Verified: Patient B denied admin endpoint (403 Forbidden).")
    
    # Admin calls admin endpoint -> 200 OK
    status, _, admin_stats = make_request(f"{BASE_URL}/api/admin/dashboard", method="GET", headers=headers_admin)
    assert status == 200 and "total_patients" in admin_stats, f"Admin dashboard stats failed: {admin_stats}"
    print(f"   - Admin Dashboard Metrics: {admin_stats}")

    # 12. MULTI-TENANT PATIENT DATA ISOLATION TEST (Item 17)
    print("\n[12/12] Testing Multi-Tenant Patient Data Isolation (Patient A vs Patient B)...")
    # Patient B fetches latest BMI -> Should receive 404 or empty because B has not calculated BMI
    status, _, b_bmi = make_request(f"{BASE_URL}/api/bmi/latest", method="GET", headers=headers_b)
    assert status in (404, 200) and (status == 404 or not b_bmi), f"Patient B should NOT see Patient A's BMI!"
    
    # Patient B fetches medicine reminders -> Should be empty list
    status, _, b_meds = make_request(f"{BASE_URL}/api/medicines", method="GET", headers=headers_b)
    assert status == 200 and len(b_meds) == 0, f"Patient B should NOT see Patient A's medicines! Got {b_meds}"

    # Patient B fetches appointments -> Should be empty list
    status, _, b_appts = make_request(f"{BASE_URL}/api/appointments", method="GET", headers=headers_b)
    assert status == 200 and len(b_appts) == 0, f"Patient B should NOT see Patient A's appointments! Got {b_appts}"
    print("[PASS] Patient Data Isolation Verified: Patient B cannot access Patient A's records!")

    print("\n==================================================================")
    print("ALL PART 13 FULL SYSTEM INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================================")

if __name__ == "__main__":
    run_integration_tests()
