param(
  [int]$Concurrency = 32,
  [int]$Limit = 10000,
  [string]$BaseUrl = 'http://127.0.0.1:9000',
  [switch]$Clean,
  [string]$PgContainer = 'encypher-tools-postgres',
  [string]$PgDb = 'encypher_tools_bench',
  [string]$PgUser = 'encypher',
  [string]$PgPassword = 'encypher_dev_password'
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'bench_helpers.ps1')
Import-BenchEnv

# Defaults from env if present
if ($env:PG_CONTAINER) { $PgContainer = $env:PG_CONTAINER }
if ($env:PG_DB) { $PgDb = $env:PG_DB }
if ($env:PG_USER) { $PgUser = $env:PG_USER }
if ($env:PG_PASSWORD) { $PgPassword = $env:PG_PASSWORD }

if (-not $env:ENCYPHER_API_KEY) { $env:ENCYPHER_API_KEY = 'demo-key-123' }
if (-not $env:PYTHONIOENCODING) { $env:PYTHONIOENCODING = 'utf-8' }

$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$logsDir = Join-Path $PSScriptRoot 'bench_logs'
Ensure-Dir -Path $logsDir
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$logPath = Join-Path $logsDir ("embeddings_{0}_{1}.log" -f $Concurrency,$ts)

if ($Clean) {
  Write-Host 'Cleaning embedded artifacts and truncating content_references...' -ForegroundColor Yellow
  $prepPath = Join-Path $repoRoot 'outputs\wikipedia_prepared'
  if (Test-Path $prepPath) {
    Get-ChildItem -Path $prepPath -Recurse -Include *.embedded.* | Remove-Item -Force -ErrorAction SilentlyContinue
    $state = Join-Path $prepPath '.encypher-state.json'
    if (Test-Path $state) { Remove-Item $state -Force }
  }
  # Truncate via Python helper script
  Write-Host 'Truncating content_references table...'
  Push-Location (Split-Path $PSScriptRoot -Parent)
  & uv run python scripts/truncate_content_refs.py
  Pop-Location
}

$cpu = Start-CpuLog -Name ("embeddings_{0}" -f $Concurrency)
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
