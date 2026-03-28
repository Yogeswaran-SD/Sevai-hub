"""
Sevai Hub — Seed Script
========================
Populates the sevaihub database with sample Tamil Nadu technicians + TTI data.
Run: python seed.py
"""

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models.technician import Technician, ServiceCategory
from app.models.user import User, UserRole
from app.core.security import get_password_hash

DEMO_USERS_DATA = [
    {
        "name": "Demo User",
        "email": "user@demo.com",
        "phone": "1234567890",
        "password": "demo123",
        "role": UserRole.USER,
    },
]

Base.metadata.create_all(bind=engine)

TECHNICIANS = [
    # ── Plumbers ──────────────────────────────────────────────────────────────
    {
        "name": "Ravi Kumar", "phone": "9876543210",
        "service_category": ServiceCategory.PLUMBER,
        "rating": 4.8, "total_reviews": 124, "is_available": True, "is_verified": True,
        "experience_years": 7, "city": "Chennai", "address": "Anna Nagar, Chennai",
        "latitude": 13.0850, "longitude": 80.2101,
        "cancellation_rate": 0.02, "response_delay_avg": 8.0,
        "rating_stability": 0.92, "availability_score": 0.95, "verification_age_days": 540,
    },
    {
        "name": "Murugan S", "phone": "9876543211",
        "service_category": ServiceCategory.PLUMBER,
        "rating": 4.5, "total_reviews": 89, "is_available": True, "is_verified": True,
        "experience_years": 5, "city": "Chennai", "address": "T.Nagar, Chennai",
        "latitude": 13.0418, "longitude": 80.2341,
        "cancellation_rate": 0.05, "response_delay_avg": 14.0,
        "rating_stability": 0.80, "availability_score": 0.82, "verification_age_days": 320,
    },
    {
        "name": "Senthil P", "phone": "9876543212",
        "service_category": ServiceCategory.PLUMBER,
        "rating": 4.2, "total_reviews": 56, "is_available": False, "is_verified": True,
        "experience_years": 3, "city": "Chennai", "address": "Velachery, Chennai",
        "latitude": 12.9815, "longitude": 80.2180,
        "cancellation_rate": 0.10, "response_delay_avg": 22.0,
        "rating_stability": 0.67, "availability_score": 0.65, "verification_age_days": 180,
    },

    # ── Electricians ──────────────────────────────────────────────────────────
    {
        "name": "Arjun Electricals", "phone": "9876543220",
        "service_category": ServiceCategory.ELECTRICIAN,
        "rating": 4.9, "total_reviews": 210, "is_available": True, "is_verified": True,
        "experience_years": 10, "city": "Chennai", "address": "Adyar, Chennai",
        "latitude": 13.0012, "longitude": 80.2565,
        "cancellation_rate": 0.01, "response_delay_avg": 6.0,
        "rating_stability": 0.96, "availability_score": 0.97, "verification_age_days": 720,
    },
    {
        "name": "Karthik E", "phone": "9876543221",
        "service_category": ServiceCategory.ELECTRICIAN,
        "rating": 4.6, "total_reviews": 143, "is_available": True, "is_verified": True,
        "experience_years": 6, "city": "Chennai", "address": "Tambaram, Chennai",
        "latitude": 12.9249, "longitude": 80.1000,
        "cancellation_rate": 0.04, "response_delay_avg": 12.0,
        "rating_stability": 0.84, "availability_score": 0.88, "verification_age_days": 410,
    },
    {
        "name": "Bala Electrician", "phone": "9876543222",
        "service_category": ServiceCategory.ELECTRICIAN,
        "rating": 4.3, "total_reviews": 78, "is_available": True, "is_verified": False,
        "experience_years": 4, "city": "Coimbatore", "address": "RS Puram, Coimbatore",
        "latitude": 11.0000, "longitude": 76.9500,
        "cancellation_rate": 0.12, "response_delay_avg": 25.0,
        "rating_stability": 0.70, "availability_score": 0.72, "verification_age_days": 0,
    },

    # ── Gas Service ───────────────────────────────────────────────────────────
    {
        "name": "Safe Gas Service", "phone": "9876543230",
        "service_category": ServiceCategory.GAS_SERVICE,
        "rating": 4.9, "total_reviews": 187, "is_available": True, "is_verified": True,
        "experience_years": 12, "city": "Chennai", "address": "Porur, Chennai",
        "latitude": 13.0340, "longitude": 80.1570,
        "cancellation_rate": 0.01, "response_delay_avg": 5.0,
        "rating_stability": 0.97, "availability_score": 0.98, "verification_age_days": 730,
    },
    {
        "name": "Vikram Gas Tech", "phone": "9876543231",
        "service_category": ServiceCategory.GAS_SERVICE,
        "rating": 4.7, "total_reviews": 99, "is_available": True, "is_verified": True,
        "experience_years": 8, "city": "Chennai", "address": "Guindy, Chennai",
        "latitude": 13.0067, "longitude": 80.2206,
        "cancellation_rate": 0.03, "response_delay_avg": 10.0,
        "rating_stability": 0.88, "availability_score": 0.91, "verification_age_days": 500,
    },

    # ── Bike Mechanics ────────────────────────────────────────────────────────
    {
        "name": "Speed Bike Works", "phone": "9876543240",
        "service_category": ServiceCategory.BIKE_MECHANIC,
        "rating": 4.7, "total_reviews": 165, "is_available": True, "is_verified": True,
        "experience_years": 9, "city": "Chennai", "address": "Perambur, Chennai",
        "latitude": 13.1187, "longitude": 80.2444,
        "cancellation_rate": 0.04, "response_delay_avg": 15.0,
        "rating_stability": 0.83, "availability_score": 0.87, "verification_age_days": 390,
    },
    {
        "name": "Raja Mechanic", "phone": "9876543241",
        "service_category": ServiceCategory.BIKE_MECHANIC,
        "rating": 4.4, "total_reviews": 112, "is_available": True, "is_verified": False,
        "experience_years": 5, "city": "Madurai", "address": "Anna Nagar, Madurai",
        "latitude": 9.9252, "longitude": 78.1198,
        "cancellation_rate": 0.09, "response_delay_avg": 20.0,
        "rating_stability": 0.72, "availability_score": 0.75, "verification_age_days": 0,
    },

    # ── Mobile Technicians ────────────────────────────────────────────────────
    {
        "name": "Phone Doctor", "phone": "9876543250",
        "service_category": ServiceCategory.MOBILE_TECHNICIAN,
        "rating": 4.8, "total_reviews": 203, "is_available": True, "is_verified": True,
        "experience_years": 6, "city": "Chennai", "address": "Kodambakkam, Chennai",
        "latitude": 13.0533, "longitude": 80.2214,
        "cancellation_rate": 0.02, "response_delay_avg": 10.0,
        "rating_stability": 0.91, "availability_score": 0.93, "verification_age_days": 620,
    },
    {
        "name": "iRepair Tamil", "phone": "9876543251",
        "service_category": ServiceCategory.MOBILE_TECHNICIAN,
        "rating": 4.6, "total_reviews": 134, "is_available": True, "is_verified": True,
        "experience_years": 4, "city": "Chennai", "address": "Nungambakkam, Chennai",
        "latitude": 13.0600, "longitude": 80.2425,
        "cancellation_rate": 0.05, "response_delay_avg": 11.0,
        "rating_stability": 0.82, "availability_score": 0.86, "verification_age_days": 300,
    },

    # ── Cleaning ──────────────────────────────────────────────────────────────
    {
        "name": "CleanHome TN", "phone": "9876543260",
        "service_category": ServiceCategory.CLEANING_SERVICE,
        "rating": 4.7, "total_reviews": 178, "is_available": True, "is_verified": True,
        "experience_years": 5, "city": "Chennai", "address": "OMR, Chennai",
        "latitude": 12.8996, "longitude": 80.2268,
        "cancellation_rate": 0.03, "response_delay_avg": 20.0,
        "rating_stability": 0.86, "availability_score": 0.89, "verification_age_days": 450,
    },

    # ── AC Technicians ────────────────────────────────────────────────────────
    {
        "name": "Cool Air Services", "phone": "9876543270",
        "service_category": ServiceCategory.AC_TECHNICIAN,
        "rating": 4.8, "total_reviews": 156, "is_available": True, "is_verified": True,
        "experience_years": 8, "city": "Chennai", "address": "Sholinganallur, Chennai",
        "latitude": 12.8997, "longitude": 80.2278,
        "cancellation_rate": 0.02, "response_delay_avg": 12.0,
        "rating_stability": 0.90, "availability_score": 0.93, "verification_age_days": 580,
    },
    {
        "name": "Suresh AC Tech", "phone": "9876543271",
        "service_category": ServiceCategory.AC_TECHNICIAN,
        "rating": 4.5, "total_reviews": 89, "is_available": True, "is_verified": True,
        "experience_years": 5, "city": "Coimbatore", "address": "Gandhipuram, Coimbatore",
        "latitude": 11.0168, "longitude": 76.9558,
        "cancellation_rate": 0.06, "response_delay_avg": 16.0,
        "rating_stability": 0.79, "availability_score": 0.83, "verification_age_days": 270,
    },

    # ── Carpenter ─────────────────────────────────────────────────────────────
    {
        "name": "Kumar Carpentry", "phone": "9876543280",
        "service_category": ServiceCategory.CARPENTER,
        "rating": 4.6, "total_reviews": 101, "is_available": True, "is_verified": True,
        "experience_years": 11, "city": "Chennai", "address": "Chromepet, Chennai",
        "latitude": 12.9516, "longitude": 80.1462,
        "cancellation_rate": 0.04, "response_delay_avg": 18.0,
        "rating_stability": 0.85, "availability_score": 0.88, "verification_age_days": 660,
    },

    # ── Painter ───────────────────────────────────────────────────────────────
    {
        "name": "ColorCraft TN", "phone": "9876543290",
        "service_category": ServiceCategory.PAINTER,
        "rating": 4.7, "total_reviews": 93, "is_available": True, "is_verified": True,
        "experience_years": 7, "city": "Chennai", "address": "Villivakkam, Chennai",
        "latitude": 13.1005, "longitude": 80.2121,
        "cancellation_rate": 0.03, "response_delay_avg": 25.0,
        "rating_stability": 0.87, "availability_score": 0.90, "verification_age_days": 490,
    },
]



