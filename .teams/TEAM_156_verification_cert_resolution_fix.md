# TEAM_156: Verification Service — Full C2PA + ZW Verification Fix + PDF Rendering

## Status: COMPLETE ✅

## Goal
Fix all verification failures for signed PDFs via the marketing site inspect tool,
fix PDF rendering quality, and display org name in signer info.

## Completed Fixes

### Phase 1: CERT_NOT_FOUND + SIGNER_UNKNOWN
- Fix `ENTERPRISE_API_URL` default to `http://localhost:9000`
- Two-path trust anchor resolution + ZW DB fallback
- Extract `signer_id` from JUMBF manifest store for minimal mode

### Phase 2: SIGNATURE_INVALID (hard binding hash mismatch)
Root cause: PDF text extraction via `pdfjs-dist` operator list is lossy.

**Fix (multi-layered):**
1. **encypher-pdf writer**: Embed original signed text as uncompressed `EncypherSignedText` metadata stream in PDF catalog
2. **Client-side extractor** (`pdfTextExtractor.ts`): Extract from `EncypherSignedText` stream, fallback to operator-list. Fixed SWC double-escaping of `\n` by using `Uint8Array` byte literal.
3. **Server-side extractor** (`pdfTextExtractorServer.ts`): NEW — Node.js extraction of `EncypherSignedText` stream, immune to browser JS caching
4. **Verify route** (`route.ts`): Accept `pdf_base64` from browser, extract text server-side, forward lossless text to verification service
5. **Browser component** (`FileInspectorTool.tsx`): Send raw PDF bytes as base64 alongside client-extracted text

### Phase 3: Signer name display
- `_fetch_trust_anchor` returns `(public_key_pem, signer_name)` tuple
- `VerifyVerdict.signer_name` priority: authenticated org name → trust anchor name → signer_id
- `organization_name` populated from trust anchor for unauthenticated requests

### Phase 4: PDF rendering quality
Root cause: CIDFont W array widths were in font design units (2048) instead of
PDF's 1000-unit coordinate system, causing pdf.js to render ~2x wider letter-spacing.

**Fixes:**
1. **W array scaling** (`font.py`): Scale widths from `units_per_em` to 1000-unit system
2. **TJ array operator** (`writer.py`): Use `[<hex> <hex>] TJ` instead of multiple `<hex> Tj` to avoid micro-spacing between separate text-showing operations
3. **Style map** (`renderer.py`): Apply proper visual styles (title, heading, body, etc.) to signed text paragraphs based on Paper structure, while keeping content byte-identical for C2PA

### Phase 5: CONTENT_DB_NOT_READY soft check
- `content_references` lookup is now a soft check — log warning and fall through to trust anchor resolution instead of hard-failing

## Test Results
- **encypher-pdf**: 19/19 ✅
- **xml-to-pdf**: 48/48 ✅
- **marketing-site**: 82/82 ✅
- **verification-service**: 40/40 ✅
- **curl e2e**: all 3 PDF types verify OK ✅
- **signer_name**: "Demo Organization" ✅

## Files Modified
### verification-service
- `app/core/config.py` — Fix ENTERPRISE_API_URL default
- `app/api/v1/endpoints.py` — Trust anchor resolution, ZW fallback, JUMBF signer_id, signer_name from trust anchor, soft content_references check
- `app/utils/zw_detect.py` — NEW: ZW detection
- `tests/test_zw_detect.py` — NEW: 10 tests
- `tests/test_verify_zw_fallback.py` — NEW: 3 tests
- `tests/test_verify_minimal_uuid_public.py` — Updated for soft-check behavior

### encypher-pdf
- `src/encypher_pdf/writer.py` — TJ array operator, EncypherSignedText stream
- `src/encypher_pdf/font.py` — Scale W array widths to 1000-unit coordinate system
- `tests/test_unicode_roundtrip.py` — Handle TJ array in CID counter

### xml-to-pdf
- `src/xml_to_pdf/renderer.py` — Style map for signed text paragraphs
- `tests/test_renderer.py` — Handle TJ array in CID counter

### marketing-site
- `src/lib/pdfTextExtractor.ts` — Client-side EncypherSignedText extraction + SWC fix
- `src/lib/pdfTextExtractorServer.ts` — NEW: Server-side extraction
- `src/lib/pdfTextExtractor.test.ts` — NEW: 11 tests
- `src/lib/pdfTextExtractorServer.test.ts` — NEW: 9 tests
- `src/app/api/tools/verify/route.ts` — Accept pdf_base64, server-side extraction
- `src/components/tools/FileInspectorTool.tsx` — Send pdf_base64 for PDFs
