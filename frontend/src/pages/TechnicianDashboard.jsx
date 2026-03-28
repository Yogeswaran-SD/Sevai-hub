import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { getTechnicianDashboard } from "../api/authApi";

const MOCK_REQUESTS = [
  { id: 1, customer: "Raj Kumar",    service: "Plumber",     time: "Today, 10:30 AM", status: "pending",   location: "Anna Nagar" },
  { id: 2, customer: "Meena S.",     service: "Plumber",     time: "Today, 09:00 AM", status: "completed", location: "T Nagar"    },
  { id: 3, customer: "Arjun Reddy",  service: "Plumber",     time: "Yesterday",       status: "cancelled", location: "Velachery"  },
];

const STATUS_COLORS = {
  pending:   { bg: "rgba(245,158,11,0.12)",  text: "#F59E0B", label: "⏳ Pending"   },
  completed: { bg: "rgba(16,185,129,0.12)",  text: "#10B981", label: "✅ Completed" },
  cancelled: { bg: "rgba(239,68,68,0.12)",   text: "#EF4444", label: "❌ Cancelled" },
};

export default function TechnicianDashboard() {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();
  const [data,    setData]    = useState(null);
  const [mounted, setMounted] = useState(false);
  const [avail,   setAvail]   = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setMounted(true);
    getTechnicianDashboard(token)
      .then(r => {
        setData(r.data);
        setAvail(r.data.is_available ?? true);
      })
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [token]);

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className={`dashboard-page ${mounted ? "dashboard-page--visible" : ""}`}>
      {/* Sidebar */}
      <aside className="dashboard-sidebar dashboard-sidebar--technician">
        <div className="sidebar-brand">
          <div className="sidebar-logo">🔧</div>
          <span>Sevai Hub</span>
        </div>

        <nav className="sidebar-nav">
          <div className="sidebar-nav-item sidebar-nav-item--active">
            <span>📋</span> My Requests
          </div>
          <div className="sidebar-nav-item">
            <span>📞</span> Contact History
          </div>
          <div className="sidebar-nav-item">
            <span>📊</span> Performance
          </div>
          <div className="sidebar-nav-item" onClick={() => navigate("/")}>
            <span>🌐</span> Home
          </div>
        </nav>

        {/* Availability Toggle */}
        <div className="sidebar-availability">
          <span>Availability</span>
          <div
            className={`avail-toggle ${avail ? "avail-toggle--on" : "avail-toggle--off"}`}
            onClick={() => setAvail(a => !a)}
            id="avail-toggle-btn"
          >
            <div className="avail-toggle-thumb" />
          </div>
          <span className={avail ? "avail-label--on" : "avail-label--off"}>
            {avail ? "Available" : "Offline"}
          </span>
        </div>

        <div className="sidebar-user-info">
          <div className="sidebar-avatar sidebar-avatar--tech">
            {user?.name?.charAt(0)?.toUpperCase() || "T"}
          </div>
          <div>
            <div className="sidebar-user-name">{user?.name || "Technician"}</div>
            <div className="sidebar-user-role">🔧 Technician</div>
          </div>
        </div>

        <button className="sidebar-logout" onClick={handleLogout} id="tech-logout-btn">
          🚪 Sign Out
        </button>
      </aside>

      {/* Main */}
      <main className="dashboard-main">
        <div className="dashboard-header">
          <div>
            <h1 className="dashboard-title">
              Technician Panel — <span>{user?.name || "Pro"}</span>
            </h1>
            <p className="dashboard-subtitle">Manage your service requests and availability</p>
          </div>
          <div className="dashboard-header-badge dashboard-header-badge--tech">
            🔧 Technician Zone
          </div>
        </div>

        {/* Stats */}
        <div className="dashboard-stats">
          {[
            { icon: "📋", label: "Pending Requests", value: "3"    },
            { icon: "✅", label: "Completed Today",  value: "7"    },
            { icon: "⭐", label: "My Rating",        value: data?.rating ? `${data.rating}★` : "4.5★" },
            { icon: "📍", label: "My City",          value: data?.city || "Chennai" },
          ].map((s, i) => (
            <div className="dash-stat-card dash-stat-card--tech" key={i}
                 style={{ animationDelay: `${i * 0.08}s` }}>
              <div className="dash-stat-icon">{s.icon}</div>
              <div className="dash-stat-value">{s.value}</div>
              <div className="dash-stat-label">{s.label}</div>
            </div>
          ))}
        </div>

        {/* Requests */}
        <div className="dashboard-section">
          <h2>📋 Customer Requests</h2>
          <div className="dash-requests-list">
            {loading ? (
              <div className="dash-loading">
                <div className="dash-loading-dots">
                  <span/><span/><span/>
                </div>
                <p>Loading requests…</p>
              </div>
            ) : (
              MOCK_REQUESTS.map(req => {
                const s = STATUS_COLORS[req.status];
                return (
                  <div className="dash-request-card" key={req.id}
                       id={`request-${req.id}`}>
                    <div className="req-info">
                      <div className="req-customer">{req.customer}</div>
                      <div className="req-meta">
                        <span>🔧 {req.service}</span>
                        <span>📍 {req.location}</span>
                        <span>🕐 {req.time}</span>
                      </div>
                    </div>
                    <div className="req-status"
                         style={{ background: s.bg, color: s.text }}>
                      {s.label}
                    </div>
                    {req.status === "pending" && (
                      <div className="req-actions">
                        <button className="req-btn req-btn--accept">✅ Accept</button>
                        <button className="req-btn req-btn--decline">❌ Decline</button>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Interaction Log */}
        <div className="dashboard-section">
          <h2>📞 Recent Contact History</h2>
          <div className="dash-contact-log">
            {["Raj Kumar — 10:30 AM — Called", "Meena S. — 09:00 AM — Completed job", "Arjun Reddy — Yesterday — Cancelled"].map((entry, i) => (
              <div className="contact-log-entry" key={i}>
                <div className="contact-log-dot" />
                <span>{entry}</span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
