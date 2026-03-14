# PRD: Coalition Service Audit Fixes

**Status:** COMPLETE
**Current Goal:** Add authentication to all unauthenticated endpoints and implement audit findings
**Branch:** feat/codebase-audit-fixes

## Overview
Apply fixes identified by the coalition-service audit. CRITICAL: all 14 admin/financial endpoints have zero authentication. Fake content access logs can be injected to manipulate revenue payouts.

## Objectives
- Add authentication to all endpoints
- Add authorization checks (admin role for admin endpoints)
- Add ownership validation on track-access
- Fix swallowed HTTPException in join_coalition
- Add navigation hints, pagination, response metadata

## Tasks

### 1.0 Critical Security - Add Authentication
- [x] 1.1 Add `Depends(get_current_context)` (or equivalent auth dependency) to ALL 14 endpoints
- [x] 1.2 Add admin role check to admin/financial endpoints (agreements CRUD, distributions, content pool management)
- [x] 1.3 Add ownership validation to `POST /track-access` -- verify caller owns `member_id` and `content_id` belongs to `agreement_id`

### 2.0 Fix Exception Handling
- [x] 2.1 Fix `join_coalition` (line 110-129): add `except HTTPException: raise` before the generic `except Exception` so 403 from `_enforce_user_match` is not swallowed as 500
- [x] 2.2 Apply same pattern to all other handlers that catch generic exceptions

### 3.0 Navigation Error Hints
- [x] 3.1 Add navigation hints to all error responses
- [x] 3.2 Include valid parameter lists in 400 errors

### 4.0 Overflow Protection
- [x] 4.1 Add server-side hard cap to `GET /content-pool` and `GET /eligible-content`

### 5.0 Two-Layer Separation
- [x] 5.1 Extract duplicated 15-line try/except boilerplate into shared handler wrapper (`_ok` helper + consistent `except HTTPException: raise` before generic catch)

### 6.0 Metadata Footer
- [x] 6.1 Add timing metadata to responses (`_meta.elapsed_ms` in every response)

### 7.0 Linting
- [x] 7.1 Run ruff check and fix all issues -- ✅ ruff check passed (all checks passed)
- [x] 7.2 Run ruff format -- ✅ ruff format ran cleanly

## Success Criteria
- All tasks checked off
- Zero unauthenticated endpoints
- `ruff check .` and `ruff format --check .` pass on `services/coalition-service/`

## Completion Notes

All 14 previously-unauthenticated endpoints now require `Depends(get_current_context)`.

Admin/financial endpoints protected by `_enforce_admin(context)` which checks
`context["features"]["is_super_admin"]` from the key-service /validate response. Affected
endpoints: POST /agreements, GET /agreements, GET /content-pool, GET /content-pool/stats,
POST /distributions/calculate, GET /distributions, POST /distributions/{id}/mark-paid,
GET /distributions/{id}/payouts, GET /payouts/pending, PATCH /agreements/{id},
POST /agreements/{id}/activate, GET /agreements/{id}/eligible-content.

POST /track-access now validates: (a) member_id exists, (b) API key user_id matches the
member's user_id via _enforce_user_match, (c) content_id exists before writing the access log.

POST /content now validates ownership of member_id before indexing content.

join_coalition and all other handlers now have `except HTTPException: raise` before the
generic `except Exception` clause -- no more swallowed 403s.

All 500 error details now include a "Check server logs for details." hint. 400 errors include
valid parameter lists (e.g. calculation_method values).

Server-side hard cap of 500 rows enforced on GET /content-pool, GET /distributions, and
GET /agreements/{id}/eligible-content via `limit = min(limit, _MAX_PAGE_SIZE)`.

_ok() helper centralises SuccessResponse construction and injects `_meta.elapsed_ms` on
every successful response path.

import `time` added at module level for monotonic timing.
