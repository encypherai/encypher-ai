# ============================================================================
# Encypher Development Environment Startup Script
# ============================================================================
#
# This script starts ALL services needed for local development, mirroring
# the production architecture. Uses docker-compose.full-stack.yml.
#
# ============================================================================
# ARCHITECTURE OVERVIEW
# ============================================================================
#
# ┌─────────────────────────────────────────────────────────────────────────┐
# │                         INFRASTRUCTURE                                   │
# ├─────────────────────────────────────────────────────────────────────────┤
# │  Traefik API Gateway     │ 8000  │ Routes /api/v1/* to microservices    │
# │  Traefik Dashboard       │ 8080  │ Traefik admin UI                     │
# │  PostgreSQL              │ 5432  │ 10 per-service databases             │
# │  Redis Cache             │ 6379  │ Caching, sessions, rate limiting     │
# │  Redis Celery            │ 6380  │ Background task queue                │
# └─────────────────────────────────────────────────────────────────────────┘
#
# ┌─────────────────────────────────────────────────────────────────────────┐
# │                         MICROSERVICES                                    │
# ├─────────────────────────────────────────────────────────────────────────┤
# │  Service              │ Port  │ Database            │ Description          │
# │  ─────────────────────┼───────┼─────────────────────┼────────────────────  │
# │  auth-service         │ 8001  │ encypher_auth       │ Authentication, JWT  │
# │  user-service         │ 8002  │ encypher_users      │ User profiles, teams │
# │  key-service          │ 8003  │ encypher_keys       │ API keys, orgs       │
# │  encoding-service     │ 8004  │ encypher_encoding   │ C2PA encoding        │
# │  verification-service │ 8005  │ encypher_verification│ Content verification│
# │  analytics-service    │ 8006  │ encypher_analytics  │ Usage metrics        │
# │  billing-service      │ 8007  │ encypher_billing    │ Subscriptions        │
# │  notification-service │ 8008  │ encypher_notifications│ Email, notifications│
# │  enterprise-api       │ 9000  │ encypher_content    │ C2PA sign/verify API │
# └─────────────────────────────────────────────────────────────────────────┘
#
# ┌─────────────────────────────────────────────────────────────────────────┐
# │                         FRONTEND APPS                                    │
# ├─────────────────────────────────────────────────────────────────────────┤
# │  Marketing Site       │ 3000  │ Next.js        │ encypherai.com         │
# │  Dashboard            │ 3001  │ Next.js        │ dashboard.encypherai   │
# └─────────────────────────────────────────────────────────────────────────┘
#
# ============================================================================
# TRAEFIK API GATEWAY ROUTING (port 8000)
# ============================================================================
#
#   /                    → Enterprise API (9000) [API landing page]
#   /docs                → Enterprise API (9000) [Swagger UI]
#   /redoc               → Enterprise API (9000) [ReDoc]
#   /openapi.json        → Enterprise API (9000) [OpenAPI spec]
#   /health              → Enterprise API (9000) [Health check]
#
#   /api/v1/auth/*       → Auth Service (8001)
#   /api/v1/organizations/* → Auth Service (8001) [Team management]
#   /api/v1/users/*      → User Service (8002)
#   /api/v1/keys/*       → Key Service (8003)
#   /api/v1/encode       → Encoding Service (8004)
#   /api/v1/verify/*     → Verification Service (8005) [specific paths]
#   /api/v1/analytics/*  → Analytics Service (8006)
#   /api/v1/billing/*    → Billing Service (8007)
#   /api/v1/notifications/* → Notification Service (8008)
#   /api/v1/*            → Enterprise API (9000) [catch-all: sign, verify, stream, etc.]
#
# ============================================================================
# DATABASE ARCHITECTURE (Per-Service Databases)
# ============================================================================
#
# Each microservice has its own isolated database (matches production):
#
#   PostgreSQL (5432) - Single container, multiple databases:
#     - encypher_auth:          auth-service
#     - encypher_users:         user-service
#     - encypher_keys:          key-service
#     - encypher_billing:       billing-service
#     - encypher_notifications: notification-service
#     - encypher_encoding:      encoding-service
#     - encypher_verification:  verification-service
#     - encypher_analytics:     analytics-service
#     - encypher_coalition:     coalition-service
#     - encypher_content:       enterprise-api (C2PA content)
#
# Each service receives DATABASE_URL pointing to its own database.
# This matches production where each service has its own PostgreSQL instance.
#
# See docs/architecture/DATABASE_ARCHITECTURE.md for full schema details.
#
# ============================================================================
# TEST USER (Development Only)
# ============================================================================
#
# A test user is automatically created on first database initialization:
#   Email:    test@encypherai.com
#   Password: TestPassword123!
#
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
  -CleanStart     Full clean rebuild:
                    - Removes Docker volumes (fresh database with test user)
                    - Rebuilds all Docker images from Dockerfiles
                    - Clears .next and node_modules caches
  -Help           Show this help message

