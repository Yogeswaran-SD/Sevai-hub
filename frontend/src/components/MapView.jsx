import React, { useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix leaflet default icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  iconUrl:       "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  shadowUrl:     "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

// ─── User location pulsing dot ─────────────────────────────────────────────
const userIcon = L.divIcon({
  html: `<div style="
    width:18px;height:18px;
    background:#F97316;
    border:3px solid white;
    border-radius:50%;
    box-shadow:0 0 0 8px rgba(249,115,22,0.3),0 0 0 14px rgba(249,115,22,0.15);
    animation:pulse-glow 2s infinite;
  " class="user-location-pulse"></div>`,
  className: "",
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});

// ─── Technician marker icons with TTI color coding ────────────────────────
function makeTechIcon(tti_score, rank) {
  const score = tti_score ?? 75;
  let color, label;
  
  if (score >= 85) {
    color = "#10B981"; // Green - Highly Reliable
    label = "★";
  } else if (score >= 70) {
    color = "#3B82F6"; // Blue - Reliable
    label = "●";
  } else if (score >= 50) {
    color = "#F59E0B"; // Amber - Fair
    label = "◆";
  } else {
    color = "#EF4444"; // Red - Low Trust
    label = "⚠";
  }

  const isTopRank = rank === 1;
  const size = isTopRank ? 44 : 36;
  const fontSize = isTopRank ? 20 : 16;
  const border = isTopRank ? "#F97316" : "rgba(255,255,255,0.7)";
  const shadow = isTopRank
    ? "0 6px 20px rgba(249,115,22,0.6), inset 0 -2px 4px rgba(0,0,0,0.3)"
    : "0 4px 12px rgba(0,0,0,0.5)";

  return L.divIcon({
    html: `<div style="
      width:${size}px;height:${size}px;
      background:linear-gradient(135deg,${color},${color}CC);
      border:2.5px solid ${border};
      border-radius:50%;
      display:flex;
      align-items:center;
      justify-content:center;
      font-size:${fontSize}px;
      font-weight:700;
      box-shadow:${shadow};
      color:white;
      cursor:pointer;
      transition:all 0.2s ease;
      ${isTopRank ? 'animation:bounce-marker 0.6s ease-in-out;' : ''}
    ">
      ${isTopRank ? `<div style="position:absolute;top:-4px;right:-4px;width:16px;height:16px;background:#FFD700;border:2px solid white;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;">🥇</div>` : ''}
      ${label}
    </div>`,
    className: "tech-marker",
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2 - 10],
  });
}

