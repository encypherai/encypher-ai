# C2PA Conformance -- CURL Verification Examples

Reproducible curl commands for C2PA conformance reviewers to independently verify
every signed sample in the Encypher submission package.

## Prerequisites

```bash
# All signed samples are in the generator_samples/ directory of the submission.
# Set this to your local path to the extracted submission:
export SAMPLES="./generator_samples"

# Conformance API key (required only for text signing, not media verification):
export ENCYPHER_API_KEY="your-api-key-here"
```

## Verification Endpoint

All media verification uses a single public endpoint (no authentication required):

```
POST https://api.encypher.com/api/v1/public/verify/media
Content-Type: multipart/form-data
Fields: file (binary), mime_type (string)
```

Text verification uses:

```
POST https://api.encypher.com/api/v1/public/verify
Content-Type: application/json
Body: {"text": "<signed text>"}
```

---

## Image Formats

### JPEG (image/jpeg)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/image/jpeg/signed_test.jpg;type=image/jpeg" \
  -F "mime_type=image/jpeg" | python3 -m json.tool
```

### PNG (image/png)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/image/png/signed_test.png;type=image/png" \
  -F "mime_type=image/png" | python3 -m json.tool
```

### WebP (image/webp)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/image/webp/signed_test.webp;type=image/webp" \
  -F "mime_type=image/webp" | python3 -m json.tool
```

### GIF (image/gif)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/image/gif/signed_test.gif;type=image/gif" \
  -F "mime_type=image/gif" | python3 -m json.tool
```

### TIFF (image/tiff)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/image/tiff/signed_test.tiff;type=image/tiff" \
  -F "mime_type=image/tiff" | python3 -m json.tool
```

### AVIF (image/avif)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/image/avif/signed_test.avif;type=image/avif" \
  -F "mime_type=image/avif" | python3 -m json.tool
```

### HEIC (image/heic)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/image/heic/signed_test.heic;type=image/heic" \
  -F "mime_type=image/heic" | python3 -m json.tool
```

### HEIF (image/heif)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/image/heif/signed_test.heif;type=image/heif" \
  -F "mime_type=image/heif" | python3 -m json.tool
```

### DNG (image/x-adobe-dng)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/image/dng/signed_test.dng;type=image/x-adobe-dng" \
  -F "mime_type=image/x-adobe-dng" | python3 -m json.tool
```

### SVG (image/svg+xml)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/image/svg/signed_test.svg;type=image/svg+xml" \
  -F "mime_type=image/svg+xml" | python3 -m json.tool
```

### JPEG XL (image/jxl) -- Pipeline B
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/image/jxl/signed_test.jxl;type=image/jxl" \
  -F "mime_type=image/jxl" | python3 -m json.tool
```

### HEIC Sequence (image/heic)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/image/heic-sequence/signed_test_heic-sequence.heic;type=image/heic" \
  -F "mime_type=image/heic" | python3 -m json.tool
```

### HEIF Sequence (image/heif)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/image/heif-sequence/signed_test_heif-sequence.heif;type=image/heif" \
  -F "mime_type=image/heif" | python3 -m json.tool
```

---

## Audio Formats

### WAV (audio/wav)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/audio/wav/signed_test.wav;type=audio/wav" \
  -F "mime_type=audio/wav" | python3 -m json.tool
```

### MP3 / MPEG (audio/mpeg)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/audio/mpeg/signed_test.mp3;type=audio/mpeg" \
  -F "mime_type=audio/mpeg" | python3 -m json.tool
```

### MP3 / MPA alias (audio/mpa)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/audio/mpa/signed_test_mpa.mp3;type=audio/mpeg" \
  -F "mime_type=audio/mpeg" | python3 -m json.tool
```

### M4A (audio/mp4)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/audio/mp4/signed_test.m4a;type=audio/mp4" \
  -F "mime_type=audio/mp4" | python3 -m json.tool
