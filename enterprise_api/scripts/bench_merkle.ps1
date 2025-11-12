param(
  [int]$Concurrency = 32,
  [int]$Limit = 10000,
  [string]$BaseUrl = 'http://127.0.0.1:9000'
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'bench_helpers.ps1')
Import-BenchEnv

if (-not $env:ENCYPHER_API_KEY) { $env:ENCYPHER_API_KEY = 'demo-key-123' }
if (-not $env:PYTHONIOENCODING) { $env:PYTHONIOENCODING = 'utf-8' }

# ALWAYS clean test artifacts before running
Write-Host "Cleaning test artifacts..." -ForegroundColor Yellow
$cleanupScript = Join-Path $PSScriptRoot 'clean_test_artifacts.ps1'
if (Test-Path $cleanupScript) {
    & $cleanupScript -TestDir 'outputs\wikipedia_prepared' | Out-Null
}

$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$logsDir = Join-Path $PSScriptRoot 'bench_logs'
Ensure-Dir -Path $logsDir
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$logPath = Join-Path $logsDir ("merkle_{0}_{1}.log" -f $Concurrency,$ts)

$cpu = Start-CpuLog -Name ("merkle_{0}" -f $Concurrency)
try {
  Push-Location $repoRoot
  & uv run python tools/large_dataset_sign_verify.py --mode merkle --limit $Limit --concurrency $Concurrency --base-url $BaseUrl 2>&1 |
    Tee-Object -FilePath $logPath | Out-Host
} finally {
  Pop-Location
  Stop-CpuLog -Pid $($cpu.Pid)
}

$avgCpu = Get-AvgCpuFromCsv -CsvPath $($cpu.File)
$summary = Select-String -Path $logPath -Pattern 'Merkle Encode Performance','Files:','Total Time:','P50 per file:','P95 per file:' | ForEach-Object { $_.Line }

Write-Host "`n=== MERKLE @ $Concurrency Summary ===" -ForegroundColor Cyan
$summary | ForEach-Object { Write-Host $_ }
Write-Host ("AVG CPU: {0}% (source: {1})" -f $avgCpu, (Split-Path $($cpu.File) -Leaf))
