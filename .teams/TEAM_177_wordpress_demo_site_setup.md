# TEAM_177 — WordPress Demo Site Setup ("The Encypher Times")

## Objective
Clean up WordPress test site, rename to "The Encypher Times", create a newsletter-style homepage, and publish 3-4 short articles about C2PA and content provenance. Sign 2 articles, leave 1-2 unsigned to demonstrate the signing/verification workflow.

## Status: COMPLETE

## Changes
- Deleted all 15 existing posts and 2 pages
- Renamed site to "The Encypher Times" with tagline "Trusted News in the Age of AI"
- Set author display name to "Editorial Staff"
- Homepage shows latest posts (blog-style)

## Articles Created

| ID | Title | Status |
|----|-------|--------|
| 61 | What Is C2PA and Why Should You Care? | **SIGNED** ✅ verified |
| 64 | How Content Signing Actually Works | **SIGNED** ✅ verified |
| 67 | The Rise of AI-Generated Misinformation | Unsigned |
| 70 | What Readers Should Know About Content Verification | Unsigned |

## Verification Results
- Post 61: `valid=true`, `reason_code=OK`, signer=`org_07dd7ff77fa7e949`
- Post 64: `valid=true`, `reason_code=OK`, signer=`org_07dd7ff77fa7e949`
- Post 67: 0 embeddings, no signing metadata
- Post 70: 0 embeddings, no signing metadata

## Fix: Verify tool SIGNATURE_INVALID on full-page paste

When users copy-paste from a rendered WordPress page, the pasted text includes
surrounding page chrome (nav bar, admin bar, footer, etc.) that was never part
of the signed content. The C2PA content hash was computed on just the article
text, so hashing the full paste produced a mismatch.

**Root cause:** Two issues compound:
1. Page chrome (nav, footer) surrounds the signed text
2. Browser copy-paste converts `<p>` tags to `\n\n` but the signed text used
   single spaces between paragraphs (WordPress `extract_text_from_html` joins
   paragraphs with spaces)

**Fix:** Added a two-variant fallback in `_verify_c2pa` (encypher-ai `unicode_metadata.py`).
When the hard binding hash fails on the full text, the code tries two text
variants: (1) the original text as-is, and (2) a whitespace-collapsed version
(all `\s+` → single space). For each variant it uses `find_wrapper_info_bytes`
to locate the C2PA wrapper's byte offset, then uses the manifest's exclusion
range to extract just the originally-signed segment and retry the hash.

**Files changed:**
- `encypher-ai/encypher/core/unicode_metadata.py` — segment extraction fallback in `_verify_c2pa`
- `encypher-ai/tests/integration/test_c2pa_text_embedding.py` — 3 new tests (page chrome, browser whitespace, tamper detection)
- `docker-compose.full-stack.yml` — volume-mount `encypher-ai` into verification service + `pip install` at startup so local changes survive container restarts

### Test Results
- ✅ 29/29 relevant tests pass (10 c2pa_text_embedding + 19 unicode_metadata)
- ✅ e2e: exact signed text → `valid=True`
- ✅ e2e: signed text + page chrome (same whitespace) → `valid=True` (original variant)
- ✅ e2e: browser paste with `\n\n` paragraphs + page chrome → `valid=True` (ws-collapsed variant)
- ✅ e2e: tampered text + page chrome → `valid=False`
- ✅ e2e: full browser-simulated paste through marketing site → `verification_status: Success`

## Git Commit Message Suggestion
```
fix(encypher-ai): verify signed text within full-page paste

When users copy-paste from a rendered WordPress page, the pasted text
includes surrounding page chrome (nav, footer, etc.) that was never
signed. The C2PA content hash covers only the article text, so hashing
the full paste produced a mismatch → SIGNATURE_INVALID.

Added a two-variant fallback in _verify_c2pa: when the hard binding
hash fails, try extracting the signed segment from (1) the original
text and (2) a whitespace-collapsed version (\s+ -> single space).
The second variant handles browser copy-paste where <p> tags become
\n\n but the signed text used single spaces between paragraphs.

Volume-mount encypher-ai into verification-service in
docker-compose.full-stack.yml so the fix survives container restarts
(start-dev.sh). pip install --force-reinstall at container startup.

Also set up WordPress demo site "The Encypher Times" with 4 articles
(2 signed, 2 unsigned) for demonstration purposes.

TEAM_177
```
