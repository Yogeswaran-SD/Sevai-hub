#!/usr/bin/env python3
# Sevai Hub - Quick Functional Test

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8080"

print("="*70)
print("SEVAI HUB - DEPLOYMENT VERIFICATION TEST")
print("="*70)
print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Track results
results = {"PASS": 0, "FAIL": 0, "WARN": 0}

# ============================================================================
# 1. HEALTH CHECKS
# ============================================================================
print("1. SYSTEM HEALTH CHECKS")
print("-" * 70)

try:
    resp = requests.get(f"{BASE_URL}/health", timeout=5)
    if resp.status_code == 200 and resp.json().get("status") == "healthy":
        print("[PASS] Backend API Health............................ OK")
        results["PASS"] += 1
    else:
        print("[FAIL] Backend API Health............................ UNHEALTHY")
        results["FAIL"] += 1
except Exception as e:
    print(f"[FAIL] Backend API Health............................ ERROR ({str(e)[:30]})")
    results["FAIL"] += 1

try:
    resp = requests.get(FRONTEND_URL, timeout=5)
    if resp.status_code == 200:
        print("[PASS] Frontend Web Server........................... OK")
        results["PASS"] += 1
    else:
        print("[FAIL] Frontend Web Server........................... ERROR")
        results["FAIL"] += 1
except Exception as e:
    print(f"[FAIL] Frontend Web Server........................... OFFLINE")
    results["FAIL"] += 1

try:
    resp = requests.get(f"{BASE_URL}/docs", timeout=5)
    if resp.status_code == 200:
        print("[PASS] API Documentation (Swagger)................... OK")
        results["PASS"] += 1
    else:
        print("[FAIL] API Documentation (Swagger)................... ERROR")
        results["FAIL"] += 1
except Exception as e:
    print(f"[FAIL] API Documentation............................ UNAVAILABLE")
    results["FAIL"] += 1

print()

# ============================================================================
# 2. AUTHENTICATION 
# ============================================================================
print("2. AUTHENTICATION TESTS")
print("-" * 70)

tokens = {}

# User Login
try:
    data = {"identifier": "1234567890", "password": "demo123"}
    resp = requests.post(f"{BASE_URL}/auth/login/user", json=data, timeout=5)
    if resp.status_code == 200:
        rdata = resp.json()
        tokens["user"] = rdata.get("access_token")
        print("[PASS] User Login...................................... OK")
        print(f"       User: {rdata.get('user', {}).get('name')}")
        results["PASS"] += 1
    else:
        print(f"[FAIL] User Login...................................... ERROR ({resp.status_code})")
        results["FAIL"] += 1
except Exception as e:
    print(f"[FAIL] User Login...................................... ERROR")
    results["FAIL"] += 1

# Technician Login
try:
    data = {"identifier": "9876543210", "password": "Sevai@123"}
    resp = requests.post(f"{BASE_URL}/auth/login/technician", json=data, timeout=5)
    if resp.status_code == 200:
        rdata = resp.json()
        tokens["tech"] = rdata.get("access_token")
        print("[PASS] Technician Login................................ OK")
        print(f"       Tech: {rdata.get('user', {}).get('name')}")
        results["PASS"] += 1
    else:
        print(f"[FAIL] Technician Login................................ ERROR ({resp.status_code})")
        results["FAIL"] += 1
except Exception as e:
    print(f"[FAIL] Technician Login................................ ERROR")
    results["FAIL"] += 1

# Admin Login
try:
    data = {"mobile": "9999999999", "aadhaar": "123456789012", "password": "admin123"}
    resp = requests.post(f"{BASE_URL}/auth/login/admin", json=data, timeout=5)
    if resp.status_code == 200:
        rdata = resp.json()
        tokens["admin"] = rdata.get("access_token")
        print("[PASS] Admin Login...................................... OK")
        print(f"       Admin: {rdata.get('user', {}).get('name')}")
        results["PASS"] += 1
    else:
        print(f"[FAIL] Admin Login...................................... ERROR ({resp.status_code})")
        results["FAIL"] += 1
except Exception as e:
    print(f"[FAIL] Admin Login...................................... ERROR")
    results["FAIL"] += 1

print()

# ============================================================================
# 3. CORE FEATURES
# ============================================================================
print("3. CORE API FEATURES")
print("-" * 70)

# Search Technicians
try:
    params = {
        "latitude": 13.0827,
        "longitude": 80.2707,
        "service_category": "Plumber",
        "radius_km": 5
    }
    resp = requests.get(f"{BASE_URL}/technicians/nearby", params=params, timeout=10)
    if resp.status_code == 200:
        rdata = resp.json()
        found = rdata.get("total_found", 0)
        print(f"[PASS] Search Technicians (Geospatial)................ OK")
        print(f"       Found: {found} technicians")
        results["PASS"] += 1
    else:
        print(f"[FAIL] Search Technicians............................. ERROR ({resp.status_code})")
        results["FAIL"] += 1
except Exception as e:
    print(f"[FAIL] Search Technicians............................. ERROR")
    results["FAIL"] += 1