```

### AAC (audio/aac)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/audio/aac/signed_test_aac.m4a;type=audio/mp4" \
  -F "mime_type=audio/mp4" | python3 -m json.tool
```

### FLAC (audio/flac) -- Pipeline B
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/audio/flac/signed_test.flac;type=audio/flac" \
  -F "mime_type=audio/flac" | python3 -m json.tool
```

---

## Video Formats

### MP4 (video/mp4)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/video/mp4/signed_test.mp4;type=video/mp4" \
  -F "mime_type=video/mp4" | python3 -m json.tool
```

### MOV / QuickTime (video/quicktime)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/video/quicktime/signed_test.mov;type=video/quicktime" \
  -F "mime_type=video/quicktime" | python3 -m json.tool
```

### AVI (video/x-msvideo)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/video/avi/signed_test.avi;type=video/x-msvideo" \
  -F "mime_type=video/x-msvideo" | python3 -m json.tool
```

---

## Document Formats -- Pipeline B

### PDF (application/pdf)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/document/pdf/signed_test.pdf;type=application/pdf" \
  -F "mime_type=application/pdf" | python3 -m json.tool
```

### EPUB (application/epub+zip)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/document/epub/signed_test.epub;type=application/epub+zip" \
  -F "mime_type=application/epub+zip" | python3 -m json.tool
```

### DOCX (application/vnd.openxmlformats-officedocument.wordprocessingml.document)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/document/docx/signed_test.docx;type=application/vnd.openxmlformats-officedocument.wordprocessingml.document" \
  -F "mime_type=application/vnd.openxmlformats-officedocument.wordprocessingml.document" | python3 -m json.tool
```

### ODT (application/vnd.oasis.opendocument.text)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/document/odt/signed_test.odt;type=application/vnd.oasis.opendocument.text" \
  -F "mime_type=application/vnd.oasis.opendocument.text" | python3 -m json.tool
```

### OXPS (application/oxps)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/document/oxps/signed_test.oxps;type=application/oxps" \
  -F "mime_type=application/oxps" | python3 -m json.tool
```

---

## Font Formats -- Pipeline B

### OTF (font/otf)
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@${SAMPLES}/font/otf/signed_test.otf;type=font/otf" \
  -F "mime_type=font/otf" | python3 -m json.tool
```

---

## Text (Extended Capability)

### Sign text content
```bash
curl -s -X POST https://api.encypher.com/api/v1/sign \
  -H "Authorization: Bearer ${ENCYPHER_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"text": "Content to sign with provenance metadata"}' | python3 -m json.tool
```

### Verify signed text
```bash
curl -s -X POST https://api.encypher.com/api/v1/public/verify \
  -H "Content-Type: application/json" \
  -d '{"text": "<paste signed text with embedded ZWC metadata>"}' | python3 -m json.tool
```

---

## Batch Verification Script

Run all verifications in sequence and report pass/fail:

