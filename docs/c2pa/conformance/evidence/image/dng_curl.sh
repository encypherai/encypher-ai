#!/usr/bin/env bash
# DNG -- C2PA Conformance Verification
# MIME type: image/x-adobe-dng
# Endpoint: POST /api/v1/public/verify/media (public, no auth required)
#
# Usage:
#   cd <submission-directory>
#   bash evidence/image/dng_curl.sh
#
# Or set SAMPLES to the generator_samples path:
#   SAMPLES=./generator_samples bash evidence/image/dng_curl.sh

set -euo pipefail

SAMPLES="${SAMPLES:-./generator_samples}"
FILE="${SAMPLES}/image/dng/signed_test.dng"

if [ ! -f "$FILE" ]; then
  echo "ERROR: Signed sample not found: $FILE"
  echo "Set SAMPLES to the generator_samples directory path."
  exit 1
fi

echo "Verifying DNG (image/x-adobe-dng)..."
echo "File: $FILE"
echo ""

curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${FILE};type=image/x-adobe-dng" \
  -F "mime_type=image/x-adobe-dng" | python3 -m json.tool

echo ""
echo "Done."
