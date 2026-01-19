# Quick verification test script
# Tests the complete C2PA workflow

Write-Host "=== C2PA Verification Test ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check services are running
Write-Host "Step 1: Checking services..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "Step 2: Testing Enterprise API health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9000/health" -Method GET
    Write-Host "✓ Enterprise API is healthy" -ForegroundColor Green
} catch {
    Write-Host "✗ Enterprise API is not responding" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Testing WordPress..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8085" -Method GET
    Write-Host "✓ WordPress is responding" -ForegroundColor Green
} catch {
    Write-Host "✗ WordPress is not responding" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 4: Checking recent WordPress logs..." -ForegroundColor Yellow
docker-compose logs wordpress --tail=20 | Select-String "Encypher" | Select-Object -Last 5

Write-Host ""
Write-Host "Step 5: Checking recent Enterprise API logs..." -ForegroundColor Yellow
docker-compose logs enterprise-api --tail=20 | Select-String "C2PA" | Select-Object -Last 5

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Go to http://localhost:8085/wp-admin" -ForegroundColor White
Write-Host "2. Edit post #9 and make a small change" -ForegroundColor White
Write-Host "3. Click 'Update'" -ForegroundColor White
Write-Host "4. View post at http://localhost:8085/?p=9" -ForegroundColor White
Write-Host "5. Look for the C2PA badge (bottom-right corner)" -ForegroundColor White
Write-Host "6. Click the badge to verify" -ForegroundColor White
Write-Host ""
Write-Host "Expected in logs:" -ForegroundColor Yellow
Write-Host "  - 'Post 9 successfully signed with C2PA wrapper (spec compliant)'" -ForegroundColor Gray
Write-Host "  - 'Adding C2PA wrapper for document wp_post_9'" -ForegroundColor Gray
Write-Host ""
