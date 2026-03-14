# PRD: User Service Audit Fixes

**Status:** COMPLETE
**Current Goal:** All audit findings implemented
**Branch:** feat/codebase-audit-fixes

## Overview
The audit agent already applied 8 simplify fixes (Pydantic v2, SQLAlchemy 2.0, dead metrics, connection pooling, etc.). This PRD covers remaining gaps: pagination on GET /teams, timing metadata, navigation hints.

## Objectives
- Add pagination to unbounded list endpoints
- Surface timing metadata in responses
- Add navigation hints to error responses

## Tasks

### 1.0 Overflow Protection
- [x] 1.1 Add pagination params (page, page_size with `le=` upper bound) to `GET /teams`
- [x] 1.2 Return pagination metadata in response

### 2.0 Metadata Footer
- [x] 2.1 Surface `duration_ms` from middleware in response header `X-Response-Time`

### 3.0 Navigation Error Hints
- [x] 3.1 Add hints to 401 errors with auth guidance
- [x] 3.2 Add hints to 503 errors (already partially fixed -- `str(e)` added)
- [x] 3.3 Add hints to 422 validation errors

### 4.0 Progressive Help
- [x] 4.1 Add capabilities summary to root/health endpoint

### 5.0 Linting
- [x] 5.1 Run ruff check and fix all issues
- [x] 5.2 Run ruff format

## Success Criteria
- All tasks checked off
- `ruff check .` and `ruff format --check .` pass on `services/user-service/`

## Completion Notes

All tasks implemented in one session. Key changes:

- `app/models/schemas.py`: Added `PaginatedResponse[T]` generic envelope (items, total, page, page_size, next_page).
- `app/api/v1/endpoints.py`:
  - `GET /teams` now accepts `page` (ge=1) and `page_size` (ge=1, le=200, default 50) query params and returns `PaginatedResponse[TeamResponse]`.
  - 401 detail is now a dict with `message` + `hint` (Bearer token format and how to obtain one).
  - 503 detail is now a dict with `message` + `hint` (retry guidance and health check URL).
  - Route docstrings enriched with parameter descriptions and examples.
- `app/middleware/logging.py`: Added `X-Response-Time` response header (value = duration_ms as string) on the success path.
- `app/main.py`:
  - Registered `RequestValidationError` handler returning 422 with field errors + `hint` pointing to /docs.
  - Added `_CAPABILITIES` dict (endpoint list, auth requirement, docs URL) surfaced in both `GET /` and `GET /health` responses.

`ruff check` and `ruff format` both pass with zero issues.