// ─── Nearby Technicians Panel (Map Overlay) ───────────────────────────────
function NearbyTechniciansList({ technicians, userLocation, maxResults = 6 }) {
  const map = useMap();
  
  if (!technicians || technicians.length === 0) return null;
  
  // Sort by distance
  const sorted = [...technicians].sort((a, b) => {
    const distA = a.distance_km || 999;
    const distB = b.distance_km || 999;
    return distA - distB;
  }).slice(0, maxResults);

  return (
    <div style={{
      position: "absolute",
      top: 16,
      left: 16,
      zIndex: 400,
      maxHeight: "60vh",
      maxWidth: 320,
      overflowY: "auto",
      backgroundColor: "rgba(10,10,15,0.95)",
      border: "1px solid rgba(249,115,22,0.3)",
      borderRadius: "12px",
      backdropFilter: "blur(10px)",
      padding: "12px",
      display: "flex",
      flexDirection: "column",
      gap: "8px",
    }}>
      <div style={{
        fontSize: 13,
        fontWeight: 700,
        color: "#F97316",
        marginBottom: 4,
        display: "flex",
        alignItems: "center",
        gap: 6,
      }}>
        📍 Nearby Technicians ({sorted.length})
      </div>

      {sorted.map((tech, idx) => {
        const getBgColor = (score) => {
          if (score >= 85) return "rgba(16,185,129,0.08)";
          if (score >= 70) return "rgba(59,130,246,0.08)";
          if (score >= 50) return "rgba(245,158,11,0.08)";
          return "rgba(239,68,68,0.08)";
        };
        const getTtiColor = (score) => {
          if (score >= 85) return "#10B981";
          if (score >= 70) return "#3B82F6";
          if (score >= 50) return "#F59E0B";
          return "#EF4444";
        };

        const tti_score = tech.tti?.tti_score ?? 75;
        const ttiColor = getTtiColor(tti_score);

        return (
          <div
            key={tech.id}
            onClick={() => {
              if (tech.latitude && tech.longitude) {
                map.setView([tech.latitude, tech.longitude], 16, { animate: true });
              }
            }}
            style={{
              backgroundColor: getBgColor(tti_score),
              border: `1px solid ${ttiColor}30`,
              borderRadius: "8px",
              padding: "10px",
              cursor: "pointer",
              transition: "all 0.2s easy",
              fontSize: 12,
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = getBgColor(tti_score);
              e.target.style.borderColor = ttiColor;
              e.target.style.transform = "translateX(4px)";
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = getBgColor(tti_score);
              e.target.style.borderColor = `${ttiColor}30`;
              e.target.style.transform = "translateX(0)";
            }}
          >
            {/* Rank + Name */}
            <div style={{
              fontWeight: 700,
              fontSize: 13,
              marginBottom: 4,
              display: "flex",
              alignItems: "center",
              gap: 6,
              color: "#F8FAFC",
            }}>
              {tech.rank === 1 ? "🥇" : tech.rank === 2 ? "🥈" : tech.rank === 3 ? "🥉" : `#${tech.rank}`}
              <span>{tech.name}</span>
            </div>

            {/* Rating + Distance */}
            <div style={{
              display: "flex",
              gap: 12,
              marginBottom: 4,
              fontSize: 11,
              color: "#94A3B8",
            }}>
              <span>⭐ {Number(tech.rating).toFixed(1)}</span>
              <span>📍 {Number(tech.distance_km || 0).toFixed(1)} km</span>
              <span>💬 {tech.total_reviews}</span>
            </div>

            {/* TTI Badge */}
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              fontSize: 11,
              color: ttiColor,
              fontWeight: 600,
            }}>
              <div style={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                backgroundColor: ttiColor,
              }} />
              Trust: {Number(tti_score).toFixed(0)}%
            </div>

            {/* ETA */}
            {tech.eta && (
              <div style={{
                marginTop: 4,
                fontSize: 11,
                color: "#C084FC",
                display: "flex",
                alignItems: "center",
                gap: 4,
              }}>
                ⏱ ETA: ~{tech.eta.eta_minutes} min
              </div>
            )}

            {/* Service */}
            {tech.service_category && (
              <div style={{
                marginTop: 4,
                fontSize: 10,
                color: "#F97316",
                fontWeight: 600,
              }}>
                {tech.service_category}
              </div>
            )}
          </div>
        );
      })}

      {technicians.length > maxResults && (
        <div style={{
          fontSize: 11,
          color: "#94A3B8",
          textAlign: "center",
          padding: "6px 0",
          borderTop: "1px solid rgba(255,255,255,0.1)",
          marginTop: 4,
        }}>
          +{technicians.length - maxResults} more
        </div>
      )}

      <style>{`
        div::-webkit-scrollbar {
          width: 4px;
        }
        div::-webkit-scrollbar-track {
          background: transparent;
        }
        div::-webkit-scrollbar-thumb {
          background: rgba(249, 115, 22, 0.4);
          border-radius: 2px;
        }
        div::-webkit-scrollbar-thumb:hover {
          background: rgba(249, 115, 22, 0.6);
        }
      `}</style>
    </div>
  );
}

