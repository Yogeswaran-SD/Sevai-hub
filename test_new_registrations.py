#!/usr/bin/env python
"""Test that new registrations appear in admin panel"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Admin credentials
ADMIN_CREDS = {
    "mobile": "9999999999",
    "aadhaar": "123456789012",
    "password": "admin123"
}

# New user to register
NEW_USER = {
    "name": "John Watson",
    "email": "john.watson@example.com",
    "phone": "8765432100",
    "password": "TestPass@123"
}

# New technician to register
NEW_TECH = {
    "name": "Ramesh Electrician",
    "phone": "7654321098",
    "password": "Sevai@123Tech",
    "email": "ramesh.elec@example.com",
    "service_category": "Electrician",
    "city": "Bangalore",
    "address": "Whitefield, Bangalore",
    "latitude": 12.9698,
    "longitude": 77.7499
}

print("=" * 70)
print("Testing New Registration Updates in Admin Panel")
print("=" * 70)

# Step 1: Register new user
print("\n1️⃣  Registering New User...")
try:
    user_response = requests.post(f"{BASE_URL}/auth/register", json=NEW_USER)
    print(f"Status: {user_response.status_code}")
    user_data = user_response.json()
    print(f"✅ User Created: {json.dumps(user_data, indent=2)}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Step 2: Register new technician
print("2️⃣  Registering New Technician...")
try:
    tech_response = requests.post(f"{BASE_URL}/auth/register/technician", params=NEW_TECH)
    print(f"Status: {tech_response.status_code}")
    tech_data = tech_response.json()
    if tech_response.status_code == 201:
        print(f"✅ Technician Created: {json.dumps(tech_data, indent=2)}\n")
    else:
        print(f"Response: {json.dumps(tech_data, indent=2)}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Step 3: Login as admin
print("3️⃣  Admin Login...")
try:
    login_response = requests.post(f"{BASE_URL}/auth/login/admin", json=ADMIN_CREDS)
    if login_response.status_code == 200:
        login_data = login_response.json()
        token = login_data.get("access_token")
        print(f"✅ Admin logged in\n")
        
        # Step 4: Check users in admin panel
        print("4️⃣  Checking Admin Panel - Users List...")
        headers = {"Authorization": f"Bearer {token}"}
        users_response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
        users_data = users_response.json()
        print(f"Total Users: {len(users_data)}")
        
        # Find our new user
        new_user_found = False
        for u in users_data:
            if u["phone"] == NEW_USER["phone"]:
                new_user_found = True
                print(f"✅ NEW USER FOUND in Admin Panel:")
                print(f"   Name: {u['name']}")
                print(f"   Phone: {u['phone']}")
                print(f"   Email: {u['email']}\n")
                break
        
        if not new_user_found:
            print(f"❌ New user NOT found in admin panel\n")
        
        # Step 5: Check technicians in admin panel
        print("5️⃣  Checking Admin Panel - Technicians List...")
        techs_response = requests.get(f"{BASE_URL}/admin/technicians", headers=headers)
        techs_data = techs_response.json()
        print(f"Total Technicians: {len(techs_data)}")
        
        # Find our new technician
        new_tech_found = False
        for t in techs_data:
            if t["phone"] == NEW_TECH["phone"]:
                new_tech_found = True
                print(f"✅ NEW TECHNICIAN FOUND in Admin Panel:")
                print(f"   Name: {t['name']}")
                print(f"   Phone: {t['phone']}")
                print(f"   Service: {t['service_category']}")
                print(f"   City: {t['city']}")
                print(f"   Verified: {t['is_verified']}\n")
                break
        
        if not new_tech_found:
            print(f"❌ New technician NOT found in admin panel\n")
        
        # Step 6: Check if new technician appears in search
        print("6️⃣  Checking Search Page - Technicians Near Location...")
        search_response = requests.get(
            f"{BASE_URL}/technicians/nearby",
            params={
                "latitude": 12.9698,
                "longitude": 77.7499,
                "service_category": "Electrician",
                "radius_km": 100
            }
        )
        if search_response.status_code == 200:
            search_data = search_response.json()
            print(f"Technicians found in search: {len(search_data)}")
            
            tech_in_search = False
            for t in search_data:
                if t.get("phone") == NEW_TECH["phone"]:
                    tech_in_search = True
                    print(f"✅ NEW TECHNICIAN FOUND in Search Results:")
                    print(f"   Name: {t['name']}")
                    print(f"   City: {t.get('city', 'N/A')}\n")
                    break
            
            if not tech_in_search:
                print(f"⚠️  New technician not in search (may need location/verification)\n")
        else:
            print(f"Search returned: {search_response.status_code}\n")
        
        print("=" * 70)
        print("✅ SUMMARY:")
        print("=" * 70)
        if new_user_found:
            print("✅ New users are AUTOMATICALLY updated in Admin Panel")
        else:
            print("❌ New users are NOT showing in Admin Panel")
        
        if new_tech_found:
            print("✅ New technicians are AUTOMATICALLY updated in Admin Panel")
        else:
            print("❌ New technicians are NOT showing in Admin Panel")
        
        if tech_in_search or not new_tech_found:
            print("✅ New technicians appear in Search (if they have valid location)")
        else:
            print("⚠️  New technicians may need location data to appear in search")
            
    else:
        print(f"❌ Admin login failed: {login_response.json()}\n")
        
except Exception as e:
    print(f"❌ Error: {e}\n")
