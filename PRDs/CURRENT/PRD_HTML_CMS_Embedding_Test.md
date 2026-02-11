# PRD: HTML CMS Embedding Test

## Status: COMPLETE

## Current Goal
Build an HTML text extractor and validate that micro_c2pa and micro_ecc_c2pa signing works for HTML content destined for a custom CMS, ensuring signed text survives browser rendering and copy-paste into the verification system.

## Overview
CMS systems store content as HTML. To sign this content with our invisible Unicode markers, we need to extract only the text that will be rendered in a browser (stripping tags, ignoring non-visible attributes like src/alt/href). The signed text with embedded invisible markers must survive the round-trip: HTML → browser render → user copy-paste → verification. This PRD covers the HTML text extractor utility and comprehensive tests for both micro_c2pa and micro_ecc_c2pa modes.

## Objectives
- Create a reusable HTML text extractor that produces signable plain text from HTML
- Preserve paragraph/section structure for proper segmentation
- Ensure invisible VS256/RS markers survive browser copy-paste
- Test with the real chesschampion example article
- Validate both micro_c2pa (36-char) and micro_ecc_c2pa (44-char RS) modes

## Tasks

### 1.0 HTML Text Extractor
- [x] 1.1 Write tests for HTML text extraction (TDD) — ✅ pytest 12/12
  - [x] 1.1.1 Test: strips HTML tags, returns only rendered text
  - [x] 1.1.2 Test: preserves paragraph boundaries (block elements → newlines)
  - [x] 1.1.3 Test: handles ordered/unordered lists correctly
  - [x] 1.1.4 Test: ignores img elements (not rendered as text)
  - [x] 1.1.5 Test: preserves link anchor text but strips href
  - [x] 1.1.6 Test: handles bold/italic inline elements (preserves text)
  - [x] 1.1.7 Test: works with the real chesschampion example_article.html
- [x] 1.2 Implement `html_text_extractor.py` in enterprise_api/app/utils/
- [x] 1.3 Tests pass

### 2.0 micro_c2pa HTML Round-Trip
- [x] 2.1 Live e2e test via production API (POST /api/v1/sign with options) — ✅ pytest
  - [x] 2.1.1 Sign chesschampion HTML text with micro_c2pa via live API
  - [x] 2.1.2 Verify via live /api/v1/verify
  - [x] 2.1.3 Output signed text to file for manual paste into encypherai.com/tools/verify
- [x] 2.2 Tests pass

### 3.0 micro_ecc_c2pa HTML Round-Trip
- [x] 3.1 Live e2e test via production API — ✅ pytest
  - [x] 3.1.1 Sign chesschampion HTML text with micro_ecc_c2pa via live API
  - [x] 3.1.2 Verify via live /api/v1/verify
  - [x] 3.1.3 Output signed text to file for manual paste into encypherai.com/tools/verify
- [x] 3.2 Tests pass

### 5.0 In-Place HTML Signing (embed signed text back into HTML)
- [x] 5.1 Implement `embed_signed_text_in_html()` — walks DOM, maps signed text back onto text nodes
- [x] 5.2 Unit tests — ✅ pytest 8/8 (tags preserved, img preserved, links preserved, markers extractable, chesschampion roundtrip, edge cases)
- [x] 5.3 Live e2e tests — ✅ pytest 2/2
  - [x] 5.3.1 micro_c2pa: sign → embed into HTML → extract text → verify via API
  - [x] 5.3.2 micro_ecc_c2pa: sign → embed into HTML → extract text → verify via API
- [x] 5.4 Output .html files with invisible markers in text nodes

### 7.0 Standalone CMS Signing Script (complex HTML)
- [x] 7.1 Implement `scripts/sign_html_cms.py` — CLI tool to sign full CMS pages
  - [x] 7.1.1 Parses full production CMS HTML (head, meta, nav, scripts, styles, footer)
  - [x] 7.1.2 Signs only `<article>` content (configurable via --selector)
  - [x] 7.1.3 Embeds signed text back into article text nodes, returns full page
  - [x] 7.1.4 Auto-verifies via API after signing
  - [x] 7.1.5 Supports micro_c2pa, micro_ecc_c2pa, basic modes
