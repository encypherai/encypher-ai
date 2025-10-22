# Setup development environment for EncypherAI Commercial projects
# This script initializes projects and ensures dependencies are properly installed

# Function to set up a project
function Initialize-Project {
    param (
        [string]$ProjectPath,
        [string]$ProjectName
    )
    
    Write-Host "`n===== Setting up $ProjectName =====" -ForegroundColor Cyan
    
    # Navigate to the project directory
    Set-Location -Path $ProjectPath
    
    # Check if pyproject.toml exists
    if (-not (Test-Path -Path "pyproject.toml")) {
        Write-Host "Error: pyproject.toml not found in $ProjectPath" -ForegroundColor Red
        return
    }
    
    # Create/update the lockfile
    Write-Host "Creating/updating lockfile..." -ForegroundColor Yellow
    uv lock
    
    # Sync the environment with the lockfile
    # This will automatically create the virtual environment if it doesn't exist
    Write-Host "Syncing environment with lockfile..." -ForegroundColor Yellow
    uv sync
    
    # Install the package in development mode
    Write-Host "Installing package in development mode..." -ForegroundColor Yellow
    uv pip install -e .
    
    # Display environment information
    Write-Host "Project environment ready!" -ForegroundColor Green
    
    # Show how to activate and use the environment
    Write-Host "To activate this environment:" -ForegroundColor Cyan
    Write-Host "  cd $ProjectPath" -ForegroundColor White
    Write-Host "  .venv\Scripts\Activate.ps1" -ForegroundColor White
    
    Write-Host "To run commands in this environment:" -ForegroundColor Cyan
    Write-Host "  uv run -- <command>" -ForegroundColor White
    Write-Host "  # For example: uv run -- pytest" -ForegroundColor White
    
    Write-Host "$ProjectName setup complete!" -ForegroundColor Green
}

# Get the root directory of the repository
$RepoRoot = Split-Path -Parent $PSScriptRoot

# First, initialize the workspace at the root level
Write-Host "`n===== Setting up Workspace Root =====" -ForegroundColor Cyan
Set-Location -Path $RepoRoot

# Update the lockfile for the entire workspace
Write-Host "Creating/updating workspace lockfile..." -ForegroundColor Yellow
uv lock

# Sync the entire workspace
Write-Host "Syncing workspace environment..." -ForegroundColor Yellow
uv sync

# Initialize shared commercial library first
Initialize-Project -ProjectPath "$RepoRoot\shared_commercial_libs" -ProjectName "Shared Commercial Library"

# Initialize audit log CLI
Initialize-Project -ProjectPath "$RepoRoot\audit_log_cli" -ProjectName "Audit Log CLI"

# Return to the repository root
Set-Location -Path $RepoRoot

Write-Host "`n===== Development Environment Setup Complete =====" -ForegroundColor Green
Write-Host "You can now activate the virtual environment in each project directory using:"
Write-Host "  cd <project_directory>"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "`nTo install the shared library in development mode for the CLI tool:"
Write-Host "  cd audit_log_cli"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  uv pip install -e ..\shared_commercial_libs"
Write-Host "`nTo run commands without activating the environment:"
Write-Host "  cd <project_directory>"
Write-Host "  uv run -- <command>"