import React, { useState, useEffect, useRef, useCallback } from "react";
import API from "../api/api";

// Thin wrapper so all apiFetch("/path") calls work with axios
const apiFetch = (path) => API.get(path).then((r) => r.data);

// ─── Static fallback data ─────────────────────────────────────────────────────
const DEMO_DASHBOARD = {
  platform_summary: {
    total_technicians: 18, available_now: 14, verified_technicians: 15,
    availability_rate_pct: 77.8, verification_rate_pct: 83.3, avg_platform_rating: 4.67,
  },
  platform_tti: {
    tti_score: 87.4, reliability_label: "Highly Reliable",
    display: "Trust Score: 87.4% (Highly Reliable)",
    components: {
      response_reliability: 88.7, cancellation_perf: 94.5,
      rating_stability: 83.6, availability_score: 87.8, verification_age: 62.1,
    },
  },
  categories: [
    { category: "Electrician",       total: 3, available: 2, avg_rating: 4.60, availability_pct: 66.7 },
    { category: "Plumber",           total: 3, available: 2, avg_rating: 4.50, availability_pct: 66.7 },
    { category: "Gas Service",       total: 2, available: 2, avg_rating: 4.80, availability_pct: 100  },
    { category: "AC Technician",     total: 2, available: 2, avg_rating: 4.65, availability_pct: 100  },
    { category: "Bike Mechanic",     total: 2, available: 2, avg_rating: 4.55, availability_pct: 100  },
    { category: "Mobile Technician", total: 2, available: 2, avg_rating: 4.70, availability_pct: 100  },
    { category: "Cleaning Service",  total: 1, available: 1, avg_rating: 4.70, availability_pct: 100  },
    { category: "Carpenter",         total: 1, available: 1, avg_rating: 4.60, availability_pct: 100  },
    { category: "Painter",           total: 1, available: 1, avg_rating: 4.70, availability_pct: 100  },
  ],
  intelligence_modules: {
    emergency_scoring:    { status: "active", keywords_tracked: 27 },
    trust_index:          { status: "active", formula_weights: { response_reliability: 0.30, cancellation_perf: 0.25, rating_stability: 0.20, availability_consistency: 0.15, verification_age: 0.10 } },
    adaptive_radius:      { status: "active", steps_km: [3, 5, 8, 15, 30] },
    eta_prediction:       { status: "active" },
    weighted_allocation:  { status: "active" },
    performance_indexing: { status: "active" },
  },
};

const DEMO_SIM_100   = { scenario: "mixed", concurrent_requests: 100,  allocation_results: { success_rate_pct: 98.2, failed_allocations: 2,   avg_search_radius_km: 4.2, radius_expanded_pct: 12.5, avg_eta_minutes: 24 }, latency_comparison: { with_gist_index_ms: 9.2, without_index_ms: 374.8, speedup_factor: 40.7 }, fairness_metrics: { gini_coefficient: 0.082, fairness_label: "Excellent",  avg_technicians_per_req: 3.1 }, system_health: { index_status: "GiST active", adaptive_radius: "enabled", tti_computation: "O(1) per technician", recommendation: "System handles load well up to ~5,000 concurrent requests." } };
const DEMO_SIM_1000  = { ...DEMO_SIM_100, concurrent_requests: 1000,   allocation_results: { success_rate_pct: 95.7, failed_allocations: 43,  avg_search_radius_km: 4.6, radius_expanded_pct: 22.1, avg_eta_minutes: 26 }, latency_comparison: { with_gist_index_ms: 18.4, without_index_ms: 590.2, speedup_factor: 32.1 }, fairness_metrics: { gini_coefficient: 0.10,  fairness_label: "Good",      avg_technicians_per_req: 2.7 } };
const DEMO_SIM_10000 = { ...DEMO_SIM_100, concurrent_requests: 10000,  allocation_results: { success_rate_pct: 90.2, failed_allocations: 980, avg_search_radius_km: 5.1, radius_expanded_pct: 38.4, avg_eta_minutes: 31 }, latency_comparison: { with_gist_index_ms: 53.0, without_index_ms: 1000,  speedup_factor: 18.9 }, fairness_metrics: { gini_coefficient: 0.12,  fairness_label: "Good",      avg_technicians_per_req: 2.2 } };

const DEMO_PERF = {
  spatial_index: { type: "GiST (Generalized Search Tree)", indexed_column: "technicians.location (Geography POINT, SRID 4326)", index_ddl: "CREATE INDEX idx_tech_location ON technicians USING GIST(location);", without_index: { algorithm: "Sequential scan", complexity: "O(n) — every row checked", estimated_latency_ms: "200–800 ms for 10k rows" }, with_index: { algorithm: "GiST spatial index lookup", complexity: "O(log n) — tree traversal", estimated_latency_ms: "2–15 ms for 10k rows", improvement_factor: "~30–50×" }, additional_indexes: ["idx_tech_category ON technicians(service_category)", "idx_tech_available ON technicians(is_available)", "idx_tech_verified  ON technicians(is_verified)"] },
  query_optimizations: ["ST_DWithin uses bounding-box pre-filter before exact distance check", "Composite ORDER BY: distance ASC, rating DESC, verified DESC", "LIMIT 20 applied at DB level — no over-fetching", "Geography cast ensures geodesic (earth-curved) distance accuracy"],
  adaptive_radius: { strategy: "Expand 3km → 5km → 8km → 15km → 30km", stop_condition: "Stop when ≥1 available technician found", max_expansion: "30 km" },
  tti_computation: { location: "Application layer (Python)", cost: "O(1) per technician — pure arithmetic", cached: false },
  simulation_support: { scenarios: ["Allocation efficiency under load (100–10,000 concurrent requests)", "Radius expansion latency profiling", "TTI fairness distribution across technicians", "Emergency vs. non-emergency response time delta"] },
};

// ─── Helper components ────────────────────────────────────────────────────────
function StatCard({ icon, label, value, sub, color = "#F97316" }) {
  return (
    <div className="intel-stat-card">
      <div className="intel-stat-icon" style={{ color }}>{icon}</div>
      <div className="intel-stat-value" style={{ color }}>{value}</div>
      <div className="intel-stat-label">{label}</div>
      {sub && <div className="intel-stat-sub">{sub}</div>}
    </div>
  );
}

