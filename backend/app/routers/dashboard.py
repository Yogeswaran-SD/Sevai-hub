"""
Role-specific dashboard data routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.technician import Technician
from app.core.security import require_user, require_technician

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/user")
def user_dashboard(db: Session = Depends(get_db), current=Depends(require_user)):
    return {
        "role": "user",
        "user_id": current.get("sub"),
        "message": "Welcome to your Sevai Hub dashboard!",
        "available_services": [
            "Plumber", "Electrician", "Gas Service", "Bike Mechanic",
            "Mobile Technician", "Cleaning Service", "AC Technician", "Carpenter", "Painter"
        ],
    }


@router.get("/technician")
def technician_dashboard(db: Session = Depends(get_db), current=Depends(require_technician)):
    tech_id = current.get("sub")
    tech = db.query(Technician).filter(Technician.id == tech_id).first()
    
    # If not found in DB, technician must be in local store only (backwards compatibility)
    if not tech:
        # Return basic profile data from token (at least technician can see their dashboard)
        return {
            "role": "technician",
            "technician_id": tech_id,
            "name": current.get("name"),
            "email": current.get("email"),
            "phone": current.get("phone"),
            "is_available": True,
            "is_verified": False,  # Local-store only technicians are unverified
            "rating": 0,
            "service_category": "Plumber",  # Default
            "city": "Chennai",  # Default
            "note": "Your profile data is limited. Please contact admin to fully set up your profile."
        }
    
    return {
        "role": "technician",
        "technician_id": tech_id,
        "name": tech.name,
        "email": tech.email,
        "phone": tech.phone,
        "is_available": tech.is_available,
        "is_verified": tech.is_verified,
        "rating": tech.rating,
        "service_category": str(tech.service_category.value if hasattr(tech.service_category, 'value') else tech.service_category),
        "city": tech.city,
    }
