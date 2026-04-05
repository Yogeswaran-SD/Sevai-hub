from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.technician import ServiceCategory


# ─── Request Schemas ──────────────────────────────────────────────────────────

class TechnicianCreate(BaseModel):
    name:             str
    phone:            str
    email:            Optional[EmailStr] = None
    password:         str
    service_category: ServiceCategory
    experience_years: Optional[float] = 0
    bio:              Optional[str] = None
    address:          Optional[str] = None
    city:             Optional[str] = "Chennai"
    latitude:         Optional[float] = None
    longitude:        Optional[float] = None
    # TTI fields (optional on registration; platform can update later)
    cancellation_rate:     Optional[float] = 0.05
    response_delay_avg:    Optional[float] = 15.0
    rating_stability:      Optional[float] = 0.80
    availability_score:    Optional[float] = 0.85
    verification_age_days: Optional[int]   = 0


class TechnicianUpdate(BaseModel):
    is_available:          Optional[bool]  = None
    latitude:              Optional[float] = None
    longitude:             Optional[float] = None
    bio:                   Optional[str]   = None
    address:               Optional[str]   = None
    cancellation_rate:     Optional[float] = None
    response_delay_avg:    Optional[float] = None
    rating_stability:      Optional[float] = None
    availability_score:    Optional[float] = None
    verification_age_days: Optional[int]   = None


class NearbySearchRequest(BaseModel):
    latitude:         float = Field(..., ge=-90, le=90)
    longitude:        float = Field(..., ge=-180, le=180)
    service_category: ServiceCategory
    radius_km:        Optional[float] = 3.0
    urgency_level:    Optional[str]   = "Low"


# ─── Intelligence Sub-Schemas ─────────────────────────────────────────────────

class TTIResult(BaseModel):
    tti_score:         float
    reliability_label: str
    display:           str


class ETAResult(BaseModel):
    eta_minutes:    int
    confidence_pct: float
    display:        str


class EmergencyRisk(BaseModel):
    score:          float
    percentage:     int
    level:          str
    icon:           str
    keywords_found: List[str]
    display:        str


# ─── Response Schemas ─────────────────────────────────────────────────────────

class TechnicianResponse(BaseModel):
    id:               UUID
    name:             str
    phone:            str
    email:            Optional[str]
    service_category: ServiceCategory
    rating:           float
    total_reviews:    float
    is_available:     bool
    is_verified:      bool
    experience_years: float
    bio:              Optional[str]
    address:          Optional[str]
    city:             str
    profile_image:    Optional[str]
    latitude:         Optional[float] = None
    longitude:        Optional[float] = None
    distance_km:      Optional[float] = None
    created_at:       datetime

    # TTI fields
    cancellation_rate:     float
    response_delay_avg:    float
    rating_stability:      float
    availability_score:    float
    verification_age_days: int

    class Config:
        from_attributes = True


class TechnicianIntelligenceResponse(TechnicianResponse):
    """Extended response that includes TTI, ETA, and weighted score."""
    tti:             Optional[TTIResult]  = None
    eta:             Optional[ETAResult]  = None
    weighted_score:  Optional[float]      = None
    rank:            Optional[int]        = None


class NearbySearchResponse(BaseModel):
    technicians:        List[TechnicianIntelligenceResponse]
    total_found:        int
    search_radius_km:   float
    radius_expanded:    bool
    expansion_steps:    List[float]
    emergency_risk:     Optional[EmergencyRisk] = None
    search_lat:         float
    search_lon:         float
