import React, { useEffect } from "react";
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

// User location pulsing dot
const userIcon = L.divIcon({
  html: `<div style="
    width:16px;height:16px;
    background:#F97316;
    border:3px solid white;
    border-radius:50%;
    box-shadow:0 0 0 6px rgba(249,115,22,0.25),0 0 0 12px rgba(249,115,22,0.10)
  "></div>`,
  className: "",
  iconSize: [16, 16],
  iconAnchor: [8, 8],
});

/** Return a tech marker icon colour-coded by TTI score */
function makeTechIcon(tti_score, rank) {
  const color =
    tti_score >= 85 ? "#10B981" :
    tti_score >= 70 ? "#3B82F6" :
    tti_score >= 50 ? "#F59E0B" : "#EF4444";

  const border = rank === 1 ? "#F97316" : "rgba(255,255,255,0.8)";
  const shadow = rank === 1
    ? "0 4px 16px rgba(249,115,22,0.5)"
    : "0 4px 12px rgba(0,0,0,0.4)";
  const size = rank === 1 ? 40 : 34;
  const half = size / 2;

  return L.divIcon({
    html: `<div style="
      width:${size}px;height:${size}px;
      background:linear-gradient(135deg,${color},${color}BB);
      border:2.5px solid ${border};
      border-radius:50%;
      display:flex;align-items:center;justify-content:center;
      font-size:${rank === 1 ? 18 : 15}px;
      box-shadow:${shadow};
      transition:transform 0.2s;
    ">🔧</div>`,
    className: "",
    iconSize: [size, size],
    iconAnchor: [half, half],
  });
}

function MapCenter({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center) map.setView(center, 13, { animate: true });
  }, [center, map]);
  return null;
}

export default function MapView({ userLocation, technicians, searchRadiusKm }) {
  const defaultCenter = userLocation || [13.0827, 80.2707];
  const radiusMeters  = (searchRadiusKm || 5) * 1000;

  return (
    <MapContainer
      center={defaultCenter}
      zoom={13}
      style={{ width: "100%", height: "100%" }}
    >
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://carto.com/">CARTO</a>'
      />
      <MapCenter center={userLocation} />

      {/* Search radius circle */}
      {userLocation && (
        <Circle
          center={userLocation}
          radius={radiusMeters}
          pathOptions={{
            color:       "rgba(249,115,22,0.6)",
            fillColor:   "rgba(249,115,22,0.04)",
            fillOpacity: 1,
            weight:      1.5,
            dashArray:   "6 4",
          }}
        />
      )}

      {/* User marker */}
      {userLocation && (
        <Marker position={userLocation} icon={userIcon}>
          <Popup>📍 <strong>Your Location</strong></Popup>
        </Marker>
      )}

      {/* Technician markers (TTI-coloured) */}
      {technicians &&
        technicians.map((t) =>
          t.latitude && t.longitude ? (
            <Marker
              key={t.id}
              position={[t.latitude, t.longitude]}
              icon={makeTechIcon(t.tti?.tti_score ?? 75, t.rank ?? 99)}
            >
              <Popup>
                <div style={{ minWidth: 180, lineHeight: 1.6 }}>
                  <div style={{ fontWeight: 700, marginBottom: 4 }}>{t.name}</div>
                  <div>⭐ {Number(t.rating).toFixed(1)} · {t.service_category}</div>
                  {t.tti && (
                    <div style={{ color: "#10B981", fontSize: 12 }}>
                      🛡 Trust: {t.tti.tti_score}% ({t.tti.reliability_label})
                    </div>
                  )}
                  {t.eta && (
                    <div style={{ color: "#A78BFA", fontSize: 12 }}>
                      ⏱ ETA: ~{t.eta.eta_minutes} min ({t.eta.confidence_pct}% conf)
                    </div>
                  )}
                  {t.distance_km && (
                    <div style={{ fontSize: 12, color: "#94A3B8" }}>
                      📍 {Number(t.distance_km).toFixed(1)} km away
                    </div>
                  )}
                  <div style={{ marginTop: 6 }}>
                    <a
                      href={`tel:${t.phone}`}
                      style={{
                        color: "#F97316", fontWeight: 600,
                        fontSize: 12, textDecoration: "none",
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
    </MapContainer>
  );
}
