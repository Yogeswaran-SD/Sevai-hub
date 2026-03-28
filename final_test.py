#!/usr/bin/env python3
# Final Deployment Test - All Functions

import requests
import json
from datetime import datetime

BASE = "http://localhost:8000"
FRONTEND = "http://localhost:8080"

print("\n" + "="*75)
print("     SEVAI HUB - FINAL DEPLOYMENT & FUNCTION VERIFICATION TEST")
print("="*75)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

checks = []

def test(name, passed, details=""):
    status = "✓ PASS" if passed else "✗ FAIL"
    checks.append(passed)
    icon = "✓" if passed else "✗"
    print(f"  [{icon}] {name:<50} {status}")
    if details and not passed:
        print(f"      └─ {details}")

print("1. SYSTEM HEALTH")
print("-" * 75)

try:
    r = requests.get(f"{BASE}/health", timeout=5)
    test("Backend API Health Check", r.status_code == 200 and r.json().get("status") == "healthy")
except:
    test("Backend API Health Check", False, "API unreachable")

try:
    r = requests.get(FRONTEND, timeout=5)
    test("Frontend Web Server", r.status_code == 200)
except:
    test("Frontend Web Server", False, "Server unreachable")

try:
    r = requests.get(f"{BASE}/docs", timeout=5)
    test("API Documentation", r.status_code == 200)
except:
    test("API Documentation", False, "Swagger unavailable")

print("\n2. AUTHENTICATION")
print("-" * 75)

tokens = {}

try:
    r = requests.post(f"{BASE}/auth/login/user",
        json={"identifier": "1234567890", "password": "demo123"}, timeout=5)
    passed = r.status_code == 200
    tokens["user"] = r.json().get("access_token") if passed else None
    test("User Login", passed, f"HTTP {r.status_code}" if not passed else "")
except Exception as e:
    test("User Login", False, str(e)[:50])

try:
    r = requests.post(f"{BASE}/auth/login/technician",
        json={"identifier": "9876543210", "password": "Sevai@123"}, timeout=5)
    passed = r.status_code == 200
    tokens["tech"] = r.json().get("access_token") if passed else None
    test("Technician Login", passed, f"HTTP {r.status_code}" if not passed else "")
except Exception as e:
    test("Technician Login", False, str(e)[:50])

try:
    r = requests.post(f"{BASE}/auth/login/admin",
        json={"mobile": "9999999999", "aadhaar": "123456789012", "password": "admin123"}, timeout=5)
    passed = r.status_code == 200
    tokens["admin"] = r.json().get("access_token") if passed else None
    test("Admin Login", passed, f"HTTP {r.status_code}" if not passed else "")
except Exception as e:
    test("Admin Login", False, str(e)[:50])

print("\n3. CORE FEATURES")
print("-" * 75)

# Test Search with correct enum value
try:
    r = requests.get(f"{BASE}/technicians/nearby", params={
        "latitude": 13.0827,
        "longitude": 80.2707,
        "service_category": "Plumber",
        "radius_km": 5
    }, timeout=10)
    passed = r.status_code == 200
    details = ""
    if passed:
        found = r.json().get("total_found", 0)
        details = f"Found {found} technicians"
    test("Search Technicians (Geospatial Query)", passed, f"HTTP {r.status_code}: {r.text[:80]}" if not passed else details)
except Exception as e:
    test("Search Technicians (Geospatial Query)", False, str(e)[:50])

try:
    r = requests.get(f"{BASE}/intelligence/dashboard", timeout=5)
    passed = r.status_code == 200 and "platform_summary" in r.json()
    test("Intelligence Dashboard", passed)
except:
    test("Intelligence Dashboard", False)

try:
    r = requests.get(f"{BASE}/services", timeout=5)
    passed = r.status_code in [200, 307]  # Allow redirects
    test("Services Configuration", passed)
except:
    test("Services Configuration", False)

try:
    r = requests.get(f"{BASE}/technicians/emergency/score", params={"query": "leak"}, timeout=5)
    passed = r.status_code == 200
    test("Emergency Risk Scoring", passed)
except:
    test("Emergency Risk Scoring", False)

try:
    r = requests.get(f"{BASE}/technicians/tti/calculate", params={
        "cancellation_rate": 0.05,
        "response_delay_avg": 15,
        "rating_stability": 0.85,
        "availability_score": 0.9
    }, timeout=5)
    passed = r.status_code == 200
    test("Trust Index (TTI) Calculation", passed)
except:
    test("Trust Index (TTI) Calculation", False)

print("\n4. PROTECTED ROUTES (Authentication Required)")
print("-" * 75)

if tokens.get("user"):
    try:
        r = requests.get(f"{BASE}/auth/me",
            headers={"Authorization": f"Bearer {tokens['user']}"}, timeout=5)
        test("Get Current User Info", r.status_code == 200)
    except:
        test("Get Current User Info", False)

    try:
        r = requests.get(f"{BASE}/dashboard/user",
            headers={"Authorization": f"Bearer {tokens['user']}"}, timeout=5)
        test("User Dashboard", r.status_code == 200)
    except:
        test("User Dashboard", False)

if tokens.get("tech"):
    try:
        r = requests.get(f"{BASE}/dashboard/technician",
            headers={"Authorization": f"Bearer {tokens['tech']}"}, timeout=5)
        passed = r.status_code == 200
        test("Technician Dashboard", passed, f"HTTP {r.status_code}" if not passed else "")
    except:
        test("Technician Dashboard", False)

if tokens.get("admin"):
    try:
        r = requests.get(f"{BASE}/dashboard/admin",
            headers={"Authorization": f"Bearer {tokens['admin']}"}, timeout=5)
        passed = r.status_code == 200
        test("Admin Dashboard", passed, f"HTTP {r.status_code}" if not passed else "")
    except:
        test("Admin Dashboard", False)

print("\n5. FRONTEND PAGES")
print("-" * 75)

pages = [
    (f"{FRONTEND}", "Home Page"),
    (f"{FRONTEND}/login", "Login Page"),
    (f"{FRONTEND}/search", "Search Page"),
]

for url, name in pages:
    try:
        r = requests.get(url, timeout=5)
        test(name, r.status_code == 200)
    except:
        test(name, False)

print("\n" + "="*75)
print("FINAL REPORT")
print("="*75)

passed = sum(checks)
failed = len(checks) - passed
total = len(checks)

print(f"\nResults: {passed}/{total} tests passed\n")

if failed == 0:
    print("Status: ✓✓✓ ALL SYSTEMS OPERATIONAL - READY FOR DEPLOYMENT ✓✓✓\n")
else:
    print(f"Status: ⚠ {failed} test(s) need review\n")

print("Quick Links:")
print(f"  - Frontend:    {FRONTEND}")
print(f"  - Backend API: {BASE}")
print(f"  - API Docs:    {BASE}/docs")
print(f"  - MinIO:       http://localhost:9001")

print("\nDemo Login Credentials:")
print("  - User Account:       1234567890 / demo123")
print("  - Technician Account: 9876543210 / Sevai@123")
print("  - Admin Account:      9999999999 (Aadhaar: 123456789012) / admin123")

print("\n" + "="*75 + "\n")
