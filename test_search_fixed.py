#!/usr/bin/env python3
"""Test search endpoint after enum fix."""

import requests
import time
import json

time.sleep(2)  # Wait for backend to stabilize

API_BASE = "http://localhost:8000"

# Test search for plumbers
print("Testing search for Plumber in Chennai...")
response = requests.get(
    f"{API_BASE}/technicians/nearby",
    params={
        "latitude": 13.0827,
        "longitude": 80.2707,
        "service_category": "Plumber",
        "radius_km": 50,
    }
)

print(f"Status: {response.status_code}")
data = response.json()
print(f"Total found: {data.get('total_found', 0)}")
print(f"Search radius expanded to: {data.get('search_radius_km')} km")

if data.get('technicians'):
    print(f"\nFound {len(data['technicians'])} technicians:")
    for tech in data['technicians'][:3]:
        print(f"  - {tech.get('name')}: {tech.get('service_category')} ({tech.get('distance_km', 0):.1f} km away)")
else:
    print("\n❌ No technicians found")

# Also test electrician
print("\n" + "="*60)
print("Testing search for Electrician in Chennai...")
response = requests.get(
    f"{API_BASE}/technicians/nearby",
    params={
        "latitude": 13.0827,
        "longitude": 80.2707,
        "service_category": "Electrician",
        "radius_km": 50,
    }
)

print(f"Status: {response.status_code}")
data = response.json()
print(f"Total found: {data.get('total_found', 0)}")

if data.get('technicians'):
    print(f"Found {len(data['technicians'])} technicians:")
    for tech in data['technicians'][:3]:
        print(f"  - {tech.get('name')}: {tech.get('service_category')} ({tech.get('distance_km', 0):.1f} km away)")
else:
    print("❌ No technicians found")
