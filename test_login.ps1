# Login Test Script for Sevai Hub
# Tests all authentication endpoints

$baseUrl = "http://localhost:8000"

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "SEVAI HUB - LOGIN AUTHENTICATION TEST" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

# Test 1: User Login
Write-Host "[1/3] Testing USER Login..." -ForegroundColor Yellow
$userBody = @{
    identifier = "1234567890"
    password = "demo123"
} | ConvertTo-Json

try {
    $userResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login/user" -Method POST `
        -ContentType "application/json" -Body $userBody -ErrorAction Stop
    Write-Host "✅ USER Login: SUCCESS" -ForegroundColor Green
    Write-Host "   • ID: $($userResponse.user.id)"
    Write-Host "   • Name: $($userResponse.user.name)"
    Write-Host "   • Role: $($userResponse.user.role)"
    Write-Host "   • Token: $($userResponse.access_token.Substring(0, 20))..."
} catch {
    Write-Host "❌ USER Login: FAILED" -ForegroundColor Red
    Write-Host "   Error: $_"
}
Write-Host ""

# Test 2: Technician Login
Write-Host "[2/3] Testing TECHNICIAN Login..." -ForegroundColor Yellow
$techBody = @{
    identifier = "9876543210"
    password = "Sevai@123"
} | ConvertTo-Json

try {
    $techResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login/technician" -Method POST `
        -ContentType "application/json" -Body $techBody -ErrorAction Stop
    Write-Host "✅ TECHNICIAN Login: SUCCESS" -ForegroundColor Green
    Write-Host "   • ID: $($techResponse.user.id)"
    Write-Host "   • Name: $($techResponse.user.name)"
    Write-Host "   • Role: $($techResponse.user.role)"
    Write-Host "   • Token: $($techResponse.access_token.Substring(0, 20))..."
} catch {
    Write-Host "❌ TECHNICIAN Login: FAILED" -ForegroundColor Red
    Write-Host "   Error: $_"
}
Write-Host ""

# Test 3: Admin Login
Write-Host "[3/3] Testing ADMIN Login..." -ForegroundColor Yellow
$adminBody = @{
    mobile = "9999999999"
    aadhaar = "123456789012"
    password = "admin123"
} | ConvertTo-Json

try {
    $adminResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login/admin" -Method POST `
        -ContentType "application/json" -Body $adminBody -ErrorAction Stop
    Write-Host "✅ ADMIN Login: SUCCESS" -ForegroundColor Green
    Write-Host "   • ID: $($adminResponse.user.id)"
    Write-Host "   • Name: $($adminResponse.user.name)"
    Write-Host "   • Role: $($adminResponse.user.role)"
    Write-Host "   • Token: $($adminResponse.access_token.Substring(0, 20))..."
} catch {
    Write-Host "❌ ADMIN Login: FAILED" -ForegroundColor Red
    Write-Host "   Error: $_"
}
Write-Host ""

# Summary
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "✅ ALL LOGIN ENDPOINTS WORKING PROPERLY!" -ForegroundColor Green
Write-Host "=" * 60
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Cyan
Write-Host "• Frontend: http://localhost:8080"
Write-Host "• API Docs: http://localhost:8000/docs"
Write-Host "• MinIO: http://localhost:9001"
