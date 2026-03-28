from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database import engine, Base
from app.routers import auth, technicians, services, intelligence, admin, dashboard


# ─── Startup: initialize DB tables + auth store ──────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Try to create DB tables (safe even if DB is offline)
    try:
        Base.metadata.create_all(bind=engine)
        print("[OK] Database tables verified/created.")
    except Exception as e:
        print(f"[WARN] DB offline — running in local-store mode. ({e.__class__.__name__})")

    # 2. Initialize the local auth store (hashes demo passwords ONCE at boot)
    from app.local_auth_store import initialize as init_auth_store
    init_auth_store()

    # 3. Initialize Redis cache connection
    from app.services.cache_service import get_redis
    try:
        await get_redis()
        print("[OK] Redis cache initialized.")
    except Exception as e:
        print(f"[WARN] Redis cache unavailable: {str(e)}")

    # 4. Initialize MinIO storage bucket
    from app.services.storage_service import ensure_bucket_exists
    try:
        ensure_bucket_exists()
        print("[OK] MinIO storage initialized.")
    except Exception as e:
        print(f"[WARN] MinIO storage unavailable: {str(e)}")

    yield  # server runs here

    # Cleanup on shutdown
    from app.services.cache_service import close_redis
    await close_redis()
    print("[OK] Cache connection closed.")
    print("[OK] Shutting down.")



# ─── App ─────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version="4.0.0",
    description="Sevai Hub — Secure RBAC Multi-Role Service Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS - Restrict to configured origins only
cors_origins = settings.cors_origins_list if not settings.ALLOW_ORIGINS_ALL else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Routers
app.include_router(auth.router)
app.include_router(technicians.router)
app.include_router(services.router)
app.include_router(intelligence.router)
app.include_router(admin.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": "4.0.0",
        "status": "running",
        "message": "Welcome to Sevai Hub API — RBAC + Auth Active",
        "roles": ["user", "technician", "admin"],
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
