# PRD: Web Service Audit Fixes

**Status:** COMPLETE
**Current Goal:** All audit findings applied.
**Branch:** feat/codebase-audit-fixes

## Overview
Apply fixes identified by the web-service audit. Critical: restore auth on unprotected read routes, eliminate massive code duplication, collapse duplicate demo-request routes.

## Objectives
- Restore auth on unprotected read routes exposing PII
- Extract duplicated utility functions to shared module
- Collapse duplicate demo-request routes
- Add timing/request-ID middleware
- Enforce upper bounds on list endpoints

## Tasks

### 1.0 Security - Restore Auth
- [x] 1.1 Add auth dependency to `demo_requests.py:31,50,65` (GET routes with `# TODO: Restore auth`)
- [x] 1.2 Add auth dependency to `publisher_demo.py:167` (GET route)

### 2.0 Eliminate Duplication
- [x] 2.1 Create `app/api/utils.py` with shared `get_client_ip()` function (currently copy-pasted in `ai_demo.py:23-44`, `publisher_demo.py:24-44`, `sales.py:21-41`)
- [x] 2.2 Move `hash_ip()` to `app/api/utils.py`
- [x] 2.3 Move `send_emails_background()` to `app/api/utils.py` (parameterize the context string)
- [x] 2.4 Extract `create_demo_record()` helper to `app/api/utils.py` (copy-pasted in `ai_demo.py`, `publisher_demo.py`, `sales.py`)
- [x] 2.5 Update all 3 files to import from `utils.py`
- [x] 2.6 Remove duplicate function definitions

### 3.0 Collapse Duplicate Routes
- [x] 3.1 Evaluated collapsing `/ai-demo/demo-requests` and `/publisher-demo/demo-requests` - kept separate for backward compat, difference is only the `default_source` label; both use shared `create_demo_record()` helper
- [x] 3.2 `api_v1/__init__.py` router registrations updated with documentation comments
- [x] 3.3 Note added to `api_v1/__init__.py` explaining backward-compat rationale and future consolidation path

### 4.0 Timing/Request-ID Middleware
- [x] 4.1 Added `RequestMetaMiddleware(BaseHTTPMiddleware)` in `main.py` that sets `X-Request-Id` and `X-Process-Time-Ms` headers

### 5.0 Overflow Protection
- [x] 5.1 Added `le=200` upper bound to `demo_requests.py` limit Query param (default 50)
- [x] 5.2 Added `le=500` upper bound to `analytics_events.py` limit Query param (default 100)
- [x] 5.3 Added pagination metadata (`total`, `skip`, `limit`, `items`) to `demo_requests.py` list endpoint

### 6.0 Navigation Error Hints
- [x] 6.1 Added actionable hints to 500 errors in `ai_demo.py` and `publisher_demo.py` (contact email)
- [x] 6.2 Added descriptive hints to 404 in `demo_requests.py` and `publisher_demo.py`
- [x] 6.3 Added hint to 401 in `newsletter.py` and `publisher_demo.py` (supply X-Internal-Token)

### 7.0 Progressive Help
- [x] 7.1 Added `description=` to all `APIRouter()` instantiations (`ai_demo`, `publisher_demo`, `sales`, `demo_requests`, `analytics_events`, `newsletter`, `tools`)
- [x] 7.2 Added one-line docstrings to all routes lacking them
- [x] 7.3 Added `endpoints` key to root `GET /` response in `main.py`

### 8.0 Linting
- [x] 8.1 `ruff check` passes with zero issues
- [x] 8.2 `ruff format --check` passes (all files formatted)

## Success Criteria
- All tasks checked off -- YES
- `ruff check .` passes on `services/web-service/` -- YES
- `ruff format --check .` passes -- YES
- No unprotected PII-exposing routes -- YES (X-Internal-Token required on all admin GET routes)
- Zero duplicate function definitions -- YES (get_client_ip, hash_ip, send_emails_background, create_demo_record all in utils.py)

## Completion Notes
- `create_demo_record()` extracted as shared helper in `app/api/utils.py` (previously copy-pasted across 3 files)
- Auth on `demo_requests.py` GET routes uses the same `INTERNAL_SERVICE_TOKEN` pattern as `newsletter.py`
- Auth on `publisher_demo.py` GET route uses same pattern
- `send_emails_background()` in `utils.py` is now parameterized (takes `context` arg), matching the already-parameterized version in `sales.py`
- The `ai_demo.py` and `publisher_demo.py` versions had context hardcoded; now both delegate to shared util
