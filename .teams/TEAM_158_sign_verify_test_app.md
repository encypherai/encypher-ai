# TEAM_158: Sign & Verify Test App + PDF Copy-Paste VS Fix

## Status: COMPLETE (Phase 3: VS256-RS Error-Correcting Embedding)

## Goal
1. Local-only web app for testing the sign-existing-PDF flow.
2. Fix variation selector (VS) embedding so invisible chars survive copy-paste
   from PDF viewers (text-based verification).

## Architecture
- **Frontend**: Single-page HTML + TailwindCSS served by FastAPI
- **Backend**: FastAPI server wrapping `sign_existing_pdf` + verification proxy
- Location: `tools/sign-verify-app/`

## Key Changes

### Unified Single-Font CID Approach (`sign_existing.py`)
**Problem**: The old dual-font approach used a separate `EncInv` font for
invisible chars with font-switching commands. PDF viewers treated VS chars
as orphaned from base glyphs and stripped them during copy-paste.

**Solution**: Replaced with a **unified single CID font** (`EncSgn` /
`EncypherSigned`) that contains BOTH visible and invisible glyphs:

1. **`_collect_visible_codepoints()`** — scans existing content streams to
   find all Unicode codepoints used by visible text.
2. **`_build_font_assets()`** — builds a CID font (LiberationSans +
   invisible glyphs) covering both visible and invisible codepoints.
3. **Rewrites ALL Tj/TJ operators** — re-encodes visible chars from 1-byte
   hex to 2-byte CID hex in the unified font. Invisible chars are injected
   inline as separate TJ chunks in the **same font** — no font switching.
4. **Font switch commands** (`/fontname Tf`) are rewritten to point to the
   unified font.
5. **Handles whitespace normalization** — the signing API may convert `\n`
   to space; the diff logic accounts for this without shifting indices.
6. **Clamps out-of-range insertions** — trailing invisible chars that
   exceed the content stream char count are appended to the last valid char.

This mirrors `encypher-pdf/writer.py`'s approach: one CID font for
everything, Identity-H encoding, ToUnicode CMap for copy-paste fidelity.

### Extraction Results
| Method | VS Recovery | Notes |
|--------|------------|-------|
| Direct stream parsing | **100%** | `extract_signed_text_from_streams()` |
| MuPDF `get_text()` | **99.1%** | Drops ~1% of overlapping zero-width glyphs |
| pdftotext (poppler) | **34%** | Poppler deduplicates repeated VS per base glyph |
| EncypherSignedText stream | **100%** | Lossless metadata stream in PDF catalog |

### Root Cause: Poppler VS Deduplication
Poppler (pdftotext) deduplicates variation selectors per base glyph per the
Unicode spec. The signing API encodes binary data (C2PA manifest) as long
sequences of repeated VS codepoints (e.g. 1749 consecutive SVS chars).
Poppler collapses duplicates, losing ~65% of the data.

### Solution: VS256 Encoding + Redistribution (Phase 2)
**`vs256_embedding`** mode encodes 32 bytes (UUID + HMAC) as only **36 VS
chars** (4 magic prefix + 32 payload, base-256). Combined with
**`_redistribute_insertions()`** which spreads VS chars evenly across
visible text (max 1 per base glyph), poppler preserves **100%** of VS chars.

| Mode | VS chars | pdftotext recovery |
|------|----------|-------------------|
| `minimal` (C2PA) | ~2000+ | 34-67% (repeated VS) |
| `vs256_sentence` | 36 | **100%** (redistributed) |

### Verification Architecture
- **PDF content stream**: VS chars redistributed (1 per base glyph) for
  poppler compatibility. Copy-paste preserves 100% of VS chars.
- **EncypherSignedText metadata stream**: Original signed text with
  contiguous VS256 signatures for server-side verification.
- **Verification-service**: Detects VS256 magic prefix in metadata stream,
  extracts UUID, resolves via enterprise API DB lookup.

### Verification Paths (all working)
1. **Server-side** (port 8200 `/api/verify`): Extracts EncypherSignedText
   metadata stream → VS256 detection → DB resolve → `valid=true, signer=org_demo` ✅
2. **EncypherSignedText metadata**: Lossless UTF-8 stream in PDF catalog → 100% ✅
3. **Copy-paste (pdftotext)**: 100% VS preservation with vs256_sentence mode ✅

