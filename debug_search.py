#!/usr/bin/env python
"""Debug search - check what technicians exist and have locations"""
import requests
import json

BASE_URL = "http://localhost:8000"
ADMIN_CREDS = {
    "mobile": "9999999999",
    "aadhaar": "123456789012",
    "password": "admin123"
}

# Login as admin
login_response = requests.post(f"{BASE_URL}/auth/login/admin", json=ADMIN_CREDS)
token = login_response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# Get all technicians
print("=" * 70)
print("All Technicians in Database:")
print("=" * 70)

techs_response = requests.get(f"{BASE_URL}/admin/technicians", headers=headers)
techs = techs_response.json()

print(f"Total: {len(techs)}\n")

# Group by service category
categories = {}
for t in techs:
    cat = t.get("service_category", "Unknown")
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(t)

# Print by category
for cat in sorted(categories.keys()):
    print(f"\n{cat} ({len(categories[cat])} technicians):")
    for t in categories[cat]:
        print(f"  • {t['name']} - Phone: {t['phone']}, City: {t['city']}, Verified: {t['is_verified']}")

# Now test search
print("\n" + "=" * 70)
print("Search Test - Electricians in Bangalore:")
print("=" * 70)

search_response = requests.get(
    f"{BASE_URL}/technicians/nearby",
    params={
        "latitude": 12.9698,
        "longitude": 77.7499,
        "service_category": "Electrician",
        "radius_km": 100
    }
)

search_data = search_response.json()
print(f"\nSearch Results: {search_data['total_found']} technicians found")
print(f"Search Radius: {search_data['search_radius_km']} km")

if search_data['technicians']:
    print("\nTechnicians found:")
    for t in search_data['technicians']:
        print(f"  • {t.get('name', 'Unknown')} - {t.get('service_category', 'Unknown')}, City: {t.get('city', 'Unknown')}")
else:
    print("\nNo technicians found in search")
    print("\nNote: Technicians must have:")
    print("  1. is_available = true")
    print("  2. service_category = requested category")
    print("  3. location coordinates (latitude/longitude)")
    print("  4. Be within the search radius")
