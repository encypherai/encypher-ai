# TEAM_147: Local E2E API Key

**Active PRD**: `PRDs/CURRENT/PRD_No_Shared_Tables_Service_Ownership.md`
**Working on**: Task 5.4
**Started**: 2026-02-02 20:00
**Status**: completed

## Session Progress
- [x] 5.4 — ✅ pytest

## Changes Made
- `enterprise_api/app/routers/signing.py`: bootstrap org before quota check to prevent 404.
- `enterprise_api/app/services/signing_executor.py`: auto-provision certificates for non-demo orgs.
- `enterprise_api/app/services/embedding_executor.py`: auto-provision certificates for advanced signing.

## Blockers
- None.

## Handoff Notes
- Local E2E tests passing (`LOCAL_API_TESTS=true uv run pytest enterprise_api/tests/e2e_local`).
- Verify production internal tokens are configured so certificate provisioning can sync to auth-service.
