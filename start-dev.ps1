Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Encypher Development Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Cert Check
Write-Host "[1/6] Checking SSL certificates..." -ForegroundColor Yellow
if (-not (Test-Path "certs/local-cert.pem")) {
    Write-Host "  SSL Certs missing. Running setup..." -ForegroundColor Yellow
    .\setup-local-https.ps1
} else {
    Write-Host "  SSL certificates found" -ForegroundColor Green
}

# 2. Docker Backend
Write-Host ""
Write-Host "[2/6] Starting Docker services..." -ForegroundColor Yellow
docker-compose -f docker-compose.full-stack.yml up -d 2>$null
if (Test-Path "docker-compose.https.yml") {
    docker-compose -f docker-compose.https.yml up -d 2>$null
}
Write-Host "  Docker services started" -ForegroundColor Green

# 3. Wait for PostgreSQL to be ready
Write-Host ""
Write-Host "[3/6] Waiting for PostgreSQL..." -ForegroundColor Yellow
$maxRetries = 30
$retryCount = 0
do {
    $retryCount++
    $result = docker exec encypher-postgres pg_isready -U encypher 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  PostgreSQL is ready!" -ForegroundColor Green
        break
    }
    Write-Host "  Waiting... ($retryCount/$maxRetries)" -ForegroundColor Gray
    Start-Sleep -Seconds 2
} while ($retryCount -lt $maxRetries)

if ($retryCount -ge $maxRetries) {
    Write-Host "  ERROR: PostgreSQL did not start in time" -ForegroundColor Red
    exit 1
}

# 4. Run Database Migrations
Write-Host ""
Write-Host "[4/6] Running database migrations..." -ForegroundColor Yellow
$migrationsDir = "services/migrations"
if (Test-Path $migrationsDir) {
    $migrations = Get-ChildItem -Path $migrationsDir -Filter "*.sql" | Sort-Object Name
    foreach ($migration in $migrations) {
        Write-Host "  Running: $($migration.Name)" -ForegroundColor Gray
        $content = Get-Content $migration.FullName -Raw
        $content | docker exec -i encypher-postgres psql -U encypher -d encypher -q 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "    Warning: Some statements may have been skipped (already exists)" -ForegroundColor DarkYellow
        }
    }
    Write-Host "  Migrations complete!" -ForegroundColor Green
} else {
    Write-Host "  No migrations directory found at $migrationsDir" -ForegroundColor Yellow
}

# 5. Verify database setup
Write-Host ""
Write-Host "[5/6] Verifying database setup..." -ForegroundColor Yellow
$orgCount = docker exec encypher-postgres psql -U encypher -d encypher -t -c "SELECT COUNT(*) FROM organizations;" 2>$null
$keyCount = docker exec encypher-postgres psql -U encypher -d encypher -t -c "SELECT COUNT(*) FROM api_keys;" 2>$null
$userCount = docker exec encypher-postgres psql -U encypher -d encypher -t -c "SELECT COUNT(*) FROM users;" 2>$null

Write-Host "  Organizations: $($orgCount.Trim())" -ForegroundColor Gray
Write-Host "  Users: $($userCount.Trim())" -ForegroundColor Gray
Write-Host "  API Keys: $($keyCount.Trim())" -ForegroundColor Gray

# Show test API keys
Write-Host ""
Write-Host "  Test API Keys:" -ForegroundColor Cyan
Write-Host "    demo-api-key-for-testing         (demo tier - all features)" -ForegroundColor Gray
Write-Host "    starter-api-key-for-testing      (starter tier)" -ForegroundColor Gray
Write-Host "    professional-api-key-for-testing (professional tier)" -ForegroundColor Gray
Write-Host "    business-api-key-for-testing     (business tier)" -ForegroundColor Gray
Write-Host "    enterprise-api-key-for-testing   (enterprise tier)" -ForegroundColor Gray

# 6. Frontends
Write-Host ""
Write-Host "[6/6] Launching Frontends..." -ForegroundColor Yellow

# Dashboard
if (Test-Path "apps/dashboard") {
    $dashboardPath = Resolve-Path "apps/dashboard"
    $cmd = "cd '$dashboardPath'; Write-Host 'Starting Dashboard...'; "
    if (-not (Test-Path "$dashboardPath\node_modules")) {
        $cmd += "Write-Host 'Installing dependencies...'; npm install; "
    }
    $cmd += "npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
} else {
    Write-Warning "apps/dashboard not found!"
}

# Marketing
if (Test-Path "apps/marketing-site") {
    $marketingPath = Resolve-Path "apps/marketing-site"
    $cmd = "cd '$marketingPath'; Write-Host 'Starting Marketing Site...'; "
    if (-not (Test-Path "$marketingPath\node_modules")) {
        $cmd += "Write-Host 'Installing dependencies...'; npm install; "
    }
    $cmd += "npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
} else {
    Write-Warning "apps/marketing-site not found!"
}

Write-Host "`nAll systems go!" -ForegroundColor Cyan
Write-Host "Access via: https://s-www.encypherai.com"
Write-Host "Dashboard:  https://s-dashboard.encypherai.com"

