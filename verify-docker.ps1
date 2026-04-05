#!/usr/bin/env powershell
<#
.SYNOPSIS
    SevaiHub Docker Troubleshooting and Verification Script
    
.DESCRIPTION
    Verifies all services are running and properly connected
#>

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     🔍 SevaiHub Service Verification & Troubleshooting        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Functions
function Test-Service {
    param([string]$ServiceName, [string]$Url, [string]$Description)
    
    Write-Host "Testing $ServiceName..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ $Description - Responding" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "   ❌ $Description - Not responding" -ForegroundColor Red
        return $false
    }
    return $false
}

function Test-Database {
    Write-Host "Testing PostgreSQL with PostGIS..." -ForegroundColor Yellow
    try {
        $output = docker-compose exec -T postgres psql -U postgres -d sevaihub -c "SELECT postgis_version();" 2>&1
        if ($output -match "PostGIS") {
            Write-Host "   ✅ PostgreSQL is running and PostGIS is installed" -ForegroundColor Green
            return $true
        } else {
            Write-Host "   ⚠️  PostGIS extension may not be initialized yet" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "   ❌ Cannot connect to PostgreSQL" -ForegroundColor Red
        Write-Host "      Error: $_" -ForegroundColor Red
        return $false
    }
}

function Get-ContainerStatus {
    Write-Host ""
    Write-Host "Container Status:" -ForegroundColor Yellow
    $containers = docker-compose ps --format "table {{.Names}}\t{{.Status}}"
    Write-Host $containers
}

function Get-Services-Health {
    Write-Host ""
    Write-Host "Service Health Check:" -ForegroundColor Yellow
    Write-Host ""
    
    $allHealthy = $true
    
    # Backend
    if (Test-Service "Backend" "http://localhost:8000/health" "Backend API") {
        Write-Host ""
    } else {
        $allHealthy = $false
        Write-Host ""
    }
    
    # Frontend
    if (Test-Service "Frontend" "http://localhost:8080" "Frontend (Nginx)") {
        Write-Host ""
    } else {
        $allHealthy = $false
        Write-Host ""
    }
    
    # Database
    if (Test-Database) {
        Write-Host ""
    } else {
        $allHealthy = $false
        Write-Host ""
    }
    
    # Redis
    Write-Host "Testing Redis..." -ForegroundColor Yellow
    try {
        docker-compose exec -T redis redis-cli ping 2>&1 | Select-String "PONG" >$null
        if ($?) {
            Write-Host "   ✅ Redis is running" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Redis is not responding" -ForegroundColor Red
            $allHealthy = $false
        }
    } catch {
        Write-Host "   ❌ Redis connection failed" -ForegroundColor Red
        $allHealthy = $false
    }
    Write-Host ""
    
    # MinIO
    Write-Host "Testing MinIO..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9000/minio/health/live" -TimeoutSec 3 -ErrorAction SilentlyContinue
        Write-Host "   ✅ MinIO is running (Console at http://localhost:9001)" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  MinIO may still be starting" -ForegroundColor Yellow
    }
    Write-Host ""
    
    return $allHealthy
}

function Show-Logs {
    param([string]$Service = "")
    
    Write-Host ""
    Write-Host "Recent Logs:" -ForegroundColor Yellow
    
    if ([string]::IsNullOrEmpty($Service)) {
        Write-Host "backend:" -ForegroundColor Gray
        docker-compose logs --tail 10 backend
        Write-Host ""
    } else {
        docker-compose logs --tail 15 $Service
    }
}

function Show-Troubleshooting-Tips {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    TROUBLESHOOTING TIPS                        ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "❌ Frontend can't reach backend?" -ForegroundColor Red
    Write-Host "   • Verify VITE_API_URL in docker-compose.yml is: http://sevaihub-backend:8000" -ForegroundColor Gray
    Write-Host "   • Clear browser cache: Ctrl+Shift+Del" -ForegroundColor Gray
    Write-Host "   • Check CORS_ORIGINS in .env includes frontend URL" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "❌ Database connection failed?" -ForegroundColor Red
    Write-Host "   • Check DATABASE_URL is: postgresql://postgres:postgres_dev_password_123@postgres:5432/sevaihub" -ForegroundColor Gray
    Write-Host "   • Verify postgres container is healthy: docker-compose ps postgres" -ForegroundColor Gray
    Write-Host "   • Reset database: docker-compose down -v && docker-compose up -d" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "❌ PostGIS not initialized?" -ForegroundColor Red
    Write-Host "   • It's in postgis/postgis:16-3.4-alpine image, automatically enabled" -ForegroundColor Gray
    Write-Host "   • Verify: docker-compose exec postgres psql -U postgres -d sevaihub -c 'CREATE EXTENSION IF NOT EXISTS postgis;'" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "❌ Port already in use?" -ForegroundColor Red
    Write-Host "   • Find process: netstat -ano | findstr :8080" -ForegroundColor Gray
    Write-Host "   • Kill process: taskkill /PID <PID> /F" -ForegroundColor Gray
    Write-Host "   • Or change ports in docker-compose.yml" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "❌ Services won't start?" -ForegroundColor Red
    Write-Host "   • Check logs: docker-compose logs" -ForegroundColor Gray
    Write-Host "   • Rebuild images: docker-compose build --no-cache" -ForegroundColor Gray
    Write-Host "   • Clean everything: docker system prune -a" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "📚 Useful Commands:" -ForegroundColor Cyan
    Write-Host "   View all logs:        docker-compose logs -f" -ForegroundColor Gray
    Write-Host "   Backend logs:         docker-compose logs -f backend" -ForegroundColor Gray
    Write-Host "   Frontend logs:        docker-compose logs -f frontend" -ForegroundColor Gray
    Write-Host "   Database shell:       docker-compose exec postgres bash" -ForegroundColor Gray
    Write-Host "   Stop services:        docker-compose down" -ForegroundColor Gray
    Write-Host "   Reset everything:     docker-compose down -v && docker-compose up -d" -ForegroundColor Gray
    Write-Host ""
}

# Main execution
Get-ContainerStatus
$healthyServices = Get-Services-Health

if ($healthyServices) {
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║              ✅ ALL SERVICES RUNNING HEALTHILY!               ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access your application:"
    Write-Host "   Frontend:  http://localhost:8080"
    Write-Host "   Backend:   http://localhost:8000"
    Write-Host "   API Docs:  http://localhost:8000/docs"
    Write-Host ""
} else {
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║         ⚠️  SOME SERVICES MAY NEED ATTENTION                   ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Show-Troubleshooting-Tips
}

Write-Host ""
Write-Host "Need more details? Run:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f      # See all logs in real-time" -ForegroundColor Gray
Write-Host ""
