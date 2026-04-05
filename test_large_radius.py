#!/usr/bin/env python3
"""Test with larger radius to find all technicians."""

import requests

API_BASE = "http://localhost:8000"

categories = [
    "Plumber", "Electrician", "Gas Service", "Bike Mechanic",
    "Mobile Technician", "Cleaning Service", "AC Technician",
    "Carpenter", "Painter"
]

print("Testing search with LARGE radius (500 km)...")
print("=" * 70)

total_found = 0
for category in categories:
    response = requests.get(
        f"{API_BASE}/technicians/nearby",
        params={
            "latitude": 13.0827,
            "longitude": 80.2707,
            "service_category": category,
            "radius_km": 500,
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        count = data.get('total_found', 0)
        total_found += count
        status = "✅" if count > 0 else "⚠️"
        tech_names = [t['name'] for t in data.get('technicians', [])]
        print(f"{status} {category:25} - Found {count:2} technicians")
        if count > 0:
            print(f"     Names: {', '.join(tech_names[:3])}")
    else:
        print(f"❌ {category:25} - Error {response.status_code}")

print("=" * 70)
print(f"Total technicians found across all categories: {total_found}")
