import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { loginUser, loginTechnician, loginAdmin, registerUser } from "../api/authApi";
import axios from "axios";

// Get API base URL from environment variable (set in .env files)
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const ROLES = [
  { key: "user",       label: "User",       icon: "👤", color: "#3B82F6", desc: "Service requester" },
  { key: "technician", label: "Technician", icon: "🔧", color: "#F97316", desc: "Service provider"  },
  { key: "admin",      label: "Admin",      icon: "🛡️", color: "#8B5CF6", desc: "System controller" },
];

// Demo credentials that ALWAYS work (backed by local_auth.json store)
const DEMO_CREDS = {
  user: [
    { label: "Demo User",   identifier: "1234567890",   password: "demo123",   note: "📱 phone" },
    { label: "Email login", identifier: "user@demo.com", password: "demo123",   note: "📧 email" },
  ],
  technician: [
    { label: "Ravi Kumar — Plumber",       identifier: "9876543210", password: "Sevai@123", note: "📱 phone" },
    { label: "Murugan S — Plumber",        identifier: "9876543211", password: "Sevai@123", note: "📱 phone" },
    { label: "Arjun Electricals",          identifier: "9876543220", password: "Sevai@123", note: "📱 phone" },
    { label: "Safe Gas Service",           identifier: "9876543230", password: "Sevai@123", note: "📱 phone" },
    { label: "Speed Bike Works",           identifier: "9876543240", password: "Sevai@123", note: "📱 phone" },
    { label: "Phone Doctor — Mobile Tech", identifier: "9876543250", password: "Sevai@123", note: "📱 phone" },
    { label: "CleanHome TN",               identifier: "9876543260", password: "Sevai@123", note: "📱 phone" },
    { label: "Cool Air Services",          identifier: "9876543270", password: "Sevai@123", note: "📱 phone" },
  ],
  admin: [
    { label: "System Administrator", mobile: "9999999999", aadhaar: "123456789012", password: "Admin@SevaiHub2024" },
  ],
};

