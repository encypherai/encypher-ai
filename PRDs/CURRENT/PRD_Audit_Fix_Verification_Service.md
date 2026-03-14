# PRD: Verification Service Audit Fixes

**Status:** COMPLETE
**Current Goal:** Implement all audit findings from unix-agent-design, simplify, and security reviews
**Branch:** feat/codebase-audit-fixes

## Overview
Apply fixes identified by the verification-service audit. Major: break up 730-line verify_text function, extract duplicate fallback blocks, consolidate portal routes, fix inline HTML XSS risk.

## Objectives
- Break up monolithic verify_text function into extracted helpers
- Consolidate three near-identical fallback blocks into one parameterized helper
- Merge duplicate portal routes
- Move inline HTML to templates (fix XSS risk)
- Add binary guard, overflow protection, navigation hints

## Tasks

### 1.0 Security - Inline HTML XSS
- [x] 1.1 Move inline HTML templates from `endpoints.py:1257-1287` and `endpoints.py:1325-1357` to `app/templates/` or a render helper
- [x] 1.2 Ensure all user-controlled values (`document_id`, `title`) are properly escaped
- [x] 1.3 Add `Accept` header negotiation so programmatic callers get JSON instead of HTML

### 2.0 Break Up verify_text (730 lines)
- [x] 2.1 Extract `_run_zw_fallback()` from the ZW detection block
- [x] 2.2 Extract `_run_vs256_fallback()` from the VS256 detection block
- [x] 2.3 Extract `_run_legacy_safe_fallback()` from the legacy-safe detection block
- [x] 2.4 Extract `_build_verdict()` from the verdict-building block (`endpoints.py:1085-1184`)
- [x] 2.5 Parameterize the three fallback functions into a single `_run_embedding_fallback(ids, detect_label, logger)` helper; all three fallbacks delegate to it

### 3.0 Consolidate Portal Routes
- [x] 3.1 Merge `GET /{document_id}`, `GET /demo/{document_id}`, `GET /api/v1/verify/{document_id}` into one route with optional prefix
- [x] 3.2 Update `main.py:88-101` route registrations

### 4.0 Deprecate Legacy Endpoints
- [x] 4.1 Mark `POST /verify/signature` and `POST /verify/document` as deprecated
- [x] 4.2 Add redirect hints to primary `POST /api/v1/verify`
- [x] 4.3 Merge status list proxy routes (10 and 11) via shared `_proxy_status_list` helper

### 5.0 Binary Content Guard
- [x] 5.1 Add null-byte and binary content check on `verify_request.text` before main verification path
- [x] 5.2 Return `ERR_BINARY_INPUT` with hint

### 6.0 Overflow Protection
- [x] 6.1 Cap `details.manifest` at safe size (50KB serialized)
- [x] 6.2 Add `manifest_truncated: true` flag when truncated

### 7.0 Navigation Error Hints
- [x] 7.1 Populate `hint` field for all non-OK reason codes (`SIGNER_UNKNOWN`, `CERT_NOT_FOUND`, `UNTRUSTED_SIGNER`)
- [x] 7.2 Add navigation hints to legacy endpoint 500 errors
- [x] 7.3 Add structured JSON error for 404 portal responses
- [x] 7.4 Attach `error_detail` to proxy error responses

### 8.0 Metadata Footer
- [x] 8.1 Add `duration_ms` to `VerifyResponse` schema for all return paths (including errors)
- [x] 8.2 Add custom 422 handler with usage example

### 9.0 Linting
- [x] 9.1 Run ruff check and fix all issues
- [x] 9.2 Run ruff format

## Success Criteria
- All tasks checked off
- `verify_text` broken into <100-line functions
- Zero inline HTML string interpolation with user data
- `ruff check .` and `ruff format --check .` pass on `services/verification-service/`

## Completion Notes

All tasks complete. Key changes:

- **Templates**: HTML moved to `app/templates/portal_not_found.html` and `portal_result.html`;
  all user-controlled values escaped via `html.escape()` before rendering.
- **Accept negotiation**: Portal routes return JSON when `Accept: application/json` is sent.
- **verify_text refactored**: Extracted helpers:
  - `_resolve_org_context()` - org credentials + trust anchor resolution (async)
  - `_run_zw_fallback()`, `_run_vs256_fallback()`, `_run_legacy_safe_fallback()` - embedding fallbacks
  - `_run_embedding_fallback()` - shared parameterized core (~40 lines)
  - `_build_verdict()` - verdict assembly
  - `_try_c2pa_fallback()` - C2PA wrapper verification
  - `_try_ws_normalized_retry()` - whitespace normalization retry
  - `_build_embedding_details()` - EmbeddingDetail construction
- **Portal routes**: Both `/{document_id}` and `/demo/{document_id}` delegate to same handler.
- **Status proxy**: Shared `_proxy_status_list()` used by both UUID and legacy routes.
- **Binary guard**: Checks for null bytes / low control chars before verification.
- **Manifest cap**: 50KB cap with `manifest_truncated: true` flag in details.
- **Hints**: `SIGNER_UNKNOWN`, `CERT_NOT_FOUND`, `UNTRUSTED_SIGNER` all have hint text.
- **duration_ms**: Added to `VerifyResponse` schema; populated on all return paths.
- **422 handler**: Custom handler in `main.py` with usage example.
- **Legacy deprecation**: `/signature` and `/document` marked `deprecated=True` with migration hint.
- **ruff**: All checks pass, format clean.