Examples:
  .\start-dev.ps1                    # Start everything (uses cached images)
  .\start-dev.ps1 -CleanStart        # Full rebuild from scratch (fixes most issues)
  .\start-dev.ps1 -SkipDocker        # Only start frontends

"@
    exit 0
}

$ErrorActionPreference = "Continue"
$script:hasErrors = $false

$postgresHostPort = 15432
if ($env:POSTGRES_HOST_PORT) {
    try {
        $postgresHostPort = [int]$env:POSTGRES_HOST_PORT
    } catch {
        $postgresHostPort = 15432
    }
}

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
    Write-Step "2/8" "Cleaning caches and Docker resources..."
    
    # Stop and remove all containers, networks, and volumes
    Write-Info "Stopping Docker containers and removing volumes..."
    docker-compose -f docker-compose.full-stack.yml down -v 2>$null
    
    # Remove old Docker images for our services to force rebuild
    Write-Info "Removing old Docker images to force rebuild..."
    $services = @(
        "encypherai-commercial-auth-service",
        "encypherai-commercial-user-service",
        "encypherai-commercial-key-service",
        "encypherai-commercial-encoding-service",
        "encypherai-commercial-verification-service",
        "encypherai-commercial-analytics-service",
        "encypherai-commercial-billing-service",
        "encypherai-commercial-notification-service",
        "encypherai-commercial-enterprise-api"
    )
    foreach ($service in $services) {
        docker rmi $service 2>$null | Out-Null
    }
    Write-Info "Docker images cleared"
    
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
    
    Write-Success "All caches and Docker resources cleaned"
} else {
    Write-Step "2/8" "Skipping cache clean (use -CleanStart to clean)"
}

# Step 3: Start All Docker Services
if (-not $SkipDocker) {
    Write-Step "3/8" "Starting all Docker services..."
    
    # Stop any existing containers first (unless already done in CleanStart)
    if (-not $CleanStart) {
        docker-compose -f docker-compose.full-stack.yml down 2>$null
    }
    
    # Start ALL services (mirrors production)
    # Infrastructure: postgres, redis-cache, redis-celery, traefik
    # Microservices: auth, user, key, encoding, verification, analytics, billing, notification
    # Enterprise API: C2PA signing/verification
    if ($CleanStart) {
        # Force rebuild all images from Dockerfiles with latest code
        Write-Info "Building all Docker images from scratch (this may take a few minutes)..."
        docker-compose -f docker-compose.full-stack.yml up -d --build --force-recreate 2>$null
    } else {
        docker-compose -f docker-compose.full-stack.yml up -d 2>$null
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Failed to start Docker services"
    } else {
        Write-Success "All Docker services starting..."
    }
} else {
    Write-Step "3/8" "Skipping Docker (use existing services)"
}

