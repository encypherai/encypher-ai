# TEAM_241 - XMP In-Image Passthrough Embedding

**Session:** 2026-02-26
**Branch:** feat/image-signing-c2pa
**PRD:** PRDs/CURRENT/PRD_Image_Signing_C2PA.md

## Goal

Implement XMP provenance embedding for passthrough mode so images carry
an in-file reference (instance_id) to the Encypher DB record. This mirrors
the ZWC marker approach for text: embed an identifier inside the binary that
survives CDN re-hosting and allows hash-miss fallback during verification.

## Work Done

### 1. app/utils/image_utils.py - XMP inject/extract

Added stdlib-only XMP functions (struct, zlib, xml.etree.ElementTree):

- `_build_xmp_packet()` - builds XMP packet with Encypher namespace fields
- `inject_encypher_xmp()` - public entry: dispatches to JPEG/PNG helpers
- `extract_encypher_xmp()` - public entry: dispatches to JPEG/PNG helpers
- `_jpeg_inject_xmp()` - inserts APP1 segment after SOI marker
- `_jpeg_extract_xmp()` - scans APP1 segments for XMP header
- `_png_inject_xmp()` - inserts iTXt chunk after IHDR (offset 33)
- `_png_extract_xmp()` - scans iTXt chunks for adobe.xmp keyword
- `_parse_encypher_xmp()` - parses XML, returns Encypher namespace attrs

No new deps. WebP/TIFF return original bytes unchanged.

### 2. app/services/image_signing_service.py - Passthrough block

Updated passthrough branch to:
1. Generate `instance_id = "urn:uuid:" + uuid4()`
2. Call `inject_encypher_xmp()` to embed XMP into clean_bytes
3. Compute `signed_hash = compute_sha256(embedded_bytes)`
4. Return `signed_bytes=embedded_bytes` with `signed_hash != original_hash`

Previously: signed_hash == original_hash (no modification).
Now: signed_hash != original_hash (XMP bytes appended inside image).

### 3. app/api/v1/image_verify.py - XMP fallback lookup

After exact hash lookup misses, extract XMP from submitted image bytes,
look up ArticleImage by `c2pa_instance_id`, and set `effective_valid = True`
if DB record found. Returns `valid=True` for passthrough images where the
hash may differ (e.g. after re-encode by CDN).

### 4. tests/unit/test_image_utils.py - New XMP tests

Added `TestEnchypherXmp` class with 6 tests:
- `test_jpeg_roundtrip` - inject then extract, verify all fields match
- `test_png_roundtrip` - same for PNG
- `test_inject_changes_bytes` - sha256 of embedded != original
- `test_extract_returns_none_on_no_xmp` - clean JPEG returns None
- `test_inject_on_unsupported_mime_returns_original` - WebP passthrough
- `test_inject_error_returns_original` - garbage bytes: no raise, returns original

### 5. tests/e2e_local/test_rich_sign_passthrough.py - Assertion updates

3 updated assertions:
- `test_passthrough_returns_exif_stripped_bytes` line ~108:
  `signed_hash == original_hash` -> `signed_hash != original_hash`
- `test_passthrough_strips_exif` line ~133:
  `original_hash == compute_sha256(signed_bytes)` -> `signed_hash == compute_sha256(signed_bytes)`
- `test_sign_rich_then_verify_image` line ~314:
  `valid is False` -> `valid is True` (XMP lookup now confirms provenance)

2 new tests:
- `test_passthrough_image_has_encypher_xmp` - JPEG: XMP fields match sign result
- `test_passthrough_png_has_encypher_xmp` - PNG: same

## Phase 2: Marketing Site Image Inspection (same session)

### Changes
- `apps/marketing-site/src/lib/fileInspector.ts`: split extensions/MIME types
  into text + image sets; added `isImageFile()`, `IMAGE_MAX_SIZE_BYTES` (10 MB),
  updated `isTextFile()` to exclude images, `validateFile()` for per-type limits
- `apps/marketing-site/src/app/api/tools/verify-image/route.ts`: new Next.js
  API route proxying POST {image_data, mime_type} to enterprise /api/v1/verify/image
  with 14 MB limit and trace headers
- `apps/marketing-site/src/components/tools/FileInspectorTool.tsx`: image
  detection, ImageVerifyResult component (green/red banner, image_id, document_id,
  SHA-256, verified_at, image preview panel), file info bar thumbnail
- `apps/marketing-site/src/app/tools/inspect/page.tsx`: SEO metadata for images
- `infrastructure/traefik/routes-local.yml`: added verify-image-router (priority
  110) -> enterprise-api; prevents capture by verify-router (priority 100) ->
  verification-service which lacks the endpoint

### Test Results
- 44/44 fileInspector tests passing
- Puppeteer e2e verified:
  - plain JPEG: "No Provenance Found" (red banner) OK
  - XMP-signed JPEG with DB record: "Provenance Verified" (green banner,
    all fields: image_id, document_id, SHA-256, verified_at) OK
- Both commits pushed to origin/feat/image-signing-c2pa

## Suggested Commit Message

```
feat(enterprise-api): XMP in-image provenance embedding for passthrough mode

Passthrough mode previously EXIF-stripped images and returned them with no
in-file provenance. Now injects Encypher XMP (ISO 16684) using stdlib only
(struct + zlib + xml.etree.ElementTree) for JPEG (APP1 segment) and PNG
(iTXt chunk). The embedded instance_id matches the ArticleImage DB record
and is used as a fallback lookup key in /verify/image when the signed_hash
differs (e.g. after CDN re-encode).

Changes:
- app/utils/image_utils.py: add inject_encypher_xmp / extract_encypher_xmp
  and private _jpeg_*/_png_*/_build_xmp_packet/_parse_encypher_xmp helpers
- app/services/image_signing_service.py: passthrough block now calls
  inject_encypher_xmp and returns signed_hash != original_hash
- app/api/v1/image_verify.py: XMP fallback lookup by instance_id after
  hash miss; effective_valid = result.valid OR db_confirmed
- tests/unit/test_image_utils.py: add TestEnchypherXmp (6 unit tests)
- tests/e2e_local/test_rich_sign_passthrough.py: update 3 assertions,
  add 2 new XMP verification tests

No new deps (stdlib only). WebP/TIFF unsupported (return unchanged).
```