export default function Login() {
  const { login, isAuthenticated, role: existingRole } = useAuth();
  const navigate  = useNavigate();
  const location  = useLocation();
  const from      = location.state?.from?.pathname || null;

  const [activeRole,  setActiveRole]  = useState("user");
  const [mode,        setMode]        = useState("login");      // 'login' | 'register' | 'reg-tech'
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState("");
  const [success,     setSuccess]     = useState("");
  const [mounted,     setMounted]     = useState(false);
  const [showDemo,    setShowDemo]    = useState(true);

  // Login fields
  const [identifier, setIdentifier] = useState("");
  const [password,   setPassword]   = useState("");
  const [aadhaar,    setAadhaar]    = useState("");
  const [showPass,   setShowPass]   = useState(false);

  // User register fields
  const [regName,  setRegName]  = useState("");
  const [regEmail, setRegEmail] = useState("");
  const [regPhone, setRegPhone] = useState("");
  const [regPass,  setRegPass]  = useState("");

  // Technician self-register fields
  const [techName,     setTechName]     = useState("");
  const [techPhone,    setTechPhone]    = useState("");
  const [techPass,     setTechPass]     = useState("");
  const [techEmail,    setTechEmail]    = useState("");
  const [techCategory, setTechCategory] = useState("Plumber");
  const [techCity,     setTechCity]     = useState("Chennai");
  const [techAddress,  setTechAddress]  = useState("");
  const [techLat,      setTechLat]      = useState(13.0827);  // Chennai center
  const [techLon,      setTechLon]      = useState(80.2707);  // Chennai center

  useEffect(() => { setMounted(true); }, []);
  useEffect(() => { if (isAuthenticated && existingRole) redirectByRole(existingRole); }, [isAuthenticated, existingRole]);

  function redirectByRole(r) {
    const dest = from || (r === "admin" ? "/admin/dashboard" : r === "technician" ? "/technician/dashboard" : "/user/dashboard");
    navigate(dest, { replace: true });
  }

  function resetForm() {
    setIdentifier(""); setPassword(""); setAadhaar(""); setError(""); setSuccess("");
    setRegName(""); setRegEmail(""); setRegPhone(""); setRegPass("");
    setTechName(""); setTechPhone(""); setTechPass(""); setTechEmail(""); setTechCategory("Plumber");
    setTechCity("Chennai"); setTechAddress(""); setTechLat(13.0827); setTechLon(80.2707);
  }

  function handleRoleChange(r) { setActiveRole(r); setMode("login"); resetForm(); }

  function fillDemo(cred) {
    setError(""); setSuccess("");
    if (activeRole === "admin") {
      setIdentifier(cred.mobile || "");
      setAadhaar(cred.aadhaar || "");
      setPassword(cred.password || "");
    } else {
      setIdentifier(cred.identifier || "");
      setPassword(cred.password || "");
    }
    setMode("login");
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(""); setSuccess(""); setLoading(true);

    try {
      // ── Register User ──────────────────────────────────────────────────────
      if (mode === "register" && activeRole === "user") {
        if (!regName || !regPhone || !regPass) throw new Error("Please fill all required fields.");
        await registerUser({ name: regName, email: regEmail || undefined, phone: regPhone, password: regPass });
        setSuccess("✅ Account created! You can now sign in.");
        setMode("login");
        setIdentifier(regPhone);
        setPassword(regPass);
        setLoading(false);
        return;
      }

      // ── Register Technician ────────────────────────────────────────────────
      if (mode === "reg-tech" && activeRole === "technician") {
        if (!techName || !techPhone || !techPass) throw new Error("Please fill all required fields.");
        const res = await axios.post(`${API_BASE}/auth/register/technician`, null, {
          params: { 
            name: techName, 
            phone: techPhone, 
            password: techPass, 
            email: techEmail || undefined, 
            service_category: techCategory,
            city: techCity,
            address: techAddress || undefined,
            latitude: techLat,
            longitude: techLon
          }
        });
        setSuccess(`✅ Technician account created for "${res.data.name}"! You're now searchable in the system.`);
        setMode("login");
        setIdentifier(techPhone);
        setPassword(techPass);
        setLoading(false);
        return;
      }

      // ── Login ─────────────────────────────────────────────────────────────
      let res;
      if (activeRole === "user")       res = await loginUser(identifier, password);
      else if (activeRole === "technician") res = await loginTechnician(identifier, password);
      else                              res = await loginAdmin(identifier, aadhaar, password);

      const { access_token, user: userData } = res.data;
      login(access_token, userData);
      setSuccess(`✅ Welcome back, ${userData.name}!`);
      setTimeout(() => redirectByRole(userData.role), 600);

    } catch (err) {
      const detail = err.response?.data?.detail;
      if (detail) {
        setError(detail);
      } else if (err.code === "ERR_NETWORK" || err.message?.toLowerCase().includes("network")) {
        setError("⚠️ Cannot reach the backend server. Make sure it is running (uvicorn app.main:app --reload).");
      } else {
        setError(err.message || "Login failed. Try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  const roleInfo   = ROLES.find(r => r.key === activeRole);
  const demoCreds  = DEMO_CREDS[activeRole] || [];

  const modeLabel = {
    login:     `${roleInfo.label} Login`,
    register:  "Create User Account",
    "reg-tech":"Register as Technician",
  }[mode] || "Login";

  const SERVICE_CATS = ["Plumber","Electrician","Gas Service","Bike Mechanic","Mobile Technician","Cleaning Service","AC Technician","Carpenter","Painter"];

  return (
    <div className={`auth-page ${mounted ? "auth-page--visible" : ""}`}>
      <div className="auth-bg">
        <div className="auth-orb auth-orb--1" />
        <div className="auth-orb auth-orb--2" />
        <div className="auth-orb auth-orb--3" />
      </div>

      <div className="auth-container">
        {/* Brand */}
        <div className="auth-brand">
          <div className="auth-brand-logo">🛠️</div>
          <h1 className="auth-brand-name">Sevai Hub</h1>
          <p className="auth-brand-tagline">Secure Role-Driven Service Platform</p>
        </div>

        {/* Role Tabs */}
        <div className="auth-role-tabs">
          {ROLES.map(r => (
            <button key={r.key}
              className={`auth-role-tab ${activeRole === r.key ? "auth-role-tab--active" : ""}`}
              style={{ "--tab-color": r.color }}
              onClick={() => handleRoleChange(r.key)}
              id={`role-tab-${r.key}`}>
              <span className="auth-role-tab-icon">{r.icon}</span>
              <span className="auth-role-tab-label">{r.label}</span>
              <span className="auth-role-tab-desc">{r.desc}</span>
            </button>
          ))}
        </div>

        {/* ── Demo Credentials Panel ─────────────────────────────── */}
        {activeRole !== "admin" && (
          <div className="demo-creds-panel">
            <button className="demo-creds-toggle" onClick={() => setShowDemo(v => !v)} type="button" id="demo-toggle-btn">
              <span>🧪 Demo / Test Credentials (click to auto-fill)</span>
              <span className="demo-creds-toggle-arrow">{showDemo ? "▲" : "▼"}</span>
            </button>
            {showDemo && (
              <div className="demo-creds-body">
                <p className="demo-creds-hint">All passwords work via local store — no PostgreSQL required:</p>
                <div className="demo-creds-list">
                  {demoCreds.map((cred, i) => (
                    <button key={i} type="button" className="demo-cred-item" id={`demo-cred-${i}`}
                      onClick={() => fillDemo(cred)}>
                      <div className="demo-cred-label">{cred.label}</div>
                      <div className="demo-cred-details">
                        {cred.note} {cred.identifier} &nbsp;|&nbsp; 🔑 {cred.password}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── Auth Card ──────────────────────────────────────────── */}
        <div className="auth-card" key={activeRole + mode}>
          <div className="auth-card-header" style={{ "--header-color": roleInfo.color }}>
            <span className="auth-card-header-icon">{roleInfo.icon}</span>
            <div>
              <h2>{modeLabel}</h2>
              <p>{roleInfo.desc} — {mode === "login" ? "sign in securely" : "create your account"}</p>
            </div>
          </div>

          {activeRole === "admin" && mode === "login" && (
            <div className="auth-security-badge">🔒 High-Security Admin Zone — Multi-Factor Verification Required</div>
          )}

          {error   && <div className="auth-alert auth-alert--error">{error}</div>}
          {success && <div className="auth-alert auth-alert--success">{success}</div>}

          <form className="auth-form" onSubmit={handleSubmit} autoComplete="off">

            {/* ── User Registration Form ─────────────────────────── */}
            {mode === "register" && activeRole === "user" && (<>
              <div className="auth-field">
                <label>Full Name *</label>
                <input id="reg-name" type="text" placeholder="Your full name"
                  value={regName} onChange={e => setRegName(e.target.value)} required />
              </div>
              <div className="auth-field">
                <label>Mobile Number *</label>
                <input id="reg-phone" type="tel" placeholder="10-digit mobile number"
                  value={regPhone} onChange={e => setRegPhone(e.target.value)} required maxLength={15} />
              </div>
              <div className="auth-field">
                <label>Email (optional)</label>
                <input id="reg-email" type="email" placeholder="your@email.com"
                  value={regEmail} onChange={e => setRegEmail(e.target.value)} />
              </div>
              <div className="auth-field">
                <label>Password *</label>
                <div className="auth-field-password">
                  <input id="reg-pass" type={showPass ? "text" : "password"} placeholder="Create a password"
                    value={regPass} onChange={e => setRegPass(e.target.value)} required />
                  <button type="button" className="auth-show-pass" onClick={() => setShowPass(p => !p)}>
                    {showPass ? "🙈" : "👁️"}
                  </button>
                </div>
              </div>
            </>)}

            {/* ── Technician Self-Register Form ─────────────────── */}
            {mode === "reg-tech" && activeRole === "technician" && (<>
              <div className="auth-field">
                <label>Full Name *</label>
                <input id="tech-name" type="text" placeholder="Your full name"
                  value={techName} onChange={e => setTechName(e.target.value)} required />
              </div>
              <div className="auth-field">
                <label>Mobile Number *</label>
                <input id="tech-phone" type="tel" placeholder="10-digit mobile number"
                  value={techPhone} onChange={e => setTechPhone(e.target.value)} required maxLength={15} />
              </div>
              <div className="auth-field">
                <label>Email (optional)</label>
                <input id="tech-email" type="email" placeholder="your@email.com"
                  value={techEmail} onChange={e => setTechEmail(e.target.value)} />
              </div>
              <div className="auth-field">
                <label>Service Category</label>
                <select id="tech-cat" value={techCategory} onChange={e => setTechCategory(e.target.value)}
                  style={{ padding: "12px 16px", background: "var(--bg-surface)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)", color: "var(--text-primary)", fontSize: "14px", fontFamily: "Inter, sans-serif" }}>
                  {SERVICE_CATS.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div className="auth-field">
                <label>City</label>
                <input id="tech-city" type="text" placeholder="e.g., Chennai, Bangalore"
                  value={techCity} onChange={e => setTechCity(e.target.value)} />
              </div>
              <div className="auth-field">
                <label>Address (optional)</label>
                <input id="tech-address" type="text" placeholder="Street address or area name"
                  value={techAddress} onChange={e => setTechAddress(e.target.value)} />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", fontSize: "12px", color: "var(--text-secondary)" }}>
                <div className="auth-field">
                  <label style={{ fontSize: "13px" }}>Latitude</label>
                  <input id="tech-lat" type="number" step="0.0001" placeholder="13.0827"
                    value={techLat} onChange={e => setTechLat(parseFloat(e.target.value))} />
                </div>
                <div className="auth-field">
                  <label style={{ fontSize: "13px" }}>Longitude</label>
                  <input id="tech-lon" type="number" step="0.0001" placeholder="80.2707"
                    value={techLon} onChange={e => setTechLon(parseFloat(e.target.value))} />
                </div>
              </div>
              <small style={{ color: "var(--text-tertiary)", display: "block", textAlign: "center", marginBottom: "8px" }}>
                📍 Use your current GPS coordinates. Defaults to Chennai center.
              </small>
              <div className="auth-field">
                <label>Password *</label>
                <div className="auth-field-password">
                  <input id="tech-pass" type={showPass ? "text" : "password"} placeholder="Create a password"
                    value={techPass} onChange={e => setTechPass(e.target.value)} required />
                  <button type="button" className="auth-show-pass" onClick={() => setShowPass(p => !p)}>
                    {showPass ? "🙈" : "👁️"}
                  </button>
                </div>
              </div>
            </>)}

            {/* ── Login Form Fields ──────────────────────────────── */}
            {mode === "login" && (<>
              <div className="auth-field">
                <label>{activeRole === "admin" ? "Admin Mobile Number" : "Email or Mobile Number"}</label>
                <input id="auth-identifier" type="text"
                  placeholder={activeRole === "admin" ? "Admin registered mobile" : "Email or mobile number"}
                  value={identifier} onChange={e => setIdentifier(e.target.value)} required autoComplete="off" />
              </div>
              {activeRole === "admin" && (
                <div className="auth-field">
                  <label>Aadhaar Number</label>
                  <input id="auth-aadhaar" type="password" placeholder="12-digit Aadhaar"
                    value={aadhaar} onChange={e => setAadhaar(e.target.value)} required maxLength={12} autoComplete="off" />
                </div>
              )}
              <div className="auth-field">
                <label>Password</label>
                <div className="auth-field-password">
                  <input id="auth-password" type={showPass ? "text" : "password"} placeholder="Enter your password"
                    value={password} onChange={e => setPassword(e.target.value)} required autoComplete="new-password" />
                  <button type="button" className="auth-show-pass" onClick={() => setShowPass(p => !p)}>
                    {showPass ? "🙈" : "👁️"}
                  </button>
                </div>
              </div>
            </>)}

            <button type="submit" id="auth-submit-btn" className="auth-submit"
              style={{ "--btn-color": roleInfo.color }} disabled={loading}>
              {loading
                ? <span className="auth-submit-spinner" />
                : <>{roleInfo.icon} {mode === "register" ? "Create Account" : mode === "reg-tech" ? "Register as Technician" : `Sign In as ${roleInfo.label}`}</>
              }
            </button>
          </form>

          {/* ── Mode Toggle Links ───────────────────────────────── */}
          {activeRole === "user" && (
            <div className="auth-mode-toggle">
              {mode === "login"
                ? <>Don't have an account? <button onClick={() => { setMode("register"); resetForm(); }}>Register here</button></>
                : <>Already have an account? <button onClick={() => { setMode("login"); resetForm(); }}>Sign In</button></>
              }
            </div>
          )}

          {activeRole === "technician" && (
            <div className="auth-mode-toggle">
              {mode === "login"
                ? <>New technician? <button onClick={() => { setMode("reg-tech"); resetForm(); }}>Register your account</button></>
                : <>Already registered? <button onClick={() => { setMode("login"); resetForm(); }}>Sign In</button></>
              }
            </div>
          )}

          {activeRole === "admin" && (
            <p className="auth-admin-hint">Admin access is restricted. No public registration.</p>
          )}
        </div>

        <a href="/" className="auth-back-link">← Back to Sevai Hub</a>
      </div>
    </div>
  );
}
