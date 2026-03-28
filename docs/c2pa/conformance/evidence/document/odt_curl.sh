#!/usr/bin/env bash
# ODT -- C2PA Conformance Verification
# MIME type: application/vnd.oasis.opendocument.text
# Endpoint: POST /api/v1/public/verify/media (public, no auth required)
# Note: Pipeline B (custom JUMBF/COSE)
#
# Usage:
#   cd <submission-directory>
#   bash evidence/document/odt_curl.sh
#
# Or set SAMPLES to the generator_samples path:
#   SAMPLES=./generator_samples bash evidence/document/odt_curl.sh

set -euo pipefail

SAMPLES="${SAMPLES:-./generator_samples}"
FILE="${SAMPLES}/document/odt/signed_test.odt"

if [ ! -f "$FILE" ]; then
  echo "ERROR: Signed sample not found: $FILE"
  echo "Set SAMPLES to the generator_samples directory path."
  exit 1
fi

echo "Verifying ODT (application/vnd.oasis.opendocument.text)..."
echo "File: $FILE"
echo ""

curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${FILE};type=application/vnd.oasis.opendocument.text" \
  -F "mime_type=application/vnd.oasis.opendocument.text" | python3 -m json.tool

echo ""
echo "Done."
