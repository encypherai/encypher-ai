# ============================================================================
# Encypher Development Environment Startup Script
# ============================================================================
# This script starts all services needed for local development:
# - Infrastructure: PostgreSQL (core + content), Redis
# - Backend: Enterprise API (Docker)
# - Frontend: Marketing Site, Dashboard (Next.js)
# ============================================================================

param(
    [switch]$SkipDocker,      # Skip Docker services (use if already running)
    [switch]$SkipFrontend,    # Skip frontend apps
    [switch]$CleanStart,      # Clean all caches and rebuild
    [switch]$Help
)

if ($Help) {
    Write-Host @"

Usage: .\start-dev.ps1 [options]

Options:
  -SkipDocker     Skip starting Docker services (use if already running)
  -SkipFrontend   Skip starting frontend applications
  -CleanStart     Clean all caches (.next, node_modules/.cache) before starting
  -Help           Show this help message

Examples:
  .\start-dev.ps1                    # Start everything
  .\start-dev.ps1 -CleanStart        # Clean start (fixes most issues)
  .\start-dev.ps1 -SkipDocker        # Only start frontends

"@
    exit 0
}

$ErrorActionPreference = "Continue"
$script:hasErrors = $false

function Write-Step {
    param([string]$Step, [string]$Message)
    Write-Host ""
    Write-Host "[$Step] $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "  $Message" -ForegroundColor Gray
}

function Write-Warn {
    param([string]$Message)
    Write-Host "  [WARN] $Message" -ForegroundColor DarkYellow
}

function Write-Err {
    param([string]$Message)
    Write-Host "  [ERR] $Message" -ForegroundColor Red
    $script:hasErrors = $true
}

function Test-Port {
    param([int]$Port)
    $connection = New-Object System.Net.Sockets.TcpClient
    try {
        $connection.Connect("127.0.0.1", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

function Wait-ForService {
    param([string]$Name, [int]$Port, [int]$MaxRetries = 30)
    $retryCount = 0
    do {
        $retryCount++
        if (Test-Port -Port $Port) {
            Write-Success "$Name is ready on port $Port"
            return $true
        }
        Write-Host "    Waiting for $Name... ($retryCount/$MaxRetries)" -ForegroundColor DarkGray
        Start-Sleep -Seconds 2
    } while ($retryCount -lt $MaxRetries)
    Write-Err "$Name did not start in time (port $Port)"
    return $false
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Encypher Development Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Check Prerequisites
Write-Step "1/8" "Checking prerequisites..."

# Check Docker
if (-not $SkipDocker) {
    $dockerRunning = docker info 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Docker is not running. Please start Docker Desktop."
        exit 1
    }
    Write-Success "Docker is running"
}

# Check Node.js
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Err "Node.js is not installed"
    exit 1
}
Write-Success "Node.js $nodeVersion"

# Step 2: Clean caches if requested
if ($CleanStart) {
    Write-Step "2/8" "Cleaning caches..."
    
    # Clean Next.js caches
    if (Test-Path "apps/marketing-site/.next") {
        Remove-Item -Recurse -Force "apps/marketing-site/.next" -ErrorAction SilentlyContinue
        Write-Info "Cleaned marketing-site/.next"
    }
    if (Test-Path "apps/dashboard/.next") {
        Remove-Item -Recurse -Force "apps/dashboard/.next" -ErrorAction SilentlyContinue
        Write-Info "Cleaned dashboard/.next"
    }
    
    # Clean node_modules cache
    if (Test-Path "apps/marketing-site/node_modules/.cache") {
        Remove-Item -Recurse -Force "apps/marketing-site/node_modules/.cache" -ErrorAction SilentlyContinue
    }
    if (Test-Path "apps/dashboard/node_modules/.cache") {
        Remove-Item -Recurse -Force "apps/dashboard/node_modules/.cache" -ErrorAction SilentlyContinue
    }
    
    Write-Success "Caches cleaned"
} else {
    Write-Step "2/8" "Skipping cache clean (use -CleanStart to clean)"
}

# Step 3: Start Docker Infrastructure
if (-not $SkipDocker) {
    Write-Step "3/8" "Starting Docker infrastructure..."
    
    # Stop any existing containers first
    docker-compose -f docker-compose.full-stack.yml down 2>$null
    
    # Start infrastructure (including Traefik API Gateway)
    docker-compose -f docker-compose.full-stack.yml up -d postgres-core postgres-content redis-cache traefik 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Failed to start Docker infrastructure"
    } else {
        Write-Success "Infrastructure containers started (including Traefik)"
    }
} else {
    Write-Step "3/8" "Skipping Docker (use existing services)"
}

# Step 4: Wait for databases
if (-not $SkipDocker) {
    Write-Step "4/8" "Waiting for databases..."
    
    # Wait for PostgreSQL Core
    $maxRetries = 30
    $retryCount = 0
    do {
        $retryCount++
        docker exec encypher-postgres-core pg_isready -U encypher -d encypher_core 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "PostgreSQL Core is ready (port 5432)"
            break
        }
        Write-Host "    Waiting for PostgreSQL Core... ($retryCount/$maxRetries)" -ForegroundColor DarkGray
        Start-Sleep -Seconds 2
    } while ($retryCount -lt $maxRetries)
    
    if ($retryCount -ge $maxRetries) {
        Write-Err "PostgreSQL Core did not start in time"
    }
    
    # Wait for PostgreSQL Content
    $retryCount = 0
    do {
        $retryCount++
        docker exec encypher-postgres-content pg_isready -U encypher -d encypher_content 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "PostgreSQL Content is ready (port 5433)"
            break
        }
        Write-Host "    Waiting for PostgreSQL Content... ($retryCount/$maxRetries)" -ForegroundColor DarkGray
        Start-Sleep -Seconds 2
    } while ($retryCount -lt $maxRetries)
    
    if ($retryCount -ge $maxRetries) {
        Write-Err "PostgreSQL Content did not start in time"
    }
    
    # Verify Redis
    $redisCheck = docker exec encypher-redis-cache redis-cli ping 2>$null
    if ($redisCheck -eq "PONG") {
        Write-Success "Redis is ready (port 6379)"
    } else {
        Write-Err "Redis is not responding"
    }
} else {
    Write-Step "4/8" "Skipping database wait (Docker skipped)"
}

