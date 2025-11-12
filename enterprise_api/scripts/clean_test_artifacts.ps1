#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Clean test artifacts before running benchmarks
.DESCRIPTION
    Removes all files with multiple extensions (.signed.txt, .embedded.txt, etc.)
    Keeps only raw .txt files for clean benchmark runs
#>

param(
    [string]$TestDir = "outputs\wikipedia_prepared",
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$fullPath = Join-Path $repoRoot $TestDir

if (-not (Test-Path $fullPath)) {
    Write-Host "Test directory not found: $fullPath" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== CLEANING TEST ARTIFACTS ===" -ForegroundColor Cyan
Write-Host "Directory: $fullPath" -ForegroundColor Yellow

# Find files with multiple extensions (e.g., .signed.txt, .embedded.txt)
$filesToRemove = Get-ChildItem -Path $fullPath -Recurse -File | Where-Object {
    # Count dots in filename (excluding directory path)
    $dotCount = ($_.Name.ToCharArray() | Where-Object { $_ -eq '.' }).Count
    $dotCount -gt 1
}

$count = ($filesToRemove | Measure-Object).Count

if ($count -eq 0) {
    Write-Host "`n[OK] No artifacts to clean - directory is already clean!" -ForegroundColor Green
    exit 0
}

Write-Host "`nFound $count files to remove:" -ForegroundColor Yellow

# Group by extension pattern for summary
$grouped = $filesToRemove | Group-Object { 
    if ($_.Name -match '\.(\w+\.\w+)$') { 
        ".$($matches[1])" 
    } else { 
        $_.Extension 
    }
}

foreach ($group in $grouped) {
    Write-Host "  $($group.Count) files with pattern: *$($group.Name)" -ForegroundColor White
}

# Show first 5 examples
Write-Host "`nExamples:" -ForegroundColor Yellow
$filesToRemove | Select-Object -First 5 | ForEach-Object {
    Write-Host "  $($_.FullName.Replace($fullPath, '.'))" -ForegroundColor DarkGray
}

if ($DryRun) {
    Write-Host "`n[DRY RUN] Would remove $count files" -ForegroundColor Cyan
    Write-Host "Run without -DryRun to actually delete files" -ForegroundColor Yellow
} else {
    Write-Host "`nRemoving $count files..." -ForegroundColor Yellow
    $filesToRemove | Remove-Item -Force -ErrorAction Continue
    
    # Also remove state file
    $stateFile = Join-Path $fullPath '.encypher-state.json'
    if (Test-Path $stateFile) {
        Remove-Item $stateFile -Force
        Write-Host "[OK] Removed state file: .encypher-state.json" -ForegroundColor Green
    }
    
    Write-Host "`n[OK] Cleanup complete! Removed $count files" -ForegroundColor Green
}

# Show remaining file count
$remaining = (Get-ChildItem -Path $fullPath -Recurse -File -Filter "*.txt" | Measure-Object).Count
Write-Host "Remaining .txt files: $remaining" -ForegroundColor Cyan
