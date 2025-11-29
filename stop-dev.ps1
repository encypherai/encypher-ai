# ============================================================================
# Encypher Development Environment Stop Script
# ============================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Stopping Encypher Dev Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Stop Docker containers
Write-Host "Stopping Docker containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.full-stack.yml down 2>$null
Write-Host "  Docker containers stopped" -ForegroundColor Green

# Kill any running Next.js processes on dev ports
Write-Host ""
Write-Host "Stopping frontend processes..." -ForegroundColor Yellow

$ports = @(3000, 3001, 3002)
foreach ($port in $ports) {
    $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | 
               Select-Object -ExpandProperty OwningProcess -First 1
    if ($process) {
        Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
        Write-Host "  Stopped process on port $port" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  All services stopped" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
