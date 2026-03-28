"""Quick self-contained test of local_auth_store without server."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.local_auth_store import initialize, auth_user, auth_technician, register_technician

initialize()
print()

tests = [
    ("User phone",         "user", "1234567890",    "demo123"),
    ("User email",         "user", "user@demo.com", "demo123"),
    ("User wrong pw",      "user", "1234567890",    "wrongpw"),
    ("Tech Ravi",          "tech", "9876543210",    "Sevai@123"),
    ("Tech Murugan",       "tech", "9876543211",    "Sevai@123"),
    ("Tech Arjun Elec",    "tech", "9876543220",    "Sevai@123"),
    ("Tech Phone Doctor",  "tech", "9876543250",    "Sevai@123"),
]

print("--- Auth Tests ---")
for label, kind, ident, pw in tests:
    fn = auth_user if kind == "user" else auth_technician
    r = fn(ident, pw)
    status = f"OK  -> {r['name']}" if r else "FAIL"
    print(f"  {label:22s}: {status}")

print()
print("--- Register New Technician ---")
try:
    rec = register_technician("Yogi Tech", "9871234560", "Yogisd@2004", None, "Electrician")
    print(f"  Registered: {rec['name']} [{rec['phone']}]")
except ValueError as e:
    print(f"  Already exists (ok): {e}")

r = auth_technician("9871234560", "Yogisd@2004")
print(f"  Login test : {'OK -> ' + r['name'] if r else 'FAIL'}")

print()
print("ALL DONE")
