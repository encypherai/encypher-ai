# TEAM_082: API Schema Rebrand

**Active PRD**: `PRDs/CURRENT/PRD_API_Schema_Rebrand.md`
**Working on**: Task 3.2
**Started**: 2026-01-17 15:21 UTC
**Status**: in_progress

## Session Progress
Reference PRD task numbers. Mark with test verification:
- [x] 1.1 — decisions locked
- [x] 2.1 — routes updated
- [x] 2.2 — chat routes updated
- [x] 2.3 — OpenAPI regenerated ✅ pytest
- [x] 2.4 — tests updated ✅ pytest
- [x] 3.1 — playground updated ✅ npm test:e2e
- [x] 3.3 — examples/docs updated
- [x] 4.1 — enterprise_api/README.md updated
- [x] 4.2 — sandbox strategy updated
- [x] 4.3 — docs/guides updated
- [ ] 3.2 — SDK regeneration pending
- [ ] 5.2 — mypy missing in env
- [ ] 5.4 — puppeteer (not run)

## Changes Made
- `enterprise_api/app/routers/streaming.py`: rebranded streaming routes to `/sign/stream` and session-scoped SSE.
- `enterprise_api/app/routers/chat.py`: rebranded OpenAI-compatible chat to `/chat/completions`.
- `enterprise_api/tests/*`: updated streaming tests to new paths.
- `apps/dashboard/src/lib/playgroundEndpoints.mjs`: updated streaming endpoint paths.
- `apps/dashboard/tests/e2e/playground.endpoints.contract.test.mjs`: updated contract expectations.
- `enterprise_api/docs/STREAMING_API.md`, `enterprise_api/docs/API.md`, `enterprise_api/app/routers/README_STREAMING.md`: updated docs.
- `enterprise_api/README.md`, `docs/company_internal_strategy/Encypher_API_Sandbox_Strategy.md`, `docs/pricing/PRICING_STRATEGY.md`, `docs/observability/ALERTS.md`: updated references.
- `enterprise_api/examples/websocket_client.py`, `enterprise_api/examples/websocket_client.js`: updated example URLs.
- `config/traefik/dynamic.yml`, `services/api-gateway/dynamic.yml`: updated routing.
- `STREAMING_FEATURES_SUMMARY.md`, `docs/postman/enterprise_api.postman_collection.json`: updated endpoints.

## Blockers
- SDK regeneration not run yet (requires `sdk/generate_sdk.py`).
- `mypy` not installed in current env (lint step blocked).

## Handoff Notes
- OpenAPI regenerated via `uv run python sdk/generate_openapi.py`.
- Tests: `uv run pytest enterprise_api/tests/test_stream_signing.py enterprise_api/tests/test_stream_runs_access_control.py enterprise_api/tests/test_openapi_docs_quality.py -vv` ✅
- Dashboard tests: `npm run test:e2e` ✅
- Lint: `uv run ruff check .` ✅, `npm run lint` (warnings only).