# Intelligence Dashboard
try:
    resp = requests.get(f"{BASE_URL}/intelligence/dashboard", timeout=5)
    if resp.status_code == 200:
        rdata = resp.json()
        total = rdata.get("platform_summary", {}).get("total_technicians", 0)
        print(f"[PASS] Intelligence Dashboard......................... OK")
        print(f"       Total Technicians: {total}")
        results["PASS"] += 1
    else:
        print(f"[FAIL] Intelligence Dashboard......................... ERROR")
        results["FAIL"] += 1
except Exception as e:
    print(f"[FAIL] Intelligence Dashboard......................... ERROR")
    results["FAIL"] += 1

# Services List
try:
    resp = requests.get(f"{BASE_URL}/services", timeout=5)
    if resp.status_code in [200, 307]:  # Allow redirect
        print("[PASS] Services Configuration.......................... OK")
        results["PASS"] += 1
    else:
        print(f"[FAIL] Services Configuration.......................... ERROR")
        results["FAIL"] += 1
except Exception as e:
    print(f"[FAIL] Services Configuration.......................... ERROR")
    results["FAIL"] += 1

# Emergency Scoring
try:
    resp = requests.get(f"{BASE_URL}/technicians/emergency/score", params={"query": "leak"}, timeout=5)
    if resp.status_code == 200:
        print("[PASS] Emergency Risk Scoring.......................... OK")
        results["PASS"] += 1
    else:
        print(f"[FAIL] Emergency Risk Scoring.......................... ERROR")
        results["FAIL"] += 1
except Exception as e:
    print(f"[FAIL] Emergency Risk Scoring.......................... ERROR")
    results["FAIL"] += 1

print()

# ============================================================================
# 4. PROTECTED FEATURES
# ============================================================================
print("4. PROTECTED FEATURES (Authenticated)")
print("-" * 70)

if tokens.get("user"):
    try:
        headers = {"Authorization": f"Bearer {tokens['user']}"}
        resp = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=5)
        if resp.status_code == 200:
            print("[PASS] Get Current User Profile....................... OK")
            results["PASS"] += 1
        else:
            print(f"[FAIL] Get Current User Profile....................... ERROR")
            results["FAIL"] += 1
    except Exception as e:
        print(f"[FAIL] Get Current User Profile....................... ERROR")
        results["FAIL"] += 1

if tokens.get("user"):
    try:
        headers = {"Authorization": f"Bearer {tokens['user']}"}
        resp = requests.get(f"{BASE_URL}/dashboard/user", headers=headers, timeout=5)
        if resp.status_code == 200:
            print("[PASS] User Dashboard.................................. OK")
            results["PASS"] += 1
        else:
            print(f"[FAIL] User Dashboard.................................. ERROR")
            results["FAIL"] += 1
    except Exception as e:
        print(f"[FAIL] User Dashboard.................................. ERROR")
        results["FAIL"] += 1

if tokens.get("tech"):
    try:
        headers = {"Authorization": f"Bearer {tokens['tech']}"}
        resp = requests.get(f"{BASE_URL}/dashboard/technician", headers=headers, timeout=5)
        if resp.status_code == 200:
            print("[PASS] Technician Dashboard........................... OK")
            results["PASS"] += 1
        else:
            print(f"[FAIL] Technician Dashboard........................... ERROR")
            results["FAIL"] += 1
    except Exception as e:
        print(f"[FAIL] Technician Dashboard........................... ERROR")
        results["FAIL"] += 1

if tokens.get("admin"):
    try:
        headers = {"Authorization": f"Bearer {tokens['admin']}"}
        resp = requests.get(f"{BASE_URL}/dashboard/admin", headers=headers, timeout=5)
        if resp.status_code == 200:
            print("[PASS] Admin Dashboard................................. OK")
            results["PASS"] += 1
        else:
            print(f"[FAIL] Admin Dashboard................................. ERROR")
            results["FAIL"] += 1
    except Exception as e:
        print(f"[FAIL] Admin Dashboard................................. ERROR")
        results["FAIL"] += 1

print()

# ============================================================================
# SUMMARY
# ============================================================================
total = results["PASS"] + results["FAIL"] + results["WARN"]
print("="*70)
print("DEPLOYMENT READINESS SUMMARY")
print("="*70)
print()

if results["FAIL"] == 0:
    print("[OK] ALL TESTS PASSED - READY FOR DEPLOYMENT")
    print()
    print("Status: ✓ PRODUCTION READY")
else:
    print(f"[WARNING] {results['FAIL']} test(s) failed")
    print()
    print("Status: ⚠ REVIEW REQUIRED")

print()
print(f"Results: {results['PASS']} PASS | {results['FAIL']} FAIL | {results['WARN']} WARN")
print()

print("Access URLs:")
print(f"  - Frontend:    {FRONTEND_URL}")
print(f"  - Backend API: {BASE_URL}")
print(f"  - API Docs:    {BASE_URL}/docs")
print(f"  - MinIO:       http://localhost:9001")
print()

print("Demo Credentials:")
print("  - User:        1234567890 / demo123")
print("  - Technician:  9876543210 / Sevai@123")
print("  - Admin:       9999999999:123456789012 / admin123")
print()
