import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const SERVICE_TILES = [
  { icon: "🔧", name: "Plumber",          color: "#3B82F6", desc: "Pipe & tap repair" },
  { icon: "⚡", name: "Electrician",       color: "#F59E0B", desc: "Wiring & circuits" },
  { icon: "🔥", name: "Gas Service",       color: "#EF4444", desc: "Gas & stoves" },
  { icon: "🏍️", name: "Bike Mechanic",    color: "#8B5CF6", desc: "Engine & repairs" },
  { icon: "📱", name: "Mobile Technician", color: "#06B6D4", desc: "Screen & battery" },
  { icon: "🧹", name: "Cleaning Service",  color: "#10B981", desc: "Deep cleaning" },
  { icon: "❄️", name: "AC Technician",    color: "#60A5FA", desc: "AC service & gas" },
  { icon: "🪚", name: "Carpenter",         color: "#D97706", desc: "Furniture & doors" },
  { icon: "🎨", name: "Painter",           color: "#EC4899", desc: "Wall painting" },
];

export default function UserDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mounted, setMounted] = useState(false);
  const [query,   setQuery]   = useState("");

  useEffect(() => { setMounted(true); }, []);

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  const filtered = query.trim()
    ? SERVICE_TILES.filter(s => s.name.toLowerCase().includes(query.toLowerCase()))
    : SERVICE_TILES;

  return (
    <div className={`dashboard-page ${mounted ? "dashboard-page--visible" : ""}`}>
      {/* Sidebar */}
      <aside className="dashboard-sidebar dashboard-sidebar--user">
        <div className="sidebar-brand">
          <div className="sidebar-logo">🛠️</div>
          <span>Sevai Hub</span>
        </div>

        <nav className="sidebar-nav">
          <div className="sidebar-nav-item sidebar-nav-item--active">
            <span>🏠</span> Dashboard
          </div>
          <div className="sidebar-nav-item" onClick={() => navigate("/search")}>
            <span>🔍</span> Find Services
          </div>
          <div className="sidebar-nav-item" onClick={() => navigate("/")}>
            <span>🌐</span> Home
          </div>
        </nav>

        <div className="sidebar-user-info">
          <div className="sidebar-avatar">
            {user?.name?.charAt(0)?.toUpperCase() || "U"}
          </div>
          <div>
            <div className="sidebar-user-name">{user?.name || "User"}</div>
            <div className="sidebar-user-role">👤 Service User</div>
          </div>
        </div>

        <button className="sidebar-logout" onClick={handleLogout} id="user-logout-btn">
          🚪 Sign Out
        </button>
      </aside>

      {/* Main Content */}
      <main className="dashboard-main">
        {/* Header */}
        <div className="dashboard-header">
          <div>
            <h1 className="dashboard-title">
              Welcome back, <span>{user?.name || "User"}!</span>
            </h1>
            <p className="dashboard-subtitle">What service do you need today?</p>
          </div>
          <div className="dashboard-header-badge dashboard-header-badge--user">
            👤 User Zone
          </div>
        </div>

        {/* Stats Row */}
        <div className="dashboard-stats">
          {[
            { icon: "🔧", label: "Services Available", value: "9" },
            { icon: "⚡", label: "Avg Response Time",  value: "15 min" },
            { icon: "⭐", label: "Platform Rating",    value: "4.8★" },
            { icon: "📍", label: "Districts Covered",  value: "38" },
          ].map((s, i) => (
            <div className="dash-stat-card" key={i} style={{ animationDelay: `${i * 0.08}s` }}>
              <div className="dash-stat-icon">{s.icon}</div>
              <div className="dash-stat-value">{s.value}</div>
              <div className="dash-stat-label">{s.label}</div>
            </div>
          ))}
        </div>

        {/* Service Search */}
        <div className="dashboard-section">
          <div className="dashboard-section-header">
            <h2>🔍 Discover Services</h2>
            <input
              className="dash-search-input"
              type="text"
              placeholder="Search services…"
              value={query}
              onChange={e => setQuery(e.target.value)}
              id="user-service-search"
            />
          </div>

          <div className="dash-services-grid">
            {filtered.map((s, i) => (
              <div
                key={s.name}
                className="dash-service-card"
                style={{ "--card-color": s.color, animationDelay: `${i * 0.06}s` }}
                onClick={() => navigate(`/search?q=${encodeURIComponent(s.name)}`)}
                id={`service-card-${s.name.replace(/\s+/g, "-").toLowerCase()}`}
              >
                <div className="dash-service-icon">{s.icon}</div>
                <div className="dash-service-name">{s.name}</div>
                <div className="dash-service-desc">{s.desc}</div>
                <div className="dash-service-arrow">Find Now →</div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="dashboard-section">
          <h2>⚡ Quick Actions</h2>
          <div className="dash-actions">
            <button className="dash-action-btn" onClick={() => navigate("/search")} id="user-find-btn">
              🔍 Find Technicians Near Me
            </button>
            <button className="dash-action-btn dash-action-btn--secondary" onClick={() => navigate("/")} id="user-home-btn">
              🌐 Back to Home
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