# Step 4: Wait for databases
if (-not $SkipDocker) {
    Write-Step "4/8" "Waiting for PostgreSQL..."
    
    # Wait for PostgreSQL (single container with multiple databases)
    $maxRetries = 30
    $retryCount = 0
    do {
        $retryCount++
        docker exec encypher-postgres pg_isready -U encypher 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "PostgreSQL is ready (port 5432)"
            break
        }
        Write-Host "    Waiting for PostgreSQL... ($retryCount/$maxRetries)" -ForegroundColor DarkGray
        Start-Sleep -Seconds 2
    } while ($retryCount -lt $maxRetries)
    
    if ($retryCount -ge $maxRetries) {
        Write-Err "PostgreSQL did not start in time"
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

# Step 5: Database Initialization
if (-not $SkipDocker) {
    Write-Step "5/8" "Databases initialized via init-databases.sql..."
    
    # The init-databases.sql script runs automatically on first PostgreSQL startup
    # It creates all per-service databases. Each service runs its own Alembic migrations.
    Write-Info "Per-service databases created by PostgreSQL init script"
    Write-Success "Database initialization complete"
} else {
    Write-Step "5/8" "Skipping database init (Docker skipped)"
}

# Step 6: Wait for Microservices
if (-not $SkipDocker) {
    Write-Step "6/8" "Waiting for microservices to be ready..."
    
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
    
    # Wait for Key Service
    $retryCount = 0
    do {
        $retryCount++
        try {
            $health = Invoke-RestMethod -Uri "http://localhost:8003/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($health.status -eq "healthy") {
                Write-Success "Key Service is ready (port 8003)"
                break
            }
        } catch {
            # Still starting
        }
        Write-Host "    Waiting for Key Service... ($retryCount/$maxRetries)" -ForegroundColor DarkGray
        Start-Sleep -Seconds 2
    } while ($retryCount -lt $maxRetries)
    
    if ($retryCount -ge $maxRetries) {
        Write-Warn "Key Service may still be starting (check docker logs)"
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
    @{Name="PostgreSQL"; Port=$postgresHostPort},
    @{Name="Redis Cache"; Port=6379},
    @{Name="Redis Celery"; Port=6380},
    @{Name="Traefik Gateway"; Port=8000},
    @{Name="Auth Service"; Port=8001},
    @{Name="User Service"; Port=8002},
    @{Name="Key Service"; Port=8003},
    @{Name="Encoding Service"; Port=8004},
    @{Name="Verification Service"; Port=8005},
    @{Name="Analytics Service"; Port=8006},
    @{Name="Billing Service"; Port=8007},
    @{Name="Notification Service"; Port=8008},
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
Write-Host "Infrastructure:" -ForegroundColor Yellow
Write-Host "  PostgreSQL:         localhost:$postgresHostPort (10 databases)" -ForegroundColor Gray
Write-Host "  Redis Cache:        localhost:6379" -ForegroundColor Gray
Write-Host "  Redis Celery:       localhost:6380" -ForegroundColor Gray
Write-Host ""
Write-Host "Microservices:" -ForegroundColor Yellow
Write-Host "  Auth Service:       http://localhost:8001" -ForegroundColor Gray
Write-Host "  User Service:       http://localhost:8002" -ForegroundColor Gray
Write-Host "  Key Service:        http://localhost:8003" -ForegroundColor Gray
Write-Host "  Encoding Service:   http://localhost:8004" -ForegroundColor Gray
Write-Host "  Verification Svc:   http://localhost:8005" -ForegroundColor Gray
Write-Host "  Analytics Service:  http://localhost:8006" -ForegroundColor Gray
Write-Host "  Billing Service:    http://localhost:8007" -ForegroundColor Gray
Write-Host "  Notification Svc:   http://localhost:8008" -ForegroundColor Gray
Write-Host "  Enterprise API:     http://localhost:9000" -ForegroundColor Gray
Write-Host ""
Write-Host "API Gateway (Traefik):" -ForegroundColor Yellow
Write-Host "  Gateway URL:        http://localhost:8000/api/v1/*" -ForegroundColor Cyan
Write-Host "  Dashboard:          http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend URLs:" -ForegroundColor Yellow
Write-Host "  Marketing Site:     http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Dashboard:          http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Credentials:" -ForegroundColor Yellow
Write-Host "  Email:    test@encypherai.com" -ForegroundColor Gray
Write-Host "  Password: TestPassword123!" -ForegroundColor Gray
Write-Host "  API Key:  demo-api-key-for-testing" -ForegroundColor Gray
Write-Host ""
Write-Host "Commands:" -ForegroundColor Yellow
Write-Host "  Stop all:    docker-compose -f docker-compose.full-stack.yml down" -ForegroundColor Gray
Write-Host "  View logs:   docker logs encypher-enterprise-api -f" -ForegroundColor Gray
Write-Host "  Clean start: .\start-dev.ps1 -CleanStart" -ForegroundColor Gray
Write-Host ""
