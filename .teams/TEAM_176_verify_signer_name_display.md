# TEAM_176 — Verify Tool: Signer Name Display & Position Fix

## Status: COMPLETE

## Problem
1. Website verification tool shows org ID (`org_07dd7ff77fa7e949`) instead of org name as the signer
2. Signer and reason code appear at the bottom after C2PA manifest — should be right below the "Verified" header

## Root Cause
- **Backend**: In `services/verification-service/app/api/v1/endpoints.py`, when ZW/VS256 DB-resolved embeddings set `signer_id`, `_fetch_trust_anchor` is never called for those paths, so `trust_anchor_name` stays `None` and `signer_name` falls back to `signer_id`
- **Frontend**: Signer/reason code section is positioned after the C2PA manifest details instead of before

## Changes

### Backend
- `services/verification-service/app/api/v1/endpoints.py` (line ~860): After ZW/VS256 DB resolution, call `_fetch_trust_anchor(signer_id)` to resolve the human-readable org name. Guarded by `not trust_anchor_name and signer_id.startswith("org_")` to avoid redundant calls.

### Frontend
- `apps/marketing-site/src/components/tools/EncodeDecodeTool.tsx`: Added signer/reason code block immediately after status description (before error/C2PA sections). Removed old signer/reason code from bottom of C2PA manifest block.
- `apps/marketing-site/src/components/tools/FileInspectorTool.tsx`: Same positioning fix — signer/reason code now appears right below the "Verified" header.

### Tests
- `services/verification-service/tests/test_verify_zw_fallback.py`: Added `test_verify_zw_embedding_resolves_org_name_via_trust_anchor` — verifies signer_name and organization_name are resolved from trust anchor API.
- `apps/marketing-site/src/lib/enterpriseApiTools.test.ts`: Added test verifying signer_name distinct from signer_id passes through mapping.

## Test Results
- ✅ 69/69 verification-service tests pass
- ✅ 8/8 enterpriseApiTools frontend tests pass

## Suggested Git Commit
```
fix(verify): show org name instead of ID as signer, move signer/reason above manifest

TEAM_176: Two fixes for the website verification tool:

1. Backend (verification-service): After ZW/VS256 DB-resolved embeddings
   set signer_id, call _fetch_trust_anchor() to resolve the human-readable
   org name. Previously trust_anchor_name stayed None for these paths,
   causing signer_name to fall back to the raw org ID.

2. Frontend (EncodeDecodeTool, FileInspectorTool): Move signer and reason
   code display to appear immediately below the "Verified Authentic" status
   header, before the C2PA manifest details section.

Files changed:
- services/verification-service/app/api/v1/endpoints.py
- apps/marketing-site/src/components/tools/EncodeDecodeTool.tsx
- apps/marketing-site/src/components/tools/FileInspectorTool.tsx
- services/verification-service/tests/test_verify_zw_fallback.py
- apps/marketing-site/src/lib/enterpriseApiTools.test.ts
```
