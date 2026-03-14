# PRD: Encoding Service Audit Fixes

**Status:** COMPLETE
**Current Goal:** All audit findings implemented
**Branch:** feat/codebase-audit-fixes

## Overview
Apply fixes identified by the encoding-service audit. Critical: remove hardcoded private key, add binary guard, improve error navigation, add response metadata.

## Objectives
- Remove hardcoded demo private key from source
- Add binary content guard on text inputs
- Add navigation hints to all error responses
- Surface processing time in responses
- Add overflow guard on list endpoints
- Separate presentation logic from business logic

## Tasks

### 1.0 Critical Security
- [x] 1.1 Remove `DEMO_PRIVATE_KEY` hardcoded Ed25519 key from `endpoints.py:25-27` -- load from env/secrets manager
- [x] 1.2 Add `.env.example` entry for the key if needed

### 2.0 Binary Content Guard
- [x] 2.1 Add `validate_text_content()` check for null bytes and control chars at `endpoints.py:101` (before `sign_document`)
- [x] 2.2 Add same guard at `endpoints.py:149` (before `embed_metadata`)
- [x] 2.3 Return HTTP 400 with clear error message for binary content

### 3.0 Navigation Error Hints
- [x] 3.1 Add `hint` field to 401 responses (`endpoints.py:39-42`, `endpoints.py:73-76`)
- [x] 3.2 Add `hint` field to 403 response (`endpoints.py:80-83`)
- [x] 3.3 Add `hint` field to 404 responses (`endpoints.py:200-203`, `endpoints.py:220-223`)
- [x] 3.4 Add `hint` field to 500 responses (`endpoints.py:122-125`, `endpoints.py:165-168`)
- [x] 3.5 Add `hint` field to 503 response (`endpoints.py:46-49`)
- [x] 3.6 Include request_id in error responses

### 4.0 Metadata Footer
- [x] 4.1 Surface `processing_time` (already computed at `encoding_service.py:99`) in `SignedDocumentResponse`
- [x] 4.2 Add `X-Processing-Time-Ms` response header via middleware or per-handler

### 5.0 Overflow Protection
- [x] 5.1 Cap `limit` param on `GET /documents` (`endpoints.py:182`) with `le=50`
- [x] 5.2 Return only document IDs/hashes in list responses, not full content

### 6.0 Two-Layer Separation
- [x] 6.1 Create shared error response helper (e.g. `make_error(status, detail, hint, request_id)`)
- [x] 6.2 Create shared success response wrapper

### 7.0 Progressive Help
- [x] 7.1 Add custom 422 exception handler in `main.py` with usage hint
- [x] 7.2 Add endpoint enumeration to root `GET /` response

### 8.0 Linting
- [x] 8.1 Run ruff check and fix all issues
- [x] 8.2 Run ruff format

## Success Criteria
- All tasks checked off
- `ruff check .` passes on `services/encoding-service/`
- `ruff format --check .` passes
- No hardcoded secrets in source

## Completion Notes

All tasks completed in a single session. Key changes:

**Security (1.0):**
- Removed `DEMO_PRIVATE_KEY` constant from `endpoints.py`
- Added `SIGNING_PRIVATE_KEY: str = ""` to `Settings` in `config.py`
- Added entry to `.env.example` with guidance to use a secrets manager in production
- `endpoints.py` now reads key from `settings.SIGNING_PRIVATE_KEY` and returns HTTP 500 if unconfigured

**Binary Guard (2.0):**
- `_validate_text_content()` helper in `endpoints.py` checks for null bytes and C0 control chars (except tab/LF/CR)
- Called before `sign_document` and before `embed_metadata`
- Returns HTTP 400 with `detail` + `hint` on failure

**Error Hints (3.0):**
- All error paths now call `make_error(status_code, detail, hint, request)` from `responses.py`
- `request_id` extracted from `request.state.request_id` (set by `RequestLoggingMiddleware`)
- 401, 403, 404, 500, 503 all carry `hint` and `request_id`

**Metadata Footer (4.0):**
- `SignedDocumentResponse` has new optional `processing_time_ms: Optional[float]` field
- `/sign` handler returns a raw `Response` with `X-Processing-Time-Ms` header

**Overflow Protection (5.0):**
- `limit` query param now uses `Query(default=20, ge=1, le=50)`
- `GET /documents` and `GET /documents/{id}` both return `DocumentSummary` (no full content)
- New `DocumentSummary` schema added to `schemas.py`

**Two-Layer Separation (6.0):**
- New module `app/api/v1/responses.py` with `make_error()` and `make_success()` helpers
- All error construction moved out of inline `HTTPException` raises into `make_error`

**Progressive Help (7.0):**
- Custom `RequestValidationError` handler in `main.py` returns hint + request_id on 422
- `GET /` now returns `endpoints` list of all routes with method/path/description

**Linting (8.0):**
- `ruff check` passes clean
- `ruff format` applied (2 files reformatted)
