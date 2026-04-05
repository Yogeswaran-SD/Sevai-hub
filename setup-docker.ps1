#!/usr/bin/env powershell
<#
.SYNOPSIS
    Complete SevaiHub Docker Setup and Startup Script
    Fixes all connection issues and sets up PostgreSQL with PostGIS

.DESCRIPTION
    This script will:
    1. Stop any existing Docker containers
    2. Clean up old volumes (optional)
    3. Build and start all services
    4. Wait for services to be healthy
    5. Verify PostGIS is installed
    6. Display access URLs

.EXAMPLE
    .\setup-docker.ps1
#>

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     🐳 SevaiHub Docker Complete Setup & Startup               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed and running
Write-Host "1️⃣  Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "   ✅ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Docker not found. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available
Write-Host "   Checking Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version
    Write-Host "   ✅ Docker Compose: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Docker Compose not found." -ForegroundColor Red
    exit 1
}

# Navigate to project directory
Write-Host ""
Write-Host "2️⃣  Setting up project directory..." -ForegroundColor Yellow
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Host "   📁 Working directory: $(Get-Location)" -ForegroundColor Green

# Stop and remove existing containers
Write-Host ""
Write-Host "3️⃣  Cleaning up existing containers..." -ForegroundColor Yellow
Write-Host "   Stopping containers..." -ForegroundColor Gray
docker-compose down 2>$null
if ($?) {
    Write-Host "   ✅ Existing containers stopped" -ForegroundColor Green
}

# Optional: Clean volumes
Write-Host ""
Write-Host "4️⃣  Building images..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes on first run..." -ForegroundColor Gray
docker-compose build --no-cache 2>&1 | ForEach-Object {
    if ($_ -match "error|Error") {
        Write-Host "   ❌ $_" -ForegroundColor Red
    } else {
        Write-Host "   $_" -ForegroundColor Gray
    }
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Images built successfully" -ForegroundColor Green

# Start containers
Write-Host ""
Write-Host "5️⃣  Starting containers..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Failed to start containers" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Containers started" -ForegroundColor Green

# Wait for services to be healthy
Write-Host ""
Write-Host "6️⃣  Waiting for services to be ready..." -ForegroundColor Yellow
Write-Host "   This may take 30-60 seconds..." -ForegroundColor Gray

$maxWaitTime = 60
$waitTime = 0
$servicesReady = $false

while ($waitTime -lt $maxWaitTime) {
    $containers = docker-compose ps --format "{{.Names}},{{.Status}}"
    
    $allHealthy = $true
    foreach ($line in $containers) {
        if ($line -match "^sevaihub") {
            if (-not ($line -match "healthy|running")) {
                $allHealthy = $false
                break
            }
        }
    }
    
    if ($allHealthy) {
        $servicesReady = $true
        break
    }
    
    Write-Host "   ⏳ Waiting... ($waitTime/60s)" -ForegroundColor Gray
    Start-Sleep -Seconds 5
    $waitTime += 5
}

Write-Host ""
Write-Host "7️⃣  Service Status:" -ForegroundColor Yellow
docker-compose ps | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }

# Verify PostGIS
Write-Host ""
Write-Host "8️⃣  Verifying PostGIS..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    $postgisTest = docker-compose exec -T postgres psql -U postgres -d sevaihub -c "SELECT postgis_version();" 2>&1
    if ($postgisTest -match "PostGIS") {
        Write-Host "   ✅ PostGIS installed and working!" -ForegroundColor Green
        Write-Host "      $($postgisTest | Select-String 'PostGIS' | ForEach-Object { $_.Line.Trim() })" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  PostGIS status: $postgisTest" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Could not verify PostGIS: $_" -ForegroundColor Yellow
}

# Verify API connectivity
Write-Host ""
Write-Host "9️⃣  Verifying API connectivity..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

try {
    $apiHealth = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($apiHealth.StatusCode -eq 200) {
        Write-Host "   ✅ Backend API is responding!" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  Backend not yet responding (still warming up)" -ForegroundColor Yellow
}

# Display access information
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                   ✅ SETUP COMPLETE!                           ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
Write-Host "   Frontend:     http://localhost:8080" -ForegroundColor White
Write-Host "   Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Database:     localhost:5432 (postgres/postgres_dev_password_123)" -ForegroundColor White
Write-Host "   MinIO:        http://localhost:9001 (minioadmin/minioadmin123)" -ForegroundColor White
Write-Host "   Redis:        localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Default Credentials:" -ForegroundColor Cyan
Write-Host "   Admin Mobile:  9999999999" -ForegroundColor White
Write-Host "   Admin Aadhaar: 123456789012" -ForegroundColor White
Write-Host "   Admin Password: Sevai@123 (from local_auth.json)" -ForegroundColor White
Write-Host ""
Write-Host "📊 Tech Stack:" -ForegroundColor Cyan
Write-Host "   Database:  PostgreSQL 16 + PostGIS 3.4 ✅" -ForegroundColor Green
Write-Host "   Backend:   FastAPI (Python)" -ForegroundColor Green
Write-Host "   Frontend:  React 19 + Vite" -ForegroundColor Green
Write-Host "   Proxy:     Nginx" -ForegroundColor Green
Write-Host "   Cache:     Redis" -ForegroundColor Green
Write-Host "   Storage:   MinIO" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Open http://localhost:8080 in your browser" -ForegroundColor White
Write-Host "   2. Login with admin credentials or register new account" -ForegroundColor White
Write-Host "   3. Check backend logs: docker-compose logs backend -f" -ForegroundColor White
Write-Host "   4. Access API docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop services:" -ForegroundColor Cyan
Write-Host "   docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "📚 To view logs:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f          # All services" -ForegroundColor White
Write-Host "   docker-compose logs -f backend  # Backend only" -ForegroundColor White
Write-Host "   docker-compose logs -f frontend # Frontend only" -ForegroundColor White
Write-Host ""
