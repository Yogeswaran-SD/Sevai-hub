"""
Admin-protected dashboard and management routes.
All endpoints require valid JWT with role=admin.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.technician import Technician
from app.core.security import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
def admin_dashboard(db: Session = Depends(get_db), _=Depends(require_admin)):
    try:
        total_users = db.query(User).filter(User.role == UserRole.USER).count()
        total_techs = db.query(Technician).count()
        verified_techs = db.query(Technician).filter(Technician.is_verified == True).count()
        pending_techs = db.query(Technician).filter(Technician.is_verified == False).count()
        active_users = db.query(User).filter(User.is_active == True, User.role == UserRole.USER).count()

        return {
            "total_users": total_users,
            "total_technicians": total_techs,
            "verified_technicians": verified_techs,
            "pending_technicians": pending_techs,
            "active_users": active_users,
        }
    except Exception:
        from app.local_auth_store import list_all_users, list_all_technicians
        users = list_all_users()
        techs = list_all_technicians()
        return {
            "total_users": len(users),
            "total_technicians": len(techs),
            "verified_technicians": len([t for t in techs if t.get("is_verified", False)]),
            "pending_technicians": len([t for t in techs if not t.get("is_verified", False)]),
            "active_users": len([u for u in users if u.get("is_active", True)]),
        }


@router.get("/users")
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    try:
        users = db.query(User).filter(User.role == UserRole.USER).all()
        return [
            {
                "id": str(u.id),
                "name": u.name,
                "email": u.email,
                "phone": u.phone,
                "is_active": u.is_active,
                "created_at": str(u.created_at),
            }
            for u in users
        ]
    except Exception:
        from app.local_auth_store import list_all_users
        users = list_all_users()
        return [
            {
                "id": u["id"],
                "name": u["name"],
                "email": u.get("email"),
                "phone": u["phone"],
                "is_active": u.get("is_active", True),
                "created_at": "Offline Mode",
            }
            for u in users
        ]


@router.patch("/users/{user_id}/toggle")
def toggle_user(user_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_active = not user.is_active
    db.commit()
    return {"id": user_id, "is_active": user.is_active}


@router.get("/technicians")
def list_technicians(db: Session = Depends(get_db), _=Depends(require_admin)):
    try:
        techs = db.query(Technician).all()
        return [
            {
                "id": str(t.id),
                "name": t.name,
                "phone": t.phone,
                "email": t.email,
                "service_category": t.service_category,
                "is_available": t.is_available,
                "is_verified": t.is_verified,
                "rating": t.rating,
                "city": t.city,
                "created_at": str(t.created_at),
            }
            for t in techs
        ]
    except Exception:
        from app.local_auth_store import list_all_technicians
        techs = list_all_technicians()
        return [
            {
                "id": t["id"],
                "name": t["name"],
                "phone": t["phone"],
                "email": t.get("email"),
                "service_category": t.get("service_category", "Unknown"),
                "is_available": t.get("is_available", True),
                "is_verified": t.get("is_verified", False),
                "rating": t.get("rating", 4.5),
                "city": t.get("city", "Demo City"),
                "created_at": "Offline Mode",
            }
            for t in techs
        ]


@router.patch("/technicians/{tech_id}/verify")
def verify_technician(tech_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    tech = db.query(Technician).filter(Technician.id == tech_id).first()
    if not tech:
        raise HTTPException(status_code=404, detail="Technician not found.")
    tech.is_verified = not tech.is_verified
    db.commit()
    return {"id": tech_id, "is_verified": tech.is_verified}


@router.delete("/technicians/{tech_id}")
def delete_technician(tech_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    tech = db.query(Technician).filter(Technician.id == tech_id).first()
    if not tech:
        raise HTTPException(status_code=404, detail="Technician not found.")
    db.delete(tech)
    db.commit()
    return {"message": "Technician removed successfully."}
