import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function Navbar() {
  const location = useLocation();
  const { t, i18n } = useTranslation();
  const isActive  = (path) => location.pathname === path ? "nav-link active" : "nav-link";
  const [online, setOnline] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/health", { signal: AbortSignal.timeout(2000) })
      .then(() => setOnline(true))
      .catch(() => setOnline(false));
  }, []);

  const toggleLanguage = () => {
    const newLanguage = i18n.language === 'en' ? 'ta' : 'en';
    i18n.changeLanguage(newLanguage);
  };

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        <div className="navbar-logo">🛠️</div>
        <span className="navbar-title">{t('nav.brand')}</span>
        <span className="navbar-version">{t('nav.version')}</span>
      </Link>

      <div className="navbar-links">
        <Link to="/"             className={isActive("/")}>{t('nav.home')}</Link>
        <Link to="/search"       className={isActive("/search")}>{t('nav.findServices')}</Link>
        <Link to="/intelligence" className={isActive("/intelligence")}>🧠 {t('nav.intelligence')}</Link>
        <div className="nav-status-dot" title={online === null ? t('nav.statusChecking') : online ? "Backend Online" : "Demo Mode"}>
          <span style={{ color: online === true ? "#10B981" : online === false ? "#EF4444" : "#F59E0B" }}>●</span>
          <span className="nav-status-label">{online === true ? t('nav.statusLive') : online === false ? t('nav.statusDemo') : t('nav.statusChecking')}</span>
        </div>
        <button 
          onClick={toggleLanguage} 
          className="btn-language"
          title={t('nav.languageTooltip')}
        >
          🌐 {t('nav.languageToggle')}
        </button>
        <Link to="/search" className="btn-nav">🔍 {t('nav.findNow')}</Link>
      </div>
    </nav>
  );
}
