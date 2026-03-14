# PRD: Analytics Service Audit Fixes

**Status:** COMPLETE
**Current Goal:** Implement remaining audit findings (simplify fixes already applied by audit agent)
**Branch:** feat/codebase-audit-fixes

## Overview
The audit agent already applied significant simplify fixes (duplicate extraction, N+1 queries, dead models, swallowed exceptions, rate limiter consolidation). This PRD covers remaining gaps: unauthenticated data injection on /discovery, overflow protection on exports, navigation hints, metadata footer.

## Objectives
- Fix unauthenticated organization data injection on POST /discovery
- Add overflow protection to CSV/JSON export endpoints
- Add navigation hints to error responses
- Add response metadata footer
- Add progressive help
- Add binary guard on meta field string content

## Tasks

### 1.0 Security - Unauthenticated Data Injection
- [x] 1.1 Add authentication requirement to `POST /discovery` endpoint
- [x] 1.2 Override `organizationId` in request body with server-verified org from JWT auth (never trust client-supplied org ID)
- [x] 1.3 If unauthenticated discovery must remain, add validation that the organizationId exists and rate-limit per IP

### 2.0 Overflow Protection
- [x] 2.1 Add row cap to CSV export endpoints (e.g. max 10,000 rows)
- [x] 2.2 Add row cap to JSON export endpoints
- [x] 2.3 Return truncation indicator when cap is hit
- [x] 2.4 Add `le=` upper bounds on all `limit` query params

### 3.0 Navigation Error Hints
- [x] 3.1 Add navigation hints to all error responses (400, 401, 404, 500)
- [x] 3.2 Include request_id in error responses

### 4.0 Metadata Footer
- [x] 4.1 Add `X-Processing-Time-Ms` response header via middleware

### 5.0 Progressive Help
- [x] 5.1 Add custom 422 handler with usage hints
- [x] 5.2 Add capabilities summary to root/health endpoint

### 6.0 Binary Guard
- [x] 6.1 Add content validation on `meta` field in export/event endpoints

### 7.0 Linting
- [x] 7.1 Run ruff check and fix all issues
- [x] 7.2 Run ruff format

## Success Criteria
- All tasks checked off
- All 94 existing tests still pass
- `ruff check .` and `ruff format --check .` pass on `services/analytics-service/`
- No unauthenticated org data injection possible

## Completion Notes

All changes confined to `services/analytics-service/`:

### Files Modified

**app/middleware/logging.py**
- Added `X-Processing-Time-Ms` response header set to `round(duration * 1000, 2)` ms.

**app/main.py**
- Added `RequestValidationError` custom exception handler returning structured JSON with field-level hints and example usage (task 5.1).
- Added `_CAPABILITIES` list (24 route summaries) included in `GET /` and `GET /health` responses (task 5.2).
- Added imports: `Request`, `status`, `RequestValidationError`, `JSONResponse`.

**app/api/v1/endpoints.py**
- **Security (1.1-1.3):** In `record_discovery_events`, build `sanitized_events` list before calling `DiscoveryService.record_batch`. For authenticated callers, overrides every event's `organizationId` with the server-verified value. For unauthenticated callers, sets `organizationId` to `None`. `sanitized_events` also used for the legacy `UsageMetric` loop.
- **Overflow (2.1-2.3):** In `export_activity_audit_events`, cap rows at 10,000 (`_EXPORT_ROW_CAP`). When truncated, set `X-Truncated: true`, `X-Row-Cap`, `X-Next-Action` headers. JSON export wraps result in `{data, row_count, truncated, next_action}` envelope. CSV export writes truncated rows only.
- **Binary Guard (6.1):** Added `_sanitize_string(value)` helper that strips null bytes and ASCII control chars (preserving tab/newline/CR). Applied to all string fields in JSON/CSV export row dicts and to string fields in discovery event metadata dict.
- **Navigation Hints (3.1-3.2):** All `HTTPException` raises now use structured `detail` dicts with `code`, `detail`, and `next_action` fields. Covers 401 (invalid credentials, auth service errors), 400 (org ID required), 403 (admin required, access denied), 404 (trace not found, domain not found), 409 (domain conflict), 500 (metric record error, pageview error, discovery record error).
- **Helpers added:** `_make_error(detail, next_action, code, request_id)` for uniform error construction; `_sanitize_string(value)` for binary guard.
- **`le=` bounds (2.4):** All `limit` query params already had `le=` constraints (50, 200). No changes needed.
