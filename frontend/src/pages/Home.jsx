import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import ServiceCard from "../components/ServiceCard";
import { getServices } from "../api/api";

export default function Home() {
  const { t } = useTranslation();
  const [services, setServices] = useState([]);
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const FEATURES = [
    { icon: "📍", title: t('home.features.proximity.title'), desc: t('home.features.proximity.desc') },
    { icon: "✅", title: t('home.features.verified.title'), desc: t('home.features.verified.desc') },
    { icon: "⚡", title: t('home.features.emergency.title'), desc: t('home.features.emergency.desc') },
    { icon: "🌐", title: t('home.features.language.title'), desc: t('home.features.language.desc') },
    { icon: "⭐", title: t('home.features.reviews.title'), desc: t('home.features.reviews.desc') },
    { icon: "🔄", title: t('home.features.availability.title'), desc: t('home.features.availability.desc') },
  ];

  const INTEL_MODULES = [
    { id: 1, label: t('home.intelModules.emergency'),    icon: "🚨" },
    { id: 2, label: t('home.intelModules.trust'),        icon: "🛡" },
    { id: 3, label: t('home.intelModules.radius'),       icon: "🔭" },
    { id: 4, label: t('home.intelModules.eta'),          icon: "⏱" },
    { id: 5, label: t('home.intelModules.heatmap'),      icon: "🌡" },
    { id: 6, label: t('home.intelModules.performance'),  icon: "⚡" },
    { id: 7, label: t('home.intelModules.allocation'),   icon: "⚖️" },
    { id: 8, label: t('home.intelModules.simulation'),   icon: "🧪" },
    { id: 9, label: t('home.intelModules.integrity'),    icon: "🔒" },
  ];

  useEffect(() => {
    getServices()
      .then((res) => setServices(res.data))
      .catch(() => {
        setServices([
          { id: "Plumber",           category: "Plumber",           name: "Plumber",        icon: "🔧", description: "Pipe leaks, tap repair, bathroom fitting",       color: "#3B82F6" },
          { id: "Electrician",       category: "Electrician",       name: "Electrician",    icon: "⚡", description: "Wiring, short circuit, switchboard repair",        color: "#F59E0B" },
          { id: "Gas Service",       category: "Gas Service",       name: "Gas Service",    icon: "🔥", description: "Gas cylinder, pipeline repair, stove",             color: "#EF4444" },
          { id: "Bike Mechanic",     category: "Bike Mechanic",     name: "Bike Mechanic",  icon: "🏍️", description: "Puncture, engine repair, oil change",             color: "#8B5CF6" },
          { id: "Mobile Technician", category: "Mobile Technician", name: "Mobile Repair",  icon: "📱", description: "Screen, battery, charging port fix",               color: "#06B6D4" },
          { id: "Cleaning Service",  category: "Cleaning Service",  name: "Cleaning",       icon: "🧹", description: "Home cleaning, deep clean, sofa wash",             color: "#10B981" },
          { id: "AC Technician",     category: "AC Technician",     name: "AC Technician",  icon: "❄️", description: "AC servicing, gas refill, installation",           color: "#60A5FA" },
          { id: "Carpenter",         category: "Carpenter",         name: "Carpenter",      icon: "🪚", description: "Furniture repair, door fitting, woodwork",          color: "#D97706" },
          { id: "Painter",           category: "Painter",           name: "Painter",        icon: "🎨", description: "Wall painting, waterproofing, texture",             color: "#EC4899" },
        ]);
      });
  }, []);

  const handleSearch = () => {
    if (query.trim()) navigate(`/search?q=${encodeURIComponent(query)}`);
    else navigate("/search");
  };

  return (
    <div>
      {/* HERO */}
      <section className="hero">
        <div className="hero-glow" />
        <div className="hero-content">
          <div className="hero-badge">
            🧠 {t('home.heroBadge')}
          </div>

          <h1 className="hero-title">
            {t('home.heroTitle')} <span>{t('home.heroTitleSpan')}</span> {t('home.heroTitleEnd')}
          </h1>

          <p className="hero-subtitle">
            {t('home.heroSubtitle')}
          </p>

          <div className="hero-search">
            <input
              type="text"
              placeholder={t('home.heroSearchPlaceholder')}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
            <button onClick={handleSearch}>{t('home.heroSearchBtn')}</button>
          </div>

          <div className="hero-stats">
            <div className="hero-stat">
              <div className="hero-stat-value">2,500+</div>
              <div className="hero-stat-label">{t('home.statVerified')}</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-value">15 min</div>
              <div className="hero-stat-label">{t('home.statResponse')}</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-value">38</div>
              <div className="hero-stat-label">{t('home.statDistricts')}</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-value">4.8★</div>
              <div className="hero-stat-label">{t('home.statRating')}</div>
            </div>
          </div>

          {/* Intelligence Module Ticker */}
          <div style={{
            marginTop: 40, padding: "16px 0",
            borderTop: "1px solid rgba(255,255,255,0.06)",
            borderBottom: "1px solid rgba(255,255,255,0.06)",
          }}>
            <div style={{
              fontSize: 10, color: "rgba(255,255,255,0.28)",
              textTransform: "uppercase", letterSpacing: 3,
              textAlign: "center", marginBottom: 12,
            }}>
              {t('home.intelActive')}
            </div>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", justifyContent: "center" }}>
              {INTEL_MODULES.map((m) => (
                <div key={m.id} style={{
                  display: "flex", alignItems: "center", gap: 6,
                  padding: "5px 12px", borderRadius: 100,
                  background: "rgba(249,115,22,0.06)",
                  border: "1px solid rgba(249,115,22,0.16)",
                  fontSize: 12, color: "rgba(255,255,255,0.65)",
                }}>
                  <span style={{ color: "#10B981", fontSize: 8 }}>●</span>
                  {m.icon} {m.label}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* SERVICES */}
      <div className="section">
        <div className="section-header">
          <span className="section-label">{t('home.servicesLabel')}</span>
          <h2 className="section-title">{t('home.servicesTitle')}</h2>
          <p className="section-subtitle">{t('home.servicesSubtitle')}</p>
        </div>
        <div className="services-grid">
          {services.map((s) => (
            <ServiceCard key={s.id} service={s} />
          ))}
        </div>
      </div>

      {/* FEATURES */}
      <div className="section" style={{ borderTop: "1px solid var(--border-subtle)" }}>
        <div className="section-header">
          <span className="section-label">{t('home.whyLabel')}</span>
          <h2 className="section-title">{t('home.whyTitle')}</h2>
          <p className="section-subtitle">{t('home.whySubtitle')}</p>
        </div>
        <div className="features-grid">
          {FEATURES.map((f) => (
            <div key={f.title} className="feature-card">
              <div className="feature-icon">{f.icon}</div>
              <div className="feature-title">{f.title}</div>
              <div className="feature-desc">{f.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* FOOTER */}
      <footer className="footer">
        <span className="footer-brand">Sevai Hub</span>
        <p>{t('home.footerTagline')}</p>
      </footer>
    </div>
  );
}
