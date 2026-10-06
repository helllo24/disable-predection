import urllib.request

def test_cors_preflight():
    url = "http://127.0.0.1:8000/api/auth/register"
    req = urllib.request.Request(
        url,
        headers={
            "Origin": "http://localhost:5174",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"
        },
        method="OPTIONS"
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Preflight Status: {resp.status}")
            allow_origin = resp.headers.get("Access-Control-Allow-Origin")
            print(f"Access-Control-Allow-Origin Header: {allow_origin}")
            assert resp.status == 200 and allow_origin in ["http://localhost:5174", "*"]
            print("[SUCCESS] CORS Preflight for http://localhost:5174 passed cleanly!")
    except Exception as e:
        print(f"[ERROR] Preflight failed: {e}")

if __name__ == "__main__":
    test_cors_preflight()
