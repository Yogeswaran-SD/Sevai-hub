"""
Direct server-side test — runs the auth logic without HTTP layer.
Equivalent to what happens during a POST /auth/login/user request.
"""
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== SERVER-SIDE AUTH TEST ===\n")

# Step 1: Test local_auth_store
print("1. Initialize store...")
from app.local_auth_store import initialize, auth_user, auth_technician
initialize()
print("   Done.")

print("\n2. auth_user('1234567890', 'demo123')...")
try:
    u = auth_user("1234567890", "demo123")
    print(f"   Result: {u}")
except Exception as e:
    traceback.print_exc()

print("\n3. auth_technician('9876543210', 'Sevai@123')...")
try:
    t = auth_technician("9876543210", "Sevai@123")
    print(f"   Result: {t}")
except Exception as e:
    traceback.print_exc()

# Step 2: Test the auth router directly
print("\n4. Importing auth router...")
try:
    from app.routers.auth import login_user
    print("   Import OK.")
except Exception as e:
    traceback.print_exc()

# Step 3: Test DB dependency
print("\n5. Testing DB dependency (get_db)...")
try:
    from app.database import SessionLocal
    db = SessionLocal()
    db.close()
    print("   DB connected OK.")
except Exception as e:
    print(f"   DB offline (expected): {type(e).__name__}")

# Step 4: Simulate the full login_user call
print("\n6. Simulating login_user endpoint call...")
try:
    from app.schemas.user import UserLoginRequest
    from app.database import get_db
    
    creds = UserLoginRequest(identifier="1234567890", password="demo123")
    
    # get a db session (might fail if DB is offline)
    try:
        db = SessionLocal()
    except Exception:
        db = None
    
    result = login_user(creds, db)
    print(f"   SUCCESS: {result}")
except Exception as e:
    print(f"   ERROR: {type(e).__name__}: {e}")
    traceback.print_exc()

print("\n=== DONE ===")
