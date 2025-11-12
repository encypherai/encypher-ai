#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Apply PostgreSQL performance tuning settings
.DESCRIPTION
    Applies performance optimizations to PostgreSQL for high-throughput writes.
    Uses ALTER SYSTEM commands to modify settings without editing postgresql.conf.
#>

param(
    [string]$PgHost = "localhost",
    [int]$Port = 5432,
    [string]$Database = "encypher_enterprise",
    [string]$User = "postgres",
    [string]$Password = "",
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

Write-Host "`n=== POSTGRESQL PERFORMANCE TUNING ===" -ForegroundColor Cyan

if (-not $Password) {
    Write-Host "Error: Password required" -ForegroundColor Red
    Write-Host "Usage: .\apply_postgres_tuning.ps1 -Password 'your_password'" -ForegroundColor Yellow
    exit 1
}

# Performance settings to apply
$settings = @(
    @{Name="synchronous_commit"; Value="off"; Description="Async commits for faster writes"},
    @{Name="wal_buffers"; Value="16MB"; Description="WAL buffer size"},
    @{Name="checkpoint_timeout"; Value="15min"; Description="Checkpoint interval"},
    @{Name="max_wal_size"; Value="4GB"; Description="Max WAL size before checkpoint"},
    @{Name="shared_buffers"; Value="4GB"; Description="Shared memory buffers"; RequiresRestart=$true},
    @{Name="effective_cache_size"; Value="16GB"; Description="Query planner cache hint"},
    @{Name="work_mem"; Value="64MB"; Description="Per-operation memory"},
    @{Name="maintenance_work_mem"; Value="1GB"; Description="Maintenance operation memory"},
    @{Name="max_connections"; Value="200"; Description="Max connections"; RequiresRestart=$true},
    @{Name="random_page_cost"; Value="1.1"; Description="SSD random access cost"},
    @{Name="effective_io_concurrency"; Value="200"; Description="Concurrent I/O operations"}
)

Write-Host "`nSettings to apply:" -ForegroundColor Yellow
foreach ($setting in $settings) {
    $restart = if ($setting.RequiresRestart) { " [REQUIRES RESTART]" } else { "" }
    Write-Host "  $($setting.Name) = $($setting.Value)$restart" -ForegroundColor White
    Write-Host "    $($setting.Description)" -ForegroundColor DarkGray
}

if ($DryRun) {
    Write-Host "`n[DRY RUN] Would apply these settings" -ForegroundColor Cyan
    Write-Host "Run without -DryRun to actually apply" -ForegroundColor Yellow
    exit 0
}

Write-Host "`nApplying settings..." -ForegroundColor Yellow

# Set PGPASSWORD environment variable
$env:PGPASSWORD = $Password

$successCount = 0
$failCount = 0
$requiresRestart = $false

foreach ($setting in $settings) {
    try {
        $sql = "ALTER SYSTEM SET $($setting.Name) = '$($setting.Value)';"
        Write-Host "  Setting $($setting.Name)..." -ForegroundColor DarkGray -NoNewline
        
        $result = & psql -h $PgHost -p $Port -U $User -d $Database -c $sql 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host " OK" -ForegroundColor Green
            $successCount++
            if ($setting.RequiresRestart) {
                $requiresRestart = $true
            }
        } else {
            Write-Host " FAILED" -ForegroundColor Red
            Write-Host "    Error: $result" -ForegroundColor Red
            $failCount++
        }
    } catch {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "    Error: $_" -ForegroundColor Red
        $failCount++
    }
}

# Reload configuration
Write-Host "`nReloading PostgreSQL configuration..." -ForegroundColor Yellow
try {
    $result = & psql -h $PgHost -p $Port -U $User -d $Database -c "SELECT pg_reload_conf();" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Configuration reloaded" -ForegroundColor Green
    } else {
        Write-Host "[FAILED] Could not reload configuration" -ForegroundColor Red
    }
} catch {
    Write-Host "[FAILED] Could not reload configuration: $_" -ForegroundColor Red
}

# Clean up password
Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue

# Summary
Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "Applied: $successCount settings" -ForegroundColor Green
if ($failCount -gt 0) {
    Write-Host "Failed: $failCount settings" -ForegroundColor Red
}

if ($requiresRestart) {
    Write-Host "`n[IMPORTANT] Some settings require PostgreSQL restart:" -ForegroundColor Yellow
    Write-Host "  - shared_buffers" -ForegroundColor White
    Write-Host "  - max_connections" -ForegroundColor White
    Write-Host "`nRestart PostgreSQL to apply these settings:" -ForegroundColor Yellow
    Write-Host "  Windows: Restart 'PostgreSQL' service" -ForegroundColor White
    Write-Host "  Linux: sudo systemctl restart postgresql" -ForegroundColor White
    Write-Host "  Docker: docker restart <container>" -ForegroundColor White
} else {
    Write-Host "`n[OK] All settings applied and active!" -ForegroundColor Green
}

Write-Host "`nVerify settings with:" -ForegroundColor Cyan
Write-Host "  psql -h $PgHost -p $Port -U $User -d $Database -c ""SHOW synchronous_commit;""" -ForegroundColor White
