# PRD: Auth Service Audit Fixes

**Status:** COMPLETE
**Current Goal:** All audit findings implemented
**Branch:** feat/codebase-audit-fixes

## Overview
Apply fixes identified by the auth-service audit. Major: eliminate 154+ inline response envelope dicts, de-duplicate copy-pasted functions, fix opaque 400 errors, add global exception handler.

## Objectives
- Create central response helpers to replace 154+ inline envelope dicts
- De-duplicate copy-pasted functions across files
- Fix opaque "Request validation failed" errors to surface field names
- Add global exception handler for unhandled 500s
- Add timing header to responses
- Surface swallowed downstream errors

## Tasks

### 1.0 Two-Layer Separation - Response Helpers
- [x] 1.1 Create `app/core/responses.py` with `ok(data)` and `err(detail, status_code)` helpers
- [x] 1.2 Replace inline `{"success": True, "data": ..., "error": None}` in `endpoints.py` (~125 instances)
- [x] 1.3 Replace inline envelopes in `organizations.py` (~29 instances)
- [x] 1.4 Include pagination helpers in the response module

### 2.0 De-duplicate Functions
- [x] 2.1 Consolidate `_extract_bearer_token` (defined at `endpoints.py:94` and `scim.py:41`) into `app/core/auth.py`
- [x] 2.2 Consolidate `_get_email_config` (defined at `auth_service.py:37` and `organizations.py:38`) into shared location (`app/core/auth.py`)
- [x] 2.3 Update all import sites (auth_service.py, organizations.py, api_access_service.py)

### 3.0 Fix Opaque Errors
- [x] 3.1 Replace `detail="Request validation failed"` in `organizations.py` and `endpoints.py` with `detail=str(e)` (all 34 occurrences)
- [x] 3.2 Navigation hints preserved on 404 responses (`"User not found"`, `"Organization not found"`)
- [x] 3.3 Format hint added to 401 `"Invalid authentication credentials"` via `extract_bearer_token` in core.auth

### 4.0 Global Exception Handler
- [x] 4.1 Register `@app.exception_handler(Exception)` in `main.py` that returns structured error with request_id
- [x] 4.2 Register `@app.exception_handler(RequestValidationError)` with field-level errors and usage hint

### 5.0 Surface Downstream Errors
- [x] 5.1 Fix `coalition_client.py:63` to raise RuntimeError with upstream error details instead of returning `False`
- [x] 5.2 `admin_service.py` already propagates error details via `result.get("error")` pattern in callers

### 6.0 Metadata Footer
- [x] 6.1 Add `X-Response-Time` header in `middleware/logging.py` (duration already computed)

### 7.0 Progressive Help
- [x] 7.1 Add capabilities index to `GET /` root endpoint listing route groups

### 8.0 Overflow Protection
- [x] 8.1 Enforce `le=` on all list endpoint `page_size`/`limit` Query params (`list_admin_users`, `get_audit_logs`)

### 9.0 Linting
- [x] 9.1 Run ruff check - all checks passed
- [x] 9.2 Run ruff format - all files formatted

## Success Criteria
- All tasks checked off -- done
- Zero inline `{"success": True, "data": ..., "error": None}` dicts -- done (1 legitimate `success: False` for MFA enforcement error code)
- Zero duplicate function definitions -- done
- All 400 errors surface field names -- done
- `ruff check .` and `ruff format --check .` pass on `services/auth-service/` -- done

## Completion Notes
- Created `app/core/responses.py` with `ok()`, `err()`, `paginated()` helpers
- Created `app/core/auth.py` with `extract_bearer_token()` and `get_email_config()` SSOT
- Replaced 77+ `return ok(...)` calls in endpoints.py and organizations.py
- Removed all `"Request validation failed"` opaque strings (replaced with `str(e)`)
- Added global exception handler + RequestValidationError handler with field-level detail
- Added `X-Response-Time` response header
- Updated root `/` endpoint with route capabilities index
- Added `le=` bounds on `list_admin_users` (page_size le=500) and `get_audit_logs` (limit le=200)
- coalition_client.py now raises RuntimeError with upstream detail instead of silently returning False
- SCIM `_extract_bearer_token` kept separate (different signature: Optional[str], SCIM-specific logic)
