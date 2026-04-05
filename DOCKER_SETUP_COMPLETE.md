# 🐳 SevaiHub Docker Complete Setup & Fix Guide

## Overview

This guide will help you set up the complete SevaiHub application with Docker, including:
- ✅ **PostgreSQL 16** with **PostGIS 3.4** (geospatial database)
- ✅ **FastAPI Backend** (runs on port 8000)
- ✅ **React Frontend** (runs on port 8080 via Nginx)
- ✅ **Redis Cache** (runs on port 6379)
- ✅ **MinIO Storage** (runs on ports 9000/9001)
- ✅ **Nginx Reverse Proxy** (runs on port 8080)

---

## ⚡ Quick Start (Recommended)

### Windows (PowerShell)
```powershell
# Navigate to project directory
cd d:\Intern\vlog\sevaihub

# Run setup script
.\setup-docker.ps1
```

### Windows (Command Prompt)
```cmd
cd d:\Intern\vlog\sevaihub
setup-docker.bat
```

### Linux/Mac (Bash)
```bash
cd /path/to/sevaihub
chmod +x setup-docker.ps1
# Or just use Docker commands below
```

---

## 🔧 Manual Setup (Step-by-Step)

If the scripts don't work, follow these steps:

### Step 1: Stop Any Running Containers
```bash
docker-compose down -v
```

### Step 2: Build All Images
```bash
docker-compose build --no-cache
```

This builds:
- `sevaihub-backend` (FastAPI)
- `sevaihub-frontend` (React)

PostgreSQL, Redis, MinIO pull pre-built images.

### Step 3: Start All Services
```bash
docker-compose up -d
```

### Step 4: Wait for Services (30-60 seconds)
Services will automatically initialize:
- PostgreSQL + PostGIS extension
- Tables and schema
- Backend health check
- Frontend static files

### Step 5: Verify Everything is Running
```bash
docker-compose ps
```

Expected output:
```
NAME                     STATUS
sevaihub-postgres       Healthy
sevaihub-redis          Healthy
sevaihub-minio          Healthy
sevaihub-backend        Healthy (or Running)
sevaihub-frontend       Healthy (or Running)
sevaihub-proxy          Running
```

### Step 6: Verify PostGIS
```bash
docker-compose exec postgres psql -U postgres -d sevaihub -c "SELECT postgis_version();"
```

Should output PostGIS version.

---

## 🌐 Access the Application

Once all containers are running:

### Frontend
- **URL:** http://localhost:8080
- **What:** React application (Nginx serves static files)

### Backend API
- **URL:** http://localhost:8000
- **Docs:** http://localhost:8000/docs (Swagger UI)
- **Health:** http://localhost:8000/health

### Database
- **Host:** localhost
- **Port:** 5432
- **Username:** postgres
- **Password:** postgres_dev_password_123
- **Database:** sevaihub
- **PostGIS:** ✅ Already installed

### MinIO (Object Storage)
- **API:** http://localhost:9000
- **Console:** http://localhost:9001
- **Username:** minioadmin
- **Password:** minioadmin123

### Redis
- **Host:** localhost
- **Port:** 6379

---

## 🔑 Default Credentials

### Admin Login
| Field | Value |
|-------|-------|
| Mobile | 9999999999 |
| Aadhaar | 123456789012 |
| Password | Check local_auth.json or use "Sevai@123" |

### Demo Technicians
All available in `local_auth_store.py` with password: **Sevai@123**

| Phone | Name |
|-------|------|
| 9876543210 | Ravi Kumar |
| 9876543211 | Murugan S |
| 9876543220 | Arjun Electricals |

---

## 🔍 Troubleshooting

### Issue: Frontend shows "Cannot reach backend server"

**Cause:** Frontend is pointing to wrong backend URL

**Solution 1:** Verify frontend `.env`:
```bash
cat frontend/.env
# Should show: VITE_API_URL=http://sevaihub-backend:8000
```

**Solution 2:** Rebuild frontend
```bash
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

**Solution 3:** Clear browser cache
- Ctrl+Shift+Del (or Cmd+Shift+Del on Mac)
- Clear all cache
- Reload page

### Issue: Database connection failed

**Cause:** PostgreSQL not initialized or password mismatch

**Solution:**
```bash
# Check database logs
docker-compose logs postgres

# Reset database and restart
docker-compose down -v
docker-compose up -d postgres