### Phase 3: VS256-RS Error-Correcting Embedding
**`vs256_rs_embedding`** mode adds Reed-Solomon error correction to the VS256
signature, enabling recovery from partial data loss (poppler dedup, partial
copy-paste) while maintaining the same 36-char footprint.

**Layout**: `MAGIC(4) + UUID(16) + HMAC-64(8) + RS_PARITY(8) = 36 chars`

| Property | vs256_embedding | vs256_rs_embedding |
|----------|----------------|-------------------|
| HMAC security | 128-bit | 64-bit (sufficient) |
| Error correction | None | RS(32,24): 4 errors / 8 erasures |
| Poppler dedup survival | Needs redistribution | Survives ~2.3 avg loss without redistribution |
| Partial copy-paste | All-or-nothing | Tolerates up to 8 missing VS chars |
| Total chars | 36 | 36 |

**Verification flow**: RS decode → HMAC-64 verify → UUID DB lookup.
Both `vs256_detect.py` and `verification_logic.py` try RS first, fall back to
plain VS256. The verification-service also reassembles distributed VS chars
from copy-paste text when contiguous detection fails.

## Tasks
- [x] 1.0 Scaffold sign-verify-app (FastAPI + HTML) — ✅ pytest
- [x] 2.0 Build FastAPI backend (/api/sign, /api/verify, /api/modes) — ✅ pytest
- [x] 3.0 Build HTML frontend (drop zone, mode selector, sign/verify/download)
- [x] 4.0 Fix verify endpoint: extract EncypherSignedText metadata stream — ✅ pytest
- [x] 5.0 Rewrite ZW injection: custom CID font + content stream rewriting — ✅ pytest
- [x] 5.1 Fix _diff_for_insertions: newline→space normalization, index clamping — ✅ pytest
- [x] 6.0 E2E test: sign PDF → extract text → verify invisible chars present — ✅ 98.8%
- [x] 7.0 Direct content stream extraction for 100% recovery — ✅ pytest
- [x] 8.0 Wire into sign-verify-app verify endpoint — ✅
- [x] 9.0 Unified single-font CID approach (no font switching) — ✅ pytest (31 tests)
- [x] 9.1 Root cause analysis: poppler VS deduplication — ✅ documented
- [x] 9.2 pdftotext preservation test (unique VS = 100%) — ✅ pytest
- [x] 9.3 E2E sign→verify via port 8200: valid=true, signer=org_demo — ✅
- [x] 10.0 Add `vs256_sentence` mode to signer.py — ✅
- [x] 10.1 Fix `vs256_embedding` in embeddings.py + streaming.py schema validation — ✅
- [x] 10.2 `_redistribute_insertions()` — spread VS across base glyphs (1 per base) — ✅ pytest
- [x] 10.3 Wire VS256 fallback into verification-service (vs256_detect.py) — ✅ pytest (7 tests)
- [x] 10.4 Update sign-verify-app to prefer EncypherSignedText metadata stream — ✅
- [x] 10.5 E2E: sign→pdftotext→verify = 100% VS, valid=true, signer=org_demo — ✅
- [x] 10.6 Unit tests for _redistribute_insertions (6 tests) — ✅ pytest
- [x] 11.0 Phase 2 team file update
- [x] 12.0 Design VS256-RS encoding (4 magic + 16 UUID + 8 HMAC-64 + 8 RS parity) — ✅
- [x] 12.1 Implement `vs256_rs_crypto.py` — ✅ pytest (25 tests)
- [x] 12.2 Add `vs256_rs_embedding` mode to embedding_service.py — ✅
- [x] 12.3 Add `vs256_rs_embedding` to schema validators (embeddings, streaming, sign_schemas) — ✅
- [x] 12.4 Add `vs256_rs_sentence` mode to signer.py — ✅
- [x] 12.5 Update vs256_detect.py: RS-aware UUID extraction + distributed reassembly — ✅ pytest (17 tests)
- [x] 12.6 Update verification_logic.py: try RS → plain VS256 → ZW fallback — ✅
- [x] 12.7 Update verification-service endpoints: distributed VS reassembly — ✅
- [x] 12.8 Add `reedsolo` to pyproject.toml (enterprise_api + verification-service) — ✅
- [x] 12.9 E2E: vs256_rs_sentence sign→metadata verify→pdftotext verify→port 8200 verify — ✅
- [x] 13.0 Phase 3 team file update
- [x] 14.0 Bugfix: C2PA modes (minimal, full, lightweight) garbled PDF text — ✅ pytest (39 tests)
- [x] 14.1 Root cause: content stream rewriting injected ~2000 invisible chars into text layer
- [x] 14.2 Fix: skip content stream rewriting for C2PA manifest modes, only inject metadata stream
- [x] 14.3 Regression tests: C2PA modes preserve text, VS/ZW modes still rewrite — ✅ pytest
- [x] 14.4 Phase 4 team file update
- [x] 15.0 Bugfix: VS/ZW modes garbled Type3/custom-encoded fonts (e.g. Chrome "Save as PDF") — ✅ pytest + puppeteer
- [x] 15.1 Root cause: unified CID font rewriting re-encoded byte values as Unicode codepoints — wrong for Type3 Differences encoding
- [x] 15.2 Fix: font-switching approach — leave original streams untouched, inject invisible chars via `/{EncSgn} Tf [<GID> -1] TJ /{origFont} Tf`
- [x] 15.3 Invisible glyph width=1 + TJ kern=-1 compensation (maintains position ordering for copy-paste without visual displacement)
- [x] 15.4 Use invisible-only font (`_get_font_assets()`) — no visible glyphs needed
- [x] 15.5 Puppeteer verified: test_article.pdf renders identically for all modes — ✅
- [x] 15.6 Copy-paste verified: VS256 100% (1548/1548), ZW 98% (5393/5504) — ✅ pdftotext
- [x] 15.7 Unit tests updated for font-switching approach — ✅ pytest (39 tests)
- [x] 15.8 Phase 5 team file update
- [x] 16.0 Bugfix: VS256 modes reported "Invisible Chars: 0" in sign response
- [x] 16.1 Root cause: Python `isprintable()` returns True for VS chars (U+E0100+)
- [x] 16.2 Fix: use `INVISIBLE_CODEPOINTS` set from encypher_pdf for accurate counting
- [x] 16.3 Bugfix: Verification returned SIGNER_UNKNOWN — was stale server; after restart all 4 modes verify valid=True signer=org_demo
- [x] 16.4 Full E2E verified: sign→verify for vs256_rs, vs256, zw, minimal — all ✅
- [x] 16.5 Phase 6 team file update
- [x] 17.0 Documentation: Created comprehensive EMBEDDING_MODES.md reference
- [x] 17.1 Covers all 7 modes: VS256, VS256+RS, ZW, C2PA Full, Lightweight, Minimal, Hybrid
- [x] 17.2 Platform compatibility tables (Word, Google Docs, PDF, browsers)
- [x] 17.3 PDF font compatibility section (Type3 caveat, font recommendation for publishers)
- [x] 17.4 Updated enterprise_api/README.md with VS256 + VS256+RS mode docs
- [x] 17.5 Updated DOCUMENTATION_INDEX.md with new reference doc
- [x] 17.6 Phase 7 team file update

