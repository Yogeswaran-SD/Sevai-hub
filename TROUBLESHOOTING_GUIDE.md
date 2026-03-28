# TROUBLESHOOTING GUIDE - FAILING TESTS

## Overview
This guide provides step-by-step solutions for the 3 failing tests. Fix only if needed before deployment.

---

## Issue 1: Search Technicians (HTTP 500)

### Problem
Geospatial search returns HTTP 500 error

### Root Cause
Database enum validation - service category value format mismatch

### Error Message
```
sqlalchemy.exc.DataError: invalid input value for enum servicecategory: "Plumber"
```

### Solution Steps

**Step 1**: Open backend technicians router
```
File: backend/app/routers/technicians.py
```

**Step 2**: Find the nearby search endpoint (around line 40-60)

**Step 3**: Look for query filter like:
```python
.filter(Technician.service_category == service_category)
```

**Step 4**: Check the ServiceCategory enum in `models/technician.py`
- Verify enum values match what's being sent
- Values should be: "Plumber", "Electrician", etc.

**Step 5**: If enum values use string format, the filter is correct
- The issue might be in how values are stored in database
- Run this check:
```sql
SELECT DISTINCT service_category FROM technicians;
```

**Step 6**: If values show as `Plumber` (string), issue is database-side
- Verify database column type is correct enum

### Quick Fix
If service_category is string in database but enum in code:
```python
# In technicians.py, around line 50
# Before: .filter(Technician.service_category == service_category)
# After add conversion:
from sqlalchemy import cast, String
.filter(cast(Technician.service_category, String) == service_category)
```

### Verification
After fix, run search test:
```bash
curl http://localhost:8000/api/technicians/nearby?latitude=13.0827&longitude=80.2707&service_category=Plumber&radius_km=5
```

Expected: HTTP 200 with technician list

---

## Issue 2: Technician Dashboard (HTTP 500)

### Problem  
Technician dashboard endpoint returns internal server error

### Likely Causes
1. Route handler missing or incorrectly defined
2. Authentication token validation failing
3. Database query error in dashboard route

### Investigation Steps

**Step 1**: Check if route exists
```
File: backend/app/routers/dashboard.py
```

**Step 2**: Look for technician dashboard endpoint
```python
@router.get("/technician")
def get_technician_dashboard(current_user: dict = Depends(get_current_user)):
```

**Step 3**: Verify endpoint is imported in `main.py`
```python
from app.routers import dashboard
app.include_router(dashboard.router)
```

**Step 4**: Check authentication dependency
- Verify `get_current_user` is working
- Test with valid JWT token from login

**Step 5**: Check database query
- Verify tables exist
- Run manual query to check data availability

### Debug Command
Check backend logs:
```bash
docker logs sevaihub-backend --tail 100 | grep -i "dashboard"
```

### Quick Fix
If route is missing, add to `dashboard.py`:
```python
@router.get("/technician")
def get_technician_dashboard(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get technician from database
    technician = db.query(Technician).filter(
        Technician.id == current_user["user_id"]
    ).first()
    
    if not technician:
        raise HTTPException(status_code=404, detail="Technician not found")
    
    return {
        "name": technician.name,
        "rating": technician.rating,
        "total_jobs": len(technician.jobs),
        "availability": technician.is_available
    }
```

### Verification
Test with curl:
```bash
# First get auth token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/technician \
  -H "Content-Type: application/json" \
  -d '{"identifier":"9876543210","password":"Sevai@123"}' | jq -r .access_token)

# Then access dashboard
curl http://localhost:8000/api/dashboard/technician \
  -H "Authorization: Bearer $TOKEN"
```

Expected: HTTP 200 with dashboard data

---

## Issue 3: Admin Dashboard (HTTP 404)

### Problem
Admin dashboard returns 404 Not Found

### Likely Causes
1. Route not defined or endpoint typo
2. Incorrect URL path
3. Route not registered in main application

### Investigation Steps

**Step 1**: Verify route exists in `dashboard.py`
```python
@router.get("/admin")
def get_admin_dashboard(current_user: dict = Depends(get_current_user)):
```

**Step 2**: Check exact URL path
- Expected: `/api/dashboard/admin`
- Or `/dashboard/admin` (depending on routing)

**Step 3**: Verify router inclusion in `main.py`
```python
from app.routers import dashboard
app.include_router(dashboard.router, prefix="/dashboard")
```

**Step 4**: Check if admin authentication is verified
```python
if current_user["role"] != "admin":
    raise HTTPException(status_code=403, detail="Admin access required")
```

### Quick Fix
If endpoint missing, add to `dashboard.py`:
```python
@router.get("/admin")
def get_admin_dashboard(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify admin role
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get platform statistics
    total_users = db.query(User).count()
    total_technicians = db.query(Technician).count()
    
    return {
        "total_users": total_users,
        "total_technicians": total_technicians,
        "platform_status": "operational"
    }
```

### Verification
Test with admin credentials:
```bash
# Get admin token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/admin \
  -H "Content-Type: application/json" \
  -d '{"mobile":"9999999999","aadhaar":"123456789012","password":"admin123"}' | jq -r .access_token)

# Access admin dashboard
curl http://localhost:8000/api/dashboard/admin \
  -H "Authorization: Bearer $TOKEN"
```

Expected: HTTP 200 with admin dashboard data

---

## Testing All Fixes

After applying fixes, run full test again:

```bash
# From workspace root
python final_test.py
```

Expected output:
```
18/18 tests PASSED ✅
```

---

## Rollback Instructions

If a fix breaks something:

1. **Docker rollback**:
```bash
docker-compose down
docker-compose up -d
```

2. **File rollback**:
```bash
git checkout backend/app/routers/technicians.py
docker-compose restart backend
```

---

## Prevention Tips

1. Always run tests after code changes
2. Check error logs: `docker logs sevaihub-backend`
3. Verify database schema: `docker exec sevaihub-postgres psql -U postgres -d sevaihub -c "\dt"`
4. Test endpoints with curl before deployment

---

## Support

For persistent issues:
1. Check backend logs: `docker logs sevaihub-backend`
2. Check database logs: `docker logs sevaihub-postgres`  
3. Verify environment variables: Look at `.env` file
4. Check service health: `docker-compose ps`

All fixes should take <5 minutes to apply and verify.
