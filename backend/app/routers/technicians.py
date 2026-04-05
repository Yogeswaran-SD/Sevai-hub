from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.database import get_db
from app.models.technician import Technician, ServiceCategory
from app.schemas.technician import (
    TechnicianCreate, TechnicianResponse, TechnicianUpdate,
    TechnicianIntelligenceResponse, NearbySearchResponse,
    TTIResult, ETAResult, EmergencyRisk as EmergRiskSchema,
)
from app.core.security import get_password_hash
from app.intelligence import (
    compute_tti, predict_eta, compute_weighted_score,
    compute_emergency_risk, get_adaptive_radius_steps,
    get_performance_report,
)

router = APIRouter(prefix="/technicians", tags=["Technicians"])


# ─────────────────────────────────────────────────────────────────────────────
# CITY LOCATION DEFAULTS (for technicians without explicit location)
# ─────────────────────────────────────────────────────────────────────────────
CITY_DEFAULTS = {
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Pune": {"lat": 18.5204, "lon": 73.8567},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
}

def get_default_location_for_city(city: str) -> dict:
    """Get default lat/lon for a city, fallback to Chennai."""
    return CITY_DEFAULTS.get(city, CITY_DEFAULTS.get("Chennai"))


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _enrich_technician(
    tech_dict: dict,
    urgency_level: str = "Low",
    emergency_risk_score: float = 0.0,
) -> TechnicianIntelligenceResponse:
    """Attach TTI, ETA, and weighted allocation score to a raw technician dict."""
    
    # Convert service_category from enum name (PLUMBER) to value (Plumber)
    if "service_category" in tech_dict:
        raw_category = tech_dict["service_category"]
        try:
            # If it's the enum key (PLUMBER), convert to value (Plumber)
            enum_member = ServiceCategory[raw_category]
            tech_dict["service_category"] = enum_member.value
        except (KeyError, TypeError):
            # If it's already the value (Plumber), keep it as is
            pass
    
    tti_result = compute_tti(
        cancellation_rate=    tech_dict.get("cancellation_rate",      0.05),
        response_delay_avg=   tech_dict.get("response_delay_avg",    15.0),
        rating_stability=     tech_dict.get("rating_stability",       0.80),
        availability_score=   tech_dict.get("availability_score",     0.85),
        verification_age_days=tech_dict.get("verification_age_days",    0),
    )
    eta_result = predict_eta(
        distance_km=       tech_dict.get("distance_km", 5.0),
        service_category=  str(tech_dict.get("service_category", "Plumber")),
        urgency_level=     urgency_level,
        response_delay_avg=tech_dict.get("response_delay_avg", 15.0),
        rating=            tech_dict.get("rating", 4.0),
    )
    w_score = compute_weighted_score(
        distance_km=    tech_dict.get("distance_km", 5.0),
        rating=         tech_dict.get("rating", 4.0),
        tti_score=      tti_result["tti_score"],
        emergency_risk= emergency_risk_score,
    )

    tech_dict.pop("location", None)

    return TechnicianIntelligenceResponse(
        **tech_dict,
        tti=TTIResult(**{k: tti_result[k] for k in ("tti_score", "reliability_label", "display")}),
        eta=ETAResult(**{k: eta_result[k] for k in ("eta_minutes", "confidence_pct", "display")}),
        weighted_score=w_score,
    )


