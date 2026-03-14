# PRD: Billing Service Audit Fixes

**Status:** COMPLETE
**Current Goal:** All audit findings implemented
**Branch:** feat/codebase-audit-fixes

## Overview
The audit agent already applied significant fixes: fail-open auth bypass fixed, dead code removed, broken tests fixed, N+1 queries resolved. This PRD covers remaining unix-agent-design gaps.

## Objectives
- Add navigation hints to error responses
- Add response metadata footer
- Add overflow protection to list endpoints
- Surface swallowed exception details

## Tasks

### 1.0 Navigation Error Hints
- [x] 1.1 Add navigation hints to all 400/404/500 error responses
- [x] 1.2 Include next-action guidance in error detail

### 2.0 Metadata Footer
- [x] 2.1 Surface `duration_ms` (already logged in middleware) as `X-Processing-Time-Ms` response header

### 3.0 Overflow Protection
- [x] 3.1 Add `le=` upper bound to `/invoices` limit param (now Query(default=20, ge=1, le=100))
- [x] 3.2 Add pagination metadata to `/coalition` responses

### 4.0 Exception Handling
- [x] 4.1 Surface exception details in 500 responses at checkout/add-on/portal endpoints instead of bare `except Exception`
- [x] 4.2 Add `except HTTPException: raise` before generic catches

### 5.0 Progressive Help
- [x] 5.1 Add capabilities summary to root/health endpoint

### 6.0 Linting
- [x] 6.1 Run ruff check and fix all issues
- [x] 6.2 Run ruff format

## Success Criteria
- All tasks checked off -- done
- All 9 tests still pass -- not run per instructions (will be verified separately)
- `ruff check .` and `ruff format --check .` pass on `services/billing-service/` -- PASS

## Completion Notes

### Files Changed
- `app/middleware/logging.py`: Added `X-Processing-Time-Ms` header alongside `X-Request-ID`
- `app/main.py`: Enhanced root endpoint with capabilities list, docs/openapi/health URLs; health endpoint also includes docs/openapi links
- `app/api/v1/endpoints.py`:
  - `/invoices`: changed limit from bare `int = 100` to `Query(default=20, ge=1, le=100)`
  - `/coalition`: added `pagination` key with `returned` count and a descriptive `note` to all response paths
  - `checkout`, `checkout/add-on`, `portal`: added `except HTTPException: raise` guards before generic `except Exception as e`, surfaced `type(e).__name__` in 500 detail, added logger.error calls
  - All 400/404/503 errors now include next-action guidance (valid values, endpoint URLs, contact info)
  - Auth 401/503 errors include actionable hints
  - `create_subscription` and internal trial 400s now include `str(e)` in detail
