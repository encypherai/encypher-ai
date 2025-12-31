# WordPress Provenance Plugin Audit

**Status:** ✅ Complete
**Current Goal:** Complete verification and archive PRD.

## Overview

Audit `integrations/wordpress-provenance-plugin` to ensure it uses the correct Enterprise API endpoints/schemas and that WordPress feature gating accurately reflects the canonical product tier model. Produce a concrete mismatch list and implement safe, tested fixes where feasible.

## Objectives

- Ensure WordPress plugin calls align with `sdk/openapi.public.json` request/response schemas and auth requirements.
- Ensure tier gating maps correctly to canonical tiers in `packages/pricing-config/src/tiers.ts`.
- Add an automated verification baseline (tests/lint) appropriate to the plugin codebase and ensure repo verification passes.

## Tasks

### 1.0 Audit & Mapping

- [x] 1.1 Establish SSOT PRD + session log
- [x] 1.2 Map plugin API call flow (auth headers, endpoints, payloads, error handling)
- [x] 1.3 Map tier gating (admin + REST + JS) and produce mismatch list vs canonical pricing tiers + OpenAPI

### 2.0 Fixes

- [x] 2.1 Implement fixes for confirmed mismatches
- [x] 2.2 Add/update tests for fixes

### 3.0 Testing & Validation

- [x] 3.1 Unit tests passing — ✅ pytest (`uv run pytest -q enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`)
- [x] 3.2 Integration tests passing — ✅ pytest (`uv run pytest -q enterprise_api/tests/test_account.py`)
- [ ] 3.3 Frontend verification — N/A (no puppeteer/playwright harness found for this plugin)

## Success Criteria

- Plugin API calls match OpenAPI paths and schemas (or mismatches documented with remediation).
- Tier gating is consistent with canonical tiers and does not claim features unavailable for a tier.
- All required verification steps are completed with explicit markers.

## Completion Notes

Implemented and validated the WordPress provenance plugin audit fixes:

- Updated tier lookup to use documented `GET /api/v1/account` (no `/stats`).
- Enforced canonical tier IDs (`starter`, `professional`, `business`, `enterprise`) throughout plugin gating and UI.
- Hardened public verify handler to reject non-published posts.
- Fixed auto-mark setting key usage (`auto_mark_on_publish`).
- Fixed Enterprise API test DB port mismatch by deriving from `POSTGRES_HOST_PORT` (default `15432`).

Verification:
- ✅ `uv run ruff check enterprise_api/tests/conftest.py enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`
- ✅ `uv run pytest -q enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`
- ✅ `uv run pytest -q enterprise_api/tests/test_account.py`