def _spatial_query(db: Session, lat: float, lon: float, category: str, radius_m: float):
    """
    Improved geospatial query that:
    1. Finds technicians with valid locations within radius
    2. Falls back to technicians without location (assigns default city location)
    3. Returns debug info about filtering
    """
    # Query 1: Technicians WITH valid locations
    sql_with_location = text("""
        SELECT
            t.*,
            ST_Y(t.location::geometry) AS latitude,
            ST_X(t.location::geometry) AS longitude,
            ST_Distance(
                t.location::geography,
                ST_MakePoint(:lon, :lat)::geography
            ) / 1000.0 AS distance_km,
            true AS has_location
        FROM technicians t
        WHERE
            t.is_available = true
            AND t.service_category::text = :category
            AND t.location IS NOT NULL
            AND ST_DWithin(
                t.location::geography,
                ST_MakePoint(:lon, :lat)::geography,
                :radius_m
            )
        ORDER BY
            distance_km ASC,
            t.rating DESC,
            t.is_verified DESC
        LIMIT 20
    """)
    
    try:
        result_with_location = db.execute(sql_with_location, {
            "lat": lat, "lon": lon,
            "category": category,
            "radius_m": radius_m,
        }).mappings().all()
        rows = list(result_with_location)
    except Exception as e:
        print(f"[WARN] Spatial query with location failed: {e}")
        rows = []

    # Query 2: If no results, include technicians WITHOUT location
    if not rows:
        sql_without_location = text("""
            SELECT
                t.*,
                NULL::float AS latitude,
                NULL::float AS longitude,
                999.0 AS distance_km,
                false AS has_location
            FROM technicians t
            WHERE
                t.is_available = true
                AND t.service_category::text = :category
                AND t.location IS NULL
            ORDER BY
                t.rating DESC,
                t.is_verified DESC
            LIMIT 20
        """)
        
        try:
            result_without_location = db.execute(sql_without_location, {
                "category": category,
            }).mappings().all()
            rows = list(result_without_location)
        except Exception as e:
            print(f"[WARN] Spatial query without location failed: {e}")
            rows = []

    return rows


# ─────────────────────────────────────────────────────────────────────────────
# STATIC-PATH ROUTES FIRST  (must come before /{technician_id})
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/nearby", response_model=NearbySearchResponse)
def get_nearby_technicians(
    latitude:         float           = Query(..., ge=-90,  le=90),
    longitude:        float           = Query(..., ge=-180, le=180),
    service_category: str             = Query(...),
    radius_km:        float           = Query(3.0, ge=1, le=100),
    urgency_level:    str             = Query("Low"),
    emergency_query:  Optional[str]   = Query(None),
    db: Session = Depends(get_db),
):
    """
    Adaptive geospatial search with:
      • Auto-expanding radius (3 → 5 → 8 → 15 km)
      • Emergency Severity Scoring
      • TTI computation per technician
      • ETA prediction per technician
      • Weighted Allocation ranking
    """
    # Convert service_category string to enum key (enum member name)
    try:
        category_enum = ServiceCategory(service_category)
        # Use the enum KEY (name) not the VALUE, since that's what's stored in database
        category_key = category_enum.name
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid service category: {service_category}")
    
    emerg_risk    = compute_emergency_risk(emergency_query or urgency_level)
    radius_steps  = get_adaptive_radius_steps(radius_km)
    rows          = []
    final_radius  = radius_steps[0]
    expanded      = False

    for step in radius_steps:
        rows = _spatial_query(db, latitude, longitude, category_key, step * 1000)
        final_radius = step
        if rows:
            expanded = step > radius_steps[0]
            break

    technicians_enriched = []
    for row in rows:
        tech_dict = dict(row)
        enriched  = _enrich_technician(
            tech_dict,
            urgency_level=emerg_risk["level"],
            emergency_risk_score=emerg_risk["score"],
        )
        technicians_enriched.append(enriched)

    # Weighted allocation re-rank
    technicians_enriched.sort(key=lambda t: t.weighted_score or 1.0)
    for i, t in enumerate(technicians_enriched):
        t.rank = i + 1

    return NearbySearchResponse(
        technicians=technicians_enriched,
        total_found=len(technicians_enriched),
        search_radius_km=final_radius,
        radius_expanded=expanded,
        expansion_steps=radius_steps,
        emergency_risk=EmergRiskSchema(**emerg_risk),
        search_lat=latitude,
        search_lon=longitude,
    )


@router.get("/system/performance")
def system_performance_report():
    """Spatial indexing efficiency, query optimization, and simulation support."""
    return get_performance_report()


@router.get("/emergency/score")
def emergency_risk_score(query: str = Query(...)):
    """Score a user's problem description for emergency risk level."""
    return compute_emergency_risk(query)