# Wait 30 seconds for initialization
docker-compose up -d
```

### Issue: PostGIS not installed

**Cause:** Extension not initialized on startup

**Solution:**
```bash
# Manually enable PostGIS
docker-compose exec postgres psql -U postgres -d sevaihub << EOF
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
SELECT postgis_version();
EOF
```

### Issue: Port already in use (Address already in use)

**Cause:** Another service is using ports 8000, 8080, 5432, etc.

**Solution 1:** Stop the conflicting service
```bash
# Find process using port 8080
netstat -ano | findstr :8080

# Kill it (replace PID)
taskkill /PID <PID> /F
```

**Solution 2:** Change ports in `docker-compose.yml`
```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Changed from 8000 to 8001

  frontend:
    ports:
      - "8081:80"    # Changed from 8080 to 8081
```

### Issue: Containers won't start

**Solution:**
```bash
# View detailed logs
docker-compose logs

# Rebuild everything
docker-compose build --no-cache

# Clean up and restart
docker system prune -a
docker-compose up -d
```

---

## 📊 What Images Are Used?

| Service | Image | Size |
|---------|-------|------|
| PostgreSQL | postgis/postgis:16-3.4-alpine | ~150MB |
| Redis | redis:7-alpine | ~30MB |
| MinIO | minio/minio:latest | ~500MB |
| Backend | `docker build from Dockerfile` | ~300MB |
| Frontend | `docker build from Dockerfile` | ~150MB |
| Nginx | Built-in with frontend | Included |

**Total disk space needed:** ~1.5GB

---

## 🔄 Common Commands

```bash
# Start services
docker-compose up -d

# Stop services (keeps data)
docker-compose down

# Stop and remove all data
docker-compose down -v

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Connect to database
docker-compose exec postgres psql -U postgres -d sevaihub

# Connect to container shell
docker-compose exec backend bash

# Rebuild images
docker-compose build --no-cache

# Rebuild specific service
docker-compose build --no-cache backend

# Remove all Docker containers/images
docker system prune -a
```

---

## 🧪 Verify Everything Works

Run the verification script:

### Windows (PowerShell)
```powershell
.\verify-docker.ps1
```

### Using Docker directly
```bash
# Check all containers
docker-compose ps

# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost:8080

# Test database
docker-compose exec postgres psql -U postgres -d sevaihub -c "SELECT postgis_version();"

# Test Redis
docker-compose exec redis redis-cli ping
```

---

## 📁 Configuration Files

### `.env` (Main configuration)
Contains database credentials, API keys, admin credentials

### `.env.docker` (Docker-specific)
Use this for Docker deployments (already configured correctly)

### `docker-compose.yml` 
Defines all services, ports, volumes, environment variables

### `frontend/.env`
Frontend configuration - **should be:** `VITE_API_URL=http://sevaihub-backend:8000`

---

## 🚀 Development Workflow

### Making Changes to Backend
```bash
# Backend code changes are hot-reloaded automatically
# Just edit files in backend/app/

# Restart only if schema changes
docker-compose restart backend

# View logs
docker-compose logs -f backend
```

### Making Changes to Frontend
```bash
# Frontend changes are hot-reloaded automatically
# Edit files in frontend/src/

# If build errors occur
docker-compose restart frontend
```

### Making Database Schema Changes
```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d sevaihub

# Or use SQLAlchemy migrations
docker-compose exec backend alembic upgrade head
```

---

## 🔐 Security Notes

⚠️ **For Development Only**
- Default credentials are hardcoded
- No HTTPS/SSL configured
- PostGIS data is stored in Docker volume

✅ **Before Production**
- Change all default passwords in `.env`
- Set `DEBUG=False` in backend
- Configure SSL/HTTPS with proper certificates
- Use environment variables for sensitive data
- Set up proper database backups
- Configure proper authentication

---

## 📝 Next Steps

1. ✅ Run `setup-docker.ps1` or `setup-docker.bat`
2. ✅ Wait for all containers to be healthy
3. ✅ Open http://localhost:8080 in browser
4. ✅ Login with admin credentials
5. ✅ Test technician registration
6. ✅ Check service search functionality
7. ✅ Verify database contains data

---

## 💬 Getting Help

If issues persist:

1. **Check logs:** `docker-compose logs -f`
2. **Run verification:** `.\verify-docker.ps1`
3. **Reset everything:** `docker-compose down -v && docker-compose up -d`
4. **Check GitHub issues:** For known problems
5. **Review docker-compose.yml:** Verify all services are configured correctly

---

## 📚 Additional Resources

- **Docker Docs:** https://docs.docker.com
- **PostGIS Docs:** https://postgis.net/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React Docs:** https://react.dev
- **Docker Compose Docs:** https://docs.docker.com/compose

---

**Status:** ✅ Complete Docker setup ready for development and testing!
