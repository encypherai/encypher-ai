# TEAM_169 — HTML CMS Embedding Test

## Session Start
- **Date**: 2026-02-11
- **Goal**: Build HTML text extractor and test micro_c2pa / micro_ecc_c2pa signing for CMS HTML content
- **PRD**: `PRDs/CURRENT/PRD_HTML_CMS_Embedding_Test.md`

## Status: COMPLETE (Session 2 update: C2PA manifest fix)

## What Was Done
1. **HTML text extractor** (`enterprise_api/app/utils/html_text_extractor.py`)
   - `extract_text_from_html()` — strips tags, preserves paragraph structure via block element detection
   - `extract_segments_from_html()` — returns list of signable text segments
   - `embed_signed_text_in_html()` — injects API-signed text back into HTML text nodes
   - Handles: block elements → newlines, inline elements → preserve text, img → skip, links → anchor text only
   - Uses BeautifulSoup4 (already a dependency)

2. **Standalone CMS signing script** (`enterprise_api/scripts/sign_html_cms.py`)
   - CLI tool: `python scripts/sign_html_cms.py INPUT.html OUTPUT.html [OPTIONS]`
   - Parses full production CMS pages (head, meta, nav, scripts, styles, footer)
   - Signs only `<article>` content by default (configurable via `--selector`)
   - Embeds signed text back into article text nodes, returns complete page
   - Auto-verifies via API after signing
   - Supports `--mode micro_c2pa|micro_ecc_c2pa|basic`
   - Supports `--env-file`, `--api-key`, `--base-url`, `--title`, `--selector`

3. **Unit tests** — 31/31 passed
   - `tests/test_html_text_extractor.py` (20 tests): extraction, in-place embedding, markers, edge cases
   - `tests/test_sign_html_cms.py` (11 tests): content isolation, structure preservation, markers in complex HTML

4. **Live e2e tests** (`tests/e2e_live/test_live_html_cms_signing.py`) — 5/5 passed
   - **Plain text signing** (3 tests): micro_c2pa, micro_ecc_c2pa, basic → `.txt` files
   - **In-place HTML signing** (2 tests): micro_c2pa, micro_ecc_c2pa → `.html` files

5. **Script runs against complex CMS HTML** — both modes verified by API
   - `example_article_complex_parsing.html` (38KB full CMS page) → signed successfully
   - 63 text nodes replaced in article, nav/footer/scripts untouched

6. **C2PA manifest preservation fix** (Session 2)
   - **Bug**: C2PA manifest not detected when copy-pasting from signed complex HTML
   - **Root cause 1**: U+FEFF (wrapper prefix) not in VS_CHAR_SET → dropped by embed functions
   - **Root cause 2**: inter-node VS chars (manifest fragments) discarded by gap-skipping loop
   - **Root cause 3**: API joins segments with spaces, HTML extraction uses newlines → NFC hash mismatch
   - **Fix 1**: include U+FEFF in `_get_vs_char_set()` in both `html_text_extractor.py` and `sign_html_cms.py`
   - **Fix 2**: collect inter-node VS chars and attach to adjacent text nodes instead of dropping
   - **Fix 3**: normalize extracted text (newlines→spaces) before signing to match API pipeline
   - **Fix 4**: added `normalize_whitespace()` utility to `encypher-ai/interop/c2pa/text_hashing.py` (pre-processing only, NOT in hash path — NFC-only per C2PA spec)
   - **Backward compatible**: no changes to C2PA hash function, old embeddings unaffected
   - **Result**: both micro_c2pa and micro_ecc_c2pa complex HTML pass signed-text AND HTML-round-trip verification

7. **Standalone CMS Signing Kit** (`tools/encypher-cms-signing-kit/`)
   - `encypher_sign_html.py` — fully self-contained, zero internal imports
   - `.env.example` — customer-facing env var names (`ENCYPHER_API_KEY`, `ENCYPHER_BASE_URL`)
   - `pyproject.toml` — uv-compatible project config (replaces requirements.txt)
   - `README.md` — uv (primary) + pip (fallback) instructions, integration example, mode comparison
   - `.gitignore` — Python, .env, __pycache__, .venv, output/
   - `LICENSE` — proprietary Encypher license, tied to API license agreement
   - `SUBTREE.md` — git subtree split/push/pull workflow for private repo
   - Tested against live API: both modes pass signed-text + HTML round-trip verification
   - Structured as git subtree — can be split to `encypherai/encypher-cms-signing-kit` private repo

8. **Output files** (in `enterprise_api/tests/e2e_live/output/`):
   - `chesschampion_micro_c2pa_signed.txt` (37KB)
   - `chesschampion_micro_ecc_c2pa_signed.txt` (41KB)
   - `chesschampion_basic_signed.txt` (19KB)
   - `chesschampion_micro_c2pa_signed.html` (34KB) — simple article HTML
   - `chesschampion_micro_ecc_c2pa_signed.html` (38KB) — simple article HTML
   - `chesschampion_complex_micro_c2pa_signed.html` (43KB) — **full CMS page, C2PA manifest intact**
   - `chesschampion_complex_micro_ecc_c2pa_signed.html` (43KB) — **full CMS page, C2PA manifest intact**

## Run Commands
```bash
# Unit tests (no network)
uv run pytest tests/test_html_text_extractor.py tests/test_sign_html_cms.py -v

# Live e2e tests (hits production API)
LIVE_API_TESTS=true uv run pytest tests/e2e_live/test_live_html_cms_signing.py -v -s

# Sign a CMS page directly (internal script)
uv run python scripts/sign_html_cms.py INPUT.html OUTPUT.html --mode micro_c2pa --env-file tests/e2e_live/.env.prod

# Standalone kit (customer-facing)
cd tools/encypher-cms-signing-kit && uv sync && uv run python encypher_sign_html.py INPUT.html OUTPUT.html

# Split subtree to private repo
git subtree split --prefix=tools/encypher-cms-signing-kit -b cms-signing-kit-split
```

## Git Commit Message Suggestion
```
feat: CMS signing kit as subtree + C2PA manifest preservation

Add standalone CMS signing kit (subtree-ready for private repo),
HTML text extractor, in-place signing, and C2PA manifest fixes.

- Add tools/encypher-cms-signing-kit/: standalone deliverable for CMS
  customers. Self-contained Python script, pyproject.toml (uv),
  .env.example, .gitignore, proprietary LICENSE, SUBTREE.md.
  Zero internal dependencies — uses only requests, beautifulsoup4,
  python-dotenv. Designed for git subtree split to private repo.
- Add enterprise_api/app/utils/html_text_extractor.py:
  - extract_text_from_html(): strips tags, preserves paragraph structure
  - extract_segments_from_html(): returns signable text segments
  - embed_signed_text_in_html(): injects API-signed text back into
    original HTML, preserving all tags/attributes/images
- Add enterprise_api/scripts/sign_html_cms.py: internal CLI tool.
- Fix C2PA manifest preservation in HTML embedding:
  - Include U+FEFF in invisible char set (C2PA wrapper prefix)
  - Collect inter-node VS chars instead of discarding (manifest bits)
  - Normalize whitespace (newlines→spaces) before signing to match
    API pipeline output, ensuring NFC hash consistency
- Add normalize_whitespace() to encypher-ai text_hashing.py as
  pre-processing utility (NFC-only hash per C2PA spec, backward
  compatible with all existing embeddings)
- Tests: 32 enterprise_api unit, 48 encypher-ai, 5 live e2e
- Tested against example_article_complex_parsing.html (38KB full CMS
  page) — both modes pass signed-text AND HTML-round-trip verification

TEAM_169
```
