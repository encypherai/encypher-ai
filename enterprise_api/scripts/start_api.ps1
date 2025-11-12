param(
  [int]$Workers = 4,
  [string]$BindHost = '127.0.0.1',
  [int]$Port = 9000
)

# Optional: load env from .env.bench if present (KEY=VALUE per line)
$envFile = Join-Path $PSScriptRoot '.env.bench'
if (Test-Path $envFile) {
  Get-Content $envFile | ForEach-Object {
    if ($_ -match '^[A-Za-z_][A-Za-z0-9_]*=') {
      $name,$val = $_ -split '=',2
      [Environment]::SetEnvironmentVariable($name, $val, 'Process')
    }
  }
}

# Defaults if not provided via env
if (-not $env:DATABASE_URL) { $env:DATABASE_URL = 'postgresql://encypher:encypher_dev_password@127.0.0.1:5433/encypher_tools_bench' }
if (-not $env:KEY_ENCRYPTION_KEY) { $env:KEY_ENCRYPTION_KEY = '0000000000000000000000000000000000000000000000000000000000000000' }
if (-not $env:ENCRYPTION_NONCE) { $env:ENCRYPTION_NONCE = '000000000000000000000000' }
if (-not $env:SSL_COM_API_KEY) { $env:SSL_COM_API_KEY = 'test-key' }
if (-not $env:DEMO_API_KEY) { $env:DEMO_API_KEY = 'demo-key-123' }
if (-not $env:DEMO_PRIVATE_KEY_HEX) { $env:DEMO_PRIVATE_KEY_HEX = '0000000000000000000000000000000000000000000000000000000000000000' }
if (-not $env:ENVIRONMENT) { $env:ENVIRONMENT = 'development' }

# Kill existing listeners on the port
$pids = (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique)
if ($pids) { Stop-Process -Id $pids -Force }

# Start uvicorn with multiple workers
Start-Process -FilePath uv -ArgumentList @('run','uvicorn','app.main:app','--host',$BindHost,'--port',$Port,'--workers',$Workers) -WorkingDirectory (Split-Path $PSScriptRoot -Parent) -WindowStyle Hidden

Start-Sleep -Seconds 2
try {
  $res = Invoke-WebRequest -Uri ("http://{0}:{1}/health" -f $BindHost,$Port) -UseBasicParsing -TimeoutSec 8
  Write-Output ("API Health: {0}" -f $res.StatusCode)
} catch {
  Write-Output 'API Health: DOWN'
}
