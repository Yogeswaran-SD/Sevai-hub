# 🛠️ Sevai Hub

> **Spatially Optimized Emergency Allocation Engine — Tamil Nadu**

Sevai Hub is not just a service discovery platform. It is a **geo-intelligent, emergency-aware urban response engine** built using geospatial intelligence, predictive modeling, weighted ranking, and performance benchmarking.

---

## 🚀 Getting Started

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Update .env with your PostgreSQL credentials + PostGIS enabled:
# psql -U postgres -c "CREATE DATABASE sevaihub;"
# psql -U postgres -d sevaihub -c "CREATE EXTENSION postgis;"

# Run server
uvicorn app.main:app --reload --port 8000

# Seed sample data (includes TTI fields)
python seed.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

---

## 🗂️ Project Structure

```
sevaihub/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── database.py          # DB session
│   │   ├── intelligence.py      # 🧠 ALL 9 intelligence modules
│   │   ├── models/
│   │   │   ├── technician.py    # TTI fields added
│   │   │   └── user.py
│   │   ├── schemas/
│   │   │   ├── technician.py    # TTI/ETA/Risk sub-schemas
│   │   │   └── user.py
│   │   ├── routers/
│   │   │   ├── technicians.py   # Intelligence-powered routes
│   │   │   ├── auth.py
│   │   │   └── services.py
│   │   └── core/
│   ├── seed.py                  # Seeder with TTI data
│   └── requirements.txt
│
└── frontend/
    └── src/
        ├── App.jsx
        ├── index.css            # Full design system + animations
        ├── api/api.js           # Intelligence API calls
        ├── pages/
        │   ├── Home.jsx
        │   └── Search.jsx       # Emergency Risk UI + Adaptive Radius
        └── components/
            ├── Navbar.jsx
            ├── ServiceCard.jsx
            ├── TechnicianCard.jsx  # TTI badge + ETA + Rank medal
            ├── MapView.jsx         # TTI-coloured markers + radius circle
            └── ChatAssistant.jsx   # Emergency severity scoring
```

---

## 🧠 Intelligence Modules

| # | Module | Location |
|---|---|---|
| 1 | Emergency Severity Scoring Engine | `intelligence.py` → `compute_emergency_risk()` |
| 2 | Technician Trust Index (TTI) | `intelligence.py` → `compute_tti()` |
| 3 | Adaptive Search Radius Algorithm | `intelligence.py` → `get_adaptive_radius_steps()` |
| 4 | Response Time Prediction Model | `intelligence.py` → `predict_eta()` |
| 5 | Weighted Allocation Model | `intelligence.py` → `compute_weighted_score()` |
| 6 | Performance Transparency Mode | `intelligence.py` → `get_performance_report()` |
| 7 | Urban Demand Heatmap Context | Services info in `services.py` |
| 8 | Emergency Simulation Awareness | `/technicians/system/performance` |
| 9 | Transparency Principles | All responses include TTI, ETA, risk score |

---

## 🔑 Key API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API health |
| `POST` | `/auth/register` | Register user |
| `POST` | `/auth/login` | Login |
| `GET` | `/services/` | All service categories |
| `GET` | `/technicians/nearby` | 🧠 Adaptive search + TTI + ETA + Risk |
| `GET` | `/technicians/emergency/score` | 🚨 Emergency risk scoring |
| `GET` | `/technicians/tti/calculate` | 🛡 TTI computation |
| `GET` | `/technicians/system/performance` | 📊 Performance transparency |
| `GET` | `/technicians/{id}` | Technician detail + intelligence |
| `PUT` | `/technicians/{id}/availability` | Update + recalculate TTI |

### `/technicians/nearby` Query Params
```
latitude          float  (required)
longitude         float  (required)
service_category  string (required)
radius_km         float  default=3   [auto-expands: 3→5→8→15km]
urgency_level     string default=Low [Low|Medium|High|Critical]
emergency_query   string (optional)  [free-text for risk scoring]
```

---

## 📊 TTI Formula

```
TTI Score =
  (0.30 × Response Reliability) +
  (0.25 × Cancellation Performance) +
  (0.20 × Rating Stability) +
  (0.15 × Availability Consistency) +
  (0.10 × Verification Age Factor)
```

| Score | Label |
|---|---|
| ≥85% | 🟢 Highly Reliable |
| ≥70% | 🔵 Reliable |
| ≥50% | 🟡 Moderate |
| <50% | 🔴 Low Trust |

---

## ⚖️ Weighted Allocation Formula

```
Final Score =
  (0.50 × Distance Weight) +
  (0.20 × Rating Weight) +
  (0.20 × Trust Index Weight) +
  (0.10 × Emergency Severity Weight)

Lower score = Higher priority
```

---

## 🗄️ PostGIS Proximity Query

```sql
SELECT t.*,
  ST_Distance(t.location::geography, ST_MakePoint(:lon, :lat)::geography) / 1000 AS distance_km
FROM technicians t
WHERE t.is_available = true
  AND t.service_category = :category
  AND ST_DWithin(t.location::geography, ST_MakePoint(:lon, :lat)::geography, :radius_m)
ORDER BY distance_km ASC, t.rating DESC, t.is_verified DESC
LIMIT 20;
-- GiST index: ~30-50× faster than sequential scan
```

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy, GeoAlchemy2 |
| Database | PostgreSQL + PostGIS (GiST spatial index) |
| Intelligence | Pure Python — `intelligence.py` |
| Auth | JWT (python-jose) |
| Frontend | React 18, Vite |
| Maps | Leaflet + react-leaflet (TTI-coloured markers) |
| Styling | Vanilla CSS (premium dark design system) |
