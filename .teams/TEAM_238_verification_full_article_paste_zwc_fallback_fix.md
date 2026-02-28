# TEAM_238: Fix Full Article Paste Verification (ZWC Fallback Guard)

## Session Summary

### Bug Fixed
Production bug: pasting a full article (with page title, author metadata, and
Encypher provenance badge) into the verify tool returned SIGNATURE_INVALID, while
pasting individual paragraphs returned "valid db-backed manifest".

### Root Cause (diagnosed by Opus in prior session)
`services/verification-service/app/api/v1/endpoints.py` had two fallback blocks:
- ZWC fallback (line 829): `if not signer_id:` -- blocked when C2PA extracted signer_id
- VS256 fallback (line 902): `if not signer_id:` -- same issue

When the user copies the full article page, extra browser content (title, author, badge
appended by `maybe_add_c2pa_badge()`) surrounds the signed text. C2PA verifies COSE
(signer_id extracted) but the content hash fails (extra bytes not in signed region).
The `if not signer_id:` guard then blocks ZWC/VS256 fallback -> SIGNATURE_INVALID.

Individual paragraphs work because they contain no C2PA wrapper, so signer_id=None
and ZWC/VS256 fallback runs, resolving per-sentence UUIDs from DB.

### Fix Applied
Changed both guards from:
```python
if not signer_id:
```
to:
```python
if not signer_id or not is_valid:
```

This allows ZWC/VS256 fallback to run whenever verification has not yet succeeded,
regardless of whether signer_id was extracted from a failed C2PA check.

Design rationale: ZWC/VS256 fallback is sentence-level provenance (DB-backed UUIDs).
It is correct to resolve provenance even when C2PA document-level hash fails due to
extra surrounding content. Tamper detection is preserved because tampered UUIDs would
not be found in the DB.

### Files Changed
- `services/verification-service/app/api/v1/endpoints.py`
  - Line 833: ZWC fallback guard `if not signer_id:` -> `if not signer_id or not is_valid:`
  - Line 908: VS256 fallback guard same change
- `services/verification-service/tests/test_verify_full_article_paste.py` (new)
  - 3 tests covering the fix, the happy path, and tamper-rejection

### Test Results
84/84 tests pass. No regressions.

### Suggested Commit Message
```
fix(verification-service): allow ZWC/VS256 fallback when C2PA hash fails

When a user copies a full article page from the browser, the pasted text
includes extra content (page title, author, Encypher badge) that is not
part of the signed region. C2PA COSE verification succeeds (signer_id
extracted) but the document content hash fails because of the surrounding
bytes.

The old guard `if not signer_id:` blocked ZWC and VS256 sentence-level
fallback in this case, returning SIGNATURE_INVALID instead of resolving
provenance via the per-sentence DB-backed UUIDs.

Fix: loosen both guards to `if not signer_id or not is_valid:` so that
ZWC/VS256 fallback runs whenever C2PA has not produced a successful result.
This is consistent with the existing behaviour for individual paragraphs
(no C2PA wrapper -> signer_id=None -> ZWC runs normally).

Tamper detection is preserved: if the tampered text's sentence UUIDs are
not in the DB, the fallback returns no results and the endpoint correctly
returns SIGNATURE_INVALID.

Tests: 84 pass, 3 new regression tests added.
```
