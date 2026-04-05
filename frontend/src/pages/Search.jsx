import React, { useState, useEffect, useCallback, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import TechnicianCard from "../components/TechnicianCard";
import MapView from "../components/MapView";
import { getNearbyTechnicians } from "../api/api";

const CATEGORIES = [
  "Plumber", "Electrician", "Gas Service", "Bike Mechanic",
  "Mobile Technician", "Cleaning Service", "AC Technician", "Carpenter", "Painter",
];

const CATEGORY_ICONS = {
  "Plumber": "🔧", "Electrician": "⚡", "Gas Service": "🔥",
  "Bike Mechanic": "🏍️", "Mobile Technician": "📱", "Cleaning Service": "🧹",
  "AC Technician": "❄️", "Carpenter": "🪚", "Painter": "🎨",
};

const EMERGENCY_CATEGORIES = ["Gas Service", "Electrician"];

const SEVERITY_COLORS = {
  Critical: { bg: "rgba(239,68,68,0.12)", border: "rgba(239,68,68,0.35)", text: "#EF4444" },
  High:     { bg: "rgba(249,115,22,0.12)", border: "rgba(249,115,22,0.35)", text: "#F97316" },
  Medium:   { bg: "rgba(245,158,11,0.12)", border: "rgba(245,158,11,0.35)", text: "#F59E0B" },
  Low:      { bg: "rgba(16,185,129,0.10)", border: "rgba(16,185,129,0.25)", text: "#10B981" },
};

// ─── Mock data (frontend fallback when backend offline) ───────────────────────
const MOCK_TECHNICIANS = [
  {
    id: "1", name: "Ravi Kumar", phone: "9876543210", service_category: "Plumber",
    rating: 4.8, total_reviews: 124, is_available: true, is_verified: true,
    experience_years: 7, address: "Anna Nagar, Chennai", city: "Chennai", distance_km: 1.2,
    latitude: 13.085, longitude: 80.210, rank: 1,
    cancellation_rate: 0.02, response_delay_avg: 8.0, rating_stability: 0.92,
    availability_score: 0.95, verification_age_days: 540, weighted_score: 0.12,
    tti: { tti_score: 94.2, reliability_label: "Highly Reliable", display: "Trust Score: 94.2% (Highly Reliable)" },
    eta: { eta_minutes: 18, confidence_pct: 92.0, display: "Estimated Arrival: 18 mins (Confidence: 92%)" },
  },
  {
    id: "2", name: "Murugan S", phone: "9876543211", service_category: "Plumber",
    rating: 4.5, total_reviews: 89, is_available: true, is_verified: true,
    experience_years: 5, address: "T.Nagar, Chennai", city: "Chennai", distance_km: 2.4,
    latitude: 13.041, longitude: 80.234, rank: 2,
    cancellation_rate: 0.05, response_delay_avg: 14.0, rating_stability: 0.80,
    availability_score: 0.82, verification_age_days: 320, weighted_score: 0.24,
    tti: { tti_score: 82.5, reliability_label: "Reliable", display: "Trust Score: 82.5% (Reliable)" },
    eta: { eta_minutes: 31, confidence_pct: 85.0, display: "Estimated Arrival: 31 mins (Confidence: 85%)" },
  },
  {
    id: "3", name: "Arjun Electricals", phone: "9876543220", service_category: "Electrician",
    rating: 4.9, total_reviews: 210, is_available: true, is_verified: true,
    experience_years: 10, address: "Adyar, Chennai", city: "Chennai", distance_km: 3.1,
    latitude: 13.001, longitude: 80.256, rank: 1,
    cancellation_rate: 0.01, response_delay_avg: 6.0, rating_stability: 0.96,
    availability_score: 0.97, verification_age_days: 720, weighted_score: 0.10,
    tti: { tti_score: 97.1, reliability_label: "Highly Reliable", display: "Trust Score: 97.1% (Highly Reliable)" },
    eta: { eta_minutes: 14, confidence_pct: 96.0, display: "Estimated Arrival: 14 mins (Confidence: 96%)" },
  },
  {
    id: "4", name: "Safe Gas Service", phone: "9876543230", service_category: "Gas Service",
    rating: 4.9, total_reviews: 187, is_available: true, is_verified: true,
    experience_years: 12, address: "Porur, Chennai", city: "Chennai", distance_km: 4.5,
    latitude: 13.034, longitude: 80.157, rank: 1,
    cancellation_rate: 0.01, response_delay_avg: 5.0, rating_stability: 0.97,
    availability_score: 0.98, verification_age_days: 730, weighted_score: 0.09,
    tti: { tti_score: 98.3, reliability_label: "Highly Reliable", display: "Trust Score: 98.3% (Highly Reliable)" },
    eta: { eta_minutes: 12, confidence_pct: 97.0, display: "Estimated Arrival: 12 mins (Confidence: 97%)" },
  },
  {
    id: "5", name: "Speed Bike Works", phone: "9876543240", service_category: "Bike Mechanic",
    rating: 4.7, total_reviews: 165, is_available: true, is_verified: true,
    experience_years: 9, address: "Perambur, Chennai", city: "Chennai", distance_km: 5.8,
    latitude: 13.118, longitude: 80.244, rank: 1,
    cancellation_rate: 0.04, response_delay_avg: 15.0, rating_stability: 0.83,
    availability_score: 0.87, verification_age_days: 390, weighted_score: 0.29,
    tti: { tti_score: 84.7, reliability_label: "Reliable", display: "Trust Score: 84.7% (Reliable)" },
    eta: { eta_minutes: 40, confidence_pct: 83.0, display: "Estimated Arrival: 40 mins (Confidence: 83%)" },
  },
  {
    id: "6", name: "Phone Doctor", phone: "9876543250", service_category: "Mobile Technician",
    rating: 4.8, total_reviews: 203, is_available: true, is_verified: true,
    experience_years: 6, address: "Kodambakkam, Chennai", city: "Chennai", distance_km: 2.9,
    latitude: 13.053, longitude: 80.221, rank: 1,
    cancellation_rate: 0.02, response_delay_avg: 10.0, rating_stability: 0.91,
    availability_score: 0.93, verification_age_days: 620, weighted_score: 0.15,
    tti: { tti_score: 92.8, reliability_label: "Highly Reliable", display: "Trust Score: 92.8% (Highly Reliable)" },
    eta: { eta_minutes: 26, confidence_pct: 91.0, display: "Estimated Arrival: 26 mins (Confidence: 91%)" },
  },
  {
    id: "7", name: "Cool Air Services", phone: "9876543270", service_category: "AC Technician",
    rating: 4.8, total_reviews: 156, is_available: true, is_verified: true,
    experience_years: 8, address: "Sholinganallur, Chennai", city: "Chennai", distance_km: 6.2,
    latitude: 12.899, longitude: 80.227, rank: 1,
    cancellation_rate: 0.02, response_delay_avg: 12.0, rating_stability: 0.90,
    availability_score: 0.93, verification_age_days: 580, weighted_score: 0.21,
    tti: { tti_score: 93.5, reliability_label: "Highly Reliable", display: "Trust Score: 93.5% (Highly Reliable)" },
    eta: { eta_minutes: 35, confidence_pct: 90.0, display: "Estimated Arrival: 35 mins (Confidence: 90%)" },
  },
  {
    id: "8", name: "CleanHome TN", phone: "9876543260", service_category: "Cleaning Service",
    rating: 4.7, total_reviews: 178, is_available: true, is_verified: true,
    experience_years: 5, address: "OMR, Chennai", city: "Chennai", distance_km: 7.1,
    latitude: 12.899, longitude: 80.226, rank: 1,
    cancellation_rate: 0.03, response_delay_avg: 20.0, rating_stability: 0.86,
    availability_score: 0.89, verification_age_days: 450, weighted_score: 0.30,
    tti: { tti_score: 87.2, reliability_label: "Reliable", display: "Trust Score: 87.2% (Reliable)" },
    eta: { eta_minutes: 65, confidence_pct: 80.0, display: "Estimated Arrival: 65 mins (Confidence: 80%)" },
  },
];

// ─── Helper: compute mock emergency risk ──────────────────────────────────────
function computeMockRisk(category) {
  const riskMap = {
    "Gas Service": 92, "Electrician": 75, "Plumber": 45,
    "Bike Mechanic": 30, "Mobile Technician": 15,
    "AC Technician": 25, "Cleaning Service": 5, "Carpenter": 10, "Painter": 5,
  };
  const pct = riskMap[category] || 10;
  const level = pct >= 75 ? "Critical" : pct >= 50 ? "High" : pct >= 25 ? "Medium" : "Low";
  const icons = { Critical: "🔴", High: "🟠", Medium: "🟡", Low: "🟢" };
  return { percentage: pct, level, icon: icons[level] };
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function EmergencyRiskBanner({ risk, t }) {
  if (!risk) return null;
  const c = SEVERITY_COLORS[risk.level] || SEVERITY_COLORS.Low;
  return (
    <div style={{
      background: c.bg, border: `1px solid ${c.border}`,
      borderRadius: 12, padding: "14px 18px", marginBottom: 16,
      display: "flex", alignItems: "center", gap: 14,
      animation: "fadeIn 0.4s ease",
    }}>
      <div style={{ fontSize: 26 }}>{risk.icon}</div>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 700, fontSize: 14, color: c.text, marginBottom: 2 }}>
          {t('search.riskLabel')}: {risk.percentage}% ({risk.level})
        </div>
        <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", lineHeight: 1.5 }}>
          {risk.level === "Critical" && t('search.riskMessages.Critical')}
          {risk.level === "High"     && t('search.riskMessages.High')}
          {risk.level === "Medium"   && t('search.riskMessages.Medium')}
          {risk.level === "Low"      && t('search.riskMessages.Low')}
        </div>
      </div>
      <div style={{
        fontSize: 22, fontWeight: 800, color: c.text,
        minWidth: 52, textAlign: "center",
      }}>
        {risk.percentage}%
      </div>
    </div>
  );
}

