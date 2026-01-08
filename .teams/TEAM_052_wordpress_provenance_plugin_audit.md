# TEAM_052 — WordPress Provenance Plugin Audit

## Status
- Complete

## Current Goal
- Audit `integrations/wordpress-provenance-plugin` for correct Enterprise API/SDK usage and correct tier-based feature gating aligned with canonical pricing tiers and OpenAPI.

## Work Log
- [x] Create SSOT PRD in `PRDs/CURRENT/` for this audit
- [x] Map plugin API call flow (auth, endpoints, payloads, error handling)
- [x] Validate tier gating alignment vs `packages/pricing-config/src/tiers.ts`
- [x] Identify mismatches and implement fixes with tests
- [x] Run verification (lint/tests) and update docs

## Verification

- ✅ `uv run ruff check enterprise_api/tests/conftest.py enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`
- ✅ `uv run pytest -q enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`
- ✅ `uv run pytest -q enterprise_api/tests/test_account.py`

## Notes
- No automated test harness present in plugin directory yet (no `composer.json`, no `phpunit.xml`, no `package.json`).
- Enterprise API tests were initially failing due to a mismatched Postgres host port; fixed by reading `POSTGRES_HOST_PORT` (default `15432`) in `enterprise_api/tests/conftest.py`.
- Plugin tier handling is canonical-only (pre-release): `starter`, `professional`, `business`, `enterprise`.
