import uuid
from sqlalchemy import Column, String, Boolean, Float, Integer, DateTime, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from geoalchemy2 import Geography
import enum
from app.database import Base


class ServiceCategory(str, enum.Enum):
    PLUMBER            = "Plumber"
    ELECTRICIAN        = "Electrician"
    GAS_SERVICE        = "Gas Service"
    BIKE_MECHANIC      = "Bike Mechanic"
    MOBILE_TECHNICIAN  = "Mobile Technician"
    CLEANING_SERVICE   = "Cleaning Service"
    AC_TECHNICIAN      = "AC Technician"
    CARPENTER          = "Carpenter"
    PAINTER            = "Painter"


class Technician(Base):
    __tablename__ = "technicians"

    # ── Core identity ──────────────────────────────────────────────────────
    id                   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name                 = Column(String(100), nullable=False)
    phone                = Column(String(15), unique=True, nullable=False)
    email                = Column(String(150), unique=True, nullable=True)
    hashed_password      = Column(String, nullable=False)

    # ── Service ────────────────────────────────────────────────────────────
    service_category     = Column(Enum(ServiceCategory), nullable=False, index=True)
    experience_years     = Column(Float, default=0)
    bio                  = Column(Text, nullable=True)

    # ── Location ───────────────────────────────────────────────────────────
    address              = Column(String(255), nullable=True)
    city                 = Column(String(100), default="Chennai")
    location             = Column(Geography(geometry_type="POINT", srid=4326), nullable=True, index=True)

    # ── Ratings ────────────────────────────────────────────────────────────
    rating               = Column(Float, default=0.0)
    total_reviews        = Column(Float, default=0)

    # ── Status ─────────────────────────────────────────────────────────────
    is_available         = Column(Boolean, default=True, index=True)
    is_verified          = Column(Boolean, default=False, index=True)
    profile_image        = Column(String, nullable=True)

    # ── Technician Trust Index (TTI) fields ────────────────────────────────
    cancellation_rate    = Column(Float, default=0.05)   # 0.0–1.0
    response_delay_avg   = Column(Float, default=15.0)   # minutes
    rating_stability     = Column(Float, default=0.80)   # 0.0–1.0
    availability_score   = Column(Float, default=0.85)   # 0.0–1.0
    verification_age_days= Column(Integer, default=0)    # days since verified

    # ── Timestamps ─────────────────────────────────────────────────────────
    created_at           = Column(DateTime(timezone=True), server_default=func.now())
    updated_at           = Column(DateTime(timezone=True), onupdate=func.now())