function RadiusExpansionNotice({ expanded, radiusKm, steps, t }) {
  if (!expanded) return null;
  return (
    <div style={{
      background: "rgba(59,130,246,0.08)", border: "1px solid rgba(59,130,246,0.25)",
      borderRadius: 10, padding: "10px 14px", marginBottom: 12,
      fontSize: 13, color: "#60A5FA", display: "flex", alignItems: "center", gap: 8,
    }}>
      <span>🔭</span>
      <span>
        {t('search.radiusExpanded')} <strong>{radiusKm} km</strong>.
        {steps && steps.length > 1 && (
          <> {t('search.radiusStepsTried')}: {steps.map(s => `${s}km`).join(" → ")}</>
        )}
      </span>
    </div>
  );
}

function SearchIntelPanel({ totalFound, radiusKm, category, t }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 12,
      marginBottom: 16, flexWrap: "wrap",
    }}>
      <div style={{
        padding: "6px 14px", background: "rgba(249,115,22,0.08)",
        border: "1px solid rgba(249,115,22,0.2)", borderRadius: 100,
        fontSize: 12, color: "#F97316", fontWeight: 600,
      }}>
        {CATEGORY_ICONS[category] || "🔧"} {totalFound} {t('search.foundLabel')}
      </div>
      <div style={{
        padding: "6px 14px", background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.1)", borderRadius: 100,
        fontSize: 12, color: "rgba(255,255,255,0.5)",
      }}>
        📡 {t('search.withinKm')} {radiusKm} km · {t('search.rankedLabel')}
      </div>
      <div style={{
        padding: "6px 14px", background: "rgba(16,185,129,0.07)",
        border: "1px solid rgba(16,185,129,0.2)", borderRadius: 100,
        fontSize: 12, color: "#10B981",
      }}>
        🛡 {t('search.ttiLabel')}
      </div>
    </div>
  );
}

