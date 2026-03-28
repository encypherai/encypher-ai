#!/usr/bin/env bash
# M4V -- C2PA Conformance Verification
# MIME type: video/x-m4v
# Endpoint: POST /api/v1/public/verify/media (public, no auth required)
#
# Note: M4V is not included in the conformance submission generator_samples.
# This script verifies against the internal signed test file.
# To use with a local M4V sample, set FILE directly:
#   FILE=./my_signed.m4v bash evidence/video/m4v_curl.sh

set -euo pipefail

FILE="${FILE:-}"

if [ -z "$FILE" ]; then
  echo "ERROR: M4V not in generator_samples. Set FILE to a signed M4V path."
  echo "  FILE=./signed_test.m4v bash evidence/video/m4v_curl.sh"
  exit 1
fi

echo "Verifying M4V (video/x-m4v)..."
echo "File: $FILE"
echo ""

curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${FILE};type=video/x-m4v" \
  -F "mime_type=video/x-m4v" | python3 -m json.tool

echo ""
echo "Done."
