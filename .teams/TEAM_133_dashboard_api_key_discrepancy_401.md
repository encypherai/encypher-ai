# TEAM_133: Dashboard API key discrepancy + 401 + Railway routing + key-service 500

**Active PRD**: `PRDs/ARCHIVE/PRD_Dashboard_API_Key_Discrepancy_401.md`
**Working on**: 1.0→2.0→3.0
**Started**: 2026-01-26 20:23 UTC
**Status**: completed (2026-01-27 14:00 UTC)

## Session Progress
- [x] 1.1 — baseline tests (pre-change) — ✅ pytest
- [x] 1.2 — identify dashboard overview vs api-keys endpoint mismatch
- [x] 1.3 — identify why new keys return 401 invalid api key
- [x] 2.1 — tests for URL normalization + correct auth behavior — ✅ pytest
- [x] 2.2 — fix dashboard overview to scope keys by active org — ✅ puppeteer
- [x] 2.3 — fix enterprise_api key-service URL handling / error behavior — ✅ pytest
- [x] 3.1 — Railway env var investigation via CLI — ✅ validated
- [x] 3.2 — Fix key-service 500 error (production DB missing `organizations.certificate_pem`) — ✅ pytest

## Changes Made
- `enterprise_api/app/middleware/api_key_auth.py`: Normalize key-service base URL and return 503 (not misleading 401) when key-service can't validate new-style `ency_` keys
- `enterprise_api/tests/test_api_key_auth.py`: Add tests for key-service validation success/unavailable and URL normalization
- `apps/dashboard/src/app/page.tsx`: Scope dashboard overview API key list to active organization
- `scripts/example_advanced_sign.py`: Fix ruff UP015
- `services/key-service/app/services/key_service.py`: Make `verify_key_with_org()` schema-compatible by retrying query without `certificate_pem` when DB column is missing; safely read `certificate_pem` via `getattr(..., None)`
- `services/key-service/tests/test_validate_key_with_org.py`: Add test coverage for missing-column fallback
- `services/key-service/tests/conftest.py`: Add mock DB simulating missing column; ensure shared libs import path for tests

## Railway Investigation Results (2026-01-27)
**Validated via `railway variables --json`:**
- ✅ `AUTH_SERVICE_URL` = `http://auth-service.railway.internal:8080`
- ✅ `KEY_SERVICE_URL` = `http://key-service.railway.internal:8080`
- ✅ All services use Railway internal DNS with correct port `:8080`
- ✅ Public API domain `https://api.encypher.com` used by clients (Dashboard)
- ✅ Traefik routing config matches Railway internal URLs
- **Conclusion**: Dual public/private routing setup is optimal and production-ready

## Blockers
- None

## Handoff Notes
- Original issue: Overview used unscoped key list; enterprise-api had misconfigured key-service URL causing fallback to legacy DB + misleading 401
- Railway routing: Already optimal, no migration needed
- New bug found: key-service 500 error due to production DB missing `organizations.certificate_pem` (fixed via fallback query)
- Deployment note: api.encypher.com will continue returning 401 until Railway `key-service` (and any callers) are redeployed with this change

## Follow-on (2026-01-27)
- [x] Fix enterprise-api /api/v1/sign/advanced NO_PRIVATE_KEY details showing "Organization <id> not found" when COMPOSE_ORG_CONTEXT_VIA_AUTH_SERVICE=true (org lives in auth-service)
- [x] Ensure enterprise-api bootstraps a minimal local organizations row before signing key/template lookups
- [x] Regression test added for composed-org bootstrap path — ✅ pytest
- [x] Verification — ✅ `uv run pytest` (enterprise_api) ✅ `uv run ruff check` (enterprise_api)
- Commit: `abfeb79`