// ─── Main Search Page ─────────────────────────────────────────────────────────
export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { t } = useTranslation();
  const [category, setCategory]       = useState(searchParams.get("category") || "Plumber");
  const [radius, setRadius]           = useState(3);
  const [query, setQuery]             = useState(searchParams.get("q") || "");
  const [technicians, setTechnicians] = useState([]);
  const [loading, setLoading]         = useState(false);
  const [userLocation, setUserLocation] = useState(null);
  const [locationError, setLocationError] = useState("");
  const [useMock, setUseMock]         = useState(false);
  const [searchMeta, setSearchMeta]   = useState(null);
  const [emergencyRisk, setEmergencyRisk] = useState(null);
  const [radiusExpanded, setRadiusExpanded] = useState(false);
  const [finalRadius, setFinalRadius] = useState(radius);
  const [expansionSteps, setExpansionSteps] = useState([]);
  const searchRef = useRef(null);

  const isEmergency = EMERGENCY_CATEGORIES.includes(category);

  // Fetch technicians - memoized with explicit params to avoid dependency issues
  const fetchTechnicians = useCallback(async (lat, lon, selectedCategory, selectedRadius, searchQuery) => {
    if (!lat || !lon || !selectedCategory) return;
    
    setLoading(true);
    try {
      const res = await getNearbyTechnicians(lat, lon, selectedCategory, selectedRadius, "Low", searchQuery);
      const data = res.data;
      
      if (!data) {
        throw new Error("No data returned from API");
      }
      
      setTechnicians(Array.isArray(data.technicians) ? data.technicians : []);
      setEmergencyRisk(data.emergency_risk || null);
      setRadiusExpanded(data.radius_expanded === true);
      setFinalRadius(data.search_radius_km || selectedRadius);
      setExpansionSteps(Array.isArray(data.expansion_steps) ? data.expansion_steps : []);
      setSearchMeta({ total: data.total_found || 0, lat, lon });
      setUseMock(false);
    } catch (error) {
      console.error("[Search Error]", error);
      // Fallback to mock data
      const filtered = MOCK_TECHNICIANS.filter((t) => t.service_category === selectedCategory);
      setTechnicians(filtered);
      setEmergencyRisk(computeMockRisk(selectedCategory));
      setRadiusExpanded(false);
      setFinalRadius(selectedRadius);
      setExpansionSteps([selectedRadius]);
      setSearchMeta({ total: filtered.length, lat, lon });
      setUseMock(true);
    } finally {
      setLoading(false);
    }
  }, []);

  // Get user location and fetch technicians  
  const getLocation = useCallback(() => {
    setLocationError("");
    
    const performSearch = (lat, lon) => {
      fetchTechnicians(lat, lon, category, radius, query);
    };
    
    if (!navigator.geolocation) {
      setLocationError(t('search.locationFallback'));
      const chennai = [13.0827, 80.2707];
      setUserLocation(chennai);
      performSearch(chennai[0], chennai[1]);
      return;
    }
    
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        setUserLocation([latitude, longitude]);
        performSearch(latitude, longitude);
      },
      (error) => {
        console.warn("[Geolocation Error]", error);
        setLocationError(t('search.locationError'));
        const fallback = [13.0827, 80.2707];
        setUserLocation(fallback);
        performSearch(fallback[0], fallback[1]);
      }
    );
  }, [t, fetchTechnicians, category, radius, query]);

  // Effect: Re-fetch when category, radius or query changes
  useEffect(() => {
    getLocation();
  }, [getLocation]);

  const handleSearch = (e) => {
    if (e) e.preventDefault();
    setSearchParams({ category, q: query });
    
    if (userLocation) {
      fetchTechnicians(userLocation[0], userLocation[1], category, radius, query);
    } else {
      getLocation();
    }
  };

  return (
    <div className="search-page">
      {/* ── Search Controls ── */}
      <div className="search-header">
        <div className="search-controls">
          <select
            id="category-select"
            className="select-input"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>{CATEGORY_ICONS[c]} {c}</option>
            ))}
          </select>

          <select
            id="radius-select"
            className="select-input"
            value={radius}
            onChange={(e) => setRadius(Number(e.target.value))}
          >
            <option value={3}>{t('search.radius3')}</option>
            <option value={5}>{t('search.radius5')}</option>
            <option value={8}>{t('search.radius8')}</option>
            <option value={15}>{t('search.radius15')}</option>
            <option value={30}>{t('search.radius30')}</option>
          </select>

          <input
            className="select-input"
            style={{ flex: 1, minWidth: 180 }}
            placeholder={t('search.problemPlaceholder')}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            ref={searchRef}
          />

          <button id="search-btn" className="btn-search" onClick={handleSearch}>
            {t('search.searchBtn')}
          </button>
          <button
            id="location-btn"
            className="btn-search"
            style={{
              background: "var(--bg-card)",
              border: "1px solid var(--border-subtle)",
              color: "var(--text-primary)",
            }}
            onClick={getLocation}
          >
            {t('search.myLocation')}
          </button>
        </div>
      </div>

      {/* ── Main Layout ── */}
      <div className="search-layout">
        {/* Results Panel */}
        <div className="results-panel">

          {/* Emergency Category Banner */}
          {isEmergency && (
            <div className="emergency-banner">
              <span className="icon">🚨</span>
              <div>
                <h4>{t('search.emergencyDetected')}</h4>
                <p>
                  {t('search.emergencyNote')}
                </p>
              </div>
            </div>
          )}

          {/* Emergency Risk Score */}
          <EmergencyRiskBanner risk={emergencyRisk} t={t} />

          {/* Radius Expansion Notice */}
          <RadiusExpansionNotice
            expanded={radiusExpanded}
            radiusKm={finalRadius}
            steps={expansionSteps}
            t={t}
          />

          {/* Location error */}
          {locationError && (
            <div style={{
              padding: "10px 14px", background: "rgba(245,158,11,0.1)",
              border: "1px solid rgba(245,158,11,0.3)", borderRadius: 8,
              fontSize: 13, color: "#F59E0B", marginBottom: 12,
            }}>
              ⚠️ {locationError}
            </div>
          )}

          {/* Demo mode notice */}
          {useMock && (
            <div style={{
              padding: "10px 14px", background: "rgba(59,130,246,0.08)",
              border: "1px solid rgba(59,130,246,0.25)", borderRadius: 8,
              fontSize: 13, color: "#3B82F6", marginBottom: 12,
            }}>
              {t('search.demoMode')}
            </div>
          )}

          {/* Intelligence summary row */}
          {!loading && searchMeta && (
            <SearchIntelPanel
              totalFound={searchMeta.total}
              radiusKm={finalRadius}
              category={category}
              t={t}
            />
          )}

          {/* Results */}
          {loading ? (
            <div style={{ textAlign: "center", padding: 40 }}>
              <div className="loading-spinner" />
              <p style={{ color: "var(--text-muted)", marginTop: 12, fontSize: 13 }}>
                {t('search.searching')}
              </p>
            </div>
          ) : technicians.length === 0 ? (
            <div className="empty-state">
              <div className="icon">🔍</div>
              <h3>{t('search.noTechnicians')}</h3>
              <p>{t('search.noTechSubtitle')}</p>
            </div>
          ) : (
            <div className="results-list">
              {technicians.map((t) => (
                <TechnicianCard
                  key={t.id}
                  technician={t}
                  onCall={(tech) => window.open(`tel:${tech.phone}`)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Map Panel */}
        <div className="map-panel">
          <MapView userLocation={userLocation} technicians={technicians} searchRadiusKm={finalRadius} />
        </div>
      </div>
    </div>
  );
}
