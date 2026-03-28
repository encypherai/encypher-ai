#!/usr/bin/env bash
# JPEG XL -- C2PA Conformance Verification
# MIME type: image/jxl
# Endpoint: POST /api/v1/public/verify/media (public, no auth required)
# Note: Pipeline B (custom JUMBF/COSE)
#
# Usage:
#   cd <submission-directory>
#   bash evidence/image/jxl_curl.sh
#
# Or set SAMPLES to the generator_samples path:
#   SAMPLES=./generator_samples bash evidence/image/jxl_curl.sh

set -euo pipefail

SAMPLES="${SAMPLES:-./generator_samples}"
FILE="${SAMPLES}/image/jxl/signed_test.jxl"

if [ ! -f "$FILE" ]; then
  echo "ERROR: Signed sample not found: $FILE"
  echo "Set SAMPLES to the generator_samples directory path."
  exit 1
fi

echo "Verifying JPEG XL (image/jxl)..."
echo "File: $FILE"
echo ""

curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${FILE};type=image/jxl" \
  -F "mime_type=image/jxl" | python3 -m json.tool

echo ""
echo "Done."