- [x] 7.2 Unit tests — ✅ pytest 11/11 (content isolation, structure preservation, markers, edge cases)
- [x] 7.3 Ran against `example_article_complex_parsing.html` — both modes verified by API
- [x] 7.4 Output .html files: full CMS pages with invisible markers in article text

### 9.0 C2PA Manifest Preservation in HTML Round-Trip
- [x] 9.1 Bug: C2PA manifest not detected when copy-pasting from signed complex HTML
  - [x] 9.1.1 Root cause 1: FEFF (U+FEFF) wrapper prefix dropped by embed functions (not in VS_CHAR_SET)
  - [x] 9.1.2 Root cause 2: inter-node VS chars (manifest fragments) discarded by gap-skipping loop
  - [x] 9.1.3 Root cause 3: API joins segments with spaces, but HTML extraction uses newlines → hash mismatch
- [x] 9.2 Fix: include U+FEFF in invisible char set (`_get_vs_char_set`) in both `html_text_extractor.py` and `sign_html_cms.py`
- [x] 9.3 Fix: collect inter-node VS chars and attach to adjacent text nodes instead of dropping
- [x] 9.4 Fix: normalize extracted text (newlines→spaces) before signing to match API pipeline output
- [x] 9.5 Fix: apply same normalization when extracting from HTML for verification
- [x] 9.6 Added `normalize_whitespace()` utility to `encypher-ai/interop/c2pa/text_hashing.py` (pre-processing, NOT in hash path — NFC-only per C2PA spec)
- [x] 9.7 Verified: both micro_c2pa and micro_ecc_c2pa complex HTML pass signed-text AND HTML-round-trip verification
- [x] 9.8 All tests pass: encypher-ai (48 passed, 16 xfailed), enterprise_api (32 passed)

### 10.0 Standalone CMS Signing Kit
- [x] 10.1 Create `tools/encypher-cms-signing-kit/encypher_sign_html.py` — fully self-contained, zero internal imports
  - [x] 10.1.1 Inline VS char set generation (no vs256_crypto dependency)
  - [x] 10.1.2 Inline BLOCK_ELEMENTS / SKIP_ELEMENTS constants (no html_text_extractor dependency)
  - [x] 10.1.3 Use `requests` instead of `httpx` (more common in customer environments)
  - [x] 10.1.4 Use `ENCYPHER_API_KEY` / `ENCYPHER_BASE_URL` env var names (customer-facing)
- [x] 10.2 Create `.env.example` with API key placeholder and base URL
- [x] 10.3 Create `pyproject.toml` (uv-compatible, replaces requirements.txt)
- [x] 10.4 Create `README.md` with uv (primary) + pip (fallback) instructions
- [x] 10.5 Create `.gitignore`, proprietary `LICENSE`, `SUBTREE.md` (git subtree workflow)
- [x] 10.6 Tested against live API: micro_c2pa PASSED, micro_ecc_c2pa PASSED (both signed-text + HTML round-trip)
- [x] 10.7 Structured as git subtree — can be split to private repo for customer access

### 11.0 Finalize
- [x] 11.1 Lint passes (ruff check clean)
- [x] 11.2 All tests pass (32 unit + 5 live e2e + 2 extraction sanity)
- [x] 11.3 PRD updated

## Success Criteria
- HTML text extractor correctly extracts only rendered text from arbitrary HTML
- micro_c2pa markers are embedded and verifiable after HTML text extraction
- micro_ecc_c2pa RS markers are embedded and verifiable after HTML text extraction
- Signed text survives simulated browser copy-paste (visible text unchanged, markers preserved)
- **In-place HTML signing**: signed text is injected back into original HTML, preserving all tags/attributes/images
- Signed HTML files can be opened in a browser, text copied, and verified at encypherai.com/tools/verify
- **Standalone CMS script**: signs full production CMS pages, isolating article content from nav/footer/scripts
- **C2PA manifest preserved**: FEFF wrapper block intact in HTML output, manifest extractable after round-trip
- **Backward compatible**: no changes to C2PA hash function (NFC-only per spec), whitespace normalization is pre-processing only
- **Standalone kit**: `examples/cms_signing_kit/` is a self-contained deliverable with zero internal dependencies
- All tests pass with `uv run pytest`
