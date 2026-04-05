#!/usr/bin/env python
"""Test technician registration with location"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Register a new test technician
NEW_TECH = {
    "name": "TestPlumber456",
    "phone": "6666666666",
    "password": "Test@123",
    "email": "test456@example.com",
    "service_category": "Plumber",
    "city": "Chennai",
    "latitude": 13.0827,  # Chennai center
    "longitude": 80.2707
}

print("Registering new technician...")
response = requests.post(f"{BASE_URL}/auth/register/technician", params=NEW_TECH)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

if response.status_code == 201:
    # Now login as admin and check if the technician was registered
    ADMIN_CREDS = {
        "mobile": "9999999999",
        "aadhaar": "123456789012",
        "password": "admin123"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login/admin", json=ADMIN_CREDS)
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get the technician from admin panel
    print("Checking admin panel...")
    techs_response = requests.get(f"{BASE_URL}/admin/technicians", headers=headers)
    techs = techs_response.json()
    
    for t in techs:
        if t["phone"] == "6666666666":
            print(f"✅ Technician found in admin panel:")
            print(f"   Name: {t['name']}")
            print(f"   Phone: {t['phone']}")
            print(f"   Service: {t['service_category']}")
            print(f"   City: {t['city']}\n")
            break
    
    # Now test search for plumbers in Chennai
    print("Testing search for plumbers in Chennai...")
    search_response = requests.get(f"{BASE_URL}/technicians/nearby", params={
        "latitude": 13.0827,
        "longitude": 80.2707,
        "service_category": "Plumber",
        "radius_km": 10
    })
    
    search_data = search_response.json()
    print(f"Search returned: {search_data['total_found']} plumbers\n")
    
    if search_data['technicians']:
        print("Technicians found:")
        for t in search_data['technicians']:
            print(f"  • {t['name']} (Phone: {t.get('phone', 'N/A')})")
            
        # Check if our new technician is in the results
        new_tech_found = any(t['phone'] == '6666666666' for t in search_data['technicians'])
        if new_tech_found:
            print("\n✅ NEW TECHNICIAN FOUND IN SEARCH!")
        else:
            print("\n⚠️ New technician created but not in search results")
    else:
        print("❌ No technicians found in search")
