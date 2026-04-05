#!/usr/bin/env python
"""Test search endpoint response format"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test search for electricians
search_response = requests.get(
    f"{BASE_URL}/technicians/nearby",
    params={
        "latitude": 12.9698,
        "longitude": 77.7499,
        "service_category": "Electrician",
        "radius_km": 100
    }
)

print("Search Response Status:", search_response.status_code)
print("\nFull Response:")
response_data = search_response.json()
print(json.dumps(response_data, indent=2)[:1000])

print("\n\nResponse Type:", type(response_data))
print("Response Keys:", response_data.keys() if isinstance(response_data, dict) else "Not a dict")

if isinstance(response_data, dict) and "technicians" in response_data:
    print(f"\nTotal Technicians: {len(response_data['technicians'])}")
    if response_data['technicians']:
        print("\nFirst Technician:")
        print(json.dumps(response_data['technicians'][0], indent=2)[:500])
