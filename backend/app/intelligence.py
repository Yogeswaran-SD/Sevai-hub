"""
Sevai Hub — Intelligence Engine
================================
Modules:
  1. Emergency Severity Scoring Engine
  2. Technician Trust Index (TTI) Calculator
  3. Adaptive Search Radius Algorithm
  4. Response Time Prediction Model
  5. Weighted Allocation Ranking
  6. Performance Transparency Metrics
"""

import math
from datetime import datetime, timezone
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# 1. EMERGENCY SEVERITY SCORING ENGINE
# ─────────────────────────────────────────────────────────────────────────────

EMERGENCY_KEYWORD_WEIGHTS: dict[str, float] = {
    # Critical — life/property threatening
    "gas leak":        1.00,
    "gas smell":       1.00,
    "fire":            1.00,
    "explosion":       1.00,
    "electric shock":  1.00,
    "electrocuted":    1.00,
    "spark":           0.90,
    "short circuit":   0.90,
    "burst pipe":      0.90,
    "flood":           0.85,
    "water flooding":  0.85,
    "no power":        0.75,
    "blackout":        0.75,
    "hissing":         0.80,
    # High
    "urgent":          0.70,
    "emergency":       0.70,
    "immediately":     0.65,
    "broken":          0.50,
    "not working":     0.45,
    "leak":            0.60,
    "overflow":        0.55,
    "damage":          0.50,
    # Medium
    "repair":          0.30,
    "fix":             0.25,
    "service":         0.20,
    "install":         0.15,
    "replace":         0.20,
    "check":           0.10,
    # Low / routine
    "clean":           0.08,
    "paint":           0.05,
    "touch up":        0.05,
}

SEVERITY_LEVELS = [
    (0.75, "Critical", "🔴"),
    (0.50, "High",     "🟠"),
    (0.25, "Medium",   "🟡"),
    (0.00, "Low",      "🟢"),
]


