#!/usr/bin/env python3
"""
Test Script: Verify Technician Registration to Database
=========================================================

This script tests that newly registered technicians are saved to the database
and appear in the Admin Panel.

Usage:
    python test_technician_registration.py
"""

import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:8000"

def test_technician_registration():
    """Test that technician registration saves to database"""
    
    print("\n" + "=" * 70)
    print("TECHNICIAN REGISTRATION TEST")
    print("=" * 70)
    
    # Generate unique phone for testing
    test_phone = f"999{int(time.time()) % 9999999:07d}"
    test_email = f"test{int(time.time())}@example.com"
    
    payload = {
        "name": "Test Technician",
        "phone": test_phone,
        "email": test_email,
        "password": "TestPassword@123",
        "service_category": "Plumber",
        "city": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
    }
    
    print(f"\n1️⃣  Registering technician...")
    print(f"   Name: {payload['name']}")
    print(f"   Phone: {payload['phone']}")
    print(f"   Email: {payload['email']}")
    print(f"   Service: {payload['service_category']}")
    print(f"   Location: ({payload['latitude']}, {payload['longitude']})")
    
    try:
        # Register technician
        response = requests.post(
            f"{BASE_URL}/auth/register/technician",
            params=payload
        )
        
        print(f"\n   Response Status: {response.status_code}")
        print(f"   Message: {response.json().get('message', 'N/A')}")
        
        if response.status_code == 201:
            print("   ✅ Registration API returned 201 Created")
        else:
            print(f"   ❌ Registration returned {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        tech_id = response.json().get('id')
        print(f"   Technician ID: {tech_id}")
        
    except Exception as e:
        print(f"   ❌ Registration request failed: {str(e)}")
        return False
    
    # Wait a moment for database to process
    time.sleep(1)
    
    # Check if technician appears in database
    print(f"\n2️⃣  Checking if technician appears in database...")
    
    try:
        response = requests.get(f"{BASE_URL}/technicians/")
        
        if response.status_code != 200:
            print(f"   ❌ Failed to fetch technicians: {response.status_code}")
            return False
        
        techs = response.json()
        print(f"   Total technicians in DB: {len(techs)}")
        
        # Find our test technician
        found = False
        for tech in techs:
            if tech.get('phone') == test_phone:
                found = True
                print(f"   ✅ Found technician in database!")
                print(f"      ID: {tech.get('id')}")
                print(f"      Name: {tech.get('name')}")
                print(f"      Phone: {tech.get('phone')}")
                print(f"      Category: {tech.get('service_category')}")
                print(f"      Available: {tech.get('is_available')}")
                print(f"      Verified: {tech.get('is_verified')}")
                break
        
        if not found:
            print(f"   ❌ Technician NOT found in database!")
            print(f"   First few technicians:")
            for tech in techs[:3]:
                print(f"      - {tech.get('name')} ({tech.get('phone')})")
            return False
        
    except Exception as e:
        print(f"   ❌ Database check failed: {str(e)}")
        return False
    
    # Check if technician appears in search
    print(f"\n3️⃣  Checking if technician appears in service search...")
    
    try:
        search_params = {
            "latitude": 13.0827,
            "longitude": 80.2707,
            "service_category": "Plumber",
            "radius_km": 50,
        }
        
        response = requests.get(f"{BASE_URL}/technicians/nearby", params=search_params)
        
        if response.status_code != 200:
            print(f"   ⚠️  Search returned {response.status_code}")
            return False
        
        data = response.json()
        found_in_search = False
        
        for tech in data.get('technicians', []):
            if tech.get('phone') == test_phone:
                found_in_search = True
                print(f"   ✅ Found in search results!")
                print(f"      Name: {tech.get('name')}")
                print(f"      Distance: {tech.get('distance_km')} km")
                print(f"      Rank: {tech.get('rank')}")
                break
        
        if not found_in_search:
            print(f"   ⚠️  Technician not in search results (may not be verified)")
        
    except Exception as e:
        print(f"   ⚠️  Search check failed: {str(e)}")
    
    print("\n" + "=" * 70)
    print("✅ TEST PASSED: Technician registered and stored in database!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + "  TECHNICIAN REGISTRATION TEST  ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    print(f"Testing against: {BASE_URL}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_technician_registration()
    
    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if success:
        print("All checks passed! ✨")
    else:
        print("Some checks failed. See details above. 🔧")
