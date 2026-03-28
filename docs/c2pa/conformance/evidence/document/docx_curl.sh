#!/usr/bin/env bash
# DOCX -- C2PA Conformance Verification
# MIME type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
# Endpoint: POST /api/v1/public/verify/media (public, no auth required)
# Note: Pipeline B (custom JUMBF/COSE)
#
# Usage:
#   cd <submission-directory>
#   bash evidence/document/docx_curl.sh
#
# Or set SAMPLES to the generator_samples path:
#   SAMPLES=./generator_samples bash evidence/document/docx_curl.sh

set -euo pipefail

SAMPLES="${SAMPLES:-./generator_samples}"
FILE="${SAMPLES}/document/docx/signed_test.docx"

if [ ! -f "$FILE" ]; then
  echo "ERROR: Signed sample not found: $FILE"
  echo "Set SAMPLES to the generator_samples directory path."
  exit 1
fi

echo "Verifying DOCX (application/vnd.openxmlformats-officedocument.wordprocessingml.document)..."
echo "File: $FILE"
echo ""

curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${FILE};type=application/vnd.openxmlformats-officedocument.wordprocessingml.document" \
  -F "mime_type=application/vnd.openxmlformats-officedocument.wordprocessingml.document" | python3 -m json.tool

echo ""
echo "Done."
