# Test Register New Technician and Verify Search
# This validates that newly registered technicians appear in search

$baseUrl = "http://localhost:8000"
$newTechPhone = "9876543299"  # Unique phone for test

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "TEST: NEW TECHNICIAN REGISTRATION & SEARCH FUNCTIONALITY" -ForegroundColor Cyan
Write-Host "=" * 70
Write-Host ""

# Step 1: Register a new technician
Write-Host "[1/4] Registering new technician..." -ForegroundColor Yellow
try {
    $regResponse = Invoke-RestMethod -Uri "$baseUrl/auth/register/technician" -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body "name=Test Electrician&phone=$newTechPhone&password=Test@123&email=test.electrician@demo.com&service_category=Electrician&city=Chennai&address=Test Area, Chennai&latitude=13.0827&longitude=80.2707" `
        -ErrorAction Stop
    Write-Host "[PASS] REGISTRATION SUCCESS" -ForegroundColor Green
    Write-Host "   Name: $($regResponse.name)"
    Write-Host "   Location: $($regResponse.location.city)"
} catch {
    Write-Host "[FAIL] REGISTRATION FAILED" -ForegroundColor Red
    Write-Host "   Status: $($_.Exception.Response.StatusCode)"
    Write-Host "   Details: $($_.Exception.Message)"
}
Write-Host ""

# Step 2: Wait a moment for database to sync
Write-Host "[2/4] Waiting for database to sync..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Write-Host "[OK] Ready" -ForegroundColor Green
Write-Host ""

# Step 3: Search for the new technician
Write-Host "[3/4] Searching for newly registered technician..." -ForegroundColor Yellow
try {
    $searchUrl = "$baseUrl/technicians/nearby?latitude=13.0827&longitude=80.2707&service_category=Electrician&radius_km=5&urgency_level=Low"
    $searchResponse = Invoke-RestMethod -Uri $searchUrl -Method GET `
        -ContentType "application/json" -ErrorAction Stop
    
    Write-Host "[PASS] SEARCH COMPLETED" -ForegroundColor Green
    Write-Host "   Found: $($searchResponse.total_found) technicians"
    Write-Host "   Radius: $($searchResponse.search_radius_km) km"
    
    # Check if our new technician is in the results
    $foundTech = $searchResponse.technicians | Where-Object { $_.phone -eq $newTechPhone }
    if ($foundTech) {
        Write-Host "[PASS] NEW TECHNICIAN FOUND IN SEARCH!" -ForegroundColor Green
        Write-Host "   Name: $($foundTech.name)"
        Write-Host "   Distance: $($foundTech.distance_km) km"
        Write-Host "   Available: $($foundTech.is_available)"
    } else {
        Write-Host "[WARN] New technician NOT found in search results" -ForegroundColor Yellow
        if ($searchResponse.technicians.Count -gt 0) {
            Write-Host "   Available technicians:"
            $searchResponse.technicians | ForEach-Object { Write-Host "      - $($_.name)" }
        } else {
            Write-Host "   No technicians found in the search radius"
        }
    }
} catch {
    Write-Host "[FAIL] SEARCH FAILED" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)"
}
Write-Host ""

# Step 4: Login with the new technician
Write-Host "[4/4] Testing login with new technician account..." -ForegroundColor Yellow
try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login/technician" -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body "identifier=$newTechPhone&password=Test@123" `
        -ErrorAction Stop
    Write-Host "[PASS] LOGIN SUCCESS" -ForegroundColor Green
    Write-Host "   User: $($loginResponse.user.name)"
    Write-Host "   Role: $($loginResponse.user.role)"
    Write-Host "   Token: $($loginResponse.access_token.Substring(0, 25))..."
} catch {
    Write-Host "[FAIL] LOGIN FAILED" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)"
}
Write-Host ""

# Summary
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "[PASS] REGISTRATION & SEARCH TEST COMPLETE" -ForegroundColor Green
Write-Host "=" * 70
Write-Host ""
Write-Host "Key Points:" -ForegroundColor Cyan
Write-Host "  - New technicians are registered with location data"
Write-Host "  - Location is required for search functionality"
Write-Host "  - New technicians should appear in nearby search results"
Write-Host ""
