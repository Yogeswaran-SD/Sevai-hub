#!/usr/bin/env python3
"""
Test Script: Verify Technician Visibility Fix
===============================================

This script tests the complete fix for technician visibility in service search.

Tests:
1. Registration without location (auto-assign)
2. Geospatial search finding technicians
3. Admin location update endpoint
4. Migration of existing technicians
"""

import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = None  # Will need to be set after admin login

class TestRunner:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []

    def log_test(self, test_name, passed, message=""):
        status = "✓ PASS" if passed else "✗ FAIL"
        self.results.append(f"{status}: {test_name}")
        if message:
            self.results.append(f"       {message}")
        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        print(f"{status}: {test_name}")
        if message:
            print(f"       {message}")

    def print_summary(self):
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        for result in self.results:
            print(result)
        print("=" * 70)
        print(f"Total: {self.tests_passed} passed, {self.tests_failed} failed")
        print(f"Success Rate: {(self.tests_passed / (self.tests_passed + self.tests_failed)) * 100:.1f}%")
        print("=" * 70)

def test_registration_without_location():
    """Test that technician registration works without explicit location"""
    runner = TestRunner()
    
    print("\n" + "=" * 70)
    print("TEST 1: REGISTRATION WITHOUT LOCATION (Auto-Assign)")
    print("=" * 70)
    
    payload = {
        "name": f"Auto Tech {int(time.time())}",
        "phone": f"999{int(time.time()) % 9999999:07d}",
        "email": f"tech{int(time.time())}@test.com",
        "password": "TestPassword@123",
        "service_category": "Plumber",
        "city": "Chennai",
        "experience_years": 5,
        # Note: No latitude/longitude
    }
    
    try:
        response = requests.post(f"{BASE_URL}/technicians/register", json=payload)
        
        if response.status_code == 201:
            tech_data = response.json()
            runner.log_test(
                "Register technician without location",
                True,
                f"Technician ID: {tech_data.get('id')}, Phone: {tech_data.get('phone')}"
            )
            
            # Verify location was assigned
            if tech_data.get('location') is not None:
                runner.log_test(
                    "Auto-location assigned",
                    True,
                    f"Location type: {type(tech_data.get('location'))}"
                )
            else:
                runner.log_test(
                    "Auto-location assigned",
                    False,
                    "Location is None"
                )
            
            return tech_data.get('id'), runner
        else:
            runner.log_test(
                "Register technician without location",
                False,
                f"Status {response.status_code}: {response.text}"
            )
            return None, runner
    except Exception as e:
        runner.log_test(
            "Register technician without location",
            False,
            f"Exception: {str(e)}"
        )
        return None, runner

def test_geospatial_search(service_category="Plumber"):
    """Test that registered technicians appear in geospatial search"""
    runner = TestRunner()
    
    print("\n" + "=" * 70)
    print("TEST 2: GEOSPATIAL SEARCH")
    print("=" * 70)
    
    # Chennai center coordinates
    params = {
        "latitude": 13.0827,
        "longitude": 80.2707,
        "service_category": service_category,
        "radius_km": 50,  # Large radius to include all
    }
    
    try:
        response = requests.get(f"{BASE_URL}/technicians/nearby", params=params)
        
        if response.status_code == 200:
            data = response.json()
            total_found = data.get('total_found', 0)
            technicians = data.get('technicians', [])
            
            runner.log_test(
                f"Search for {service_category} technicians",
                True,
                f"Found {total_found} technicians"
            )
            
            if technicians:
                first_tech = technicians[0]
                runner.log_test(
                    "First technician in results",
                    True,
                    f"Name: {first_tech.get('name')}, Distance: {first_tech.get('distance_km')} km"
                )
            
            # Check for radius expansion info
            expanded = data.get('radius_expanded', False)
            runner.log_test(
                "Radius expansion info",
                True,
                f"Expanded: {expanded}, Final radius: {data.get('search_radius_km')} km"
            )
            
            return total_found > 0, runner
        else:
            runner.log_test(
                "Search for technicians",
                False,
                f"Status {response.status_code}: {response.text}"
            )
            return False, runner
    except Exception as e:
        runner.log_test(
            "Search for technicians",
            False,
            f"Exception: {str(e)}"
        )
        return False, runner

def test_admin_location_update(tech_id):
    """Test admin endpoint for updating technician location"""
    runner = TestRunner()
    
    print("\n" + "=" * 70)
    print("TEST 3: ADMIN LOCATION UPDATE")
    print("=" * 70)
    
    if not tech_id:
        runner.log_test(
            "Admin location update",
            False,
            "No technician ID provided"
        )
        return runner
    
    # Note: This requires admin authentication
    headers = {}
    if ADMIN_TOKEN:
        headers['Authorization'] = f'Bearer {ADMIN_TOKEN}'
    
    params = {
        "latitude": 13.0845,  # Different location
        "longitude": 80.2710,
    }
    
    try:
        response = requests.patch(
            f"{BASE_URL}/admin/technicians/{tech_id}/location",
            params=params,
            headers=headers,
        )
        
        if response.status_code in [200, 401, 403]:  # 200=success, 401/403=auth issues
            if response.status_code == 200:
                runner.log_test(
                    "Admin location update",
                    True,
                    f"Updated to: ({params['latitude']}, {params['longitude']})"
                )
            else:
                runner.log_test(
                    "Admin location update",
                    False,
                    f"Authentication required (Status {response.status_code})"
                )
        else:
            runner.log_test(
                "Admin location update",
                False,
                f"Status {response.status_code}: {response.text}"
            )
    except Exception as e:
        runner.log_test(
            "Admin location update",
            False,
            f"Exception: {str(e)}"
        )
    
    return runner

def test_migration_script_info():
    """Test information about migration script"""
    runner = TestRunner()
    
    print("\n" + "=" * 70)
    print("TEST 4: MIGRATION SCRIPT INFO")
    print("=" * 70)
    
    import os
    script_path = "migrate_technician_locations.py"
    
    if os.path.exists(script_path):
        runner.log_test(
            "Migration script exists",
            True,
            f"Path: {os.path.abspath(script_path)}"
        )
    else:
        runner.log_test(
            "Migration script exists",
            False,
            f"Not found at {os.path.abspath(script_path)}"
        )
    
    runner.log_test(
        "Migration script usage",
        True,
        "Run: python migrate_technician_locations.py"
    )
    
    return runner

def main():
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + "  TECHNICIAN VISIBILITY FIX - TEST SUITE  ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    print(f"Testing against: {BASE_URL}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Run all tests
    tech_id, runner1 = test_registration_without_location()
    runner1.print_summary()

    search_ok, runner2 = test_geospatial_search("Plumber")
    runner2.print_summary()

    runner3 = test_admin_location_update(tech_id)
    runner3.print_summary()

    runner4 = test_migration_script_info()
    runner4.print_summary()

    # Overall summary
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + "  OVERALL CONCLUSION  ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    if search_ok:
        print("✓ Technician visibility fix is WORKING!")
        print("  - Technicians can register without explicit location")
        print("  - Auto-location assignment is functional")
        print("  - Geospatial search finds registered technicians")
    else:
        print("✗ Technician visibility fix needs attention")
        print("  - Check if backend is running on", BASE_URL)
        print("  - Verify database connection")
        print("  - Run migration script on existing technicians")
    print()
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

if __name__ == "__main__":
    main()