def compute_emergency_risk(query: str) -> dict:
    """
    Analyse a free-text query and return:
      { score: float(0-1), percentage: int, level: str, icon: str, keywords_found: list }
    """
    lower = query.lower().strip()
    matched_weights: list[float] = []
    keywords_found: list[str] = []

    for keyword, weight in EMERGENCY_KEYWORD_WEIGHTS.items():
        if keyword in lower:
            matched_weights.append(weight)
            keywords_found.append(keyword)

    if not matched_weights:
        raw_score = 0.0
    else:
        # Weighted combination — max dominates, others add diminishing returns
        sorted_w = sorted(matched_weights, reverse=True)
        raw_score = sorted_w[0]
        for i, w in enumerate(sorted_w[1:], start=1):
            raw_score += w * (0.3 ** i)
        raw_score = min(raw_score, 1.0)

    percentage = round(raw_score * 100)
    level, icon = "Low", "🟢"
    for threshold, lv, ic in SEVERITY_LEVELS:
        if raw_score >= threshold:
            level, icon = lv, ic
            break

    return {
        "score": round(raw_score, 4),
        "percentage": percentage,
        "level": level,
        "icon": icon,
        "keywords_found": keywords_found,
        "display": f"Emergency Risk Level: {percentage}% ({level})",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. TECHNICIAN TRUST INDEX (TTI)
# ─────────────────────────────────────────────────────────────────────────────

def compute_tti(
    cancellation_rate: float,       # 0.0–1.0  (e.g. 0.05 = 5% cancellations)
    response_delay_avg: float,      # minutes  (e.g. 12.0)
    rating_stability: float,        # 0.0–1.0
    availability_score: float,      # 0.0–1.0
    verification_age_days: int,     # days since verification
    max_delay_threshold: float = 45.0,
    max_verification_days: float = 730.0,
) -> dict:
    """
    TTI Score =
      (0.30 × Response Reliability) +
      (0.25 × Cancellation Performance) +
      (0.20 × Rating Stability) +
      (0.15 × Availability Consistency) +
      (0.10 × Verification Age Factor)
    """
    response_reliability   = max(0.0, 1.0 - (response_delay_avg / max_delay_threshold))
    cancellation_perf      = max(0.0, 1.0 - cancellation_rate)
    rating_stab            = max(0.0, min(1.0, rating_stability))
    avail_consistency      = max(0.0, min(1.0, availability_score))
    verif_age_factor       = min(1.0, verification_age_days / max_verification_days)

    tti_raw = (
        0.30 * response_reliability +
        0.25 * cancellation_perf +
        0.20 * rating_stab +
        0.15 * avail_consistency +
        0.10 * verif_age_factor
    )
    tti_score = round(tti_raw * 100, 1)

    if tti_score >= 85:
        reliability_label = "Highly Reliable"
    elif tti_score >= 70:
        reliability_label = "Reliable"
    elif tti_score >= 50:
        reliability_label = "Moderate"
    else:
        reliability_label = "Low Trust"

    return {
        "tti_score": tti_score,
        "reliability_label": reliability_label,
        "components": {
            "response_reliability":  round(response_reliability * 100, 1),
            "cancellation_perf":     round(cancellation_perf * 100, 1),
            "rating_stability":      round(rating_stab * 100, 1),
            "availability_score":    round(avail_consistency * 100, 1),
            "verification_age":      round(verif_age_factor * 100, 1),
        },
        "display": f"Trust Score: {tti_score}% ({reliability_label})",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. ADAPTIVE SEARCH RADIUS ALGORITHM
# ─────────────────────────────────────────────────────────────────────────────

RADIUS_STEPS = [3.0, 5.0, 8.0, 15.0, 30.0]


def get_adaptive_radius_steps(initial_km: float = 3.0) -> list[float]:
    """Return radius expansion steps starting from the given initial radius."""
    for i, r in enumerate(RADIUS_STEPS):
        if r >= initial_km:
            return RADIUS_STEPS[i:]
    return RADIUS_STEPS


# ─────────────────────────────────────────────────────────────────────────────
# 4. RESPONSE TIME PREDICTION MODEL
# ─────────────────────────────────────────────────────────────────────────────

# Average km/h speed per urgency level (city traffic estimates)
SPEED_BY_URGENCY = {
    "Critical": 35.0,
    "High":     30.0,
    "Medium":   25.0,
    "Low":      20.0,
}

CATEGORY_BASE_PREP = {
    "Gas Service":        3,
    "Electrician":        5,
    "Plumber":            7,
    "Bike Mechanic":      8,
    "AC Technician":      10,
    "Mobile Technician":  12,
    "Cleaning Service":   15,
    "Carpenter":          15,
    "Painter":            20,
}


def predict_eta(
    distance_km: float,
    service_category: str,
    urgency_level: str = "Low",
    response_delay_avg: float = 15.0,
    rating: float = 4.0,
) -> dict:
    """
    Estimate arrival time and confidence level.

    ETA = travel_time + preparation_time + expected_delay_buffer
    Confidence is penalised by response delay history and boosted by high rating.
    """
    speed = SPEED_BY_URGENCY.get(urgency_level, 25.0)
    travel_minutes = (distance_km / speed) * 60.0
    prep_minutes   = CATEGORY_BASE_PREP.get(service_category, 10)

    # Delay buffer: average historical delay scaled by urgency
    urgency_scale = {"Critical": 0.3, "High": 0.5, "Medium": 0.7, "Low": 1.0}
    delay_buffer   = response_delay_avg * urgency_scale.get(urgency_level, 1.0)

    eta_minutes = math.ceil(travel_minutes + prep_minutes + delay_buffer * 0.4)

    # Confidence: start at 0.85, penalise high delay, boost for high rating
    confidence = 0.85
    confidence -= min(0.20, response_delay_avg / 200.0)
    confidence += min(0.10, (rating - 4.0) * 0.10)
    confidence  = max(0.40, min(0.98, confidence))

    return {
        "eta_minutes":    eta_minutes,
        "confidence_pct": round(confidence * 100, 1),
        "display":        f"Estimated Arrival: {eta_minutes} mins (Confidence: {round(confidence*100)}%)",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. WEIGHTED ALLOCATION RANKING
# ─────────────────────────────────────────────────────────────────────────────

def compute_weighted_score(
    distance_km: float,
    rating: float,
    tti_score: float,
    emergency_risk: float = 0.0,
    max_distance: float = 30.0,
) -> float:
    """
    Final Score =
      (0.50 × Distance Weight) +
      (0.20 × Rating Weight) +
      (0.20 × Trust Index Weight) +
      (0.10 × Emergency Severity Weight)

    Lower final score → higher priority.
    All components normalised to [0, 1].
    """
    dist_norm    = min(distance_km / max_distance, 1.0)
    rating_norm  = 1.0 - (rating / 5.0)                   # lower is better
    tti_norm     = 1.0 - (tti_score / 100.0)              # lower is better
    emerg_norm   = 1.0 - emergency_risk                    # higher risk → lower penalty score

    final = (
        0.50 * dist_norm +
        0.20 * rating_norm +
        0.20 * tti_norm +
        0.10 * emerg_norm
    )
    return round(final, 6)


# ─────────────────────────────────────────────────────────────────────────────
# 6. PERFORMANCE TRANSPARENCY METRICS
# ─────────────────────────────────────────────────────────────────────────────

PERFORMANCE_REPORT = {
    "spatial_index": {
        "type": "GiST (Generalized Search Tree)",
        "indexed_column": "technicians.location (Geography POINT, SRID 4326)",
        "index_ddl": "CREATE INDEX idx_tech_location ON technicians USING GIST(location);",
        "without_index": {
            "algorithm": "Sequential scan",
            "complexity": "O(n) — every row checked",
            "estimated_latency_ms": "200–800 ms for 10k rows",
        },
        "with_index": {
            "algorithm": "GiST spatial index lookup",
            "complexity": "O(log n) — tree traversal",
            "estimated_latency_ms": "2–15 ms for 10k rows",
            "improvement_factor": "~30–50×",
        },
        "additional_indexes": [
            "idx_tech_category ON technicians(service_category)",
            "idx_tech_available ON technicians(is_available)",
            "idx_tech_verified  ON technicians(is_verified)",
        ],
    },
    "query_optimizations": [
        "ST_DWithin uses bounding-box pre-filter before exact distance check",
        "Composite ORDER BY: distance ASC, rating DESC, verified DESC",
        "LIMIT 20 applied at DB level — no over-fetching",
        "Geography cast ensures geodesic (earth-curved) distance accuracy",
    ],
    "adaptive_radius": {
        "strategy": "Expand 3km → 5km → 8km → 15km → 30km",
        "stop_condition": "Stop when ≥1 available technician found",
        "max_expansion": "30 km",
    },
    "tti_computation": {
        "location": "Application layer (Python)",
        "cost": "O(1) per technician — pure arithmetic",
        "cached": False,
    },
    "simulation_support": {
        "scenarios": [
            "Allocation efficiency under load (100–10,000 concurrent requests)",
            "Radius expansion latency profiling",
            "TTI fairness distribution across technicians",
            "Emergency vs. non-emergency response time delta",
        ]
    },
}


def get_performance_report() -> dict:
    return PERFORMANCE_REPORT
