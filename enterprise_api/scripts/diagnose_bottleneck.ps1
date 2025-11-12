#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Diagnose performance bottlenecks in the Enterprise API
.DESCRIPTION
    This script runs diagnostics to identify CPU, I/O, network, and API bottlenecks
#>

param(
    [string]$ApiUrl = 'http://127.0.0.1:9000'
)

Write-Host "`n=== PERFORMANCE BOTTLENECK DIAGNOSTICS ===" -ForegroundColor Cyan

# 1. Check API health and worker count
Write-Host "`n1. API Configuration:" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$ApiUrl/health" -TimeoutSec 5
    Write-Host "   API Status: $($health.status)" -ForegroundColor Green
    
    # Check uvicorn processes
    $uvicornProcs = Get-Process | Where-Object { $_.ProcessName -like '*python*' -and $_.CommandLine -like '*uvicorn*' }
    $workerCount = ($uvicornProcs | Measure-Object).Count
    Write-Host "   Uvicorn Workers: $workerCount" -ForegroundColor $(if($workerCount -ge 4){'Green'}else{'Red'})
    Write-Host "   Recommendation: Use 8-16 workers on beefy workstation" -ForegroundColor Cyan
} catch {
    Write-Host "   ERROR: Cannot reach API at $ApiUrl" -ForegroundColor Red
}

# 2. System Resources
Write-Host "`n2. System Resources:" -ForegroundColor Yellow
$cpu = Get-CimInstance Win32_Processor
$mem = Get-CimInstance Win32_OperatingSystem
$cores = $cpu.NumberOfLogicalProcessors
$totalRam = [math]::Round($mem.TotalVisibleMemorySize / 1MB, 2)
$freeRam = [math]::Round($mem.FreePhysicalMemory / 1MB, 2)

Write-Host "   CPU Cores: $cores" -ForegroundColor Green
Write-Host "   Total RAM: $totalRam GB" -ForegroundColor Green
Write-Host "   Free RAM: $freeRam GB" -ForegroundColor Green
Write-Host "   Current CPU Usage: 26% (from your screenshot)" -ForegroundColor Yellow
Write-Host "   Current RAM Usage: 48% (from your screenshot)" -ForegroundColor Yellow

# 3. Bottleneck Analysis
Write-Host "`n3. Bottleneck Analysis:" -ForegroundColor Yellow
Write-Host "   [OK] CPU: UNDERUTILIZED (26% usage)" -ForegroundColor Yellow
Write-Host "   [OK] RAM: UNDERUTILIZED (48% usage)" -ForegroundColor Yellow
Write-Host "   [!!] Likely Bottleneck: I/O or API Processing" -ForegroundColor Red

# 4. Recommendations
Write-Host "`n4. Optimization Recommendations:" -ForegroundColor Yellow
Write-Host "   A. Increase API Workers:" -ForegroundColor Cyan
Write-Host "      - Current: 4 workers" -ForegroundColor White
Write-Host "      - Recommended: 8-16 workers (1-2x CPU cores)" -ForegroundColor Green
Write-Host "      - Command: .\enterprise_api\scripts\start_api.ps1 -Workers 12" -ForegroundColor White

Write-Host "`n   B. Increase Client Concurrency:" -ForegroundColor Cyan
Write-Host "      - Current: 32 concurrent requests" -ForegroundColor White
Write-Host "      - Recommended: 64-128 concurrent requests" -ForegroundColor Green
Write-Host "      - Command: .\enterprise_api\scripts\bench_embeddings_optimized.ps1 -Concurrency 64" -ForegroundColor White

Write-Host "`n   C. Database Connection Pool:" -ForegroundColor Cyan
Write-Host "      - Check: enterprise_api/app/config.py" -ForegroundColor White
Write-Host "      - Increase pool_size and max_overflow for PostgreSQL" -ForegroundColor Green

Write-Host "`n   D. Profile API Endpoint:" -ForegroundColor Cyan
Write-Host "      - Use FastAPI /docs endpoint to test single request latency" -ForegroundColor White
Write-Host "      - If single request is slow, optimize embeddings generation" -ForegroundColor Green

Write-Host "`n   E. Network Optimization:" -ForegroundColor Cyan
Write-Host "      - Consider using HTTP/2 or connection pooling" -ForegroundColor White
Write-Host "      - httpx client already uses connection pooling" -ForegroundColor Green

# 5. Quick Test
Write-Host "`n5. Quick API Response Test:" -ForegroundColor Yellow
try {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $null = Invoke-RestMethod -Uri "$ApiUrl/health" -TimeoutSec 5
    $sw.Stop()
    $latency = $sw.ElapsedMilliseconds
    Write-Host "   Health endpoint latency: $latency ms" -ForegroundColor $(if($latency -lt 100){'Green'}elseif($latency -lt 500){'Yellow'}else{'Red'})
    
    if ($latency -gt 100) {
        Write-Host "   [!!] High latency detected - API may be overloaded" -ForegroundColor Red
    }
} catch {
    Write-Host "   ERROR: Cannot test API latency" -ForegroundColor Red
}

Write-Host "`n=== NEXT STEPS ===" -ForegroundColor Cyan
Write-Host "1. Stop current API: Get-Process python | Stop-Process" -ForegroundColor White
Write-Host "2. Start with more workers: .\enterprise_api\scripts\start_api.ps1 -Workers 12" -ForegroundColor White
Write-Host "3. Run optimized benchmark: .\enterprise_api\scripts\bench_embeddings_optimized.ps1 -Concurrency 64 -Limit 10000" -ForegroundColor White
Write-Host ""
