import axios from "axios";

// Get API base URL from environment variable (set in .env files)
// Defaults to localhost if not set (for development)
const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ─── Auth APIs ────────────────────────────────────────────────────────────────

export function registerUser(data) {
  return axios.post(`${BASE}/auth/register`, data);
}

export function loginUser(identifier, password) {
  return axios.post(`${BASE}/auth/login/user`, { identifier, password });
}

export function loginTechnician(identifier, password) {
  return axios.post(`${BASE}/auth/login/technician`, { identifier, password });
}

export function loginAdmin(mobile, aadhaar, password) {
  return axios.post(`${BASE}/auth/login/admin`, { mobile, aadhaar, password });
}

// ─── Dashboard APIs ──────────────────────────────────────────────────────────

export function getUserDashboard(token) {
  return axios.get(`${BASE}/dashboard/user`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function getTechnicianDashboard(token) {
  return axios.get(`${BASE}/dashboard/technician`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

// ─── Admin APIs ───────────────────────────────────────────────────────────────

export function getAdminDashboard(token) {
  return axios.get(`${BASE}/admin/dashboard`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function getAdminUsers(token) {
  return axios.get(`${BASE}/admin/users`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function toggleUser(token, userId) {
  return axios.patch(`${BASE}/admin/users/${userId}/toggle`, {}, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function getAdminTechnicians(token) {
  return axios.get(`${BASE}/admin/technicians`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function verifyTechnician(token, techId) {
  return axios.patch(`${BASE}/admin/technicians/${techId}/verify`, {}, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function deleteTechnician(token, techId) {
  return axios.delete(`${BASE}/admin/technicians/${techId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}
