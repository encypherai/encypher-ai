param(
  [int]$Concurrency = 64,  # Increased from 32
  [int]$Limit = 10000,
  [string]$BaseUrl = 'http://127.0.0.1:9000',
  [switch]$Clean
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'bench_helpers.ps1')
Import-BenchEnv

if (-not $env:ENCYPHER_API_KEY) { $env:ENCYPHER_API_KEY = 'demo-key-local' }
if (-not $env:PYTHONIOENCODING) { $env:PYTHONIOENCODING = 'utf-8' }

$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$logsDir = Join-Path $PSScriptRoot 'bench_logs'
Ensure-Dir -Path $logsDir
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$logPath = Join-Path $logsDir ("embeddings_opt_{0}_{1}.log" -f $Concurrency,$ts)

if ($Clean) {
  Write-Host 'Cleaning test artifacts...' -ForegroundColor Yellow
  
  # Use the dedicated cleanup script to remove all multi-extension files
  $cleanupScript = Join-Path $PSScriptRoot 'clean_test_artifacts.ps1'
  if (Test-Path $cleanupScript) {
    & $cleanupScript -TestDir 'outputs\wikipedia_prepared'
  } else {
    # Fallback: manual cleanup
    $prepPath = Join-Path $repoRoot 'outputs\wikipedia_prepared'
    if (Test-Path $prepPath) {
      Write-Host "  Removing .signed.* files..." -ForegroundColor DarkGray
      Get-ChildItem -Path $prepPath -Recurse -Include *.signed.* | Remove-Item -Force -ErrorAction SilentlyContinue
      Write-Host "  Removing .embedded.* files..." -ForegroundColor DarkGray
      Get-ChildItem -Path $prepPath -Recurse -Include *.embedded.* | Remove-Item -Force -ErrorAction SilentlyContinue
      $state = Join-Path $prepPath '.encypher-state.json'
      if (Test-Path $state) { 
        Remove-Item $state -Force 
        Write-Host "  Removed state file" -ForegroundColor DarkGray
      }
    }
  }
  Write-Host 'Skipping table truncate (table may not exist yet)' -ForegroundColor Yellow
}

Write-Host "`n=== OPTIMIZED EMBEDDINGS BENCHMARK ===" -ForegroundColor Cyan
Write-Host "Concurrency: $Concurrency (increased for better CPU utilization)" -ForegroundColor Green
Write-Host "Files: $Limit" -ForegroundColor Green
Write-Host "API: $BaseUrl" -ForegroundColor Green
Write-Host "`nStarting benchmark...`n" -ForegroundColor Yellow

$cpu = Start-CpuLog -Name ("embeddings_opt_{0}" -f $Concurrency)
try {
  Push-Location $repoRoot
  & uv run python tools/large_dataset_sign_verify.py --mode embeddings --limit $Limit --concurrency $Concurrency --base-url $BaseUrl 2>&1 |
    Tee-Object -FilePath $logPath | Out-Host
} finally {
  Pop-Location
  Stop-CpuLog -Pid $($cpu.Pid)
}

$avgCpu = Get-AvgCpuFromCsv -CsvPath $($cpu.File)
$summary = Select-String -Path $logPath -Pattern 'Embeddings Performance','Files:','Total Time:','P50 per file:','P95 per file:' | ForEach-Object { $_.Line }

Write-Host "`n=== EMBEDDINGS @ $Concurrency Summary ===" -ForegroundColor Cyan
$summary | ForEach-Object { Write-Host $_ }
Write-Host ("AVG CPU: {0}% (source: {1})" -f $avgCpu, (Split-Path $($cpu.File) -Leaf))
