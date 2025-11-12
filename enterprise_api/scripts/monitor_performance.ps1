#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Real-time performance monitoring during benchmarks
.DESCRIPTION
    Monitors CPU, RAM, and API request rate in real-time
#>

param(
    [int]$RefreshSeconds = 2
)

Write-Host "`n=== REAL-TIME PERFORMANCE MONITOR ===" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop monitoring`n" -ForegroundColor Yellow

$iteration = 0
while ($true) {
    $iteration++
    
    # Get Python processes (API workers)
    $pythonProcs = Get-Process python -ErrorAction SilentlyContinue
    
    if ($pythonProcs) {
        $totalCpu = ($pythonProcs | Measure-Object -Property CPU -Sum).Sum
        $totalMem = ($pythonProcs | Measure-Object -Property WorkingSet64 -Sum).Sum / 1MB
        $procCount = ($pythonProcs | Measure-Object).Count
        
        # Get system totals
        $mem = Get-CimInstance Win32_OperatingSystem
        $totalRam = [math]::Round($mem.TotalVisibleMemorySize / 1MB, 2)
        $usedRam = [math]::Round(($mem.TotalVisibleMemorySize - $mem.FreePhysicalMemory) / 1MB, 2)
        $ramPercent = [math]::Round(($usedRam / $totalRam) * 100, 1)
        
        # Display
        Clear-Host
        Write-Host "`n=== REAL-TIME PERFORMANCE MONITOR ===" -ForegroundColor Cyan
        Write-Host "Iteration: $iteration | Refresh: ${RefreshSeconds}s | Press Ctrl+C to stop`n" -ForegroundColor Yellow
        
        Write-Host "API Workers:" -ForegroundColor Green
        Write-Host "  Processes: $procCount" -ForegroundColor White
        Write-Host "  Total CPU Time: $([math]::Round($totalCpu, 2))s" -ForegroundColor White
        Write-Host "  Memory Usage: $([math]::Round($totalMem, 2)) MB" -ForegroundColor White
        
        Write-Host "`nSystem Resources:" -ForegroundColor Green
        Write-Host "  RAM: $usedRam GB / $totalRam GB ($ramPercent%)" -ForegroundColor $(if($ramPercent -gt 80){'Red'}elseif($ramPercent -gt 60){'Yellow'}else{'White'})
        
        # Check for log files to estimate progress
        $logDir = Join-Path $PSScriptRoot 'bench_logs'
        if (Test-Path $logDir) {
            $latestLog = Get-ChildItem $logDir -Filter "embeddings_opt_*.log" -ErrorAction SilentlyContinue | 
                Sort-Object LastWriteTime -Descending | Select-Object -First 1
            
            if ($latestLog) {
                $logSize = [math]::Round($latestLog.Length / 1KB, 2)
                $lastWrite = (Get-Date) - $latestLog.LastWriteTime
                Write-Host "`nBenchmark Progress:" -ForegroundColor Green
                Write-Host "  Log File: $($latestLog.Name)" -ForegroundColor White
                Write-Host "  Log Size: $logSize KB" -ForegroundColor White
                Write-Host "  Last Updated: $([math]::Round($lastWrite.TotalSeconds, 0))s ago" -ForegroundColor White
                
                # Try to count completed files from log
                $content = Get-Content $latestLog.FullName -Tail 50 -ErrorAction SilentlyContinue
                $embedPattern = $content | Select-String -Pattern "Embedding.*sentences" -AllMatches
                if ($embedPattern) {
                    Write-Host "  Status: Processing embeddings..." -ForegroundColor Cyan
                }
            }
        }
        
        Write-Host "`nTip: Watch Task Manager for CPU/RAM usage trends" -ForegroundColor Yellow
        Write-Host "Expected: 50-80% CPU with 16 workers and 64 concurrency" -ForegroundColor Yellow
        
    } else {
        Clear-Host
        Write-Host "`n=== REAL-TIME PERFORMANCE MONITOR ===" -ForegroundColor Cyan
        Write-Host "Iteration: $iteration | Refresh: ${RefreshSeconds}s | Press Ctrl+C to stop`n" -ForegroundColor Yellow
        Write-Host "No Python processes found - API may not be running" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds $RefreshSeconds
}
