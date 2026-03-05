import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 12000,
});

// Attach token if available
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("sevai_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ─── Services ─────────────────────────────────────────────────────────────────
export const getServices = () => API.get("/services/");

// ─── Technicians ──────────────────────────────────────────────────────────────

/**
 * Adaptive nearby search — returns NearbySearchResponse with TTI, ETA,
 * weighted scores, emergency risk, and radius expansion info.
 */
export const getNearbyTechnicians = (
  latitude,
  longitude,
  service_category,
  radius_km = 3,
  urgency_level = "Low",
  emergency_query = ""
) =>
  API.get("/technicians/nearby", {
    params: {
      latitude,
      longitude,
      service_category,
      radius_km,
      urgency_level,
      ...(emergency_query ? { emergency_query } : {}),
    },
  });

export const getTechnicianById = (id) => API.get(`/technicians/${id}`);
export const listTechnicians = (category, skip = 0, limit = 20) =>
  API.get("/technicians/", { params: { category, skip, limit } });

// ─── Intelligence Endpoints ───────────────────────────────────────────────────

/** Score a user's problem text for emergency risk. */
export const scoreEmergencyRisk = (query) => 
  API.get("/intelligence/emergency/score", { params: { query } });

/** Get complete intelligence dashboard — live platform summary. */
export const getIntelligenceDashboard = () => 
  API.get("/intelligence/dashboard");

/** Get urban service demand heatmap. */
export const getServiceDemandHeatmap = () => 
  API.get("/intelligence/heatmap");

/** Simulate emergency allocation under load. */
export const simulateAllocation = (concurrent_requests = 100, scenario = "mixed") =>
  API.get("/intelligence/simulate", { params: { concurrent_requests, scenario } });

/** Explain TTI calculation with step-by-step breakdown. */
export const explainTTI = (
  cancellation_rate = 0.05,
  response_delay_avg = 15.0,
  rating_stability = 0.80,
  availability_score = 0.85,
  verification_age_days = 365
) =>
  API.get("/intelligence/tti/explain", {
    params: {
      cancellation_rate,
      response_delay_avg,
      rating_stability,
      availability_score,
      verification_age_days,
    },
  });

/** Explain weighted allocation formula step-by-step. */
export const explainWeightedAllocation = (
  distance_km = 3.0,
  rating = 4.5,
  tti_score = 85.0,
  emergency_risk = 0.0
) =>
  API.get("/intelligence/weighted/explain", {
    params: { distance_km, rating, tti_score, emergency_risk },
  });

/** Get system performance transparency report. */
export const getPerformanceReport = () => 
  API.get("/intelligence/performance");

/** Get intelligence modules version and status. */
export const getIntelligenceVersion = () => 
  API.get("/intelligence/version");

/** Compute TTI for arbitrary input (simulation / demo). */
export const calculateTTI = (params) =>
  API.get("/technicians/tti/calculate", { params });

// ─── Auth ─────────────────────────────────────────────────────────────────────
export const registerUser = (data) => API.post("/auth/register", data);
export const loginUser = (data) => API.post("/auth/login", data);

export default API;