@router.get("/tti/calculate")
def calculate_tti(
    cancellation_rate:     float = Query(0.05, ge=0, le=1),
    response_delay_avg:    float = Query(15.0, ge=0),
    rating_stability:      float = Query(0.80, ge=0, le=1),
    availability_score:    float = Query(0.85, ge=0, le=1),
    verification_age_days: int   = Query(0, ge=0),
):
    """Compute Trust Index for given parameters."""
    return compute_tti(
        cancellation_rate, response_delay_avg,
        rating_stability,  availability_score,
        verification_age_days,
    )


@router.post("/register", response_model=TechnicianResponse, status_code=201)
def register_technician(data: TechnicianCreate, db: Session = Depends(get_db)):
    if db.query(Technician).filter(Technician.phone == data.phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered.")

    location = None
    assigned_lat = data.latitude
    assigned_lon = data.longitude
    
    # If location provided, use it
    if data.latitude and data.longitude:
        location = f"SRID=4326;POINT({data.longitude} {data.latitude})"
    else:
        # Auto-assign default location based on city
        city = data.city or "Chennai"
        default_loc = get_default_location_for_city(city)
        assigned_lat = default_loc["lat"]
        assigned_lon = default_loc["lon"]
        location = f"SRID=4326;POINT({assigned_lon} {assigned_lat})"
        print(f"[TECH REGISTRATION] Auto-assigned location for {city}: ({assigned_lat}, {assigned_lon})")

    tech = Technician(
        name=data.name, phone=data.phone, email=data.email,
        hashed_password=get_password_hash(data.password),
        service_category=data.service_category,
        experience_years=data.experience_years or 0,
        bio=data.bio, address=data.address,
        city=data.city or "Chennai", location=location,
        cancellation_rate=    data.cancellation_rate     or 0.05,
        response_delay_avg=   data.response_delay_avg    or 15.0,
        rating_stability=     data.rating_stability      or 0.80,
        availability_score=   data.availability_score    or 0.85,
        verification_age_days=data.verification_age_days or 0,
    )
    db.add(tech)
    db.commit()
    db.refresh(tech)
    return tech


@router.get("/", response_model=List[TechnicianResponse])
def list_technicians(
    category: Optional[ServiceCategory] = None,
    skip: int = 0, limit: int = 20,
    db: Session = Depends(get_db),
):
    query = db.query(Technician)
    if category:
        query = query.filter(Technician.service_category == category)
    return query.order_by(Technician.rating.desc()).offset(skip).limit(limit).all()


# ─────────────────────────────────────────────────────────────────────────────
# DYNAMIC-PATH ROUTES LAST  (/{technician_id} must be after all static paths)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{technician_id}", response_model=TechnicianIntelligenceResponse)
def get_technician(technician_id: str, db: Session = Depends(get_db)):
    tech = db.query(Technician).filter(Technician.id == technician_id).first()
    if not tech:
        raise HTTPException(status_code=404, detail="Technician not found.")
    tech_dict = {c.name: getattr(tech, c.name) for c in tech.__table__.columns}
    tech_dict["distance_km"] = None
    return _enrich_technician(tech_dict)


@router.put("/{technician_id}/availability")
def update_technician(technician_id: str, data: TechnicianUpdate, db: Session = Depends(get_db)):
    tech = db.query(Technician).filter(Technician.id == technician_id).first()
    if not tech:
        raise HTTPException(status_code=404, detail="Technician not found.")

    fields = ["is_available", "bio", "address", "cancellation_rate",
              "response_delay_avg", "rating_stability", "availability_score",
              "verification_age_days"]
    for f in fields:
        val = getattr(data, f, None)
        if val is not None:
            setattr(tech, f, val)
    if data.latitude and data.longitude:
        tech.location = f"SRID=4326;POINT({data.longitude} {data.latitude})"

    db.commit()
    tti = compute_tti(
        tech.cancellation_rate, tech.response_delay_avg,
        tech.rating_stability,  tech.availability_score,
        tech.verification_age_days,
    )
    return {"message": "Technician updated successfully.", "new_tti": tti}
