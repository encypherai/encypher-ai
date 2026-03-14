# PRD: Key Service Audit Fixes

**Status:** COMPLETE
**Current Goal:** Fix privilege escalation vulnerability and implement audit findings
**Branch:** feat/codebase-audit-fixes

## Overview
Apply fixes identified by the key-service audit. CRITICAL: any authenticated user can self-assign super_admin permissions. Also: add navigation hints, pagination, response metadata, shared response layer.

## Objectives
- Close privilege escalation via unrestricted permission self-assignment
- Add server-side permission allowlist
- Add navigation hints to error responses
- Add pagination to list endpoint
- Add response metadata footer

## Tasks

### 1.0 Critical Security - Permission Allowlist
- [x] 1.1 Create a server-side permission allowlist constant (`ALLOWED_USER_PERMISSIONS = frozenset({"sign", "verify", "read"})` and `PRIVILEGED_PERMISSIONS = frozenset({"super_admin", "admin", "merkle"})`) in `key_service.py`
- [x] 1.2 Enforce allowlist in `update_key` handler before writing permissions to DB (via `_validate_permissions` + `caller_is_superadmin` param)
- [x] 1.3 Enforce allowlist in `create_key`/`generate` handler before writing permissions to DB (via `_validate_permissions` + `caller_is_superadmin` param)
- [x] 1.4 `ADMIN_PERMISSIONS = {"super_admin", "admin", "merkle"}` defined as `PRIVILEGED_PERMISSIONS`; require existing superadmin caller to assign them
- [x] 1.5 Return HTTP 403 with clear error if restricted permissions are requested (ValueError -> HTTPException 403 in both endpoints)

### 2.0 Navigation Error Hints
- [x] 2.1 Add navigation hints to all error responses (401, 403, 404, 500) via `make_error_body()` in `app/core/response.py`
- [x] 2.2 Include `request_id` in error responses (auto-generated UUID in `make_error_body`)

### 3.0 Overflow Protection
- [x] 3.1 Add pagination params to `GET /` list endpoint (`limit` and `offset` query params; `limit` clamped to 1-200)

### 4.0 Metadata Footer
- [x] 4.1 Add `X-Processing-Time-Ms` response header via `TimingMiddleware` in `app/middleware/timing.py`, registered in `main.py`

### 5.0 Two-Layer Separation
- [x] 5.1 Create shared error/success response helpers in `app/core/response.py` (`make_error_body`, `make_success_body`)
- [x] 5.2 All handlers use `make_error_body` for consistent error shapes; `_is_superadmin` helper centralises superadmin detection across all endpoints

### 6.0 Deployment Note
- [x] 6.1 Document in README: set `SUPERADMIN_USER_IDS` env var in all environments (with example and explanation of the two superadmin mechanisms)

### 7.0 Linting
- [x] 7.1 Run ruff check - all checks passed
- [x] 7.2 Run ruff format - all files formatted clean

## Success Criteria
- All tasks checked off
- No unrestricted permission assignment possible
- `ruff check .` and `ruff format --check .` pass on `services/key-service/`

## Completion Notes

All implemented in a single session. Key changes:

| File | Change |
|---|---|
| `app/services/key_service.py` | Added `ALLOWED_USER_PERMISSIONS`, `PRIVILEGED_PERMISSIONS`, `_validate_permissions()`; updated `create_key` and `update_key` to accept `caller_is_superadmin` and enforce allowlist |
| `app/api/v1/endpoints.py` | Added `_is_superadmin()` helper; passed `caller_is_superadmin` to service calls; added `limit`/`offset` pagination to `GET /`; replaced bare string errors with `make_error_body()` on all 401/403/404/500 paths; replaced all `current_user.get("is_super_admin")` with `_is_superadmin()` |
| `app/core/response.py` | New file: `make_error_body()` and `make_success_body()` with hint table and request_id |
| `app/middleware/timing.py` | New file: `TimingMiddleware` adds `X-Processing-Time-Ms` to every response |
| `app/main.py` | Registered `TimingMiddleware`; updated root `GET /` to return endpoint index |
| `README.md` | Documented `SUPERADMIN_USER_IDS` env var, updated architecture section |

Security fix summary: `_validate_permissions()` raises `ValueError` (-> HTTP 403) when a non-superadmin caller includes any value from `PRIVILEGED_PERMISSIONS` (`super_admin`, `admin`, `merkle`) in their requested permissions. The check runs before any DB write in both `create_key` and `update_key`. Superadmin status is determined by `_is_superadmin()` which combines the auth-service `is_super_admin` flag and the `SUPERADMIN_USER_IDS` config set.
