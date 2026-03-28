#!/usr/bin/env bash
# AAC -- C2PA Conformance Verification
# MIME type: audio/mp4
# Endpoint: POST /api/v1/public/verify/media (public, no auth required)
# Note: AAC in MP4 container; use audio/mp4 MIME type
#
# Usage:
#   cd <submission-directory>
#   bash evidence/audio/aac_curl.sh
#
# Or set SAMPLES to the generator_samples path:
#   SAMPLES=./generator_samples bash evidence/audio/aac_curl.sh

set -euo pipefail

SAMPLES="${SAMPLES:-./generator_samples}"
FILE="${SAMPLES}/audio/aac/signed_test_aac.m4a"

if [ ! -f "$FILE" ]; then
  echo "ERROR: Signed sample not found: $FILE"
  echo "Set SAMPLES to the generator_samples directory path."
  exit 1
fi

echo "Verifying AAC (audio/mp4)..."
echo "File: $FILE"
echo ""

curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${FILE};type=audio/mp4" \
  -F "mime_type=audio/mp4" | python3 -m json.tool

echo ""
echo "Done."
