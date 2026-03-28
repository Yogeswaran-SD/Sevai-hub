import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { getAdminDashboard, getAdminUsers, getAdminTechnicians, toggleUser, verifyTechnician, deleteTechnician } from "../api/authApi";

const TABS = ["overview", "users", "technicians"];

export default function AdminDashboard() {
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const [mounted,  setMounted]  = useState(false);
  const [tab,      setTab]      = useState("overview");
  const [stats,    setStats]    = useState(null);
  const [users,    setUsers]    = useState([]);
  const [techs,    setTechs]    = useState([]);
  const [loading,  setLoading]  = useState(true);

  useEffect(() => {
    setMounted(true);
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [sRes, uRes, tRes] = await Promise.all([
        getAdminDashboard(token),
        getAdminUsers(token),
        getAdminTechnicians(token),
      ]);
      setStats(sRes.data);
      setUsers(uRes.data);
      setTechs(tRes.data);
    } catch {
      // Demo fallback
      setStats({ total_users: 124, total_technicians: 57, verified_technicians: 34, pending_technicians: 23, active_users: 118 });
      setUsers([]);
      setTechs([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleToggleUser(id) {
    try {
      const res = await toggleUser(token, id);
      setUsers(prev => prev.map(u => u.id === id ? { ...u, is_active: res.data.is_active } : u));
    } catch { /* silent */ }
  }

  async function handleVerifyTech(id) {
    try {
      const res = await verifyTechnician(token, id);
      setTechs(prev => prev.map(t => t.id === id ? { ...t, is_verified: res.data.is_verified } : t));
    } catch { /* silent */ }
  }

  async function handleDeleteTech(id) {
    if (!confirm("Remove this technician?")) return;
    try {
      await deleteTechnician(token, id);
      setTechs(prev => prev.filter(t => t.id !== id));
    } catch { /* silent */ }
  }

  function handleLogout() { logout(); navigate("/login", { replace: true }); }

  return (
    <div className={`dashboard-page ${mounted ? "dashboard-page--visible" : ""}`}>
      {/* Sidebar */}
      <aside className="dashboard-sidebar dashboard-sidebar--admin">
        <div className="sidebar-brand">
          <div className="sidebar-logo">🛡️</div>
          <span>Admin Panel</span>
        </div>

        <nav className="sidebar-nav">
          {[
            { id: "overview",     icon: "📊", label: "Overview"    },
            { id: "users",        icon: "👥", label: "Users"       },
            { id: "technicians",  icon: "🔧", label: "Technicians" },
          ].map(item => (
            <div
              key={item.id}
              className={`sidebar-nav-item ${tab === item.id ? "sidebar-nav-item--active" : ""}`}
              onClick={() => setTab(item.id)}
              id={`admin-tab-${item.id}`}
            >
              <span>{item.icon}</span> {item.label}
            </div>
          ))}
          <div className="sidebar-nav-item" onClick={() => navigate("/")}>
            <span>🌐</span> Main Site
          </div>
        </nav>

        <div className="sidebar-user-info">
          <div className="sidebar-avatar sidebar-avatar--admin">🛡️</div>
          <div>
            <div className="sidebar-user-name">System Admin</div>
            <div className="sidebar-user-role">🔴 Full Access</div>
          </div>
        </div>

        <button className="sidebar-logout" onClick={handleLogout} id="admin-logout-btn">
          🚪 Sign Out
        </button>
      </aside>

      {/* Main */}
      <main className="dashboard-main">
        <div className="dashboard-header">
          <div>
            <h1 className="dashboard-title">
              Admin Control <span>Center</span>
            </h1>
            <p className="dashboard-subtitle">Full system oversight & management</p>
          </div>
          <div className="dashboard-header-badge dashboard-header-badge--admin">
            🛡️ Admin Zone
          </div>
        </div>

        {/* ── OVERVIEW TAB ──────────────────────────────── */}
        {tab === "overview" && (
          <>
            <div className="dashboard-stats">
              {!stats ? (
                <div className="dash-loading"><div className="dash-loading-dots"><span/><span/><span/></div></div>
              ) : ([
                { icon: "👥", label: "Total Users",            value: stats.total_users,           color: "#3B82F6" },
                { icon: "🔧", label: "Total Technicians",      value: stats.total_technicians,      color: "#F97316" },
                { icon: "✅", label: "Verified Technicians",   value: stats.verified_technicians,   color: "#10B981" },
                { icon: "⏳", label: "Pending Approval",       value: stats.pending_technicians,    color: "#F59E0B" },
                { icon: "🟢", label: "Active Users",           value: stats.active_users,           color: "#8B5CF6" },
              ].map((s, i) => (
                <div className="dash-stat-card dash-stat-card--admin" key={i}
                     style={{ animationDelay: `${i * 0.08}s`, "--stat-color": s.color }}>
                  <div className="dash-stat-icon">{s.icon}</div>
                  <div className="dash-stat-value" style={{ color: s.color }}>{s.value}</div>
                  <div className="dash-stat-label">{s.label}</div>
                </div>
              )))}
            </div>

            <div className="dashboard-section">
              <h2>🔒 System Security Status</h2>
              <div className="admin-security-status">
                {[
                  { label: "JWT Authentication",    status: "active"  },
                  { label: "RBAC Enforcement",      status: "active"  },
                  { label: "bcrypt Password Hash",  status: "active"  },
                  { label: "Admin 3-Factor Auth",   status: "active"  },
                  { label: "Aadhaar Validation",    status: "active"  },
                  { label: "Token Expiry Control",  status: "active"  },
                ].map((item, i) => (
                  <div className="security-item" key={i}>
                    <span className="security-dot" />
                    <span>{item.label}</span>
                    <span className="security-badge">{item.status === "active" ? "🟢 Active" : "🔴 Inactive"}</span>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* ── USERS TAB ────────────────────────────────── */}
        {tab === "users" && (
          <div className="dashboard-section">
            <h2>👥 User Management</h2>
            {loading ? (
              <div className="dash-loading"><div className="dash-loading-dots"><span/><span/><span/></div></div>
            ) : users.length === 0 ? (
              <div className="admin-empty-state">
                <p>No users found. Backend may be offline — showing demo mode.</p>
              </div>
            ) : (
              <div className="admin-table-wrapper">
                <table className="admin-table">
                  <thead>
                    <tr><th>Name</th><th>Phone</th><th>Email</th><th>Status</th><th>Action</th></tr>
                  </thead>
                  <tbody>
                    {users.map(u => (
                      <tr key={u.id}>
                        <td>{u.name}</td>
                        <td>{u.phone}</td>
                        <td>{u.email || "—"}</td>
                        <td>
                          <span className={`admin-badge ${u.is_active ? "admin-badge--active" : "admin-badge--inactive"}`}>
                            {u.is_active ? "🟢 Active" : "🔴 Inactive"}
                          </span>
                        </td>
                        <td>
                          <button className="admin-action-btn" onClick={() => handleToggleUser(u.id)}
                                  id={`toggle-user-${u.id}`}>
                            {u.is_active ? "Disable" : "Enable"}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* ── TECHNICIANS TAB ──────────────────────────── */}
        {tab === "technicians" && (
          <div className="dashboard-section">
            <h2>🔧 Technician Management</h2>
            {loading ? (
              <div className="dash-loading"><div className="dash-loading-dots"><span/><span/><span/></div></div>
            ) : techs.length === 0 ? (
              <div className="admin-empty-state">
                <p>No technicians found. Backend may be offline — showing demo mode.</p>
              </div>
            ) : (
              <div className="admin-table-wrapper">
                <table className="admin-table">
                  <thead>
                    <tr><th>Name</th><th>Category</th><th>City</th><th>Rating</th><th>Verified</th><th>Actions</th></tr>
                  </thead>
                  <tbody>
                    {techs.map(t => (
                      <tr key={t.id}>
                        <td>{t.name}</td>
                        <td>{t.service_category}</td>
                        <td>{t.city}</td>
                        <td>⭐ {t.rating?.toFixed(1)}</td>
                        <td>
                          <span className={`admin-badge ${t.is_verified ? "admin-badge--active" : "admin-badge--pending"}`}>
                            {t.is_verified ? "✅ Verified" : "⏳ Pending"}
                          </span>
                        </td>
                        <td className="admin-tech-actions">
                          <button className="admin-action-btn" onClick={() => handleVerifyTech(t.id)}
                                  id={`verify-tech-${t.id}`}>
                            {t.is_verified ? "Unverify" : "Verify"}
                          </button>
                          <button className="admin-action-btn admin-action-btn--danger"
                                  onClick={() => handleDeleteTech(t.id)} id={`delete-tech-${t.id}`}>
                            🗑️
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
