# TEAM_147: Local E2E API Key

**Active PRD**: `PRDs/CURRENT/PRD_No_Shared_Tables_Service_Ownership.md`
**Working on**: Prod warning fixes + test updates
**Started**: 2026-02-02 20:00
**Status**: in progress

## Session Progress
- [x] 5.4 — ✅ pytest
- [x] Normalize certificate expiry handling + remove certificate_pem join
- [x] Update key-service tests + add naive expiry regression test

## Changes Made
- `enterprise_api/app/routers/signing.py`: bootstrap org before quota check to prevent 404.
- `enterprise_api/app/services/signing_executor.py`: auto-provision certificates for non-demo orgs.
- `enterprise_api/app/services/embedding_executor.py`: auto-provision certificates for advanced signing.
- `enterprise_api/app/services/provisioning_service.py`: compare cert expiry in UTC to avoid naive/aware warnings.
- `enterprise_api/tests/test_certificate_provisioning.py`: regression test for naive expiry.
- `services/key-service/app/services/key_service.py`: drop certificate_pem join; fetch from auth-service.
- `services/key-service/tests/conftest.py`: simplify fixtures.
- `services/key-service/tests/test_validate_key_with_org.py`: align tests with auth-service certificate fetch.

## Blockers
- None.

## Handoff Notes
- Local E2E tests passing (`LOCAL_API_TESTS=true uv run pytest enterprise_api/tests/e2e_local`).
- Verify production internal tokens are configured so certificate provisioning can sync to auth-service.
- Verification: ✅ `uv run ruff check .`, ✅ `uv run pytest services/key-service/tests/test_validate_key_with_org.py`, ✅ `uv run pytest enterprise_api/tests/test_certificate_provisioning.py`.