```bash
#!/usr/bin/env bash
set -euo pipefail

SAMPLES="${1:-.}/generator_samples"
API="https://api.encypher.com/api/v1/public/verify/media"
PASS=0; FAIL=0

verify() {
  local file="$1" mime="$2" label="$3"
  result=$(curl -s -X POST "$API" \
    -F "file=@${file};type=${mime}" \
    -F "mime_type=${mime}")
  valid=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('valid',''))" 2>/dev/null)
  if [ "$valid" = "True" ]; then
    echo "  PASS  $label ($mime)"
    ((PASS++))
  else
    echo "  FAIL  $label ($mime)"
    echo "        $result" | head -c 200
    echo
    ((FAIL++))
  fi
}

echo "=== Encypher C2PA Conformance Verification ==="
echo ""

echo "-- Images --"
verify "$SAMPLES/image/jpeg/signed_test.jpg"     "image/jpeg"         "JPEG"
verify "$SAMPLES/image/png/signed_test.png"       "image/png"          "PNG"
verify "$SAMPLES/image/webp/signed_test.webp"     "image/webp"         "WebP"
verify "$SAMPLES/image/gif/signed_test.gif"       "image/gif"          "GIF"
verify "$SAMPLES/image/tiff/signed_test.tiff"     "image/tiff"         "TIFF"
verify "$SAMPLES/image/avif/signed_test.avif"     "image/avif"         "AVIF"
verify "$SAMPLES/image/heic/signed_test.heic"     "image/heic"         "HEIC"
verify "$SAMPLES/image/heif/signed_test.heif"     "image/heif"         "HEIF"
verify "$SAMPLES/image/dng/signed_test.dng"       "image/x-adobe-dng"  "DNG"
verify "$SAMPLES/image/svg/signed_test.svg"       "image/svg+xml"      "SVG"
verify "$SAMPLES/image/jxl/signed_test.jxl"       "image/jxl"          "JPEG XL"

echo ""
echo "-- Audio --"
verify "$SAMPLES/audio/wav/signed_test.wav"       "audio/wav"    "WAV"
verify "$SAMPLES/audio/mpeg/signed_test.mp3"      "audio/mpeg"   "MP3"
verify "$SAMPLES/audio/mp4/signed_test.m4a"       "audio/mp4"    "M4A"
verify "$SAMPLES/audio/aac/signed_test_aac.m4a"   "audio/mp4"    "AAC"
verify "$SAMPLES/audio/flac/signed_test.flac"     "audio/flac"   "FLAC"

echo ""
echo "-- Video --"
verify "$SAMPLES/video/mp4/signed_test.mp4"             "video/mp4"        "MP4"
verify "$SAMPLES/video/quicktime/signed_test.mov"       "video/quicktime"  "MOV"
verify "$SAMPLES/video/avi/signed_test.avi"             "video/x-msvideo"  "AVI"

echo ""
echo "-- Documents --"
verify "$SAMPLES/document/pdf/signed_test.pdf"     "application/pdf"                                                              "PDF"
verify "$SAMPLES/document/epub/signed_test.epub"   "application/epub+zip"                                                         "EPUB"
verify "$SAMPLES/document/docx/signed_test.docx"   "application/vnd.openxmlformats-officedocument.wordprocessingml.document"       "DOCX"
verify "$SAMPLES/document/odt/signed_test.odt"     "application/vnd.oasis.opendocument.text"                                      "ODT"
verify "$SAMPLES/document/oxps/signed_test.oxps"   "application/oxps"                                                             "OXPS"

echo ""
echo "-- Fonts --"
verify "$SAMPLES/font/otf/signed_test.otf"         "font/otf"     "OTF"

echo ""
echo "=== Results: ${PASS} passed, ${FAIL} failed ==="
```

---

## Expected Response

A successful verification returns:

```json
{
  "success": true,
  "valid": true,
  "tampered": false,
  "reason_code": "VALID_SIGNATURE",
  "media_type": "<mime-type>",
  "verified_at": "<ISO-8601 timestamp>",
  "content": {
    "hash_verified": true,
    "c2pa_manifest_valid": true,
    "c2pa_instance_id": "urn:uuid:<...>",
    "manifest_data": { ... }
  }
}
```

### Notes for reviewers

- **No authentication required** for verification -- all `/verify/media` calls are public.
- **`timeStamp.untrusted`** in validation results is expected. The conformance test
  certificate is not enrolled on the C2PA trust list; the timestamp from SSL.com's TSA
  is cryptographically valid but not yet trust-anchored.
- **Pipeline A** (c2pa-rs): images (except JXL), audio (except FLAC), video.
- **Pipeline B** (custom JUMBF/COSE): PDF, EPUB, DOCX, ODT, OXPS, OTF, FLAC, JXL.
  Both pipelines verify through the same unified endpoint.
