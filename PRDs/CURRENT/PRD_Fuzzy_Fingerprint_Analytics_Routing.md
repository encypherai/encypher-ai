# PRD: Fuzzy Fingerprint Entitlement + Analytics Routing

**Status:** ✅ Complete
**Current Goal:** ✅ Completed — Fuzzy fingerprint entitlement + analytics routing fixes

## Overview

Enterprise fuzzy fingerprinting is gated by org feature flags, but Enterprise/Strategic Partner orgs are not receiving the `fuzzy_fingerprint` flag from auth-service. Separately, analytics routing conflicts send `/api/v1/analytics` requests to web-service, causing 404s for analytics-service endpoints. This PRD aligns entitlement flags and resolves analytics routing while preserving marketing analytics endpoints via a dedicated path.

## Objectives

- Ensure Enterprise+ orgs receive the `fuzzy_fingerprint` feature flag from auth-service.
- Route `/api/v1/analytics/*` requests to analytics-service without web-service conflicts.
- Preserve marketing analytics event ingestion on a dedicated web-service path.
- Maintain tests and documentation accuracy for updated paths and feature flags.

## Tasks

### 1.0 Feature Entitlements (Auth Service)
- [x] 1.1 Add `fuzzy_fingerprint` flag to Enterprise and Strategic Partner tier configs
- [x] 1.2 Add/extend tests for tier feature configuration — ✅ pytest

### 2.0 Analytics Routing & Marketing Events
- [x] 2.1 Move web-service marketing analytics endpoint to `/api/v1/marketing-analytics`
- [x] 2.2 Update API gateway routing to remove `/api/v1/analytics` from web-service
- [x] 2.3 Update web-service tests + docs for the new marketing analytics path — ✅ pytest

### 3.0 Testing & Validation
- [x] 3.1 Auth-service unit tests passing — ✅ pytest
- [x] 3.2 Web-service tests passing — ✅ pytest
- [x] 3.3 Lint checks passing — ✅ ruff

## Success Criteria

- Enterprise/Strategic Partner org contexts include `fuzzy_fingerprint` in features.
- `/api/v1/analytics/usage|timeseries|activity` routes to analytics-service without 404s.
- Marketing analytics events work under `/api/v1/marketing-analytics`.
- All tests pass with verification markers.

## Completion Notes

- Added `fuzzy_fingerprint` to enterprise/strategic partner tier configs and tests to assert entitlement.
- Moved marketing analytics ingestion to `/api/v1/marketing-analytics` and updated Traefik routing/docs/tests.
- Verification: ✅ `uv run pytest tests/test_organization_service.py` (auth-service), ✅ `uv run pytest tests/test_endpoints.py` (web-service), ✅ `uv run ruff check app/` (auth-service + web-service).
- Follow-up: re-sync existing Enterprise/Strategic Partner orgs via internal tier update to refresh feature flags if needed.
