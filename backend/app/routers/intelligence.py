"""
Sevai Hub — Intelligence Router
================================
New endpoints:
  GET /intelligence/dashboard    — live system intelligence summary
  GET /intelligence/heatmap      — service demand heatmap context
  GET /intelligence/simulate     — emergency allocation simulation
  GET /intelligence/tti/explain  — explain TTI formula with example
  GET /intelligence/performance  — detailed performance transparency
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.database import get_db
from app.models.technician import Technician, ServiceCategory
from app.intelligence import (
    compute_emergency_risk, compute_tti, predict_eta,
    compute_weighted_score, get_adaptive_radius_steps,
    get_performance_report, RADIUS_STEPS, SEVERITY_LEVELS,
    EMERGENCY_KEYWORD_WEIGHTS,
)
import random, math

router = APIRouter(prefix="/intelligence", tags=["Intelligence"])


# ─────────────────────────────────────────────────────────────────────────────
# INTELLIGENCE DASHBOARD — live summary
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/dashboard")
def intelligence_dashboard(db: Session = Depends(get_db)):
    """
    Returns a complete live intelligence summary:
    - Total / available technicians
    - Average TTI across platform
    - Emergency module stats
    - Radius expansion stats
    - System health
    """
    try:
        total_techs     = db.query(Technician).count()
        available_techs = db.query(Technician).filter(Technician.is_available == True).count()
        verified_techs  = db.query(Technician).filter(Technician.is_verified == True).count()

        # Aggregate TTI components from DB
        tti_rows = db.query(
            func.avg(Technician.cancellation_rate).label("avg_cancel"),
            func.avg(Technician.response_delay_avg).label("avg_delay"),
            func.avg(Technician.rating_stability).label("avg_stability"),
            func.avg(Technician.availability_score).label("avg_avail"),
            func.avg(Technician.verification_age_days).label("avg_verif"),
            func.avg(Technician.rating).label("avg_rating"),
        ).one()

        platform_tti = compute_tti(
            cancellation_rate=     float(tti_rows.avg_cancel    or 0.05),
            response_delay_avg=    float(tti_rows.avg_delay     or 15.0),
            rating_stability=      float(tti_rows.avg_stability  or 0.80),
            availability_score=    float(tti_rows.avg_avail     or 0.85),
            verification_age_days= int(tti_rows.avg_verif       or 0),
        )

        # Category breakdown
        cat_rows = db.execute(text("""
            SELECT service_category,
                   COUNT(*)                        AS total,
                   SUM(CASE WHEN is_available THEN 1 ELSE 0 END) AS available,
                   AVG(rating)                     AS avg_rating
            FROM technicians
            GROUP BY service_category
            ORDER BY total DESC
        """)).mappings().all()

        categories = []
        for row in cat_rows:
            categories.append({
                "category":    row["service_category"],
                "total":       row["total"],
                "available":   row["available"],
                "avg_rating":  round(float(row["avg_rating"] or 0), 2),
                "availability_pct": round((row["available"] / row["total"]) * 100, 1) if row["total"] else 0,
            })

        return {
            "platform_summary": {
                "total_technicians":     total_techs,
                "available_now":         available_techs,
                "verified_technicians":  verified_techs,
                "availability_rate_pct": round((available_techs / total_techs * 100), 1) if total_techs else 0,
                "verification_rate_pct": round((verified_techs / total_techs * 100), 1) if total_techs else 0,
                "avg_platform_rating":   round(float(tti_rows.avg_rating or 0), 2),
            },
            "platform_tti": platform_tti,
            "categories":   categories,
            "intelligence_modules": {
                "emergency_scoring":     {"status": "active", "keywords_tracked": len(EMERGENCY_KEYWORD_WEIGHTS)},
                "trust_index":           {"status": "active", "formula_weights": {"response_reliability": 0.30, "cancellation_perf": 0.25, "rating_stability": 0.20, "availability_consistency": 0.15, "verification_age": 0.10}},
                "adaptive_radius":       {"status": "active", "steps_km": RADIUS_STEPS},
                "eta_prediction":        {"status": "active", "confidence_model": "distance + prep + urgency-scaled delay"},
                "weighted_allocation":   {"status": "active", "formula_weights": {"distance": 0.50, "rating": 0.20, "tti": 0.20, "emergency": 0.10}},
                "performance_indexing":  {"status": "active", "index_type": "GiST spatial"},
            },
        }

    except Exception as e:
        # Return a sensible degraded response if DB is not connected
        return {
            "error": "Database not connected. Running in demo mode.",
            "platform_summary": {
                "total_technicians": 18, "available_now": 14,
                "verified_technicians": 15, "availability_rate_pct": 77.8,
                "verification_rate_pct": 83.3, "avg_platform_rating": 4.67,
            },
            "platform_tti": compute_tti(0.04, 13.5, 0.85, 0.88, 420),
            "categories": [],
            "intelligence_modules": {
                "emergency_scoring":   {"status": "active", "keywords_tracked": len(EMERGENCY_KEYWORD_WEIGHTS)},
                "trust_index":         {"status": "active"},
                "adaptive_radius":     {"status": "active", "steps_km": RADIUS_STEPS},
                "eta_prediction":      {"status": "active"},
                "weighted_allocation": {"status": "active"},
                "performance_indexing":{"status": "active"},
            },
        }


# ─────────────────────────────────────────────────────────────────────────────
# HEATMAP CONTEXT
# ─────────────────────────────────────────────────────────────────────────────

DEMAND_ZONES = [
    {"zone": "Anna Nagar",      "lat": 13.0850, "lon": 80.2101, "demand_score": 92, "peak_hour": "08:00–11:00", "top_service": "Plumber"},
    {"zone": "T.Nagar",         "lat": 13.0418, "lon": 80.2341, "demand_score": 88, "peak_hour": "09:00–12:00", "top_service": "Electrician"},
    {"zone": "Adyar",           "lat": 13.0012, "lon": 80.2565, "demand_score": 85, "peak_hour": "07:00–10:00", "top_service": "Electrician"},
    {"zone": "Velachery",       "lat": 12.9815, "lon": 80.2180, "demand_score": 80, "peak_hour": "18:00–21:00", "top_service": "AC Technician"},
    {"zone": "OMR",             "lat": 12.8996, "lon": 80.2268, "demand_score": 75, "peak_hour": "08:00–10:00", "top_service": "AC Technician"},
    {"zone": "Porur",           "lat": 13.0340, "lon": 80.1570, "demand_score": 70, "peak_hour": "10:00–13:00", "top_service": "Gas Service"},
    {"zone": "Tambaram",        "lat": 12.9249, "lon": 80.1000, "demand_score": 65, "peak_hour": "07:00–09:00", "top_service": "Plumber"},
    {"zone": "Perambur",        "lat": 13.1187, "lon": 80.2444, "demand_score": 60, "peak_hour": "09:00–11:00", "top_service": "Bike Mechanic"},
    {"zone": "Sholinganallur",  "lat": 12.8997, "lon": 80.2278, "demand_score": 78, "peak_hour": "08:00–10:00", "top_service": "AC Technician"},
    {"zone": "Kodambakkam",     "lat": 13.0533, "lon": 80.2214, "demand_score": 72, "peak_hour": "10:00–14:00", "top_service": "Mobile Technician"},
]

@router.get("/heatmap")
def service_demand_heatmap():
    """Urban service demand heatmap with zone-level demand scores."""
    high_demand = [z for z in DEMAND_ZONES if z["demand_score"] >= 80]
    medium_demand = [z for z in DEMAND_ZONES if 60 <= z["demand_score"] < 80]
    return {
        "heatmap_zones":    DEMAND_ZONES,
        "high_demand_zones": high_demand,
        "medium_demand_zones": medium_demand,
        "peak_emergency_hours": ["07:00–09:00", "18:00–21:00"],
        "emergency_clustering": {
            "gas_leaks":    {"primary_zone": "Porur–Guindy corridor", "avg_response_time_mins": 14},
            "electrical":   {"primary_zone": "T.Nagar–Anna Nagar corridor", "avg_response_time_mins": 18},
            "plumbing":     {"primary_zone": "Velachery–Tambaram corridor", "avg_response_time_mins": 22},
        },
        "total_zones_tracked": len(DEMAND_ZONES),
    }


# ─────────────────────────────────────────────────────────────────────────────
# EMERGENCY ALLOCATION SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/simulate")
def simulate_allocation(
    concurrent_requests: int = Query(100, ge=1, le=10000),
    scenario:            str  = Query("mixed", description="mixed | emergency | routine"),
):
    """
    Simulate emergency allocation under load.
    Returns allocation efficiency, latency estimates, and fairness metrics.
    """
    random.seed(42)

    # Simulate latency based on load
    base_latency_ms = 8  # with GiST index
    seq_latency_ms  = 350  # without index

    # As load increases, latency scales sub-linearly (index benefit)
    load_factor = math.log10(max(concurrent_requests, 1)) / math.log10(10000)
    indexed_latency   = base_latency_ms  + load_factor * 45
    unindexed_latency = seq_latency_ms   + load_factor * 650

    # Simulate allocation results
    if scenario == "emergency":
        success_rate = max(0.88, 0.99 - load_factor * 0.08)
        avg_radius   = 3.8
        avg_eta      = 16
    elif scenario == "routine":
        success_rate = max(0.92, 0.99 - load_factor * 0.04)
        avg_radius   = 4.9
        avg_eta      = 32
    else:  # mixed
        success_rate = max(0.90, 0.99 - load_factor * 0.06)
        avg_radius   = 4.2
        avg_eta      = 24

    radius_expansions_pct = round(min(45, 10 + load_factor * 35), 1)
    fairness_gini = round(0.08 + load_factor * 0.04, 3)  # lower = fairer

    return {
        "scenario":            scenario,
        "concurrent_requests": concurrent_requests,
        "allocation_results": {
            "success_rate_pct":       round(success_rate * 100, 1),
            "failed_allocations":     int(concurrent_requests * (1 - success_rate)),
            "avg_search_radius_km":   avg_radius,
            "radius_expanded_pct":    radius_expansions_pct,
            "avg_eta_minutes":        avg_eta,
        },
        "latency_comparison": {
            "with_gist_index_ms":     round(indexed_latency, 1),
            "without_index_ms":       round(unindexed_latency, 1),
            "speedup_factor":         round(unindexed_latency / indexed_latency, 1),
        },
        "fairness_metrics": {
            "gini_coefficient":        fairness_gini,
            "fairness_label":          "Excellent" if fairness_gini < 0.10 else "Good" if fairness_gini < 0.15 else "Moderate",
            "avg_technicians_per_req": round(3.2 - load_factor * 0.8, 1),
        },
        "system_health": {
            "index_status":    "GiST active",
            "adaptive_radius": "enabled",
            "tti_computation": "O(1) per technician",
            "recommendation":  "System handles load well up to ~5,000 concurrent requests with current indexing.",
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# TTI EXPLAINER
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/tti/explain")
def explain_tti(
    cancellation_rate:     float = Query(0.05, ge=0, le=1),
    response_delay_avg:    float = Query(15.0, ge=0),
    rating_stability:      float = Query(0.80, ge=0, le=1),
    availability_score:    float = Query(0.85, ge=0, le=1),
    verification_age_days: int   = Query(365, ge=0),
):
    """Returns TTI breakdown with step-by-step explanation."""
    result = compute_tti(
        cancellation_rate, response_delay_avg,
        rating_stability, availability_score, verification_age_days,
    )
    return {
        "inputs": {
            "cancellation_rate":     cancellation_rate,
            "response_delay_avg":    response_delay_avg,
            "rating_stability":      rating_stability,
            "availability_score":    availability_score,
            "verification_age_days": verification_age_days,
        },
        "formula": "TTI = (0.30 × Response Reliability) + (0.25 × Cancellation Perf) + (0.20 × Rating Stability) + (0.15 × Availability) + (0.10 × Verification Age)",
        "computed": result,
        "interpretation": {
            "score_range":  "0–100 (higher = more trustworthy)",
            "band_85_100":  "Highly Reliable — Priority allocation",
            "band_70_84":   "Reliable — Standard allocation",
            "band_50_69":   "Moderate — Monitored allocation",
            "band_0_49":    "Low Trust — Requires review",
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# PERFORMANCE TRANSPARENCY (enhanced version)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/performance")
def get_performance():
    """Detailed spatial indexing efficiency and query optimization report."""
    return get_performance_report()


# ─────────────────────────────────────────────────────────────────────────────
# LIVE EMERGENCY RISK SCORER
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/emergency/score")
def score_emergency_query(query: str = Query(..., description="Free-text problem description")):
    """
    Score a free-text query for emergency risk level.
    Returns score, level, icon, matched keywords, and display string.
    """
    return compute_emergency_risk(query)


# ─────────────────────────────────────────────────────────────────────────────
# WEIGHTED ALLOCATION EXPLAINER
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/weighted/explain")
def explain_weighted_allocation(
    distance_km:      float = Query(3.0, ge=0),
    rating:           float = Query(4.5, ge=0, le=5),
    tti_score:        float = Query(85.0, ge=0, le=100),
    emergency_risk:   float = Query(0.0, ge=0, le=1),
):
    """
    Explain the weighted allocation formula step-by-step.
    Final Score = 0.5×dist + 0.2×rating + 0.2×tti + 0.1×emergency
    Lower score = higher priority.
    """
    dist_norm   = min(distance_km / 30.0, 1.0)
    rating_norm = 1.0 - (rating / 5.0)
    tti_norm    = 1.0 - (tti_score / 100.0)
    emerg_norm  = 1.0 - emergency_risk

    final = round(
        0.50 * dist_norm +
        0.20 * rating_norm +
        0.20 * tti_norm +
        0.10 * emerg_norm,
        6
    )

    return {
        "inputs": {
            "distance_km": distance_km,
            "rating": rating,
            "tti_score": tti_score,
            "emergency_risk_score": emergency_risk,
        },
        "normalized_components": {
            "distance":  round(dist_norm, 4),
            "rating":    round(rating_norm, 4),
            "tti":       round(tti_norm, 4),
            "emergency": round(emerg_norm, 4),
        },
        "weighted_contributions": {
            "distance_contribution":  round(0.50 * dist_norm, 4),
            "rating_contribution":    round(0.20 * rating_norm, 4),
            "tti_contribution":       round(0.20 * tti_norm, 4),
            "emergency_contribution": round(0.10 * emerg_norm, 4),
        },
        "final_score": final,
        "priority_label": (
            "🥇 Highest Priority" if final < 0.20 else
            "🥈 High Priority"    if final < 0.35 else
            "🥉 Medium Priority"  if final < 0.50 else
            "⬇ Lower Priority"
        ),
        "formula": "Final Score = (0.50 × dist_norm) + (0.20 × rating_norm) + (0.20 × tti_norm) + (0.10 × emergency_norm)",
        "note": "Lower final score = higher allocation priority. Technician must be available and within radius.",
    }


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM VERSION
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/version")
def intelligence_version():
    """Return the current intelligence engine version and module manifest."""
    return {
        "version": "3.0.0",
        "engine": "Sevai Hub Spatially Optimized Emergency Allocation Engine",
        "modules": [
            {"id": 1, "name": "Emergency Severity Scoring Engine",   "status": "active"},
            {"id": 2, "name": "Technician Trust Index (TTI)",         "status": "active"},
            {"id": 3, "name": "Adaptive Search Radius Algorithm",     "status": "active"},
            {"id": 4, "name": "Response Time Prediction Model",       "status": "active"},
            {"id": 5, "name": "Urban Service Demand Heatmap",         "status": "active"},
            {"id": 6, "name": "Performance Transparency Mode",        "status": "active"},
            {"id": 7, "name": "Weighted Allocation Model",            "status": "active"},
            {"id": 8, "name": "Emergency Simulation Engine",          "status": "active"},
            {"id": 9, "name": "Transparency & Integrity Principles",  "status": "active"},
        ],
        "spatial_index": "GiST (PostgreSQL/PostGIS)",
        "allocation_formula": "0.5×dist + 0.2×rating + 0.2×tti + 0.1×emergency",
    }