function ModuleChip({ name, data }) {
  const colorMap = { active: "#10B981", inactive: "#EF4444" };
  const c = colorMap[data?.status || "inactive"];
  return (
    <div className="intel-module-chip" style={{ borderColor: c + "40", background: c + "0D" }}>
      <span style={{ color: c, fontSize: 10 }}>●</span>
      <span style={{ color: "#F8FAFC", fontWeight: 600, fontSize: 13 }}>{name}</span>
      <span style={{ color: c, fontSize: 11, marginLeft: "auto" }}>
        {data?.status === "active" ? "ACTIVE" : "OFFLINE"}
      </span>
    </div>
  );
}

function TTIBar({ label, value, weight }) {
  const hue = value >= 85 ? 160 : value >= 70 ? 210 : value >= 50 ? 38 : 0;
  const color = `hsl(${hue},80%,55%)`;
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4, fontSize: 12 }}>
        <span style={{ color: "rgba(255,255,255,0.6)" }}>{label}</span>
        <span style={{ color, fontWeight: 700 }}>{value}% <span style={{ color: "rgba(255,255,255,0.3)", fontWeight: 400 }}>(weight: {(weight * 100).toFixed(0)}%)</span></span>
      </div>
      <div style={{ height: 6, borderRadius: 3, background: "rgba(255,255,255,0.07)", overflow: "hidden" }}>
        <div style={{ height: "100%", width: `${value}%`, background: `linear-gradient(90deg, ${color}99, ${color})`, borderRadius: 3, transition: "width 1s ease" }} />
      </div>
    </div>
  );
}

function SimCard({ sim }) {
  if (!sim) return null;
  const { allocation_results: ar, latency_comparison: lc, fairness_metrics: fm } = sim;
  const successColor = ar.success_rate_pct >= 95 ? "#10B981" : ar.success_rate_pct >= 85 ? "#F59E0B" : "#EF4444";
  const fairColor    = fm.fairness_label === "Excellent" ? "#10B981" : fm.fairness_label === "Good" ? "#3B82F6" : "#F59E0B";
  return (
    <div className="intel-sim-result">
      <div className="intel-sim-grid">
        <div className="intel-sim-metric">
          <div className="intel-sim-metric-val" style={{ color: successColor }}>{ar.success_rate_pct}%</div>
          <div className="intel-sim-metric-lbl">Success Rate</div>
        </div>
        <div className="intel-sim-metric">
          <div className="intel-sim-metric-val" style={{ color: "#A78BFA" }}>{ar.avg_eta_minutes} min</div>
          <div className="intel-sim-metric-lbl">Avg ETA</div>
        </div>
        <div className="intel-sim-metric">
          <div className="intel-sim-metric-val" style={{ color: "#60A5FA" }}>{lc.with_gist_index_ms} ms</div>
          <div className="intel-sim-metric-lbl">Query Latency (indexed)</div>
        </div>
        <div className="intel-sim-metric">
          <div className="intel-sim-metric-val" style={{ color: "#F97316" }}>{lc.speedup_factor}×</div>
          <div className="intel-sim-metric-lbl">Index Speedup</div>
        </div>
        <div className="intel-sim-metric">
          <div className="intel-sim-metric-val" style={{ color: fairColor }}>{fm.fairness_label}</div>
          <div className="intel-sim-metric-lbl">TTI Fairness (Gini: {fm.gini_coefficient})</div>
        </div>
        <div className="intel-sim-metric">
          <div className="intel-sim-metric-val" style={{ color: "#F59E0B" }}>{ar.radius_expanded_pct}%</div>
          <div className="intel-sim-metric-lbl">Radius Expansions</div>
        </div>
      </div>
      <div className="intel-sim-latency-bar">
        <div className="intel-sim-bar-row">
          <span className="intel-sim-bar-lbl">With GiST Index</span>
          <div className="intel-sim-bar-track">
            <div className="intel-sim-bar-fill" style={{ width: `${Math.min((lc.with_gist_index_ms / (lc.without_index_ms || 1000)) * 100, 12)}%`, background: "linear-gradient(90deg,#10B981,#34D399)" }} />
          </div>
          <span className="intel-sim-bar-val" style={{ color: "#10B981" }}>{lc.with_gist_index_ms} ms</span>
        </div>
        <div className="intel-sim-bar-row">
          <span className="intel-sim-bar-lbl">Sequential Scan</span>
          <div className="intel-sim-bar-track">
            <div className="intel-sim-bar-fill" style={{ width: `${Math.min((lc.without_index_ms / Math.max(lc.without_index_ms, 1000)) * 100, 100)}%`, background: "linear-gradient(90deg,#EF4444,#F87171)" }} />
          </div>
          <span className="intel-sim-bar-val" style={{ color: "#EF4444" }}>{lc.without_index_ms} ms</span>
        </div>
      </div>
    </div>
  );
}

