#!/usr/bin/env bash
# FLAC -- C2PA Conformance Verification
# MIME type: audio/flac
# Endpoint: POST /api/v1/public/verify/media (public, no auth required)
# Note: Pipeline B (custom JUMBF/COSE)
#
# Usage:
#   cd <submission-directory>
#   bash evidence/audio/flac_curl.sh
#
# Or set SAMPLES to the generator_samples path:
#   SAMPLES=./generator_samples bash evidence/audio/flac_curl.sh

set -euo pipefail

SAMPLES="${SAMPLES:-./generator_samples}"
FILE="${SAMPLES}/audio/flac/signed_test.flac"

if [ ! -f "$FILE" ]; then
  echo "ERROR: Signed sample not found: $FILE"
  echo "Set SAMPLES to the generator_samples directory path."
  exit 1
fi

echo "Verifying FLAC (audio/flac)..."
echo "File: $FILE"
echo ""

curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${FILE};type=audio/flac" \
  -F "mime_type=audio/flac" | python3 -m json.tool

echo ""
echo "Done."
