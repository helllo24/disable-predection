import urllib.request
import json
import sqlite3
import subprocess
import time
import os

cwd = os.path.abspath('backend')
proc = subprocess.Popen([os.path.join(cwd, '.venv', 'Scripts', 'python.exe'), '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], cwd=cwd)
time.sleep(3)

try:
    url = 'http://127.0.0.1:8000/api/auth/register'
    payload = {
        'email': 'verifytest2026@gmail.com',
        'password': 'Password123!',
        'full_name': 'Verified Test User',
        'role': 'PATIENT',
        'age': 35,
        'gender': 'Female',
        'weight': 65.0,
        'height': 165.0
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        print('REGISTRATION API RESPONSE:', resp.status, resp.read().decode())
    
    # Check DB
    conn = sqlite3.connect('backend/smart_healthcare.db')
    cur = conn.cursor()
    cur.execute("SELECT id, email, full_name, role FROM users WHERE email='verifytest2026@gmail.com'")
    user_row = cur.fetchone()
    print('DB VERIFICATION ROW:', user_row)
    conn.close()
finally:
    proc.terminate()
