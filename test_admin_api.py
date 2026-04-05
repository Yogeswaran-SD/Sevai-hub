#!/usr/bin/env python
"""Test admin API endpoints"""
import requests
import json

BASE_URL = "http://localhost:8000"
ADMIN_CREDENTIALS = {
    "mobile": "9999999999",
    "aadhaar": "123456789012",
    "password": "admin123"
}

# Step 1: Login as admin
print("1. Testing admin login...")
try:
    login_response = requests.post(f"{BASE_URL}/auth/login/admin", json=ADMIN_CREDENTIALS)
    print(f"Status: {login_response.status_code}")
    login_data = login_response.json()
    print(f"Response: {json.dumps(login_data, indent=2)}")
    
    if login_response.status_code == 200:
        token = login_data.get("access_token")
        print(f"\n✅ Login successful! Token: {token[:50]}...\n")
        
        # Step 2: Test admin dashboard
        print("2. Testing /admin/dashboard...")
        headers = {"Authorization": f"Bearer {token}"}
        dashboard_response = requests.get(f"{BASE_URL}/admin/dashboard", headers=headers)
        print(f"Status: {dashboard_response.status_code}")
        print(f"Response: {json.dumps(dashboard_response.json(), indent=2)}\n")
        
        # Step 3: Test admin users
        print("3. Testing /admin/users...")
        users_response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
        print(f"Status: {users_response.status_code}")
        users_data = users_response.json()
        print(f"Response Length: {len(users_data) if isinstance(users_data, list) else 'Not a list'}")
        print(f"First few items: {json.dumps(users_data[:2] if isinstance(users_data, list) else users_data, indent=2)}\n")
        
        # Step 4: Test admin technicians
        print("4. Testing /admin/technicians...")
        techs_response = requests.get(f"{BASE_URL}/admin/technicians", headers=headers)
        print(f"Status: {techs_response.status_code}")
        techs_data = techs_response.json()
        print(f"Response Length: {len(techs_data) if isinstance(techs_data, list) else 'Not a list'}")
        print(f"First few items: {json.dumps(techs_data[:2] if isinstance(techs_data, list) else techs_data, indent=2)}")
    else:
        print("❌ Login failed!")
        
except Exception as e:
    print(f"Error: {e}")
