Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Encypher Development Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Cert Check
Write-Host "[1/7] Checking SSL certificates..." -ForegroundColor Yellow
if (-not (Test-Path "certs/local-cert.pem")) {
    Write-Host "  SSL Certs missing. Running setup..." -ForegroundColor Yellow
    .\setup-local-https.ps1
} else {
    Write-Host "  SSL certificates found" -ForegroundColor Green
}

# 2. Docker Backend
Write-Host ""
Write-Host "[2/7] Starting Docker services..." -ForegroundColor Yellow
docker-compose -f docker-compose.full-stack.yml up -d postgres-core postgres-content redis-cache redis-celery 2>$null
Write-Host "  Infrastructure services started" -ForegroundColor Green

# 3. Wait for PostgreSQL Core to be ready
Write-Host ""
Write-Host "[3/7] Waiting for PostgreSQL Core..." -ForegroundColor Yellow
$maxRetries = 30
$retryCount = 0
do {
    $retryCount++
    $result = docker exec encypher-postgres-core pg_isready -U encypher -d encypher_core 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  PostgreSQL Core is ready!" -ForegroundColor Green
        break
    }
    Write-Host "  Waiting... ($retryCount/$maxRetries)" -ForegroundColor Gray
    Start-Sleep -Seconds 2
} while ($retryCount -lt $maxRetries)

if ($retryCount -ge $maxRetries) {
    Write-Host "  ERROR: PostgreSQL Core did not start in time" -ForegroundColor Red
    exit 1
}

# 4. Wait for PostgreSQL Content to be ready
Write-Host ""
Write-Host "[4/7] Waiting for PostgreSQL Content..." -ForegroundColor Yellow
$retryCount = 0
do {
    $retryCount++
    $result = docker exec encypher-postgres-content pg_isready -U encypher -d encypher_content 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  PostgreSQL Content is ready!" -ForegroundColor Green
        break
    }
    Write-Host "  Waiting... ($retryCount/$maxRetries)" -ForegroundColor Gray
    Start-Sleep -Seconds 2
} while ($retryCount -lt $maxRetries)

if ($retryCount -ge $maxRetries) {
    Write-Host "  ERROR: PostgreSQL Content did not start in time" -ForegroundColor Red
    exit 1
}

# 5. Run Database Migrations (Two-Database Architecture)
Write-Host ""
Write-Host "[5/7] Running database migrations..." -ForegroundColor Yellow

# Core DB migrations
Write-Host "  Core DB migrations:" -ForegroundColor Cyan
$coreDir = "services/migrations/core_db"
if (Test-Path $coreDir) {
    $migrations = Get-ChildItem -Path $coreDir -Filter "*.sql" | Sort-Object Name
    foreach ($migration in $migrations) {
        Write-Host "    Running: $($migration.Name)" -ForegroundColor Gray
        $content = Get-Content $migration.FullName -Raw
        $content | docker exec -i encypher-postgres-core psql -U encypher -d encypher_core -q 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "      Warning: Some statements may have been skipped" -ForegroundColor DarkYellow
        }
    }
}

# Content DB migrations
Write-Host "  Content DB migrations:" -ForegroundColor Cyan
$contentDir = "services/migrations/content_db"
if (Test-Path $contentDir) {
    $migrations = Get-ChildItem -Path $contentDir -Filter "*.sql" | Sort-Object Name
    foreach ($migration in $migrations) {
        Write-Host "    Running: $($migration.Name)" -ForegroundColor Gray
        $content = Get-Content $migration.FullName -Raw
        $content | docker exec -i encypher-postgres-content psql -U encypher -d encypher_content -q 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "      Warning: Some statements may have been skipped" -ForegroundColor DarkYellow
        }
    }
}
Write-Host "  Migrations complete!" -ForegroundColor Green

# 6. Verify database setup
Write-Host ""
Write-Host "[6/7] Verifying database setup..." -ForegroundColor Yellow

# Core DB
Write-Host "  Core DB (postgres-core:5432):" -ForegroundColor Cyan
$orgCount = docker exec encypher-postgres-core psql -U encypher -d encypher_core -t -c "SELECT COUNT(*) FROM organizations;" 2>$null
$userCount = docker exec encypher-postgres-core psql -U encypher -d encypher_core -t -c "SELECT COUNT(*) FROM users;" 2>$null
$keyCount = docker exec encypher-postgres-core psql -U encypher -d encypher_core -t -c "SELECT COUNT(*) FROM api_keys;" 2>$null
Write-Host "    Organizations: $($orgCount.Trim())" -ForegroundColor Gray
Write-Host "    Users: $($userCount.Trim())" -ForegroundColor Gray
Write-Host "    API Keys: $($keyCount.Trim())" -ForegroundColor Gray

# Content DB
Write-Host "  Content DB (postgres-content:5433):" -ForegroundColor Cyan
$docCount = docker exec encypher-postgres-content psql -U encypher -d encypher_content -t -c "SELECT COUNT(*) FROM encoded_documents;" 2>$null
$verifyCount = docker exec encypher-postgres-content psql -U encypher -d encypher_content -t -c "SELECT COUNT(*) FROM verification_results;" 2>$null
Write-Host "    Encoded Documents: $($docCount.Trim())" -ForegroundColor Gray
Write-Host "    Verification Results: $($verifyCount.Trim())" -ForegroundColor Gray

# Show test API keys
Write-Host ""
Write-Host "  Test API Keys:" -ForegroundColor Cyan
Write-Host "    demo-api-key-for-testing         (demo tier - all features)" -ForegroundColor Gray
Write-Host "    starter-api-key-for-testing      (starter tier)" -ForegroundColor Gray
Write-Host "    professional-api-key-for-testing (professional tier)" -ForegroundColor Gray
Write-Host "    business-api-key-for-testing     (business tier)" -ForegroundColor Gray
Write-Host "    enterprise-api-key-for-testing   (enterprise tier)" -ForegroundColor Gray

# 7. Frontends
Write-Host ""
Write-Host "[7/7] Launching Frontends..." -ForegroundColor Yellow

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

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  All systems go!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Infrastructure:" -ForegroundColor Yellow
Write-Host "  PostgreSQL Core:    localhost:5432 (encypher_core)" -ForegroundColor Gray
Write-Host "  PostgreSQL Content: localhost:5433 (encypher_content)" -ForegroundColor Gray
Write-Host "  Redis Cache:        localhost:6379" -ForegroundColor Gray
Write-Host ""
Write-Host "Frontend URLs:" -ForegroundColor Yellow
Write-Host "  Marketing Site: http://localhost:3000" -ForegroundColor Gray
Write-Host "  Dashboard:      http://localhost:3001" -ForegroundColor Gray
Write-Host ""
Write-Host "To start microservices:" -ForegroundColor Yellow
Write-Host "  docker-compose -f docker-compose.full-stack.yml up auth-service" -ForegroundColor Gray
Write-Host "  # Or start all: docker-compose -f docker-compose.full-stack.yml up" -ForegroundColor Gray

