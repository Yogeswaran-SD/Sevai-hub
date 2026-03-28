"""
generate_auth_store.py
======================
One-time script: pre-generates local_auth.json with bcrypt-hashed
demo credentials so the server never has to hash at request time.

Run once: python generate_auth_store.py
"""
import sys, os, json, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bcrypt
from pathlib import Path

OUT = Path(__file__).parent / "local_auth.json"

def h(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt(rounds=10)).decode()

print("Generating bcrypt hashes (this takes ~10 seconds)...")

DEMO_PW  = "demo123"
TECH_PW  = "Sevai@123"

demo_hash = h(DEMO_PW);  print(f"  hashed demo123")
tech_hash = h(TECH_PW);  print(f"  hashed Sevai@123")

store = {
    "users": {
        "1234567890":   {"id":"demo-user-001","name":"Demo User",         "email":"user@demo.com","phone":"1234567890","hpw":demo_hash,"role":"user","is_active":True},
        "user@demo.com":{"id":"demo-user-001","name":"Demo User",         "email":"user@demo.com","phone":"1234567890","hpw":demo_hash,"role":"user","is_active":True},
    },
    "technicians": {
        "9876543210": {"id":"demo-tech-001","name":"Ravi Kumar",         "email":"ravi@demo.com","phone":"9876543210","hpw":tech_hash,"role":"technician"},
        "9876543211": {"id":"demo-tech-002","name":"Murugan S",          "email":None,           "phone":"9876543211","hpw":tech_hash,"role":"technician"},
        "9876543220": {"id":"demo-tech-003","name":"Arjun Electricals",  "email":None,           "phone":"9876543220","hpw":tech_hash,"role":"technician"},
        "9876543230": {"id":"demo-tech-004","name":"Safe Gas Service",   "email":None,           "phone":"9876543230","hpw":tech_hash,"role":"technician"},
        "9876543240": {"id":"demo-tech-005","name":"Speed Bike Works",   "email":None,           "phone":"9876543240","hpw":tech_hash,"role":"technician"},
        "9876543250": {"id":"demo-tech-006","name":"Phone Doctor",        "email":None,           "phone":"9876543250","hpw":tech_hash,"role":"technician"},
        "9876543260": {"id":"demo-tech-007","name":"CleanHome TN",        "email":None,           "phone":"9876543260","hpw":tech_hash,"role":"technician"},
        "9876543270": {"id":"demo-tech-008","name":"Cool Air Services",   "email":None,           "phone":"9876543270","hpw":tech_hash,"role":"technician"},
        "9876543280": {"id":"demo-tech-009","name":"Kumar Carpentry",     "email":None,           "phone":"9876543280","hpw":tech_hash,"role":"technician"},
        "9876543290": {"id":"demo-tech-010","name":"ColorCraft TN",       "email":None,           "phone":"9876543290","hpw":tech_hash,"role":"technician"},
        "ravi@demo.com":{"id":"demo-tech-001","name":"Ravi Kumar",        "email":"ravi@demo.com","phone":"9876543210","hpw":tech_hash,"role":"technician"},
    }
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(store, f, indent=2, ensure_ascii=False)

print(f"\nSaved to: {OUT}")
print(f"  {len(store['users'])} user entries")
print(f"  {len(store['technicians'])} technician entries")
print()
print("=== Verify all logins ===")
for key, rec in list(store["users"].items())[:2]:
    ok = bcrypt.checkpw(DEMO_PW.encode(), rec["hpw"].encode())
    print(f"  user [{key}] => {'OK' if ok else 'FAIL'}")
for key, rec in list(store["technicians"].items())[:3]:
    ok = bcrypt.checkpw(TECH_PW.encode(), rec["hpw"].encode())
    print(f"  tech [{key}] => {'OK' if ok else 'FAIL'}")
print()
print("Done! Now restart uvicorn.")
