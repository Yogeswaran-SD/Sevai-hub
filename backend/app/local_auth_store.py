"""
local_auth_store.py
===================
File-based persistent authentication store.
Works completely without PostgreSQL.

IMPORTANT: Call initialize() at server startup (see main.py).
This ensures hashing happens once at boot, never during a request.
"""
import json
import uuid
import bcrypt
from pathlib import Path

STORE_PATH = Path(__file__).parent.parent / "local_auth.json"

# Demo plaintext passwords
_DEMO_PW_USER = "demo123"
_DEMO_PW_TECH = "Sevai@123"

# Demo accounts definition (no hashes here — hashed at init time)
_DEMO_USERS = [
    {"id": "demo-user-001", "name": "Demo User",    "email": "user@demo.com", "phone": "1234567890",  "role": "user",       "is_active": True},
]

_DEMO_TECHNICIANS = [
    {"id": "demo-tech-001", "name": "Ravi Kumar",          "email": "ravi@demo.com", "phone": "9876543210"},
    {"id": "demo-tech-002", "name": "Murugan S",           "email": None,            "phone": "9876543211"},
    {"id": "demo-tech-003", "name": "Arjun Electricals",   "email": None,            "phone": "9876543220"},
    {"id": "demo-tech-004", "name": "Safe Gas Service",    "email": None,            "phone": "9876543230"},
    {"id": "demo-tech-005", "name": "Speed Bike Works",    "email": None,            "phone": "9876543240"},
    {"id": "demo-tech-006", "name": "Phone Doctor",        "email": None,            "phone": "9876543250"},
    {"id": "demo-tech-007", "name": "CleanHome TN",        "email": None,            "phone": "9876543260"},
    {"id": "demo-tech-008", "name": "Cool Air Services",   "email": None,            "phone": "9876543270"},
    {"id": "demo-tech-009", "name": "Kumar Carpentry",     "email": None,            "phone": "9876543280"},
    {"id": "demo-tech-010", "name": "ColorCraft TN",       "email": None,            "phone": "9876543290"},
]

# In-memory cache — loaded once at startup
_CACHE: dict | None = None


# ─── Hashing helpers (direct bcrypt, no passlib) ─────────────────────────────

def _hash(pw: str, rounds: int = 12) -> str:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt(rounds)).decode("utf-8")

def _verify(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ─── Build default store (called once at startup) ─────────────────────────────

def _build_default_store() -> dict:
    """Hash demo passwords with rounds=4 (fast ≈5ms each) for seeding."""
    print("[AuthStore] Building demo credential store (first-time setup)...")
    store: dict = {"users": {}, "technicians": {}}

    user_hpw = _hash(_DEMO_PW_USER, rounds=4)      # fast for demo
    tech_hpw = _hash(_DEMO_PW_TECH, rounds=4)      # fast for demo

    for u in _DEMO_USERS:
        rec = {**u, "hpw": user_hpw}
        store["users"][u["phone"]] = rec
        if u.get("email"):
            store["users"][u["email"]] = rec

    for t in _DEMO_TECHNICIANS:
        rec = {**t, "role": "technician", "hpw": tech_hpw}
        store["technicians"][t["phone"]] = rec
        if t.get("email"):
            store["technicians"][t["email"]] = rec

    print(f"[AuthStore] Created {len(_DEMO_USERS)} users, {len(_DEMO_TECHNICIANS)} technicians.")
    return store


# ─── Initialize (call at server startup) ─────────────────────────────────────

def initialize() -> None:
    """
    Initialize the auth store. Call this in FastAPI startup event.
    Loads from disk if local_auth.json exists, otherwise creates it.
    """
    global _CACHE
    if STORE_PATH.exists():
        try:
            with open(STORE_PATH, "r", encoding="utf-8") as f:
                _CACHE = json.load(f)
            print(f"[AuthStore] Loaded {len(_CACHE['users'])} users, {len(_CACHE['technicians'])} technicians from {STORE_PATH.name}")
            return
        except Exception as e:
            print(f"[AuthStore] Warning: could not read {STORE_PATH}: {e}. Rebuilding...")

    _CACHE = _build_default_store()
    _save_cache()


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _load() -> dict:
    """Return the in-memory cache, initializing if not already done."""
    global _CACHE
    if _CACHE is None:
        initialize()
    return _CACHE

def _save_cache() -> None:
    try:
        with open(STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(_CACHE, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[AuthStore] Warning: could not save store: {e}")


# ─── Public API ───────────────────────────────────────────────────────────────

def find_user(identifier: str):
    return _load()["users"].get(identifier.strip())

def find_technician(identifier: str):
    return _load()["technicians"].get(identifier.strip())

def auth_user(identifier: str, password: str):
    u = find_user(identifier)
    if u and _verify(password, u["hpw"]):
        return u
    return None

def auth_technician(identifier: str, password: str):
    t = find_technician(identifier)
    if t and _verify(password, t["hpw"]):
        return t
    return None

def register_user(name: str, phone: str, password: str, email: str = None) -> dict:
    store = _load()
    phone = phone.strip()
    if phone in store["users"]:
        raise ValueError("Phone number is already registered.")
    if email and email.strip() in store["users"]:
        raise ValueError("Email is already registered.")

    uid = str(uuid.uuid4())
    hpw = _hash(password, rounds=12)   # full rounds for real accounts
    rec = {"id": uid, "name": name, "email": email, "phone": phone,
           "hpw": hpw, "role": "user", "is_active": True}
    store["users"][phone] = rec
    if email:
        store["users"][email.strip()] = rec
    _save_cache()
    return rec

def register_technician(name: str, phone: str, password: str,
                        email: str = None, service_category: str = "Plumber") -> dict:
    store = _load()
    phone = phone.strip()
    if phone in store["technicians"]:
        raise ValueError(f"Phone {phone} is already registered as a technician.")
    if email and email.strip() in store["technicians"]:
        raise ValueError(f"Email {email} is already registered as a technician.")

    uid = str(uuid.uuid4())
    hpw = _hash(password, rounds=12)
    rec = {"id": uid, "name": name, "email": email, "phone": phone,
           "hpw": hpw, "role": "technician", "service_category": service_category}
    store["technicians"][phone] = rec
    if email:
        store["technicians"][email.strip()] = rec
    _save_cache()
    return rec

def list_all_users() -> list:
    seen, out = set(), []
    for u in _load()["users"].values():
        if u["id"] not in seen:
            seen.add(u["id"])
            out.append(u)
    return out

def list_all_technicians() -> list:
    seen, out = set(), []
    for t in _load()["technicians"].values():
        if t["id"] not in seen:
            seen.add(t["id"])
            out.append(t)
    return out
