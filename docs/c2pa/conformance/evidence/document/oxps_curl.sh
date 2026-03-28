#!/usr/bin/env bash
# OXPS -- C2PA Conformance Verification
# MIME type: application/oxps
# Endpoint: POST /api/v1/public/verify/media (public, no auth required)
# Note: Pipeline B (custom JUMBF/COSE)
#
# Usage:
#   cd <submission-directory>
#   bash evidence/document/oxps_curl.sh
#
# Or set SAMPLES to the generator_samples path:
#   SAMPLES=./generator_samples bash evidence/document/oxps_curl.sh

set -euo pipefail

SAMPLES="${SAMPLES:-./generator_samples}"
FILE="${SAMPLES}/document/oxps/signed_test.oxps"

if [ ! -f "$FILE" ]; then
  echo "ERROR: Signed sample not found: $FILE"
  echo "Set SAMPLES to the generator_samples directory path."
  exit 1
fi

echo "Verifying OXPS (application/oxps)..."
echo "File: $FILE"
echo ""

curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${FILE};type=application/oxps" \
  -F "mime_type=application/oxps" | python3 -m json.tool

echo ""
echo "Done."
