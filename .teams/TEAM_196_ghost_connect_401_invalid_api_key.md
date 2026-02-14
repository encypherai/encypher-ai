# TEAM_196: Ghost connect 401 invalid API key

**Active PRD**: `PRDs/CURRENT/PRD_Hosted_Ghost_Webhook_Endpoint.md`
**Working on**: Investigate/fix dashboard Ghost connect Step 2 unauthorized flow
**Started**: 2026-02-14 18:12 UTC
**Status**: completed

## Session Progress
- [x] 1.1 — baseline tests (pre-change) — ✅ pytest
- [x] 1.2 — identify root cause of dashboard Ghost connect 401
- [x] 2.1 — add regression tests for auth fallback path — ✅ pytest
- [x] 2.2 — implement minimal fix
- [x] 3.1 — post-change verification (pytest + ruff) — ✅ pytest ✅ ruff
- [ ] 3.2 — manual UI verification guidance (pending user-side dashboard check)

## Changes Made
- `enterprise_api/app/dependencies.py`: Added JWT access-token fallback org resolution (`_get_org_context_from_jwt_access_token`) and wired it into `get_current_organization` after key-service validation fallback.
- `enterprise_api/tests/test_demo_key_gating.py`: Added regression tests covering JWT auth with default org (success) and JWT without default org (401).

## Blockers
- Manual dashboard + Ghost connect UI verification (Step 2) still requires runtime env and user-side flow execution.

## Handoff Notes
- Root cause: Ghost integration endpoints use `require_sign_permission -> get_current_organization`, which previously only accepted API keys via key-service/demo-key fallback. Dashboard sends auth-service JWT bearer tokens (`session.user.accessToken`), causing 401 "Invalid API key" on `POST /api/v1/integrations/ghost`.
- Fix implemented by adding JWT fallback to resolve org context from `/api/v1/auth/verify` + internal org context lookup.
- Validation run:
  - `uv run pytest enterprise_api/tests/test_demo_key_gating.py` ✅
  - `uv run ruff check enterprise_api/app/dependencies.py enterprise_api/tests/test_demo_key_gating.py` ✅
  - `uv run pytest enterprise_api/tests/test_ghost_integration.py` ✅

## Suggested Commit Message
```
fix(enterprise_api): accept dashboard JWT auth for ghost integration endpoints

Root cause:
- Dashboard Ghost connect flow sends auth-service JWT bearer tokens.
- enterprise_api get_current_organization only validated API keys (key-service + demo fallback).
- POST /api/v1/integrations/ghost returned 401 "Invalid API key" during setup step 2.

Changes:
- Add _get_org_context_from_jwt_access_token() in app/dependencies.py
  - verifies bearer token via auth-service /api/v1/auth/verify
  - reads user's default_organization_id
  - fetches org context via internal auth-service organization context endpoint
  - normalizes org context for downstream permission checks
- Wire JWT fallback into get_current_organization() when key validation returns no org context
- Add regression tests in test_demo_key_gating.py:
  - accepts JWT with default organization
  - rejects JWT without default organization (401)

Verification:
- pytest enterprise_api/tests/test_demo_key_gating.py
- pytest enterprise_api/tests/test_ghost_integration.py
- ruff check enterprise_api/app/dependencies.py enterprise_api/tests/test_demo_key_gating.py
```
