# Enterprise API Mypy Fixes

**Status:** ✅ Complete
**Current Goal:** All tasks complete — mypy/ruff/pytest verified

## Overview
The enterprise_api package must pass mypy cleanly before release tagging. Remaining typing issues are concentrated in service and router layers, especially around optional handling, Redis/HTTP responses, and embedding/merkle workflows. This PRD tracks the targeted fixes and verification steps required to reach a clean mypy run.

## Objectives
- Eliminate remaining mypy errors in enterprise_api application code.
- Preserve runtime behavior while tightening typing for Redis, HTTP, and segmentation utilities.
- Complete verification checks (ruff + mypy + pytest) for the enterprise_api scope.

## Tasks

### 1.0 Typing Fixes
- [x] 1.1 Resolve Redis/HTTP Any returns in services and middleware.
- [x] 1.2 Fix segmentation and hashing typing (normalize_for_hashing imports, Optional guards).
- [x] 1.3 Correct embedding/merkle workflow typing (return types, optional IDs, payload casts).
- [x] 1.4 Address router Optional guards (org identifiers, certificate checks, audit events).

### 2.0 Validation
- [x] 2.1 Re-run mypy until clean (enterprise_api scope).
- [x] 2.2 Re-run ruff check.
- [x] 2.3 Run pytest for enterprise_api (targeted as needed).

## Success Criteria
- `uv run mypy --config-file mypy.ini` returns no errors.
- `uv run ruff check .` passes.
- Relevant pytest runs complete with no failures.

## Completion Notes
- ✅ `uv run mypy app --no-pretty --hide-error-context --no-error-summary` (clean)
- ✅ `uv run ruff check .`
- ✅ `uv run pytest`
