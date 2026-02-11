# TEAM_088: Marketing Site C2PA Text Embedding Compliance

## Status: Complete — Verified Spec-Compliant

## Goal
Ensure the marketing-site sign tool uses the actual C2PA-compliant `C2PATextManifestWrapper` embedding technique per the spec in `docs/c2pa/Manifests_Text.txt`.

## Verification Summary

### Marketing-site sign flow (exact path)
```
EncodeDecodeTool.tsx (provenance="" → no custom_assertions)
  → /api/tools/sign (Next.js proxy)
    → buildSignBasicRequest (options.custom_assertions = undefined)
      → enterprise API /api/v1/sign
        → _needs_advanced_signing = False (no non-default options)
          → _execute_basic_signing
            → signing_executor.execute_signing
              → UnicodeMetadata.embed_metadata(metadata_format="c2pa")
                → _embed_c2pa → encode_wrapper (c2pa_text library)
                → return text + wrapper_text  ← CORRECT: appends at end
```

### Confirmed correct via 4 independent methods:
1. **Python unit test**: `_embed_c2pa` places wrapper at index 709 (= len(NFC text)), after "action."
2. **curl to enterprise API** (localhost:9000): first invisible at index 709
3. **curl to marketing-site** (localhost:3000/api/tools/sign): first invisible at index 709
4. **Puppeteer browser test**: DOM `textContent` first invisible at index 709

### C2PA Spec Compliance (all 25 tests pass)
Every requirement from `docs/c2pa/Manifests_Text.txt` verified:
- **Placement**: wrapper at end of visible text (Rule 3) ✅
- **ZWNBSP prefix**: U+FEFF before variation selectors (Rule 2) ✅
- **Contiguous block**: single unbroken block (Rule 1) ✅
- **No split**: no invisible chars within visible text (Rule 4) ✅
- **Magic bytes**: C2PATXT\0 (0x4332504154585400) ✅
- **Version**: 1 ✅
- **manifestLength**: correct uint32 ✅
- **Byte↔VS encoding**: all 256 bytes roundtrip correctly ✅
- **NFC normalization**: text NFC-normalized before hashing ✅
- **find_and_decode**: wrapper extractable, clean_text matches original ✅
- **Hard binding**: verify succeeds, tamper detection works ✅
- **Custom assertions**: don't affect wrapper placement ✅
- **Whitespace preservation**: newlines, em-dashes preserved ✅

## Preventive Fix (advanced path)
**File**: `enterprise_api/app/services/embedding_service.py`

The advanced signing path (triggered when `custom_assertions` is set, e.g., with provenance text) had a latent bug:
- Per-segment basic embeddings used `MetadataTarget.WHITESPACE` (mid-text insertion)
- Segments re-joined with `" ".join()` destroying original whitespace

Fix: skip per-segment basic embeddings for document-level signing (`len(segments) == 1`) and preserve original text structure.

## Test Files
1. **`tests/test_c2pa_spec_compliance.py`** (25 tests) — Full C2PA spec compliance
2. **`tests/test_document_level_c2pa_placement.py`** (5 tests) — Advanced path regression

All 39 tests pass (+ 7 skipped API-dependent tests).
