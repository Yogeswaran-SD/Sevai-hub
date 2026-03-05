from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database import engine, Base
from app.routers import auth, technicians, services, intelligence

# Create all tables (graceful — works even if DB is offline)
try:
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables verified/created.")
except Exception as e:
    print(f"[WARN] DB not available at startup - running in demo mode. ({e.__class__.__name__})")

app = FastAPI(
    title=settings.APP_NAME,
    version="3.0.0",
    description="Spatially Optimized Emergency-Aware Urban Response Engine — 9 Intelligence Modules Active",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(technicians.router)
app.include_router(services.router)
app.include_router(intelligence.router)

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "message": "Welcome to Sevai Hub API 🛠️"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