def seed():
    db = SessionLocal()
    try:
        # ── Seed demo users ──────────────────────────────────────────────────
        user_count = db.query(User).count()
        if user_count == 0:
            for u in DEMO_USERS_DATA:
                db.add(User(
                    name=u["name"],
                    email=u["email"],
                    phone=u["phone"],
                    hashed_password=get_password_hash(u["password"]),
                    role=u["role"],
                    is_active=True,
                ))
            db.commit()
            print(f"✅ Seeded {len(DEMO_USERS_DATA)} demo user(s).")
        else:
            print(f"⚠️  DB already has {user_count} user(s). Skipping user seed.")

        # ── Seed technicians ─────────────────────────────────────────────────
        existing = db.query(Technician).count()
        if existing > 0:
            print(f"⚠️  DB already has {existing} technicians. Skipping technician seed.")
            return

        for t in TECHNICIANS:
            lat = t.pop("latitude")
            lon = t.pop("longitude")
            location = f"SRID=4326;POINT({lon} {lat})"
            tech = Technician(
                **t,
                email=None,
                hashed_password=get_password_hash("Sevai@123"),
                bio=f"Experienced {t['service_category'].value} serving {t['city']} with {t['experience_years']} years of expertise.",
                location=location,
            )
            db.add(tech)

        db.commit()
        print(f"✅ Seeded {len(TECHNICIANS)} technicians with TTI data successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
