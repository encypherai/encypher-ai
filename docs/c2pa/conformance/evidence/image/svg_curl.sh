#!/usr/bin/env bash
# SVG -- C2PA Conformance Verification
# MIME type: image/svg+xml
# Endpoint: POST /api/v1/public/verify/media (public, no auth required)
#
# Usage:
#   cd <submission-directory>
#   bash evidence/image/svg_curl.sh
#
# Or set SAMPLES to the generator_samples path:
#   SAMPLES=./generator_samples bash evidence/image/svg_curl.sh

set -euo pipefail

SAMPLES="${SAMPLES:-./generator_samples}"
FILE="${SAMPLES}/image/svg/signed_test.svg"

if [ ! -f "$FILE" ]; then
  echo "ERROR: Signed sample not found: $FILE"
  echo "Set SAMPLES to the generator_samples directory path."
  exit 1
fi

echo "Verifying SVG (image/svg+xml)..."
echo "File: $FILE"
echo ""

curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${FILE};type=image/svg+xml" \
  -F "mime_type=image/svg+xml" | python3 -m json.tool

echo ""
echo "Done."
