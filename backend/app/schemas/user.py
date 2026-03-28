from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

# ─── Registration ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: str
    password: str

class UserRegisterResponse(BaseModel):
    """Works for both DB rows and local auth store dicts."""
    id: str                           # str, not UUID — works with 'demo-user-001' or real UUIDs
    name: str
    email: Optional[str] = None
    phone: str
    role: str
    is_active: bool = True
    created_at: Optional[datetime] = None  # optional — local store doesn't have it

    class Config:
        from_attributes = True

# ─── Login (flexible: email OR phone) ────────────────────────────────────────

class UserLoginRequest(BaseModel):
    identifier: str   # email or phone
    password: str

class TechnicianLoginRequest(BaseModel):
    identifier: str   # email or phone
    password: str

# ─── Admin Login (high-security) ──────────────────────────────────────────────

class AdminLoginRequest(BaseModel):
    mobile: str
    aadhaar: str
    password: str

# ─── Token Response ──────────────────────────────────────────────────────────

class TokenPayload(BaseModel):
    id: str
    name: str
    role: str
    email: Optional[str] = None
    phone: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: TokenPayload

# ─── Legacy compat ───────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: str                           # str to match UserRegisterResponse
    name: str
    email: Optional[str] = None
    phone: str
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