// ─── Map controls and legend ───────────────────────────────────────────────
function MapControls({ technicians, searchRadiusKm }) {
  const map = useMap();
  
  // Add custom legend
  useEffect(() => {
    const legend = L.control({ position: "bottomright" });
    
    legend.onAdd = () => {
      const div = L.DomUtil.create("div", "map-legend");
      div.style.background = "rgba(10,10,15,0.95)";
      div.style.padding = "12px 16px";
      div.style.borderRadius = "8px";
      div.style.border = "1px solid rgba(249,115,22,0.3)";
      div.style.fontSize = "12px";
      div.style.lineHeight = "1.8";
      div.style.color = "#F8FAFC";
      div.style.backdrop = "blur(10px)";
      
      div.innerHTML = `
        <div style="margin-bottom:8px;font-weight:700;color:#F97316;">TTI Trust Scores</div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
          <div style="width:20px;height:20px;background:#10B981;border-radius:50%;border:1.5px solid rgba(255,255,255,0.5);"></div>
          <span>≥85% — Highly Reliable</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
          <div style="width:20px;height:20px;background:#3B82F6;border-radius:50%;border:1.5px solid rgba(255,255,255,0.5);"></div>
          <span>70-84% — Reliable</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
          <div style="width:20px;height:20px;background:#F59E0B;border-radius:50%;border:1.5px solid rgba(255,255,255,0.5);"></div>
          <span>50-69% — Fair</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
          <div style="width:20px;height:20px;background:#EF4444;border-radius:50%;border:1.5px solid rgba(255,255,255,0.5);"></div>
          <span>&lt;50% — Low Trust</span>
        </div>
        <div style="margin-top:10px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.2);font-size:11px;color:#94A3B8;">
          🥇 Rank 1 (Top match)
          <br/>Search radius: ${searchRadiusKm} km
        </div>
      `;
      return div;
    };
    
    legend.addTo(map);
    return () => legend.remove();
  }, [map, searchRadiusKm]);

  // Fit bounds to all markers and user location  
  useEffect(() => {
    if (!map || !technicians || technicians.length === 0) return;
    
    const group = L.featureGroup();
    
    // Add user location
    if (map.getCenter()) {
      group.addLayer(L.marker(map.getCenter()));
    }
    
    // Add technician locations
    technicians.forEach((t) => {
      if (t.latitude && t.longitude) {
        group.addLayer(L.marker([t.latitude, t.longitude]));
      }
    });
    
    if (group.getLayers().length > 1) {
      try {
        map.fitBounds(group.getBounds(), { padding: [50, 50], maxZoom: 15 });
      } catch (e) {
        // Silently handle if bounds are invalid
      }
    }
  }, [map, technicians]);
  
  return null;
}

function MapCenter({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, map.getZoom(), { animate: true });
    }
  }, [center, map]);
  return null;
}

