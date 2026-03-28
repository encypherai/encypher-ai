#!/usr/bin/env bash
# OTF -- C2PA Conformance Verification
# MIME type: font/otf
# Endpoint: POST /api/v1/public/verify/media (public, no auth required)
# Note: Pipeline B (custom JUMBF/COSE, SFNT C2PA table)
#
# Usage:
#   cd <submission-directory>
#   bash evidence/font/otf_curl.sh
#
# Or set SAMPLES to the generator_samples path:
#   SAMPLES=./generator_samples bash evidence/font/otf_curl.sh

set -euo pipefail

SAMPLES="${SAMPLES:-./generator_samples}"
FILE="${SAMPLES}/font/otf/signed_test.otf"

if [ ! -f "$FILE" ]; then
  echo "ERROR: Signed sample not found: $FILE"
  echo "Set SAMPLES to the generator_samples directory path."
  exit 1
fi

echo "Verifying OTF (font/otf)..."
echo "File: $FILE"
echo ""

curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${FILE};type=font/otf" \
  -F "mime_type=font/otf" | python3 -m json.tool

echo ""
echo "Done."
