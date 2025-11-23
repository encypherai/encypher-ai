# Check if .env exists in marketing-site
if (-not (Test-Path "apps/marketing-site/.env")) {
    Copy-Item "apps/marketing-site/.env.example" "apps/marketing-site/.env"
    Write-Host "Created .env for marketing-site"
}

# Start Backend Services
Write-Host "Starting backend services with Docker..."
Set-Location services
docker-compose -f docker-compose.dev.yml up -d --build web-service enterprise-api postgres redis

# Wait for DB
Write-Host "Waiting for database..."
Start-Sleep -Seconds 10

# Run Migrations
Write-Host "Running database migrations..."
try {
    docker exec encypher-web-service alembic upgrade head
} catch {
    Write-Host "Migration failed. Please check container logs: docker logs encypher-web-service"
}

# Instructions
Write-Host "`nBackend services are running!"
Write-Host "Web Service: http://localhost:8002"
Write-Host "`nTo start the frontend:"
Write-Host "1. cd apps/marketing-site"
Write-Host "2. npm install --legacy-peer-deps"
Write-Host "3. npm run dev"

# Return to root
Set-Location ..
