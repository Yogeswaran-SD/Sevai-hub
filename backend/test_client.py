"""
Test auth via FastAPI TestClient — captures actual exception, no server needed.
"""
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient

print("Loading app...")
from app.main import app
print("App loaded OK\n")

client = TestClient(app, raise_server_exceptions=True)

TESTS = [
    ("User demo phone",   "POST", "/auth/login/user",       {"identifier": "1234567890",    "password": "demo123"}),
    ("User demo email",   "POST", "/auth/login/user",       {"identifier": "user@demo.com", "password": "demo123"}),
    ("Tech Ravi",         "POST", "/auth/login/technician", {"identifier": "9876543210",    "password": "Sevai@123"}),
    ("Tech Murugan",      "POST", "/auth/login/technician", {"identifier": "9876543211",    "password": "Sevai@123"}),
    ("Admin",             "POST", "/auth/login/admin",      {"mobile": "9999999999", "aadhaar": "123456789012", "password": "Admin@SevaiHub2024"}),
]

print("=== TestClient Login Tests ===")
for label, method, path, body in TESTS:
    try:
        r = client.post(path, json=body)
        if r.status_code == 200:
            d = r.json()
            print(f"  OK   {label}: {d['user']['name']} [{d['user']['role']}]")
        else:
            print(f"  FAIL {label}: HTTP {r.status_code} - {r.text[:200]}")
    except Exception as e:
        print(f"  EXCEPTION {label}:")
        traceback.print_exc()

print()
print("=== Register + Login ===")
try:
    r = client.post("/auth/register", json={"name": "TestUser", "phone": "9991111111", "password": "Test@1234"})
    print(f"  Register: HTTP {r.status_code} - {r.text[:200]}")
    if r.status_code == 201:
        r2 = client.post("/auth/login/user", json={"identifier": "9991111111", "password": "Test@1234"})
        d2 = r2.json()
        print(f"  Login: {d2.get('user', {}).get('name', r2.text)}")
except Exception as e:
    traceback.print_exc()

print("\nDone.")
