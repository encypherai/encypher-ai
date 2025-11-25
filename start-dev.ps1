Write-Host "Starting Encypher Development Environment..." -ForegroundColor Cyan

# 1. Cert Check
if (-not (Test-Path "certs/local-cert.pem")) {
    Write-Host "SSL Certs missing. Running setup..." -ForegroundColor Yellow
    .\setup-local-https.ps1
}

# 2. Docker Backend
Write-Host "Starting Backend & Proxy..." -ForegroundColor Green
docker-compose -f docker-compose.full-stack.yml up -d
docker-compose -f docker-compose.https.yml up -d

# 3. Frontends
Write-Host "Launching Frontends in new windows..." -ForegroundColor Green

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

