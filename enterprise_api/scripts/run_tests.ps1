# Enterprise API Test Runner Script
# This script sets up the environment and runs tests against the local Docker stack

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Enterprise API Test Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if Docker is running
Write-Host "`n[1/5] Checking Docker status..." -ForegroundColor Yellow
$dockerStatus = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host "Docker is running." -ForegroundColor Green

# Check if PostgreSQL is available
Write-Host "`n[2/5] Checking PostgreSQL connection..." -ForegroundColor Yellow
$pgCheck = docker exec encypher-postgres pg_isready -U encypher 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PostgreSQL is not ready. Starting full-stack..." -ForegroundColor Red
    docker-compose -f ../docker-compose.full-stack.yml up -d postgres redis-cache
    Start-Sleep -Seconds 10
}
Write-Host "PostgreSQL is ready." -ForegroundColor Green

# Set environment variables for testing
Write-Host "`n[3/5] Setting environment variables..." -ForegroundColor Yellow
$env:DATABASE_URL = "postgresql+asyncpg://encypher:encypher_dev_password@localhost:5432/encypher"
$env:KEY_ENCRYPTION_KEY = "test-encryption-key-32-bytes!!"
$env:ENCRYPTION_NONCE = "test-nonce12"
$env:SSL_COM_API_KEY = "test-ssl-com-key"
$env:SSL_COM_API_URL = "https://sandbox.ssl.com"
$env:DEMO_API_KEY = "demo-api-key-for-testing"
$env:DEMO_ORGANIZATION_ID = "org_demo"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:ENVIRONMENT = "development"
$env:LOG_LEVEL = "DEBUG"
Write-Host "Environment variables set." -ForegroundColor Green

# Run database migrations
Write-Host "`n[4/5] Running database migrations..." -ForegroundColor Yellow
Push-Location $PSScriptRoot\..
try {
    python -m alembic upgrade head 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Warning: Migrations may have failed, continuing anyway..." -ForegroundColor Yellow
    } else {
        Write-Host "Migrations complete." -ForegroundColor Green
    }
} catch {
    Write-Host "Warning: Could not run migrations: $_" -ForegroundColor Yellow
}
Pop-Location

# Run tests
Write-Host "`n[5/5] Running tests..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

Push-Location $PSScriptRoot\..

# Parse command line arguments
$testFiles = $args
if ($testFiles.Count -eq 0) {
    # Default: run all new pricing endpoint tests
    $testFiles = @(
        "tests/test_usage_api.py",
        "tests/test_audit_api.py",
        "tests/test_team_api.py",
        "tests/test_coalition_api.py"
    )
}

Write-Host "Running tests: $($testFiles -join ', ')" -ForegroundColor Cyan

python -m pytest $testFiles -v --tb=short -x

$exitCode = $LASTEXITCODE
Pop-Location

Write-Host "`n========================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "All tests passed!" -ForegroundColor Green
} else {
    Write-Host "Some tests failed. Exit code: $exitCode" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan

exit $exitCode
