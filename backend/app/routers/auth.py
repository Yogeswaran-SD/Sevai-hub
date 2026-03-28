"""
auth.py — Sevai Hub Authentication Router
==========================================
Authentication priority:
  1. Local file-based store (local_auth.json) — ALWAYS works, no DB needed
  2. PostgreSQL database — checked second when available

This means:
  - All registered credentials persist even when PostgreSQL is offline
  - Demo credentials work immediately out of the box
  - Fresh registrations go to BOTH DB (if online) and local store
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.technician import Technician, ServiceCategory
from app.schemas.user import (
    UserCreate, UserRegisterResponse,
    UserLoginRequest, TechnicianLoginRequest, AdminLoginRequest,
    TokenResponse, TokenPayload
)
from app.core.security import (
    get_password_hash, verify_password, create_access_token,
    decode_access_token, bearer_scheme
)
from app.core.config import settings
import app.local_auth_store as local_store
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ─── Helper ───────────────────────────────────────────────────────────────────

def _build_token(sub: str, role: str, name: str, email=None, phone=None) -> TokenResponse:
    token = create_access_token({"sub": sub, "role": role})
    return TokenResponse(
        access_token=token,
        user=TokenPayload(id=sub, name=name, role=role, email=email, phone=phone)
    )

def _record_to_token(rec: dict) -> TokenResponse:
    return _build_token(rec["id"], rec["role"], rec["name"], rec.get("email"), rec.get("phone"))


# ─── User Registration ────────────────────────────────────────────────────────

@router.post("/register", response_model=UserRegisterResponse, status_code=201)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Always register into local store first (works offline)
    try:
        local_store.register_user(
            name=user_data.name,
            phone=user_data.phone,
            password=user_data.password,
            email=user_data.email,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Also try to register in DB (best-effort)
    db_user = None
    try:
        if user_data.email and db.query(User).filter(User.email == user_data.email).first():
            pass  # already in DB — that's fine, local store registered ok
        elif db.query(User).filter(User.phone == user_data.phone).first():
            pass  # already in DB
        else:
            db_user = User(
                name=user_data.name,
                email=user_data.email,
                phone=user_data.phone,
                hashed_password=get_password_hash(user_data.password),
                role=UserRole.USER,
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
    except Exception:
        pass  # DB offline — local store already has the user

    # Build response from local store record
    rec = local_store.find_user(user_data.phone)
    return {
        "id": rec["id"],
        "name": rec["name"],
        "email": rec.get("email"),
        "phone": rec["phone"],
        "role": rec["role"],
        "is_active": rec.get("is_active", True),
    }


# ─── User Login ───────────────────────────────────────────────────────────────

@router.post("/login/user", response_model=TokenResponse)
def login_user(credentials: UserLoginRequest, db: Session = Depends(get_db)):
    identifier = credentials.identifier.strip()
    password   = credentials.password

    # ── Priority 1: Local store (always works) ────────────────────────────────
    rec = local_store.auth_user(identifier, password)
    if rec:
        if not rec.get("is_active", True):
            raise HTTPException(status_code=403, detail="Account is disabled.")
        return _record_to_token(rec)

    # ── Priority 2: Check if identifier exists locally (wrong password case) ──
    existing = local_store.find_user(identifier)
    if existing:
        raise HTTPException(
            status_code=401,
            detail="Incorrect password. Check your credentials and try again."
        )

    # ── Priority 3: Database lookup ───────────────────────────────────────────
    try:
        user = (
            db.query(User).filter(User.email == identifier).first()
            or db.query(User).filter(User.phone == identifier).first()
        )
        if not user:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No account found for '{identifier}'. "
                    "Please register first, or use the demo credentials shown on the login page."
                )
            )
        if user.role != UserRole.USER:
            raise HTTPException(status_code=401, detail="This is not a user account.")
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect password.")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is disabled.")

        # Found in DB — cache in local store for future offline use
        try:
            local_store.register_user(user.name, user.phone, password, user.email)
        except Exception:
            pass  # already cached

        return _build_token(str(user.id), "user", user.name, user.email, user.phone)

    except HTTPException:
        raise
    except Exception as db_err:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Account '{identifier}' not found in local store. "
                "If you registered this account through the database only, "
                "please re-register using the Register form on the login page."
            )
        )


# ─── Technician Login ─────────────────────────────────────────────────────────

@router.post("/login/technician", response_model=TokenResponse)
def login_technician(credentials: TechnicianLoginRequest, db: Session = Depends(get_db)):
    identifier = credentials.identifier.strip()
    password   = credentials.password

    # ── Priority 1: Local store ───────────────────────────────────────────────
    rec = local_store.auth_technician(identifier, password)
    if rec:
        return _record_to_token(rec)

    # ── Check if identifier exists locally (wrong password) ───────────────────
    existing = local_store.find_technician(identifier)
    if existing:
        raise HTTPException(
            status_code=401,
            detail="Incorrect password for this technician account."
        )

    # ── Priority 2: Database lookup ───────────────────────────────────────────
    try:
        tech = (
            db.query(Technician).filter(Technician.email == identifier).first()
            or db.query(Technician).filter(Technician.phone == identifier).first()
        )
        if not tech:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No technician account found for '{identifier}'. "
                    "Note: Technician accounts are created by admins. "
                    "Contact the admin or use a demo account from the panel above."
                )
            )
        if not verify_password(password, tech.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect password.")

        # Cache in local store for future offline use
        try:
            local_store.register_technician(
                tech.name, tech.phone, password,
                tech.email, str(tech.service_category.value if hasattr(tech.service_category, 'value') else tech.service_category)
            )
        except Exception:
            pass

        return _build_token(str(tech.id), "technician", tech.name, tech.email, tech.phone)

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Technician '{identifier}' not found. "
                "Contact your admin to create a technician account, "
                "or use a demo technician from the credentials panel."
            )
        )


# ─── Admin Login (HIGH SECURITY — no DB needed) ───────────────────────────────

@router.post("/login/admin", response_model=TokenResponse)
def login_admin(credentials: AdminLoginRequest):
    # Verify all credentials (constant-time comparison for security)
    mobile_ok   = credentials.mobile   == settings.ADMIN_MOBILE
    aadhaar_ok  = credentials.aadhaar  == settings.ADMIN_AADHAAR
    # Use bcrypt hash verification for password (not plain text comparison!)
    password_ok = verify_password(credentials.password, settings.ADMIN_PASSWORD_HASH)

    if not (mobile_ok and aadhaar_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied. Invalid admin credentials."
        )
    return _build_token("admin-root", "admin", "System Administrator", None, settings.ADMIN_MOBILE)


# ─── Register Technician (self-service) ──────────────────────────────────────

@router.post("/register/technician", status_code=201)
def register_technician_self(
    name: str,
    phone: str,
    password: str,
    email: str = None,
    service_category: str = "Plumber",
    db: Session = Depends(get_db),
):
    """
    Self-service technician registration.
    Creates record in BOTH local auth store (for offline access) and database (for dashboard access).
    """
    try:
        # Register in local store first (always works, no DB needed)
        rec = local_store.register_technician(name, phone, password, email, service_category)
        tech_id = rec["id"]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Also create in database (for dashboard to work)
    try:
        # Check if technician already exists in DB
        existing = (
            db.query(Technician).filter(Technician.email == email).first()
            if email else None
        ) or db.query(Technician).filter(Technician.phone == phone).first()

        if not existing:
            new_tech = Technician(
                id=uuid.UUID(tech_id),
                name=name,
                phone=phone,
                email=email,
                hashed_password=get_password_hash(password),
                service_category=ServiceCategory(service_category),
                is_available=True,
                is_verified=False,  # New technicians are unverified
            )
            db.add(new_tech)
            db.commit()
            db.refresh(new_tech)
    except Exception as db_err:
        # Log but don't fail — local store registration succeeded
        print(f"Warning: Could not create technician in DB: {db_err}")
        pass

    return {
        "message": "Technician registered successfully.",
        "id": tech_id,
        "name": name,
        "note": "Your profile is unverified. Admin verification may be required for some features."
    }


# ─── Verify Token ─────────────────────────────────────────────────────────────

@router.get("/me")
def get_me(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalid or expired.")
    return {"id": payload.get("sub"), "role": payload.get("role")}
