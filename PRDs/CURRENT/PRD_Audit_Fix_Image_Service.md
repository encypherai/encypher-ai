# PRD: Image Service Audit Fixes

**Status:** COMPLETE
**Current Goal:** All audit findings implemented
**Branch:** feat/codebase-audit-fixes

## Overview
The audit agent already applied simplify fixes (extracted helpers, navigation hints, named constants, dead code removal). This PRD covers the remaining gaps: enforce image size limit, add magic-byte guard, add hex validator, add timing middleware.

## Objectives
- Enforce the defined but unused MAX_IMAGE_SIZE_BYTES limit
- Add image magic-byte validation before PIL.Image.open()
- Add hex-only pattern validator on message_bits field
- Add processing time middleware

## Tasks

### 1.0 Enforce Size Limit
- [x] 1.1 Add size check in `_decode_image_b64()` against `MAX_IMAGE_SIZE_BYTES` from config
- [x] 1.2 Return HTTP 413 with clear error message

### 2.0 Binary/Image Guard
- [x] 2.1 Add image magic-byte check (JPEG, PNG, WebP, etc.) before `PIL.Image.open()`
- [x] 2.2 Return HTTP 400 with supported format list on invalid magic bytes

### 3.0 Input Validation
- [x] 3.1 Add hex-only pattern validator on `message_bits` field in request schema
- [x] 3.2 Return HTTP 422 with format hint on invalid input

### 4.0 Metadata Footer
- [x] 4.1 Add `BaseHTTPMiddleware` for `X-Processing-Time-Ms` on all response paths

### 5.0 Linting
- [x] 5.1 Run ruff check and fix all issues
- [x] 5.2 Run ruff format

## Success Criteria
- All tasks checked off
- All 19 existing tests still pass
- `ruff check .` and `ruff format --check .` pass on `services/image-service/`

## Completion Notes

All four features implemented. Files changed:
- `app/routers/watermark.py`: added `_MAGIC_*` constants, `_check_magic_bytes()`, size check and magic-byte check inside `_decode_image_b64()`; imported `settings` from config.
- `app/schemas/watermark_schemas.py`: added `pattern=r"^[0-9a-fA-F]{26}$"` to `message_bits` Field.
- `app/main.py`: added `ProcessingTimeMiddleware(BaseHTTPMiddleware)` that sets `X-Processing-Time-Ms` on every response; registered with `app.add_middleware()`.
- `ruff check` and `ruff format` both pass clean.