# Step 5: Run Database Migrations
if (-not $SkipDocker) {
    Write-Step "5/8" "Running database migrations..."
    
    # Core DB migrations
    $coreDir = "services/migrations/core_db"
    if (Test-Path $coreDir) {
        $migrations = Get-ChildItem -Path $coreDir -Filter "*.sql" | Sort-Object Name
        foreach ($migration in $migrations) {
            $content = Get-Content $migration.FullName -Raw
            $content | docker exec -i encypher-postgres-core psql -U encypher -d encypher_core -q 2>$null | Out-Null
        }
        Write-Info "Core DB: $($migrations.Count) migration files processed"
    }
    
    # Content DB migrations
    $contentDir = "services/migrations/content_db"
    if (Test-Path $contentDir) {
        $migrations = Get-ChildItem -Path $contentDir -Filter "*.sql" | Sort-Object Name
        foreach ($migration in $migrations) {
            $content = Get-Content $migration.FullName -Raw
            $content | docker exec -i encypher-postgres-content psql -U encypher -d encypher_content -q 2>$null | Out-Null
        }
        Write-Info "Content DB: $($migrations.Count) migration files processed"
    }
    
    Write-Success "Migrations complete"
} else {
    Write-Step "5/8" "Skipping migrations (Docker skipped)"
}

# Step 6: Start Microservices and Enterprise API
if (-not $SkipDocker) {
    Write-Step "6/8" "Starting microservices and Enterprise API..."
    
    # Build and start essential microservices + enterprise-api
    # auth-service: Authentication (required for login)
    # user-service: User management
    # key-service: API key management
    docker-compose -f docker-compose.full-stack.yml up -d auth-service user-service key-service enterprise-api 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Failed to start services"
    } else {
        # Wait for auth-service (required for login)
        $retryCount = 0
        $maxRetries = 30
        do {
            $retryCount++
            try {
                $health = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
                if ($health.status -eq "healthy") {
                    Write-Success "Auth Service is ready (port 8001)"
                    break
                }
            } catch {
                # Still starting
            }
            Write-Host "    Waiting for Auth Service... ($retryCount/$maxRetries)" -ForegroundColor DarkGray
            Start-Sleep -Seconds 2
        } while ($retryCount -lt $maxRetries)
        
        if ($retryCount -ge $maxRetries) {
            Write-Warn "Auth Service may still be starting (check docker logs)"
        }
        
        # Wait for Enterprise API
        $retryCount = 0
        do {
            $retryCount++
            try {
                $health = Invoke-RestMethod -Uri "http://localhost:9000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
                if ($health.status -eq "healthy") {
                    Write-Success "Enterprise API is ready (port 9000)"
                    break
                }
            } catch {
                # Still starting
            }
            Write-Host "    Waiting for Enterprise API... ($retryCount/$maxRetries)" -ForegroundColor DarkGray
            Start-Sleep -Seconds 2
        } while ($retryCount -lt $maxRetries)
        
        if ($retryCount -ge $maxRetries) {
            Write-Warn "Enterprise API may still be starting (check docker logs)"
        }
    }
} else {
    Write-Step "6/8" "Skipping microservices (Docker skipped)"
}

