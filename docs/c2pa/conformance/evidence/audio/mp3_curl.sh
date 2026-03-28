#!/usr/bin/env bash
# MP3 -- C2PA Conformance Verification
# MIME type: audio/mpeg
# Endpoint: POST /api/v1/public/verify/media (public, no auth required)
#
# Usage:
#   cd <submission-directory>
#   bash evidence/audio/mp3_curl.sh
#
# Or set SAMPLES to the generator_samples path:
#   SAMPLES=./generator_samples bash evidence/audio/mp3_curl.sh

set -euo pipefail

SAMPLES="${SAMPLES:-./generator_samples}"
FILE="${SAMPLES}/audio/mpeg/signed_test.mp3"

if [ ! -f "$FILE" ]; then
  echo "ERROR: Signed sample not found: $FILE"
  echo "Set SAMPLES to the generator_samples directory path."
  exit 1
fi

echo "Verifying MP3 (audio/mpeg)..."
echo "File: $FILE"
echo ""

curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${FILE};type=audio/mpeg" \
  -F "mime_type=audio/mpeg" | python3 -m json.tool

echo ""
echo "Done."