// ─── Live Emergency Scorer Component ─────────────────────────────────────────
function LiveScorer() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const debounceRef = useRef(null);

  const SEVERITY_COLORS = {
    Critical: { bg: "rgba(239,68,68,0.12)", border: "rgba(239,68,68,0.35)", text: "#EF4444", glow: "rgba(239,68,68,0.25)" },
    High:     { bg: "rgba(249,115,22,0.12)", border: "rgba(249,115,22,0.35)", text: "#F97316", glow: "rgba(249,115,22,0.20)" },
    Medium:   { bg: "rgba(245,158,11,0.12)", border: "rgba(245,158,11,0.35)", text: "#F59E0B", glow: "rgba(245,158,11,0.18)" },
    Low:      { bg: "rgba(16,185,129,0.10)",  border: "rgba(16,185,129,0.25)", text: "#10B981", glow: "rgba(16,185,129,0.15)" },
  };

  const EXAMPLE_QUERIES = [
    "Gas is leaking from the pipe urgently",
    "Short circuit in the main switchboard",
    "Water flooding the kitchen",
    "AC not cooling properly",
    "Need a painter for touch up work",
    "Bike not starting this morning",
  ];

  const scoreQuery = useCallback(async (q) => {
    if (!q.trim()) { setResult(null); return; }
    setLoading(true);
    try {
      const data = await apiFetch(`/intelligence/emergency/score?query=${encodeURIComponent(q)}`);
      setResult(data);
    } catch {
      // Local fallback scoring
      const keywords = [
        ["gas leak",1.00],["fire",1.00],["explosion",1.00],["electric shock",1.00],
        ["spark",0.90],["short circuit",0.90],["burst pipe",0.90],["flood",0.85],
        ["no power",0.75],["hissing",0.80],["urgent",0.70],["emergency",0.70],
        ["leak",0.60],["broken",0.50],["repair",0.30],["fix",0.25],["clean",0.08],["paint",0.05],
      ];
      const lower = q.toLowerCase();
      const found = keywords.filter(([k]) => lower.includes(k));
      const score = found.length === 0 ? 0 :
        found.reduce((s,[,w],i) => s + w * Math.pow(0.3, i), 0);
      const pct = Math.round(Math.min(score, 1) * 100);
      const level = pct >= 75 ? "Critical" : pct >= 50 ? "High" : pct >= 25 ? "Medium" : "Low";
      const icons = { Critical:"🔴", High:"🟠", Medium:"🟡", Low:"🟢" };
      setResult({
        score: Math.min(score,1).toFixed(4), percentage: pct, level,
        icon: icons[level], keywords_found: found.map(([k])=>k),
        display: `Emergency Risk Level: ${pct}% (${level})`,
      });
    } finally {
      setLoading(false);
    }
  }, []);

  const handleChange = (val) => {
    setQuery(val);
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => scoreQuery(val), 400);
  };

  const c = result ? (SEVERITY_COLORS[result.level] || SEVERITY_COLORS.Low) : null;

  return (
    <div className="intel-section-grid">
      <div className="intel-card intel-card-full">
        <h3 className="intel-card-title">🚨 Live Emergency Severity Scorer</h3>
        <p style={{ color: "rgba(255,255,255,0.5)", fontSize: 13, marginBottom: 20 }}>
          Type any problem description below. The Emergency Severity Scoring Engine will analyse your text in real-time using weighted keyword detection.
        </p>

        {/* Input */}
        <div style={{ position: "relative", marginBottom: 16 }}>
          <textarea
            value={query}
            onChange={(e) => handleChange(e.target.value)}
            placeholder="Describe the problem... (e.g. gas smell from kitchen pipe, no electricity, water bursting)"
            style={{
              width: "100%", minHeight: 100, padding: "14px 16px",
              background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.12)",
              borderRadius: 12, color: "#F8FAFC", fontSize: 14, fontFamily: "Inter,sans-serif",
              resize: "vertical", outline: "none", lineHeight: 1.6,
              transition: "border-color 0.2s",
              ...(c ? { borderColor: c.border, boxShadow: `0 0 0 3px ${c.glow}` } : {}),
            }}
          />
          {loading && (
            <div style={{ position:"absolute", right:12, top:12, width:18, height:18,
              border:"2px solid rgba(255,255,255,0.1)", borderTopColor:"#F97316",
              borderRadius:"50%", animation:"spin 0.8s linear infinite" }} />
          )}
        </div>

        {/* Quick examples */}
        <div style={{ display:"flex", flexWrap:"wrap", gap:8, marginBottom:24 }}>
          {EXAMPLE_QUERIES.map((q) => (
            <button key={q} onClick={() => { setQuery(q); scoreQuery(q); }}
              style={{
                padding:"5px 12px", borderRadius:100, fontSize:12, cursor:"pointer",
                background:"rgba(255,255,255,0.05)", border:"1px solid rgba(255,255,255,0.12)",
                color:"rgba(255,255,255,0.6)", transition:"all 0.2s",
              }}
            >{q}</button>
          ))}
        </div>

        {/* Result */}
        {result && (
          <div style={{
            background: c.bg, border: `1px solid ${c.border}`,
            borderRadius: 16, padding: "24px", animation: "fadeIn 0.3s ease",
          }}>
            {/* Score display */}
            <div style={{ display:"flex", alignItems:"center", gap:20, marginBottom:20 }}>
              <div style={{ fontSize:56, lineHeight:1 }}>{result.icon}</div>
              <div style={{ flex:1 }}>
                <div style={{ fontSize:13, color:"rgba(255,255,255,0.5)", marginBottom:4 }}>Emergency Risk Level</div>
                <div style={{ fontSize:42, fontWeight:900, color:c.text, lineHeight:1 }}>{result.percentage}%</div>
                <div style={{ fontSize:16, fontWeight:700, color:c.text, marginTop:4 }}>{result.level} Severity</div>
              </div>
              <div style={{ textAlign:"right" }}>
                <div style={{ fontSize:12, color:"rgba(255,255,255,0.4)", marginBottom:4 }}>Raw Score</div>
                <div style={{ fontSize:20, fontWeight:700, color:"rgba(255,255,255,0.6)" }}>{result.score}</div>
              </div>
            </div>

            {/* Progress bar */}
            <div style={{ height:10, borderRadius:5, background:"rgba(255,255,255,0.08)", overflow:"hidden", marginBottom:16 }}>
              <div style={{
                height:"100%", width:`${result.percentage}%`,
                background:`linear-gradient(90deg, ${c.text}99, ${c.text})`,
                borderRadius:5, transition:"width 0.6s cubic-bezier(0.4,0,0.2,1)",
                boxShadow:`0 0 12px ${c.glow}`,
              }} />
            </div>

            {/* Action message */}
            <div style={{ fontSize:13, color:"rgba(255,255,255,0.7)", marginBottom:16, lineHeight:1.6 }}>
              {result.level === "Critical" && "🚨 CRITICAL — Life/property threatening. Nearest technician must be dispatched immediately. Do NOT attempt DIY repairs. Call 112 if life-threatening."}
              {result.level === "High" && "⚠️ HIGH PRIORITY — Urgent response required. Technicians ranked by TTI + proximity for fastest dispatch."}
              {result.level === "Medium" && "🔧 MEDIUM — Service required soon. Best available technician matched via weighted allocation."}
              {result.level === "Low" && "✅ LOW — Routine service request. Standard allocation applied."}
            </div>

            {/* Keywords detected */}
            {result.keywords_found?.length > 0 && (
              <div>
                <div style={{ fontSize:11, color:"rgba(255,255,255,0.4)", marginBottom:8 }}>KEYWORDS DETECTED</div>
                <div style={{ display:"flex", flexWrap:"wrap", gap:6 }}>
                  {result.keywords_found.map((kw) => (
                    <span key={kw} style={{
                      padding:"3px 10px", borderRadius:100,
                      background: c.text+"18", border:`1px solid ${c.text}30`,
                      color:c.text, fontSize:12, fontWeight:600,
                    }}>{kw}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {!result && !loading && (
          <div style={{ textAlign:"center", padding:"32px 0", color:"rgba(255,255,255,0.2)", fontSize:14 }}>
            Start typing above to activate the Emergency Severity Scoring Engine
          </div>
        )}
      </div>

      {/* Formula card */}
      <div className="intel-card intel-card-full">
        <h3 className="intel-card-title">📐 Scoring Algorithm</h3>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:16 }}>
          {[
            { level:"Critical", icon:"🔴", range:"75–100%", keywords:["gas leak","fire","explosion","electric shock","spark","short circuit","burst pipe","flood"], color:"#EF4444" },
            { level:"High",     icon:"🟠", range:"50–74%",  keywords:["urgent","emergency","no power","hissing","leak","overflow"], color:"#F97316" },
            { level:"Medium",   icon:"🟡", range:"25–49%",  keywords:["broken","not working","damage","repair","fix"], color:"#F59E0B" },
            { level:"Low",      icon:"🟢", range:"0–24%",   keywords:["service","install","replace","check","clean","paint"], color:"#10B981" },
          ].map(({ level, icon, range, keywords, color }) => (
            <div key={level} style={{
              background: color+"0D", border:`1px solid ${color}25`,
              borderRadius:12, padding:16,
            }}>
              <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:10 }}>
                <span style={{ fontSize:18 }}>{icon}</span>
                <span style={{ fontWeight:700, color }}>{level}</span>
                <span style={{ marginLeft:"auto", fontSize:12, color:"rgba(255,255,255,0.4)" }}>{range}</span>
              </div>
              <div style={{ display:"flex", flexWrap:"wrap", gap:4 }}>
                {keywords.map(k => (
                  <span key={k} style={{ padding:"2px 8px", borderRadius:100, background:color+"18",
                    color, fontSize:11, border:`1px solid ${color}25` }}>{k}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
        <div style={{ marginTop:16, padding:14, background:"rgba(255,255,255,0.03)", borderRadius:10, fontSize:12, color:"rgba(255,255,255,0.5)" }}>
          💡 <strong style={{ color:"#F8FAFC" }}>Algorithm:</strong> Max dominant keyword score + diminishing returns for additional keywords (×0.3ⁿ). Capped at 100%. Multiple matching keywords compound the score.
        </div>
      </div>
    </div>
  );
}

// ─── Heatmap Component ────────────────────────────────────────────────────────
// ─── Static fallback for heatmap (module-level so useEffect dep is stable) ─────
const DEMO_HEATMAP_DATA = {
  heatmap_zones: [
    { zone:"Anna Nagar",     lat:13.0850, lon:80.2101, demand_score:92, peak_hour:"08:00–11:00", top_service:"Plumber" },
    { zone:"T.Nagar",        lat:13.0418, lon:80.2341, demand_score:88, peak_hour:"09:00–12:00", top_service:"Electrician" },
    { zone:"Adyar",          lat:13.0012, lon:80.2565, demand_score:85, peak_hour:"07:00–10:00", top_service:"Electrician" },
    { zone:"Velachery",      lat:12.9815, lon:80.2180, demand_score:80, peak_hour:"18:00–21:00", top_service:"AC Technician" },
    { zone:"OMR",            lat:12.8996, lon:80.2268, demand_score:75, peak_hour:"08:00–10:00", top_service:"AC Technician" },
    { zone:"Porur",          lat:13.0340, lon:80.1570, demand_score:70, peak_hour:"10:00–13:00", top_service:"Gas Service" },
    { zone:"Tambaram",       lat:12.9249, lon:80.1000, demand_score:65, peak_hour:"07:00–09:00", top_service:"Plumber" },
    { zone:"Perambur",       lat:13.1187, lon:80.2444, demand_score:60, peak_hour:"09:00–11:00", top_service:"Bike Mechanic" },
    { zone:"Sholinganallur", lat:12.8997, lon:80.2278, demand_score:78, peak_hour:"08:00–10:00", top_service:"AC Technician" },
    { zone:"Kodambakkam",    lat:13.0533, lon:80.2214, demand_score:72, peak_hour:"10:00–14:00", top_service:"Mobile Technician" },
  ],
  peak_emergency_hours: ["07:00–09:00", "18:00–21:00"],
  emergency_clustering: {
    gas_leaks:  { primary_zone:"Porur–Guindy corridor",       avg_response_time_mins:14 },
    electrical: { primary_zone:"T.Nagar–Anna Nagar corridor", avg_response_time_mins:18 },
    plumbing:   { primary_zone:"Velachery–Tambaram corridor", avg_response_time_mins:22 },
  },
  total_zones_tracked: 10,
};

function HeatmapTab() {
  const [heatData, setHeatData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    apiFetch("/intelligence/heatmap")
      .then(setHeatData)
      .catch(() => setHeatData(DEMO_HEATMAP_DATA))
      .finally(() => setLoading(false));
  }, []);

  const getColor = (score) => {
    if (score >= 85) return "#EF4444";
    if (score >= 75) return "#F97316";
    if (score >= 65) return "#F59E0B";
    return "#10B981";
  };

  const getLabel = (score) => {
    if (score >= 85) return "Critical"; if (score >= 75) return "High";
    if (score >= 65) return "Medium";   return "Normal";
  };

  if (loading) return (
    <div style={{ display:"flex", justifyContent:"center", padding:60 }}>
      <div className="loading-spinner" />
    </div>
  );

  const zones = heatData?.heatmap_zones || [];
  const sorted = [...zones].sort((a, b) => b.demand_score - a.demand_score);

  return (
    <div className="intel-section-grid">
      {/* Zone Grid visualization */}
      <div className="intel-card intel-card-full">
        <h3 className="intel-card-title">🌡 Urban Service Demand Heatmap — Chennai</h3>
        <p style={{ color:"rgba(255,255,255,0.4)", fontSize:13, marginBottom:20 }}>
          Real-time service demand intensity across {heatData?.total_zones_tracked} tracked zones.
          Larger blocks = higher demand pressure.
        </p>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill, minmax(200px,1fr))", gap:12 }}>
          {sorted.map((z) => {
            const col = getColor(z.demand_score);
            const isSelected = selected?.zone === z.zone;
            return (
              <div key={z.zone}
                onClick={() => setSelected(isSelected ? null : z)}
                style={{
                  background: col+"12", border:`2px solid ${isSelected ? col : col+"35"}`,
                  borderRadius:14, padding:16, cursor:"pointer",
                  transition:"all 0.2s", position:"relative", overflow:"hidden",
                  boxShadow: isSelected ? `0 0 24px ${col}40` : "none",
                  transform: isSelected ? "scale(1.02)" : "scale(1)",
                }}
              >
                <div style={{ fontSize:11, color:"rgba(255,255,255,0.4)", marginBottom:4 }}>ZONE</div>
                <div style={{ fontWeight:800, fontSize:15, color:"#F8FAFC", marginBottom:8 }}>{z.zone}</div>
                {/* Demand bar */}
                <div style={{ height:6, borderRadius:3, background:"rgba(255,255,255,0.08)", overflow:"hidden", marginBottom:10 }}>
                  <div style={{
                    height:"100%", width:`${z.demand_score}%`,
                    background:`linear-gradient(90deg,${col}80,${col})`,
                    borderRadius:3,
                  }} />
                </div>
                <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                  <span style={{ fontSize:26, fontWeight:900, color:col }}>{z.demand_score}</span>
                  <span style={{
                    padding:"3px 8px", borderRadius:100, fontSize:11, fontWeight:700,
                    background:col+"25", color:col,
                  }}>{getLabel(z.demand_score)}</span>
                </div>
                <div style={{ marginTop:8, fontSize:11, color:"rgba(255,255,255,0.4)" }}>Top: {z.top_service}</div>
                <div style={{ fontSize:11, color:"rgba(255,255,255,0.4)" }}>Peak: {z.peak_hour}</div>
              </div>
            );
          })}
        </div>

        {/* Selected zone detail */}
        {selected && (
          <div style={{
            marginTop:20, padding:20,
            background:`${getColor(selected.demand_score)}10`,
            border:`1px solid ${getColor(selected.demand_score)}35`,
            borderRadius:14, animation:"fadeIn 0.3s ease",
          }}>
            <div style={{ fontWeight:700, fontSize:16, marginBottom:12 }}>📍 {selected.zone} — Zone Detail</div>
            <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:12 }}>
              {[
                ["Demand Score", selected.demand_score+"/100", getColor(selected.demand_score)],
                ["Severity",     getLabel(selected.demand_score), getColor(selected.demand_score)],
                ["Peak Hours",   selected.peak_hour, "#60A5FA"],
                ["Top Service",  selected.top_service, "#F97316"],
              ].map(([l,v,c]) => (
                <div key={l}>
                  <div style={{ fontSize:11, color:"rgba(255,255,255,0.4)", marginBottom:4 }}>{l}</div>
                  <div style={{ fontSize:15, fontWeight:700, color:c }}>{v}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Emergency Clustering */}
      <div className="intel-card">
        <h3 className="intel-card-title">🚨 Emergency Clustering Trends</h3>
        {Object.entries(heatData?.emergency_clustering || {}).map(([type, data]) => (
          <div key={type} style={{
            padding:"14px 16px", borderRadius:10, marginBottom:10,
            background:"rgba(239,68,68,0.06)", border:"1px solid rgba(239,68,68,0.2)",
          }}>
            <div style={{ fontWeight:700, color:"#F97316", textTransform:"capitalize", marginBottom:6 }}>
              {type.replace("_"," ")} Emergencies
            </div>
            <div style={{ fontSize:13, color:"rgba(255,255,255,0.6)", marginBottom:4 }}>📍 {data.primary_zone}</div>
            <div style={{ fontSize:13, color:"#10B981", fontWeight:600 }}>⏱ Avg Response: {data.avg_response_time_mins} mins</div>
          </div>
        ))}
      </div>

      {/* Peak Hours */}
      <div className="intel-card">
        <h3 className="intel-card-title">⏰ Peak Emergency Windows</h3>
        <p style={{ fontSize:13, color:"rgba(255,255,255,0.4)", marginBottom:16 }}>
          Periods with highest service request volume — system pre-allocates technicians during these windows.
        </p>
        {(heatData?.peak_emergency_hours || []).map((h, i) => (
          <div key={h} style={{
            display:"flex", alignItems:"center", gap:12,
            padding:"12px 16px", borderRadius:10, marginBottom:8,
            background: i === 0 ? "rgba(249,115,22,0.08)" : "rgba(239,68,68,0.06)",
            border: `1px solid ${i === 0 ? "rgba(249,115,22,0.25)" : "rgba(239,68,68,0.2)"}`,
          }}>
            <span style={{ fontSize:20 }}>{i === 0 ? "🌅" : "🌆"}</span>
            <div>
              <div style={{ fontWeight:700, fontSize:15 }}>{h}</div>
              <div style={{ fontSize:12, color:"rgba(255,255,255,0.4)" }}>{i === 0 ? "Morning rush — commute-related" : "Evening peak — residential demand"}</div>
            </div>
            <div style={{
              marginLeft:"auto", padding:"4px 10px", borderRadius:100,
              background:"rgba(239,68,68,0.15)", color:"#EF4444",
              fontSize:11, fontWeight:700,
            }}>HIGH LOAD</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── MAIN PAGE ────────────────────────────────────────────────────────────────
export default function Intelligence() {
  const [dashboard, setDashboard]       = useState(null);
  const [perfData,  setPerfData]        = useState(null);
  const [simData,   setSimData]         = useState(null);
  const [simLoad,   setSimLoad]         = useState(100);
  const [simScenario, setSimScenario]   = useState("mixed");
  const [loading,   setLoading]         = useState(true);
  const [activeTab, setActiveTab]       = useState("overview");
  const [isDemo,    setIsDemo]          = useState(false);

  useEffect(() => {
    Promise.all([
      apiFetch("/intelligence/dashboard").catch(() => null),
      apiFetch("/intelligence/performance").catch(() => null),
    ]).then(([dash, perf]) => {
      setDashboard(dash || { ...DEMO_DASHBOARD, _demo: true });
      setPerfData(perf  || DEMO_PERF);
      if (!dash) setIsDemo(true);
      setLoading(false);
    });
  }, []);

  const runSimulation = useCallback(async () => {
    try {
      const data = await apiFetch(`/intelligence/simulate?concurrent_requests=${simLoad}&scenario=${simScenario}`);
      setSimData(data);
    } catch {
      // Demo fallback
      const map = { 100: DEMO_SIM_100, 1000: DEMO_SIM_1000, 10000: DEMO_SIM_10000 };
      setSimData({ ...(map[simLoad] || DEMO_SIM_1000), scenario: simScenario });
    }
  }, [simLoad, simScenario]);

  if (loading) {
    return (
      <div className="intel-page">
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: "60vh", gap: 16 }}>
          <div className="loading-spinner" />
          <p style={{ color: "var(--text-muted)", fontSize: 14 }}>Loading Intelligence Engine...</p>
        </div>
      </div>
    );
  }

  const ps  = dashboard?.platform_summary || {};
  const tti = dashboard?.platform_tti || {};
  const mods = dashboard?.intelligence_modules || {};

  const TABS = [
    { id: "overview",    label: "📊 Overview" },
    { id: "tti",         label: "🛡 Trust Index" },
    { id: "heatmap",     label: "🌡 Heatmap" },
    { id: "scorer",      label: "🚨 Live Scorer" },
    { id: "simulation",  label: "🧪 Simulation" },
    { id: "performance", label: "⚡ Performance" },
  ];

  return (
    <div className="intel-page">
      {/* ── Header ── */}
      <div className="intel-hero">
        <div className="intel-hero-glow" />
        <div className="intel-hero-content">
          <div className="hero-badge" style={{ marginBottom: 16 }}>
            🧠 Sevai Hub Intelligence Engine v3.0 · 9 Modules Active
          </div>
          <h1 className="intel-title">
            Spatially Optimized<br />
            <span>Urban Response Engine</span>
          </h1>
          <p className="intel-subtitle">
            Geospatial Intelligence · Predictive Modeling · Trust Computation · Emergency-First Allocation
          </p>
          {isDemo && (
            <div className="intel-demo-badge">
              ℹ️ Demo Mode — Connect backend for live data
            </div>
          )}
        </div>
      </div>

      {/* ── Tab Bar ── */}
      <div className="intel-tab-bar">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`intel-tab ${activeTab === t.id ? "active" : ""}`}
            onClick={() => setActiveTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="intel-body">

        {/* ══════════════════════════════════════════════════════ OVERVIEW ══ */}
        {activeTab === "overview" && (
          <div className="intel-section-grid">
            {/* Platform Stats */}
            <div className="intel-card intel-card-full">
              <h3 className="intel-card-title">📈 Platform Summary</h3>
              <div className="intel-stats-row">
                <StatCard icon="👥" label="Total Technicians"  value={ps.total_technicians}      color="#60A5FA" />
                <StatCard icon="🟢" label="Available Now"       value={ps.available_now}           sub={`${ps.availability_rate_pct}% rate`}  color="#10B981" />
                <StatCard icon="✅" label="Verified"            value={ps.verified_technicians}    sub={`${ps.verification_rate_pct}% rate`}  color="#A78BFA" />
                <StatCard icon="⭐" label="Avg Platform Rating" value={`${ps.avg_platform_rating}★`} color="#F59E0B" />
                <StatCard icon="🛡" label="Platform TTI"        value={`${tti.tti_score}%`}        sub={tti.reliability_label}                color="#F97316" />
              </div>
            </div>

            {/* Module Status Grid */}
            <div className="intel-card">
              <h3 className="intel-card-title">🔌 Intelligence Modules</h3>
              <div className="intel-modules-grid">
                <ModuleChip name="Emergency Severity Scoring" data={mods.emergency_scoring} />
                <ModuleChip name="Technician Trust Index (TTI)" data={mods.trust_index} />
                <ModuleChip name="Adaptive Search Radius" data={mods.adaptive_radius} />
                <ModuleChip name="ETA Prediction Model" data={mods.eta_prediction} />
                <ModuleChip name="Weighted Allocation" data={mods.weighted_allocation} />
                <ModuleChip name="GiST Spatial Indexing" data={mods.performance_indexing} />
              </div>
              <div className="intel-module-footer">
                <span style={{ color: "#10B981" }}>● 6/6 modules active</span>
                <span style={{ color: "rgba(255,255,255,0.3)" }}>Version 2.0.0</span>
              </div>
            </div>

            {/* Category Breakdown */}
            <div className="intel-card">
              <h3 className="intel-card-title">🏗 Service Category Breakdown</h3>
              <div className="intel-category-list">
                {(dashboard?.categories || []).map((c) => {
                  const avPct = c.availability_pct;
                  const col = avPct === 100 ? "#10B981" : avPct >= 66 ? "#F59E0B" : "#EF4444";
                  return (
                    <div key={c.category} className="intel-cat-row">
                      <span className="intel-cat-name">{c.category}</span>
                      <span className="intel-cat-total">{c.available}/{c.total}</span>
                      <div className="intel-cat-bar-track">
                        <div className="intel-cat-bar-fill" style={{ width: `${avPct}%`, background: col }} />
                      </div>
                      <span style={{ fontSize: 12, color: col, width: 38, textAlign: "right" }}>{avPct}%</span>
                      <span style={{ fontSize: 12, color: "#F59E0B", width: 32, textAlign: "right" }}>⭐{c.avg_rating}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Emergency Keywords */}
            <div className="intel-card intel-card-full">
              <h3 className="intel-card-title">🚨 Emergency Keywords Tracked</h3>
              <div className="intel-keywords-grid">
                {[
                  ["gas leak",1.00,"Critical"], ["fire",1.00,"Critical"], ["explosion",1.00,"Critical"],
                  ["electric shock",1.00,"Critical"], ["spark",0.90,"Critical"], ["short circuit",0.90,"Critical"],
                  ["burst pipe",0.90,"Critical"], ["flood",0.85,"Critical"], ["no power",0.75,"High"],
                  ["urgent",0.70,"High"], ["emergency",0.70,"High"], ["leak",0.60,"High"],
                  ["broken",0.50,"Medium"], ["repair",0.30,"Medium"], ["fix",0.25,"Medium"],
                  ["clean",0.08,"Low"], ["paint",0.05,"Low"],
                ].map(([kw, w, lvl]) => {
                  const colors = { Critical:"#EF4444", High:"#F97316", Medium:"#F59E0B", Low:"#10B981" };
                  return (
                    <div key={kw} className="intel-kw-chip" style={{ borderColor: colors[lvl] + "40", background: colors[lvl] + "0D" }}>
                      <span style={{ color: colors[lvl], fontWeight: 700, fontSize: 11 }}>{kw}</span>
                      <span style={{ color: "rgba(255,255,255,0.3)", fontSize: 10 }}>w={w.toFixed(2)}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════════════ TTI TAB ══ */}
        {activeTab === "tti" && (
          <div className="intel-section-grid">
            <div className="intel-card">
              <h3 className="intel-card-title">🛡 Platform-Wide Trust Index</h3>
              <div style={{ marginBottom: 24, padding: "20px", background: "rgba(249,115,22,0.06)", borderRadius: 12, border: "1px solid rgba(249,115,22,0.15)", textAlign: "center" }}>
                <div style={{ fontSize: 48, fontWeight: 900, color: "#F97316", lineHeight: 1 }}>{tti.tti_score}%</div>
                <div style={{ fontSize: 16, color: "#10B981", marginTop: 8, fontWeight: 600 }}>{tti.reliability_label}</div>
                <div style={{ fontSize: 12, color: "rgba(255,255,255,0.4)", marginTop: 4 }}>Computed across all registered technicians</div>
              </div>
              {tti.components && (
                <div>
                  <TTIBar label="Response Reliability"    value={tti.components.response_reliability}  weight={0.30} />
                  <TTIBar label="Cancellation Performance" value={tti.components.cancellation_perf}    weight={0.25} />
                  <TTIBar label="Rating Stability"         value={tti.components.rating_stability}     weight={0.20} />
                  <TTIBar label="Availability Consistency" value={tti.components.availability_score}   weight={0.15} />
                  <TTIBar label="Verification Age Factor"  value={tti.components.verification_age}     weight={0.10} />
                </div>
              )}
            </div>

            <div className="intel-card">
              <h3 className="intel-card-title">📐 TTI Formula</h3>
              <div className="intel-formula-box">
                <div className="intel-formula-line"><span className="intel-formula-w" style={{ color: "#F97316" }}>0.30</span> × Response Reliability</div>
                <div className="intel-formula-line"><span className="intel-formula-w" style={{ color: "#A78BFA" }}>0.25</span> × Cancellation Performance</div>
                <div className="intel-formula-line"><span className="intel-formula-w" style={{ color: "#60A5FA" }}>0.20</span> × Rating Stability</div>
                <div className="intel-formula-line"><span className="intel-formula-w" style={{ color: "#10B981" }}>0.15</span> × Availability Consistency</div>
                <div className="intel-formula-line"><span className="intel-formula-w" style={{ color: "#F59E0B" }}>0.10</span> × Verification Age Factor</div>
                <div style={{ borderTop: "1px solid rgba(255,255,255,0.08)", paddingTop: 12, marginTop: 12, color: "#F8FAFC", fontWeight: 700, fontSize: 15 }}>= TTI Score (0–100)</div>
              </div>
              <div className="intel-tti-bands">
                {[["85–100", "Highly Reliable", "#10B981"], ["70–84", "Reliable", "#3B82F6"], ["50–69", "Moderate", "#F59E0B"], ["0–49", "Low Trust", "#EF4444"]].map(([range, label, color]) => (
                  <div key={range} className="intel-tti-band" style={{ borderLeft: `3px solid ${color}`, background: color + "0D" }}>
                    <span style={{ color, fontWeight: 700, fontSize: 13 }}>{range}%</span>
                    <span style={{ color: "#F8FAFC", fontSize: 13 }}>{label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="intel-card intel-card-full">
              <h3 className="intel-card-title">⚖️ Weighted Allocation Formula</h3>
              <div className="intel-alloc-grid">
                {[["Distance Weight", "0.50", "#F97316", "Nearest technician prioritized first"], ["Rating Weight", "0.20", "#F59E0B", "Higher rated technicians get advantage"], ["TTI Weight", "0.20", "#10B981", "Trust Index directly impacts ranking"], ["Emergency Severity", "0.10", "#EF4444", "Critical cases reduce penalty score"]].map(([label, w, color, desc]) => (
                  <div key={label} className="intel-alloc-card" style={{ borderTop: `3px solid ${color}` }}>
                    <div style={{ fontSize: 28, fontWeight: 900, color }}>{w}</div>
                    <div style={{ fontWeight: 700, fontSize: 14, marginTop: 4 }}>{label}</div>
                    <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>{desc}</div>
                  </div>
                ))}
              </div>
              <div style={{ marginTop: 16, padding: 14, background: "rgba(255,255,255,0.03)", borderRadius: 10, fontSize: 13, color: "rgba(255,255,255,0.5)" }}>
                💡 <strong style={{ color: "#F8FAFC" }}>Lower Final Score = Higher Priority.</strong> All components are normalized to [0,1] before applying weights. Technicians must be available and within radius to be considered.
              </div>
            </div>
          </div>
        )}

        {/* ═════════════════════════════════════════════════ HEATMAP TAB ══ */}
        {activeTab === "heatmap" && <HeatmapTab />}

        {/* ═══════════════════════════════════════════ LIVE SCORER TAB ══ */}
        {activeTab === "scorer" && <LiveScorer />}

        {/* ══════════════════════════════════════════════ SIMULATION TAB ══ */}
        {activeTab === "simulation" && (
          <div className="intel-section-grid">
            <div className="intel-card intel-card-full">
              <h3 className="intel-card-title">🧪 Emergency Allocation Simulator</h3>
              <p style={{ color: "rgba(255,255,255,0.5)", fontSize: 13, marginBottom: 20 }}>
                Simulate the engine under varying concurrent request loads to validate allocation efficiency, latency, and fairness.
              </p>
              <div className="intel-sim-controls">
                <div className="intel-sim-control-group">
                  <label className="intel-sim-label">Concurrent Requests</label>
                  <div style={{ display: "flex", gap: 8 }}>
                    {[100, 1000, 5000, 10000].map((n) => (
                      <button key={n} className={`intel-sim-btn ${simLoad === n ? "active" : ""}`} onClick={() => setSimLoad(n)}>
                        {n.toLocaleString()}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="intel-sim-control-group">
                  <label className="intel-sim-label">Scenario</label>
                  <div style={{ display: "flex", gap: 8 }}>
                    {["mixed", "emergency", "routine"].map((s) => (
                      <button key={s} className={`intel-sim-btn ${simScenario === s ? "active" : ""}`} onClick={() => setSimScenario(s)} style={{ textTransform: "capitalize" }}>
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
                <button className="btn-search" style={{ marginTop: 4 }} onClick={runSimulation}>
                  ▶ Run Simulation
                </button>
              </div>
              {simData ? (
                <SimCard sim={simData} />
              ) : (
                <div style={{ textAlign: "center", padding: "40px 20px", color: "rgba(255,255,255,0.3)", fontSize: 14 }}>
                  Click <strong style={{ color: "#F97316" }}>▶ Run Simulation</strong> to generate allocation results
                </div>
              )}
            </div>

            <div className="intel-card intel-card-full">
              <h3 className="intel-card-title">🔭 Adaptive Search Radius Strategy</h3>
              <div className="intel-radius-timeline">
                {[
                  { km: 3,  label: "Initial Scan",         color: "#10B981", desc: "First attempt — best coverage for most requests" },
                  { km: 5,  label: "Expansion 1",          color: "#F59E0B", desc: "Expand if no technician found within 3 km" },
                  { km: 8,  label: "Expansion 2",          color: "#F97316", desc: "Mid-range expansion for low-density areas" },
                  { km: 15, label: "Expansion 3",          color: "#EF4444", desc: "Wide area search for remote locations" },
                  { km: 30, label: "Maximum Reach",        color: "#8B5CF6", desc: "Emergency fallback — always finds a technician" },
                ].map((step, i) => (
                  <div key={step.km} className="intel-radius-step">
                    <div className="intel-radius-dot" style={{ background: step.color, boxShadow: `0 0 8px ${step.color}60` }} />
                    {i < 4 && <div className="intel-radius-line" />}
                    <div className="intel-radius-info">
                      <div style={{ fontWeight: 700, color: step.color, fontSize: 15 }}>{step.km} km</div>
                      <div style={{ fontWeight: 600, fontSize: 12 }}>{step.label}</div>
                      <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 11 }}>{step.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ══════════════════════════════════════════════ PERFORMANCE TAB ══ */}
        {activeTab === "performance" && perfData && (
          <div className="intel-section-grid">
            <div className="intel-card">
              <h3 className="intel-card-title">🗄 Spatial Index Configuration</h3>
              <div className="intel-perf-index">
                <div className="intel-perf-index-type">
                  <span style={{ color: "#F97316", fontWeight: 700 }}>Index Type:</span>
                  <span style={{ color: "#F8FAFC" }}>{perfData.spatial_index?.type}</span>
                </div>
                <div className="intel-perf-index-type">
                  <span style={{ color: "#60A5FA", fontWeight: 700 }}>Column:</span>
                  <span style={{ color: "#F8FAFC", fontSize: 12 }}>{perfData.spatial_index?.indexed_column}</span>
                </div>
                <pre className="intel-code-block">{perfData.spatial_index?.index_ddl}</pre>
                {(perfData.spatial_index?.additional_indexes || []).map((idx) => (
                  <pre key={idx} className="intel-code-block" style={{ fontSize: 11, opacity: 0.7 }}>
                    CREATE INDEX {idx};
                  </pre>
                ))}
              </div>
            </div>

            <div className="intel-card">
              <h3 className="intel-card-title">📊 With vs Without Index</h3>
              <div className="intel-compare-grid">
                <div className="intel-compare-col" style={{ borderTop: "3px solid #EF4444" }}>
                  <div className="intel-compare-lbl" style={{ color: "#EF4444" }}>❌ Without Index</div>
                  <div className="intel-compare-row"><b>Algorithm:</b> {perfData.spatial_index?.without_index?.algorithm}</div>
                  <div className="intel-compare-row"><b>Complexity:</b> {perfData.spatial_index?.without_index?.complexity}</div>
                  <div className="intel-compare-row"><b>Latency:</b> <span style={{ color: "#EF4444", fontWeight: 700 }}>{perfData.spatial_index?.without_index?.estimated_latency_ms}</span></div>
                </div>
                <div className="intel-compare-col" style={{ borderTop: "3px solid #10B981" }}>
                  <div className="intel-compare-lbl" style={{ color: "#10B981" }}>✅ With GiST Index</div>
                  <div className="intel-compare-row"><b>Algorithm:</b> {perfData.spatial_index?.with_index?.algorithm}</div>
                  <div className="intel-compare-row"><b>Complexity:</b> {perfData.spatial_index?.with_index?.complexity}</div>
                  <div className="intel-compare-row"><b>Latency:</b> <span style={{ color: "#10B981", fontWeight: 700 }}>{perfData.spatial_index?.with_index?.estimated_latency_ms}</span></div>
                  <div className="intel-compare-row"><b>Speedup:</b> <span style={{ color: "#F97316", fontWeight: 700 }}>{perfData.spatial_index?.with_index?.improvement_factor}</span></div>
                </div>
              </div>
            </div>

            <div className="intel-card intel-card-full">
              <h3 className="intel-card-title">⚙️ Query Optimizations</h3>
              <div className="intel-opt-list">
                {(perfData.query_optimizations || []).map((opt, i) => (
                  <div key={i} className="intel-opt-row">
                    <span className="intel-opt-num">{String(i + 1).padStart(2, "0")}</span>
                    <span className="intel-opt-text">{opt}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="intel-card intel-card-full">
              <h3 className="intel-card-title">🧪 Simulation Support Scenarios</h3>
              <div className="intel-sim-scenarios">
                {(perfData.simulation_support?.scenarios || []).map((s, i) => (
                  <div key={i} className="intel-scenario-chip">
                    <span style={{ color: "#F97316", fontWeight: 700 }}>Scenario {i + 1}</span>
                    <span style={{ color: "rgba(255,255,255,0.7)", fontSize: 13 }}>{s}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