## Files Modified
- `tools/xml-to-pdf/src/xml_to_pdf/sign_existing.py` — font-switching injection + TJ kern + C2PA skip + redistribution
- `tools/xml-to-pdf/src/xml_to_pdf/signer.py` — added `vs256_sentence` + `vs256_rs_sentence` modes
- `tools/xml-to-pdf/tests/test_sign_existing.py` — 39 tests (all passing)
- `tools/sign-verify-app/sign_verify_app/server.py` — prefer metadata stream for verify
- `tools/sign-verify-app/pyproject.toml` — project config
- `enterprise_api/app/utils/vs256_rs_crypto.py` — NEW: RS-protected VS256 crypto module
- `enterprise_api/app/schemas/embeddings.py` — added vs256_rs_embedding to allowed modes
- `enterprise_api/app/schemas/streaming.py` — added vs256_rs_embedding to allowed modes
- `enterprise_api/app/schemas/sign_schemas.py` — added vs256_rs_embedding to allowed modes
- `enterprise_api/app/services/embedding_service.py` — added vs256_rs_embedding handler
- `enterprise_api/app/services/verification_logic.py` — VS256-RS → VS256 → ZW fallback chain
- `enterprise_api/pyproject.toml` — added reedsolo dependency
- `enterprise_api/tests/test_vs256_rs_crypto.py` — NEW: 25 tests
- `services/verification-service/app/utils/vs256_detect.py` — RS-aware UUID extraction + distributed reassembly
- `services/verification-service/app/api/v1/endpoints.py` — distributed VS reassembly in verify endpoint
- `services/verification-service/pyproject.toml` — added reedsolo dependency
- `services/verification-service/tests/test_vs256_detect.py` — expanded to 17 tests
