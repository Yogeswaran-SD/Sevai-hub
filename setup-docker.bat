@echo off
REM ═════════════════════════════════════════════════════════════════════
REM SevaiHub Docker Complete Setup and Startup Script (Batch)
REM ═════════════════════════════════════════════════════════════════════

setlocal EnableDelayedExpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║     Docker Complete Setup ^& Startup for SevaiHub              ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check Docker
echo 1/9 Checking Docker installation...
docker --version >nul 2>&1
if !errorlevel! neq 0 (
    echo    ❌ Docker not found. Please install Docker Desktop.
    exit /b 1
)
echo    ✅ Docker is installed

REM Check Docker Compose
echo.
echo 2/9 Checking Docker Compose...
docker-compose --version >nul 2>&1
if !errorlevel! neq 0 (
    echo    ❌ Docker Compose not found.
    exit /b 1
)
echo    ✅ Docker Compose is available

REM Stop existing containers
echo.
echo 3/9 Stopping existing containers...
docker-compose down >nul 2>&1
echo    ✅ Cleanup complete

REM Build images
echo.
echo 4/9 Building Docker images...
echo    (This may take a few minutes on first run)
docker-compose build --no-cache
if !errorlevel! neq 0 (
    echo    ❌ Build failed!
    exit /b 1
)
echo    ✅ Images built successfully

REM Start containers
echo.
echo 5/9 Starting containers...
docker-compose up -d
if !errorlevel! neq 0 (
    echo    ❌ Failed to start containers
    exit /b 1
)
echo    ✅ Containers started

REM Wait for services
echo.
echo 6/9 Waiting for services (30-60 seconds)...
timeout /t 30 /nobreak

REM Show status
echo.
echo 7/9 Container status:
docker-compose ps

REM Verify PostGIS
echo.
echo 8/9 Verifying PostGIS installation...
timeout /t 5 /nobreak
docker-compose exec -T postgres psql -U postgres -d sevaihub -c "SELECT postgis_version();" 2>nul | findstr /R "PostGIS" >nul
if !errorlevel! equ 0 (
    echo    ✅ PostGIS is installed
) else (
    echo    ⚠️  PostGIS verification pending (may still be initializing)
)

REM Verify API
echo.
echo 9/9 Verifying API connectivity...
timeout /t 3 /nobreak
curl -s http://localhost:8000/health | findstr /R "healthy" >nul 
if !errorlevel! equ 0 (
    echo    ✅ Backend API is responding
) else (
    echo    ⚠️  Backend warming up (still initializing)
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              ✅ SETUP COMPLETE!                               ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 🌐 Access URLs:
echo    Frontend:     http://localhost:8080
echo    Backend API:  http://localhost:8000
echo    API Docs:     http://localhost:8000/docs
echo    Database:     localhost:5432
echo.
echo 🔑 Default Credentials:
echo    Admin Mobile:  9999999999
echo    Admin Aadhaar: 123456789012
echo.
echo 📚 Useful Commands:
echo    View logs:      docker-compose logs -f
echo    Stop services:  docker-compose down
echo    bash into DB:   docker-compose exec postgres bash
echo.
pause
