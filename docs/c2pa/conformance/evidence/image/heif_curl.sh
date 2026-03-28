#!/usr/bin/env bash
# HEIF -- C2PA Conformance Verification
# MIME type: image/heif
# Endpoint: POST /api/v1/public/verify/media (public, no auth required)
#
# Usage:
#   cd <submission-directory>
#   bash evidence/image/heif_curl.sh
#
# Or set SAMPLES to the generator_samples path:
#   SAMPLES=./generator_samples bash evidence/image/heif_curl.sh

set -euo pipefail

SAMPLES="${SAMPLES:-./generator_samples}"
FILE="${SAMPLES}/image/heif/signed_test.heif"

if [ ! -f "$FILE" ]; then
  echo "ERROR: Signed sample not found: $FILE"
  echo "Set SAMPLES to the generator_samples directory path."
  exit 1
fi

echo "Verifying HEIF (image/heif)..."
echo "File: $FILE"
echo ""

curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${FILE};type=image/heif" \
  -F "mime_type=image/heif" | python3 -m json.tool

echo ""
echo "Done."
