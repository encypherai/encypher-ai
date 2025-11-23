# Script to build and run the benchmark container, then execute load tests

$ErrorActionPreference = "Stop"
$NetworkName = "encypher-bench-net"
$DbContainerName = "encypher-bench-db"
$ApiContainerName = "encypher-bench-api"
$DbPort = 54323 # Avoid conflict with default 5432

# 1. Create Docker Network
if (!(docker network ls -q -f name=$NetworkName)) {
    Write-Host "==> Creating Docker Network: $NetworkName"
    docker network create $NetworkName
}

try {
    # 2. Start Postgres
    Write-Host "==> Starting Postgres Container..."
    docker run -d --name $DbContainerName --network $NetworkName `
        -e POSTGRES_USER=encypher -e POSTGRES_PASSWORD=password -e POSTGRES_DB=encypher_enterprise `
        -p "${DbPort}:5432" postgres:15-alpine

    # Wait for DB
    Write-Host "waiting for DB..."
    Start-Sleep -Seconds 5

    # Get DB IP to avoid DNS issues
    $DbIp = docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $DbContainerName
    Write-Host "DB IP: $DbIp"

    # 3. Initialize Database (from Host)
    Write-Host "==> Initializing Database Schema & Tuning..."
    # We set DATABASE_URL for the python script to connect to localhost mapped port
    $env:DATABASE_URL = "postgresql://encypher:password@localhost:${DbPort}/encypher_enterprise"
    
    # Use python to run the SQL init script
    # We read the SQL file and execute it using a temporary python snippet for simplicity and portability
    $InitScript = @"
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psycopg2.connect("$env:DATABASE_URL")
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

# Apply Performance Tuning
print('Applying Postgres tuning...')
cur.execute("ALTER SYSTEM SET synchronous_commit = 'off';")
cur.execute("ALTER SYSTEM SET wal_writer_delay = '200ms';")
cur.execute("SELECT pg_reload_conf();")

with open('scripts/init_db.sql', 'r') as f:
    cur.execute(f.read())

print('Schema initialized.')
conn.close()
"@
    
    # Run the init snippet
    python -c "$InitScript"

    # 4. Build & Run API
    Write-Host "==> Building Benchmark Docker Image..."
    docker build --no-cache -f Dockerfile.benchmark -t encypher-api-benchmark ..

    Write-Host "==> Starting Benchmark API Container..."
    # Connect to same network, pass DB URL using container IP
    docker run -d --name $ApiContainerName --network $NetworkName -p 8000:8000 `
        -e DATABASE_URL="postgresql+asyncpg://encypher:password@${DbIp}:5432/encypher_enterprise" `
        -e KEY_ENCRYPTION_KEY="0000000000000000000000000000000000000000000000000000000000000000" `
        -e ENCRYPTION_NONCE="000000000000000000000000" `
        -e SSL_COM_API_KEY="test" `
        -e DEMO_API_KEY="demo-key-load-test" `
        encypher-api-benchmark

    # Wait for API
    Write-Host "==> Waiting for API to be ready..."
    $retries = 0
    $healthy = $false
    while ($retries -lt 60) {
        try {
            $resp = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Get -ErrorAction SilentlyContinue
            if ($resp.StatusCode -eq 200) { $healthy = $true; break }
        } catch { Start-Sleep -Seconds 1 }
        $retries++
        Write-Host "." -NoNewline
    }
    Write-Host ""

    if (-not $healthy) {
        Write-Host "API failed to start. Container Logs:" -ForegroundColor Red
        docker logs $ApiContainerName
        throw "API health check failed."
    }

    # 5. Run Benchmark Script
    Write-Host "==> API is UP. Installing dependencies & Running 5K Benchmark..."
    
    # Ensure dependencies are installed on host
    pip install httpx rich

    python scripts/benchmark_5k_comparison.py --base-url http://localhost:8000 --limit 5000 --concurrency 20

}
catch {
    Write-Error "An error occurred: $_"
}
finally {
    Write-Host "==> Cleaning up..."
    docker rm -f $ApiContainerName $DbContainerName 2>$null
    docker network rm $NetworkName 2>$null
    Write-Host "==> Done."
}
