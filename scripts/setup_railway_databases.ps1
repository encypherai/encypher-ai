# Railway Database Setup Script
# Run this script to link each database to its corresponding service
# 
# Prerequisites:
# - Railway CLI installed and logged in
# - Databases already created (db-auth, db-keys, etc.)
#
# Usage: .\scripts\setup_railway_databases.ps1

Write-Host "=== Railway Database Setup ===" -ForegroundColor Cyan
Write-Host "This script links each database to its corresponding service" -ForegroundColor Gray
Write-Host ""

# Database to Service mapping
$mappings = @(
    @{ Service = "auth-service"; Database = "db-auth" },
    @{ Service = "key-service"; Database = "db-keys" },
    @{ Service = "billing-service"; Database = "db-billing" },
    @{ Service = "user-service"; Database = "db-users" },
    @{ Service = "notification-service"; Database = "db-notifications" },
    @{ Service = "encoding-service"; Database = "db-encoding" },
    @{ Service = "verification-service"; Database = "db-verification" },
    @{ Service = "analytics-service"; Database = "db-analytics" },
    @{ Service = "coalition-service"; Database = "db-coalition" }
)

foreach ($mapping in $mappings) {
    $service = $mapping.Service
    $database = $mapping.Database
    
    Write-Host "Linking $database to $service..." -ForegroundColor Yellow
    
    # Set DATABASE_URL to reference the database service
    $varValue = "`${{$database.DATABASE_URL}}"
    
    try {
        railway variables --service $service --set "DATABASE_URL=$varValue"
        Write-Host "  ✓ Successfully linked $database to $service" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Failed to link $database to $service" -ForegroundColor Red
        Write-Host "    Error: $_" -ForegroundColor Red
    }
    
    # Small delay to avoid rate limiting
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Verify variables in Railway dashboard: railway open" -ForegroundColor Gray
Write-Host "2. Redeploy services: railway redeploy --service <service-name>" -ForegroundColor Gray
Write-Host "3. Check logs: railway logs --service <service-name>" -ForegroundColor Gray
