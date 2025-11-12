#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start the Enterprise API with visible logs
.DESCRIPTION
    Starts the FastAPI application with Uvicorn workers and displays logs in real-time
#>

param(
    [int]$Workers = 16,
    [string]$BindHost = '127.0.0.1',
    [int]$Port = 9000,
    [switch]$Background
)

$ErrorActionPreference = 'Stop'

# Navigate to enterprise_api directory
$apiDir = Split-Path $PSScriptRoot -Parent
Push-Location $apiDir

Write-Host "`n=== STARTING ENTERPRISE API WITH LOGS ===" -ForegroundColor Cyan
Write-Host "Workers: $Workers" -ForegroundColor Green
Write-Host "Host: $BindHost" -ForegroundColor Green
Write-Host "Port: $Port" -ForegroundColor Green
Write-Host "Background: $Background" -ForegroundColor Green

# Create logs directory
$logsDir = Join-Path $PSScriptRoot 'api_logs'
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logFile = Join-Path $logsDir "api_${Workers}workers_${timestamp}.log"

Write-Host "`nLog file: $logFile" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the API`n" -ForegroundColor Yellow

if ($Background) {
    # Start in background and tail the log
    Write-Host "Starting API in background..." -ForegroundColor Cyan
    $job = Start-Job -ScriptBlock {
        param($apiDir, $BindHost, $Port, $Workers, $logFile)
        Set-Location $apiDir
        & uv run uvicorn app.main:app --host $BindHost --port $Port --workers $Workers 2>&1 | 
            Tee-Object -FilePath $logFile
    } -ArgumentList $apiDir, $BindHost, $Port, $Workers, $logFile
    
    Write-Host "Job ID: $($job.Id)" -ForegroundColor Green
    Write-Host "Waiting for API to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Test health
    try {
        $response = Invoke-WebRequest -Uri "http://${BindHost}:${Port}/health" -UseBasicParsing -TimeoutSec 5
        Write-Host "`n✓ API is healthy!" -ForegroundColor Green
        Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "Response: $($response.Content)" -ForegroundColor White
    } catch {
        Write-Host "`n✗ API health check failed!" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        Write-Host "`nCheck log file: $logFile" -ForegroundColor Yellow
    }
    
    Write-Host "`nTo view logs in real-time:" -ForegroundColor Cyan
    Write-Host "  Get-Content ""$logFile"" -Wait -Tail 50" -ForegroundColor White
    Write-Host "`nTo stop the API:" -ForegroundColor Cyan
    Write-Host "  Stop-Job $($job.Id); Remove-Job $($job.Id)" -ForegroundColor White
    
} else {
    # Start in foreground with live output
    Write-Host "Starting API in foreground (logs will appear below)..." -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor DarkGray
    
    try {
        & uv run uvicorn app.main:app --host $BindHost --port $Port --workers $Workers 2>&1 | 
            Tee-Object -FilePath $logFile
    } finally {
        Pop-Location
        Write-Host ("`n" + ("=" * 80)) -ForegroundColor DarkGray
        Write-Host "API stopped. Log saved to: $logFile" -ForegroundColor Yellow
    }
}

Pop-Location
