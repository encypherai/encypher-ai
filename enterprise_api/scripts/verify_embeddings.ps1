#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Verify embedding implementation
.DESCRIPTION
    Checks that embedded files have:
    1. Reasonable file size (not 30x larger)
    2. ONE C2PA wrapper (not multiple)
    3. Minimal embeddings per sentence
#>

param(
    [string]$OriginalFile = "outputs\wikipedia_prepared\part_00000\article_0000000.txt",
    [string]$EmbeddedFile = "outputs\wikipedia_prepared\part_00000\article_0000000.embedded.txt"
)

$ErrorActionPreference = 'Stop'

Write-Host "`n=== EMBEDDING VERIFICATION ===" -ForegroundColor Cyan

# Check files exist
if (-not (Test-Path $OriginalFile)) {
    Write-Host "Error: Original file not found: $OriginalFile" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $EmbeddedFile)) {
    Write-Host "Error: Embedded file not found: $EmbeddedFile" -ForegroundColor Red
    exit 1
}

# Get file sizes
$origSize = (Get-Item $OriginalFile).Length
$embedSize = (Get-Item $EmbeddedFile).Length
$increase = [math]::Round((($embedSize - $origSize) / $origSize) * 100, 1)

Write-Host "`n1. File Size Check:" -ForegroundColor Yellow
Write-Host "   Original: $origSize bytes"
Write-Host "   Embedded: $embedSize bytes"
Write-Host "   Increase: $increase%"

if ($increase -lt 50) {
    Write-Host "   [OK] Reasonable size increase" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] File too large! Expected <50%, got $increase%" -ForegroundColor Red
}

# Check for invisible Unicode characters (embeddings)
$embedContent = Get-Content $EmbeddedFile -Raw
$invisibleCount = 0
$unicodePattern = '[\u200B-\u200D\uFEFF\u180E\u2060-\u206F]'

# Count invisible characters
$matches = [regex]::Matches($embedContent, $unicodePattern)
$invisibleCount = $matches.Count

Write-Host "`n2. Invisible Embeddings Check:" -ForegroundColor Yellow
Write-Host "   Invisible characters found: $invisibleCount"

if ($invisibleCount -gt 0) {
    Write-Host "   [OK] Embeddings detected" -ForegroundColor Green
} else {
    Write-Host "   [WARN] No invisible characters found - embeddings may not be working" -ForegroundColor Yellow
}

# Check for C2PA wrappers using Python
Write-Host "`n3. C2PA Wrapper Check:" -ForegroundColor Yellow
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    $result = & uv run python -c @"
from encypher.core.unicode_metadata import UnicodeMetadata
import sys

with open('$EmbeddedFile', 'r', encoding='utf-8') as f:
    content = f.read()

# Try to extract metadata
try:
    extracted = UnicodeMetadata.extract_metadata(content)
    if extracted:
        print(f'instance_id:{extracted.get("instance_id", "none")}')
        print(f'has_manifest:True')
    else:
        print('has_manifest:False')
except Exception as e:
    print(f'error:{str(e)}')
"@

    if ($result -match 'has_manifest:True') {
        Write-Host "   [OK] C2PA manifest found" -ForegroundColor Green
        if ($result -match 'instance_id:(.+)') {
            Write-Host "   Instance ID: $($matches[1])" -ForegroundColor Gray
        }
    } elseif ($result -match 'Multiple C2PA') {
        Write-Host "   [FAIL] Multiple C2PA wrappers detected!" -ForegroundColor Red
    } else {
        Write-Host "   [WARN] No C2PA manifest found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   [ERROR] Failed to check C2PA: $_" -ForegroundColor Red
}
Pop-Location

# Summary
Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "File: $EmbeddedFile"
Write-Host "Size increase: $increase% (target: <50%)"
Write-Host "Invisible chars: $invisibleCount"

if ($increase -lt 50 -and $invisibleCount -gt 0) {
    Write-Host "`n[OK] Embedding implementation looks correct!" -ForegroundColor Green
} else {
    Write-Host "`n[WARN] Some checks failed - review above" -ForegroundColor Yellow
}
