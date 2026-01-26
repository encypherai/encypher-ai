# Enterprise API Mypy Errors Overview

**Status:** ✅ Complete
**Current Goal:** Restore clean enterprise_api mypy checks and verify tests.

## Overview
The enterprise_api codebase currently fails `uv run mypy .` due to script and auxiliary module typing errors. This PRD captures the error inventory and the fix plan needed to return the repo to a clean type-checking state.

## Objectives
- Record the current mypy error inventory and impacted files.
- Define remediation tasks for each error category.
- Restore a clean mypy run while preserving runtime behavior.

## Tasks

### 1.0 Error Inventory
- [x] 1.1 Capture current mypy output and map errors to files (scripts and tests).
- [x] 1.2 Confirm ownership/priority for script-only fixes versus application code fixes.

### 2.0 Remediation Plan
- [x] 2.1 Guard Optional settings.database_url usage in `scripts/verify_merkle_tables.py` and `scripts/run_merkle_migrations.py`.
- [x] 2.2 Fix `rowcount` typing usage in `scripts/prune_batch_requests.py` (SQLAlchemy Result typing).
- [x] 2.3 Resolve Async `sessionmaker` typing mismatch in `scripts/populate_demo_public_key.py`.
- [x] 2.4 Remove unused `type: ignore` or replace with typed import in `app/routers/coalition.py`.
- [x] 2.5 Fix `test_spacy_import.py` typing issues around `segment_sentences_default` call.
- [x] 2.6 Align batch script typing in `scripts/bench_batch_async.py` and `scripts/batch_smoke.py` (BatchItemStatus import, method assignment, execute_signing signatures, Optional response handling).

### 3.0 Testing & Validation
- [x] 3.1 Mypy clean run — ✅ `uv run mypy .`
- [x] 3.2 Lint clean run — ✅ `uv run ruff check .`
- [x] 3.3 Targeted pytest (enterprise_api) — ✅ `uv run pytest enterprise_api/tests`

## Success Criteria
- `uv run mypy .` completes with zero errors.
- Targeted tests pass with verification markers.
- No runtime regressions in enterprise_api scripts.

## Completion Notes
- Mypy, ruff, and enterprise_api pytest now pass after typing fixes across scripts, middleware, and test harness.
