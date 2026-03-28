"""
security.py — Direct bcrypt (no passlib wrapper)
=================================================
Passlib 1.7.x is incompatible with bcrypt >= 4.0 due to a missing
__about__.__version__ attribute. We use bcrypt directly instead.
"""
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


# ─── Password hashing (direct bcrypt, no passlib) ─────────────────────────────

def get_password_hash(password: str) -> str:
    """Hash a plain-text password with bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ─── JWT ──────────────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


# ─── FastAPI dependency: get authenticated user from Bearer token ──────────────

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise exc
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise exc
    return payload


# ─── Role guards (use as FastAPI Depends) ────────────────────────────────────

def require_role(*roles: str):
    def _checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required: {', '.join(roles)}",
            )
        return current_user
    return _checker


def require_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "user":
        raise HTTPException(status_code=403, detail="User role required.")
    return current_user


def require_technician(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "technician":
        raise HTTPException(status_code=403, detail="Technician role required.")
    return current_user


def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin role required.")
    return current_user
