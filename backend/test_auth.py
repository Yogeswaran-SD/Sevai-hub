"""Quick live API test for Sevai Hub auth endpoints."""
import urllib.request, urllib.error, json

def post(url, body):
    data = json.dumps(body).encode()
    req  = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read())
        except Exception:
            err = {"detail": str(e)}
        return None, f"HTTP {e.code}: {err.get('detail', err)}"
    except Exception as e:
        return None, str(e)

BASE = "http://localhost:8000"

print("=== DEMO LOGIN TESTS ===")
tests = [
    ("User demo phone",   "user",       {"identifier": "1234567890",    "password": "demo123"}),
    ("User demo email",   "user",       {"identifier": "user@demo.com", "password": "demo123"}),
    ("Tech Ravi",         "technician", {"identifier": "9876543210",    "password": "Sevai@123"}),
    ("Tech Murugan",      "technician", {"identifier": "9876543211",    "password": "Sevai@123"}),
    ("Tech Arjun Elec",   "technician", {"identifier": "9876543220",    "password": "Sevai@123"}),
    ("Safe Gas",          "technician", {"identifier": "9876543230",    "password": "Sevai@123"}),
    ("Phone Doctor",      "technician", {"identifier": "9876543250",    "password": "Sevai@123"}),
]

all_ok = True
for label, role, body in tests:
    r, err = post(f"{BASE}/auth/login/{role}", body)
    if r:
        print(f"  OK   {label}: {r['user']['name']} [{r['user']['role']}]")
    else:
        print(f"  FAIL {label}: {err}")
        all_ok = False

print()
print("=== ADMIN LOGIN TEST ===")
r, err = post(f"{BASE}/auth/login/admin",
              {"mobile": "9999999999", "aadhaar": "123456789012", "password": "Admin@SevaiHub2024"})
if r:
    print(f"  OK   Admin: {r['user']['name']} [{r['user']['role']}]")
else:
    print(f"  FAIL Admin: {err}")
    all_ok = False

print()
print("=== REGISTER NEW USER ===")
r, err = post(f"{BASE}/auth/register",
              {"name": "Live TestUser", "phone": "9001234567", "password": "Live@1234", "email": "live@test.com"})
if r:
    print(f"  OK   Registered: {r['name']} [{r['role']}]")
else:
    print(f"  Note: {err}")

print()
print("=== LOGIN WITH NEW USER ===")
r, err = post(f"{BASE}/auth/login/user", {"identifier": "9001234567", "password": "Live@1234"})
if r:
    print(f"  OK   New user login: {r['user']['name']} [{r['user']['role']}]")
else:
    print(f"  FAIL: {err}")
    all_ok = False

print()
print("=== RESULT:", "ALL PASS" if all_ok else "SOME FAILURES - check above ===")
