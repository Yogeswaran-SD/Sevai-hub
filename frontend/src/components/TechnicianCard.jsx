import React from "react";
import { useTranslation } from "react-i18next";

function TTIBadge({ tti, t }) {
  if (!tti) return null;
  const score = tti.tti_score;
  const color =
    score >= 85 ? "#10B981" :
    score >= 70 ? "#3B82F6" :
    score >= 50 ? "#F59E0B" : "#EF4444";
  const bg = color + "18";
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 6,
      padding: "4px 10px", borderRadius: "100px",
      background: bg, border: `1px solid ${color}30`,
      fontSize: 12, color, fontWeight: 600,
    }}>
      <span style={{ fontSize: 10 }}>🛡</span>
      {t('technician.trustScore')} {score}% · {tti.reliability_label}
    </div>
  );
}

function ETABadge({ eta, t }) {
  if (!eta) return null;
  const conf = eta.confidence_pct;
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 6,
      padding: "4px 10px", borderRadius: "100px",
      background: "rgba(139,92,246,0.10)",
      border: "1px solid rgba(139,92,246,0.25)",
      fontSize: 12, color: "#A78BFA", fontWeight: 600,
    }}>
      <span style={{ fontSize: 10 }}>⏱</span>
      ~{eta.eta_minutes} {t('technician.mins')} {t('technician.eta')} · {conf}% {t('technician.confidence')}
    </div>
  );
}

function RankBadge({ rank }) {
  if (!rank) return null;
  const colors = ["#F97316", "#94A3B8", "#D97706"];
  const color  = colors[rank - 1] || "rgba(255,255,255,0.3)";
  const emojis = ["🥇", "🥈", "🥉"];
  const emoji  = emojis[rank - 1] || `#${rank}`;
  return (
    <div style={{
      position: "absolute", top: 12, right: 12,
      width: 28, height: 28, borderRadius: "50%",
      background: color + "22", border: `1.5px solid ${color}`,
      display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: rank <= 3 ? 14 : 11, fontWeight: 700, color,
    }}>
      {emoji}
    </div>
  );
}

export default function TechnicianCard({ technician, onCall }) {
  const { t } = useTranslation();
  const initials = technician.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const distanceText = technician.distance_km != null
    ? `${Number(technician.distance_km).toFixed(1)} ${t('technician.distance')}`
    : null;

  return (
    <div className="technician-card" style={{ position: "relative" }}>
      <RankBadge rank={technician.rank} />

      <div className="technician-avatar">{initials}</div>

      <div className="technician-info">
        <div className="technician-name">{technician.name}</div>

        {/* Status tags */}
        <div className="technician-tags">
          <span className={`tag ${technician.is_available ? "tag-available" : "tag-unavailable"}`}>
            {technician.is_available ? `● ${t('technician.available')}` : `● ${t('technician.busy')}`}
          </span>
          {technician.is_verified && <span className="tag tag-verified">✓ {t('technician.verified')}</span>}
          <span className="tag tag-category">{technician.service_category}</span>
        </div>

        {/* Core meta */}
        <div className="technician-meta">
          <div className="rating">⭐ {Number(technician.rating).toFixed(1)}</div>
          <div className="meta-item"><span>{technician.experience_years}</span>{t('technician.experience')}</div>
          {distanceText && (
            <div className="meta-item">📍 <span>{distanceText}</span></div>
          )}
          <div className="meta-item">
            💬 <span>{technician.total_reviews}</span> {t('technician.reviews')}
          </div>
        </div>

        {/* Intelligence badges */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 8 }}>
          <TTIBadge tti={technician.tti} t={t} />
          <ETABadge eta={technician.eta} t={t} />
        </div>

        {/* Address */}
        {technician.address && (
          <div className="meta-item" style={{ marginTop: 6, fontSize: 12 }}>
            📌 {technician.address}
          </div>
        )}

        {/* Weighted score (debug / transparency) */}
        {technician.weighted_score != null && (
          <div style={{
            marginTop: 6, fontSize: 11, color: "rgba(255,255,255,0.2)",
            display: "flex", alignItems: "center", gap: 4,
          }}>
            <span>Allocation Score:</span>
            <span style={{ color: "rgba(255,255,255,0.35)", fontWeight: 600 }}>
              {(technician.weighted_score * 100).toFixed(1)}
            </span>
          </div>
        )}

        <button className="btn-call" onClick={() => onCall && onCall(technician)}>
          {t('technician.callNow')} — {technician.phone}
        </button>
      </div>
    </div>
  );
}
