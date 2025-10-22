# Example script to demonstrate the audit_log_cli functionality
# with the shared commercial library

# Navigate to the audit_log_cli directory
Set-Location -Path $PSScriptRoot\..\audit_log_cli

# Ensure we're using the virtual environment
if (-not (Test-Path -Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    uv venv
}

# Activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
.\.venv\Scripts\Activate.ps1

# Install dependencies if needed
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    uv pip sync
}

# Create a directory for trusted signers (for demonstration)
$TrustedSignersDir = "$PSScriptRoot\trusted_signers"
if (-not (Test-Path -Path $TrustedSignersDir)) {
    Write-Host "Creating trusted signers directory..." -ForegroundColor Yellow
    New-Item -Path $TrustedSignersDir -ItemType Directory | Out-Null
    
    # Note: In a real scenario, you would place actual PEM files here
    # This is just for demonstration purposes
    "# Example public key file" | Out-File -FilePath "$TrustedSignersDir\example-signer.pem"
}

# Run the audit_log_cli to scan the sample file
Write-Host "Running audit_log_cli to scan sample file..." -ForegroundColor Cyan
uv run python app/main.py generate-report `
    --target "$PSScriptRoot\sample_with_metadata.txt" `
    --trusted-signers "$TrustedSignersDir" `
    --output "$PSScriptRoot\audit_report.csv" `
    --verbose

# Display the generated report
if (Test-Path -Path "$PSScriptRoot\audit_report.csv") {
    Write-Host "`nGenerated audit report:" -ForegroundColor Green
    Get-Content -Path "$PSScriptRoot\audit_report.csv"
}

# Deactivate the virtual environment
deactivate

Write-Host "`nExample completed. See $PSScriptRoot\audit_report.csv for results." -ForegroundColor Green
