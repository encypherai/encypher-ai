#!/usr/bin/env bash
# TIFF -- C2PA Conformance Verification
# MIME type: image/tiff
# Endpoint: POST /api/v1/public/verify/media (public, no auth required)
#
# Usage:
#   cd <submission-directory>
#   bash evidence/image/tiff_curl.sh
#
# Or set SAMPLES to the generator_samples path:
#   SAMPLES=./generator_samples bash evidence/image/tiff_curl.sh

set -euo pipefail

SAMPLES="${SAMPLES:-./generator_samples}"
FILE="${SAMPLES}/image/tiff/signed_test.tiff"

if [ ! -f "$FILE" ]; then
  echo "ERROR: Signed sample not found: $FILE"
  echo "Set SAMPLES to the generator_samples directory path."
  exit 1
fi

echo "Verifying TIFF (image/tiff)..."
echo "File: $FILE"
echo ""

curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${FILE};type=image/tiff" \
  -F "mime_type=image/tiff" | python3 -m json.tool

echo ""
echo "Done."
