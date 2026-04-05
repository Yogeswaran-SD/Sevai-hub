#!/usr/bin/env python3
"""
Migration Script: Assign Default Locations to Technicians Without Location Data
================================================================================

This script:
1. Finds all technicians without location data (location IS NULL)
2. Assigns default location based on their city
3. Logs all changes for audit trail

Run: python migrate_technician_locations.py
"""

from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from app.database import DATABASE_URL
from app.models.technician import Technician

# City location defaults
CITY_DEFAULTS = {
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Pune": {"lat": 18.5204, "lon": 73.8567},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
}

def main():
    # Create DB session
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("=" * 70)
    print("TECHNICIAN LOCATION MIGRATION")
    print("=" * 70)

    try:
        # Find technicians without location
        technicians_without_location = session.query(Technician).filter(
            Technician.location == None
        ).all()

        if not technicians_without_location:
            print("✓ All technicians have locations! No migration needed.")
            print("=" * 70)
            return

        print(f"\n Found {len(technicians_without_location)} technicians without location data\n")

        updated = 0
        for tech in technicians_without_location:
            city = tech.city or "Chennai"
            default_loc = CITY_DEFAULTS.get(city, CITY_DEFAULTS["Chennai"])
            
            lat = default_loc["lat"]
            lon = default_loc["lon"]
            tech.location = f"SRID=4326;POINT({lon} {lat})"
            
            print(f"  ✓ {tech.name} ({tech.service_category})")
            print(f"    City: {city} → Location: ({lat}, {lon})")
            print(f"    Phone: {tech.phone} | Verified: {tech.is_verified}\n")
            
            updated += 1

        # Commit all changes
        session.commit()
        
        print("=" * 70)
        print(f"✓ MIGRATION COMPLETE: {updated} technicians updated")
        print("=" * 70)
        print("\nTechnicians will now appear in service search results!")
        print("The system will use their city's center location for geospatial filtering.")

    except Exception as e:
        session.rollback()
        print(f"✗ ERROR: {str(e)}")
        print("Migration rolled back.")
    finally:
        session.close()

if __name__ == "__main__":
    main()
