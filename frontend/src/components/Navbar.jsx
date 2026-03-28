import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../contexts/AuthContext";

export default function Navbar() {
  const location = useLocation();
  const navigate  = useNavigate();
  const { t, i18n } = useTranslation();
  const { isAuthenticated, user, role, logout } = useAuth();
  const isActive = (path) => location.pathname === path ? "nav-link active" : "nav-link";
  const [online, setOnline] = useState(null);

  useEffect(() => {
    const apiBase = import.meta.env.VITE_API_URL || "http://localhost:8000";
    fetch(`${apiBase}/health`, { signal: AbortSignal.timeout(2000) })
      .then(() => setOnline(true))
      .catch(() => setOnline(false));
  }, []);

  const toggleLanguage = () => {
    i18n.changeLanguage(i18n.language === "en" ? "ta" : "en");
  };

  const ROLE_META = {
    user:       { icon: "👤", label: "My Dashboard", path: "/user/dashboard",       color: "#3B82F6" },
    technician: { icon: "🔧", label: "My Panel",     path: "/technician/dashboard", color: "#F97316" },
    admin:      { icon: "🛡️", label: "Admin Panel",  path: "/admin/dashboard",      color: "#8B5CF6" },
  };

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        <div className="navbar-logo">🛠️</div>
        <span className="navbar-title">{t("nav.brand")}</span>
        <span className="navbar-version">{t("nav.version")}</span>
      </Link>

      <div className="navbar-links">
        <Link to="/"             className={isActive("/")}>{t("nav.home")}</Link>
        <Link to="/search"       className={isActive("/search")}>{t("nav.findServices")}</Link>

        <div className="nav-status-dot" title={online === null ? t("nav.statusChecking") : online ? "Backend Online" : "Demo Mode"}>
          <span style={{ color: online === true ? "#10B981" : online === false ? "#EF4444" : "#F59E0B" }}>●</span>
          <span className="nav-status-label">
            {online === true ? t("nav.statusLive") : online === false ? t("nav.statusDemo") : t("nav.statusChecking")}
          </span>
        </div>

        <button onClick={toggleLanguage} className="btn-language" title={t("nav.languageTooltip")}>
          🌐 {t("nav.languageToggle")}
        </button>

        {/* Auth section */}
        {isAuthenticated && role ? (
          <div className="navbar-auth-group">
            <Link
              to={ROLE_META[role]?.path || "/"}
              className="btn-nav btn-nav--dashboard"
              style={{ "--dash-color": ROLE_META[role]?.color }}
              id="nav-dashboard-btn"
            >
              {ROLE_META[role]?.icon} {ROLE_META[role]?.label}
            </Link>
            <div className="navbar-user-chip" id="navbar-user-chip">
              <div className="navbar-user-avatar">{user?.name?.charAt(0)?.toUpperCase() || "U"}</div>
              <span>{user?.name?.split(" ")[0]}</span>
            </div>
            <button className="btn-logout" onClick={handleLogout} id="nav-logout-btn">
              Sign Out
            </button>
          </div>
        ) : (
          <Link to="/login" className="btn-nav" id="nav-login-btn">
            🔐 Sign In
          </Link>
        )}
      </div>
    </nav>
  );
}