// ─── Main Map Component ───────────────────────────────────────────────────
export default function MapView({ userLocation, technicians, searchRadiusKm }) {
  const defaultCenter = userLocation || [13.0827, 80.2707];
  const radiusMeters = (searchRadiusKm || 5) * 1000;
  const mapRef = useRef(null);

  return (
    <MapContainer
      ref={mapRef}
      center={defaultCenter}
      zoom={13}
      style={{ width: "100%", height: "100%" }}
      zoomControl={true}
      attributionControl={true}
    >
      {/* Dark themed base map */}
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://carto.com/">CARTO</a> | &copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
        maxZoom={19}
        minZoom={2}
      />
      
      <MapCenter center={userLocation} />
      <MapControls technicians={technicians} searchRadiusKm={searchRadiusKm} />
      <NearbyTechniciansList technicians={technicians} userLocation={userLocation} />

      {/* Search radius circle with gradient effect */}
      {userLocation && (
        <>
          {/* Outer glow ring */}
          <Circle
            center={userLocation}
            radius={radiusMeters}
            pathOptions={{
              color: "rgba(249,115,22,0.2)",
              fillColor: "transparent",
              weight: 1,
              dashArray: "8 4",
              lineCap: "round",
            }}
          />
          {/* Main search radius */}
          <Circle
            center={userLocation}
            radius={radiusMeters}
            pathOptions={{
              color: "rgba(249,115,22,0.8)",
              fillColor: "rgba(249,115,22,0.02)",
              fillOpacity: 1,
              weight: 2,
              dashArray: "6 3",
              lineCap: "round",
            }}
          />
        </>
      )}

      {/* User location marker with animated pulse */}
      {userLocation && (
        <Marker position={userLocation} icon={userIcon}>
          <Popup className="custom-popup">
            <div style={{ padding: "8px 0" }}>
              <div style={{ fontWeight: 700, marginBottom: 4, color: "#F97316" }}>📍 Your Location</div>
              <div style={{ fontSize: 12, color: "#94A3B8" }}>
                Latitude: {userLocation[0].toFixed(4)}<br/>
                Longitude: {userLocation[1].toFixed(4)}
              </div>
            </div>
          </Popup>
        </Marker>
      )}

      {/* Technician markers with enhanced popups */}
      {technicians &&
        technicians.map((t) =>
          t.latitude && t.longitude ? (
            <Marker
              key={t.id}
              position={[t.latitude, t.longitude]}
              icon={makeTechIcon(t.tti?.tti_score ?? 75, t.rank ?? 99)}
              title={`${t.name} - Rating: ${t.rating?.toFixed(1) || 'N/A'}`}
            >
              <Popup className="custom-popup" maxWidth={250}>
                <div style={{ padding: "8px 0" }}>
                  <div style={{ 
                    fontWeight: 700, 
                    marginBottom: 6, 
                    fontSize: 14,
                    backgroundColor: `${t.rank === 1 ? '#F97316' : '#F8FAFC'}20`,
                    padding: "6px 8px",
                    borderRadius: "4px",
                  }}>
                    {t.rank === 1 ? '🥇 ' : ''}
                    {t.name}
                  </div>
                  
                  <div style={{ marginBottom: 6, fontSize: 13, display: "flex", gap: 12 }}>
                    <span>⭐ {Number(t.rating).toFixed(1)}</span>
                    <span>💬 {t.total_reviews || 0}</span>
                    <span>👤 {t.experience_years}y</span>
                  </div>
                  
                  {t.service_category && (
                    <div style={{ marginBottom: 6, fontSize: 12, color: "#F97316", fontWeight: 600 }}>
                      {t.service_category}
                    </div>
                  )}

                  {t.tti && (
                    <div style={{ 
                      marginBottom: 6, 
                      padding: "6px 8px", 
                      backgroundColor: "rgba(16,185,129,0.1)",
                      borderRadius: "4px",
                      fontSize: 12, 
                      color: "#10B981"
                    }}>
                      🛡 Trust: {Number(t.tti.tti_score).toFixed(1)}% ({t.tti.reliability_label})
                    </div>
                  )}

                  {t.eta && (
                    <div style={{ 
                      marginBottom: 6, 
                      padding: "6px 8px", 
                      backgroundColor: "rgba(168,85,247,0.1)",
                      borderRadius: "4px",
                      fontSize: 12, 
                      color: "#C084FC"
                    }}>
                      ⏱ ETA: ~{t.eta.eta_minutes} min ({t.eta.confidence_pct}% confidence)
                    </div>
                  )}

                  {t.distance_km && (
                    <div style={{ marginBottom: 6, fontSize: 12, color: "#94A3B8" }}>
                      📍 {Number(t.distance_km).toFixed(2)} km away
                    </div>
                  )}

                  <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid rgba(255,255,255,0.2)" }}>
                    <a
                      href={`tel:${t.phone}`}
                      style={{
                        display: "inline-block",
                        color: "#fff",
                        backgroundColor: "#F97316",
                        padding: "6px 12px",
                        borderRadius: "4px",
                        fontWeight: 600,
                        fontSize: 12,
                        textDecoration: "none",
                        transition: "all 0.2s",
                      }}
                      onMouseOver={(e) => {
                        e.target.style.backgroundColor = "#EC4899";
                        e.target.style.transform = "scale(1.05)";
                      }}
                      onMouseOut={(e) => {
                        e.target.style.backgroundColor = "#F97316";
                        e.target.style.transform = "scale(1)";
                      }}
                    >
                      📞 Call {t.phone}
                    </a>
                  </div>
                </div>
              </Popup>
            </Marker>
          ) : null
        )}
      
      {/* Attribution notice */}
      <style>{`
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 0 8px rgba(249,115,22,0.3), 0 0 0 14px rgba(249,115,22,0.15); }
          50% { box-shadow: 0 0 0 12px rgba(249,115,22,0.2), 0 0 0 18px rgba(249,115,22,0.08); }
        }
        
        @keyframes bounce-marker {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.15); }
        }
        
        .tech-marker:hover {
          filter: drop-shadow(0 0 8px rgba(255,255,255,0.4));
        }
        
        .custom-popup .leaflet-popup-content-wrapper {
          background: rgba(21, 21, 30, 0.98) !important;
          border: 1px solid rgba(249, 115, 22, 0.2) !important;
          border-radius: 8px !important;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8) !important;
          color: #F8FAFC !important;
        }
        
        .custom-popup .leaflet-popup-tip {
          border-top-color: rgba(21, 21, 30, 0.98) !important;
        }
        
        .map-legend {
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6) !important;
        }
      `}</style>
    </MapContainer>
  );
}
