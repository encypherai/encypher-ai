$ErrorActionPreference = "Stop"

Write-Host "Setting up local HTTPS environment..." -ForegroundColor Green

# 1. Ensure bin directory exists
if (-not (Test-Path ".\bin")) {
    New-Item -ItemType Directory -Path ".\bin" | Out-Null
}

# 2. Check/Install mkcert
$mkcert = "mkcert"
if (-not (Get-Command mkcert -ErrorAction SilentlyContinue)) {
    $mkcert = ".\bin\mkcert.exe"
    if (-not (Test-Path $mkcert)) {
        Write-Host "Downloading mkcert..."
        $url = "https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-windows-amd64.exe"
        Invoke-WebRequest -Uri $url -OutFile $mkcert
        Write-Host "mkcert downloaded."
    }
}

# 3. Install Root CA
Write-Host "Installing Root CA (may prompt for permission)..."
& $mkcert -install

# 4. Generate Certs
Write-Host "Generating certificates in ./certs..."
if (-not (Test-Path ".\certs")) {
    New-Item -ItemType Directory -Path ".\certs" | Out-Null
}

$domains = @(
    "encypherai.com",
    "*.encypherai.com",
    "localhost",
    "127.0.0.1",
    "::1"
)

& $mkcert -cert-file ".\certs\local-cert.pem" -key-file ".\certs\local-key.pem" $domains

Write-Host "Certificates generated!" -ForegroundColor Green
Write-Host "------------------------------------------------"
Write-Host "NEXT STEPS:"
Write-Host "1. Run: docker-compose -f docker-compose.https.yml up -d"
Write-Host "2. Update your 'hosts' file (C:\Windows\System32\drivers\etc\hosts) with:"
Write-Host "   127.0.0.1 s-dashboard.encypherai.com"
Write-Host "   127.0.0.1 s-www.encypherai.com"
Write-Host "   127.0.0.1 s-api.encypherai.com"
Write-Host "   127.0.0.1 encypherai.com"
Write-Host "------------------------------------------------"