# Step 7: Start Frontend Applications
if (-not $SkipFrontend) {
    Write-Step "7/8" "Starting frontend applications..."
    
    # Marketing Site
    if (Test-Path "apps/marketing-site") {
        $marketingPath = Resolve-Path "apps/marketing-site"
        
        # Clean .next cache if corrupted
        if (Test-Path "$marketingPath\.next\trace") {
            Remove-Item -Recurse -Force "$marketingPath\.next" -ErrorAction SilentlyContinue
            Write-Info "Cleaned corrupted marketing-site/.next cache"
        }
        
        # Build the startup command (single line to avoid here-string issues)
        $cmd = "Set-Location '$marketingPath'; `$Host.UI.RawUI.WindowTitle = 'Marketing Site (3000)'; if (-not (Test-Path 'node_modules')) { npm install }; npm run dev"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
        Write-Info "Marketing Site starting on port 3000"
    } else {
        Write-Warn "apps/marketing-site not found"
    }
    
    # Dashboard
    if (Test-Path "apps/dashboard") {
        $dashboardPath = Resolve-Path "apps/dashboard"
        
        # Clean .next cache if corrupted
        if (Test-Path "$dashboardPath\.next\trace") {
            Remove-Item -Recurse -Force "$dashboardPath\.next" -ErrorAction SilentlyContinue
            Write-Info "Cleaned corrupted dashboard/.next cache"
        }
        
        $cmd = "Set-Location '$dashboardPath'; `$Host.UI.RawUI.WindowTitle = 'Dashboard (3001)'; if (-not (Test-Path 'node_modules')) { npm install }; npm run dev"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
        Write-Info "Dashboard starting on port 3001"
    } else {
        Write-Warn "apps/dashboard not found"
    }
} else {
    Write-Step "7/8" "Skipping frontends (-SkipFrontend)"
}

# Step 8: Health Check Summary
Write-Step "8/8" "Verifying services..."
Start-Sleep -Seconds 3  # Give services a moment

$services = @(
    @{Name="PostgreSQL Core"; Port=5432},
    @{Name="PostgreSQL Content"; Port=5433},
    @{Name="Redis"; Port=6379},
    @{Name="Traefik Gateway"; Port=8000},
    @{Name="Auth Service"; Port=8001},
    @{Name="User Service"; Port=8002},
    @{Name="Key Service"; Port=8003},
    @{Name="Enterprise API"; Port=9000}
)

foreach ($svc in $services) {
    if (Test-Port -Port $svc.Port) {
        Write-Success "$($svc.Name) (port $($svc.Port))"
    } else {
        Write-Warn "$($svc.Name) not responding (port $($svc.Port))"
    }
}

# Final Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($script:hasErrors) {
    Write-Host "  Started with warnings" -ForegroundColor Yellow
} else {
    Write-Host "  All systems go!" -ForegroundColor Green
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services:" -ForegroundColor Yellow
Write-Host "  PostgreSQL Core:    localhost:5432" -ForegroundColor Gray
Write-Host "  PostgreSQL Content: localhost:5433" -ForegroundColor Gray
Write-Host "  Redis:              localhost:6379" -ForegroundColor Gray
Write-Host "  Traefik Gateway:    http://localhost:8000 (API routing)" -ForegroundColor Gray
Write-Host "  Traefik Dashboard:  http://localhost:8080" -ForegroundColor Gray
Write-Host "  Enterprise API:     http://localhost:9000 (direct)" -ForegroundColor Gray
Write-Host ""
Write-Host "Frontend URLs:" -ForegroundColor Yellow
Write-Host "  Marketing Site:     http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Dashboard:          http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Gateway (Traefik routes to microservices):" -ForegroundColor Yellow
Write-Host "  All API calls:      http://localhost:8000/api/v1/*" -ForegroundColor Cyan
Write-Host "  Routes:" -ForegroundColor Gray
Write-Host "    /api/v1/keys/*    -> Key Service (8003)" -ForegroundColor DarkGray
Write-Host "    /api/v1/auth/*    -> Auth Service (8001)" -ForegroundColor DarkGray
Write-Host "    /api/v1/users/*   -> User Service (8002)" -ForegroundColor DarkGray
Write-Host "    /api/v1/sign      -> Enterprise API (9000)" -ForegroundColor DarkGray
Write-Host "    /api/v1/verify    -> Enterprise API (9000)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Test API Keys:" -ForegroundColor Yellow
Write-Host "  demo-api-key-for-testing (all features)" -ForegroundColor Gray
Write-Host ""
Write-Host "Commands:" -ForegroundColor Yellow
Write-Host "  Stop all:    docker-compose -f docker-compose.full-stack.yml down" -ForegroundColor Gray
Write-Host "  View logs:   docker logs encypher-enterprise-api -f" -ForegroundColor Gray
Write-Host "  Clean start: .\start-dev.ps1 -CleanStart" -ForegroundColor Gray
Write-Host ""
