#!/usr/bin/env python
"""Debug search - check database directly"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test a simple API call to list all technicians with their location status
print("=" * 70)
print("Checking Backend Technician Data:")
print("=" * 70)

# Get admin token
admin_creds = {
    "mobile": "9999999999",
    "aadhaar": "123456789012",
    "password": "admin123"
}

login_response = requests.post(f"{BASE_URL}/auth/login/admin", json=admin_creds)
token = login_response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# Get all technicians from admin
techs_response = requests.get(f"{BASE_URL}/admin/technicians", headers=headers)
techs = techs_response.json()

print(f"\nTotal Technicians in DB: {len(techs)}\n")

# Count by category
categories = {}
for t in techs:
    cat = t.get("service_category", "Unknown")
    if cat not in categories:
        categories[cat] = {"total": 0, "available": 0, "verified": 0}
    categories[cat]["total"] += 1
    if t.get("is_available"):
        categories[cat]["available"] += 1
    if t.get("is_verified"):
        categories[cat]["verified"] += 1

print("Technicians by Category:")
for cat in sorted(categories.keys()):
    stats = categories[cat]
    print(f"  {cat}: {stats['total']} total, {stats['available']} available, {stats['verified']} verified")

# Now test search with wider radius
print("\n" + "=" * 70)
print("Search Tests:")
print("=" * 70)

# Test 1: Search for Plumber in Chennai (where most technicians are)
print("\nTest 1: Search for Plumbers (radius 100 km)")
search1 = requests.get(f"{BASE_URL}/technicians/nearby", params={
    "latitude": 13.0827,
    "longitude": 80.2707,
    "service_category": "Plumber",
    "radius_km": 100
})
print(f"  Results: {search1.json()['total_found']} technicians")

# Test 2: Try Electrician
print("\nTest 2: Search for Electricians (radius 100 km)")
search2 = requests.get(f"{BASE_URL}/technicians/nearby", params={
    "latitude": 13.0827,
    "longitude": 80.2707,
    "service_category": "Electrician",
    "radius_km": 100
})
print(f"  Results: {search2.json()['total_found']} technicians")

# Test 3: Try any category with huge radius
print("\nTest 3: Search any category in radius 500 km")
search3 = requests.get(f"{BASE_URL}/technicians/nearby", params={
    "latitude": 13.0827,
    "longitude": 80.2707,
    "service_category": "Plumber",
    "radius_km": 500
})
print(f"  Results: {search3.json()['total_found']} technicians")

print("\n" + "=" * 70)
print("Summary:")
print("=" * 70)
if all(s.json()['total_found'] == 0 for s in [search1, search2, search3]):
    print("❌ NO TECHNICIANS FOUND IN ANY SEARCH")
    print("   Possible causes:")
    print("   1. Location data not saved in PostGIS")
    print("   2. PostGIS queries failing silently")
    print("   3. Service category mismatch")
else:
    print("✅ Search is working!")
