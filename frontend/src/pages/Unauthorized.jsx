import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Unauthorized() {
  const navigate = useNavigate();
  const { role, logout } = useAuth();

  return (
    <div className="unauthorized-page">
      <div className="unauthorized-card">
        <div className="unauthorized-icon">🔒</div>
        <h1>Access Denied</h1>
        <p>You don't have permission to view this page.</p>
        <p className="unauthorized-role">Your role: <strong>{role || "Unknown"}</strong></p>
        <div className="unauthorized-actions">
          <button onClick={() => navigate(-1)} className="btn-unauth-back" id="unauth-back-btn">
            ← Go Back
          </button>
          <button onClick={() => { logout(); navigate("/login"); }} className="btn-unauth-logout" id="unauth-logout-btn">
            Sign In as Different Role
          </button>
        </div>
      </div>
    </div>
  );
}
