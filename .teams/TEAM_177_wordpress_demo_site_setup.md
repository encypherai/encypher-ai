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

**Fix:** Added a fallback in `_verify_c2pa` (encypher-ai `unicode_metadata.py`).
When the hard binding hash fails on the full text, the code uses
`find_wrapper_info_bytes` to locate the C2PA wrapper's byte offset in the
current text, then uses the manifest's exclusion range (which records the
wrapper's byte offset in the *original* signed text) to compute where the
signed segment starts. It extracts just that segment and retries the hash.

**Files changed:**
- `encypher-ai/encypher/core/unicode_metadata.py` — segment extraction fallback in `_verify_c2pa`
- `encypher-ai/tests/integration/test_c2pa_text_embedding.py` — 2 new tests
- `docker-compose.full-stack.yml` — volume-mount `encypher-ai` into verification service + `pip install` at startup so local changes survive container restarts

### Test Results
- ✅ 67 passed, 16 xfailed in encypher-ai tests
- ✅ 12/12 enterprise API tests pass
- ✅ e2e: exact signed text → `valid=True`
- ✅ e2e: signed text + page chrome → `valid=True` (segment extraction)
- ✅ e2e: tampered text + page chrome → `valid=False`
- ✅ e2e: full-page paste through marketing site → `verification_status: Success` (byte range 265-19716)

## Git Commit Message Suggestion
```
fix(encypher-ai): verify signed text within full-page paste

When users copy-paste from a rendered WordPress page, the pasted text
includes surrounding page chrome (nav, footer, etc.) that was never
signed. The C2PA content hash covers only the article text, so hashing
the full paste produced a mismatch → SIGNATURE_INVALID.

Added a fallback in _verify_c2pa: when the hard binding hash fails,
use find_wrapper_info_bytes to locate the C2PA wrapper's byte offset
in the current text, then use the manifest's exclusion range to
extract just the originally-signed segment and retry the hash.

Volume-mount encypher-ai into verification-service in
docker-compose.full-stack.yml so the fix survives container restarts
(start-dev.sh). pip install --no-deps at container startup.

Also set up WordPress demo site "The Encypher Times" with 4 articles
(2 signed, 2 unsigned) for demonstration purposes.

TEAM_177
```
