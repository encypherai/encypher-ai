#!/usr/bin/env bash
# EPUB -- C2PA Conformance Verification
# MIME type: application/epub+zip
# Endpoint: POST /api/v1/public/verify/media (public, no auth required)
# Note: Pipeline B (custom JUMBF/COSE)
#
# Usage:
#   cd <submission-directory>
#   bash evidence/document/epub_curl.sh
#
# Or set SAMPLES to the generator_samples path:
#   SAMPLES=./generator_samples bash evidence/document/epub_curl.sh

set -euo pipefail

SAMPLES="${SAMPLES:-./generator_samples}"
FILE="${SAMPLES}/document/epub/signed_test.epub"

if [ ! -f "$FILE" ]; then
  echo "ERROR: Signed sample not found: $FILE"
  echo "Set SAMPLES to the generator_samples directory path."
  exit 1
fi

echo "Verifying EPUB (application/epub+zip)..."
echo "File: $FILE"
echo ""

curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${FILE};type=application/epub+zip" \
  -F "mime_type=application/epub+zip" | python3 -m json.tool

echo ""
echo "Done."
