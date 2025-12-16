# PRD: Web Service DB Connection Fix

## Status
complete

## Current Goal
Fix `web-service` startup DB connection so it correctly honors Railway `DATABASE_URL` (and uses the same URL for Alembic migrations) while keeping local development behavior intact.

## Overview
`services/web-service` fails startup with `psycopg2.OperationalError` because it attempts to connect to `localhost:5432` when deployed, indicating the configured database URL is not being honored. We also currently hit `ModuleNotFoundError: encypher_commercial_shared`, which blocks running tests and importing `app.main`.

## Objectives
- Resolve `encypher_commercial_shared` import availability for `services/web-service` runtime and tests.
- Prefer `DATABASE_URL` (Railway) over `POSTGRES_*` assembly for SQLAlchemy URL construction.
- Ensure Alembic migrations run against the same resolved database URL.
- Add tests that lock in DB URL resolution precedence and normalization.

## Tasks
- [x] 1.0 Baseline verification
  - [x] 1.1 Capture current failing behavior via `uv run pytest` (web-service) ✅

- [x] 2.0 Fix shared library import (`encypher_commercial_shared`)
  - [x] 2.1 Identify current installation/path strategy for `services/web-service` ✅
  - [x] 2.2 Make `encypher-commercial-shared` importable in both runtime + pytest ✅
  - [x] 2.3 Verify: `uv run python -c "import encypher_commercial_shared"` ✅

- [x] 3.0 DB URL resolution (TDD)
  - [x] 3.1 Add tests to ensure `DATABASE_URL` wins over `POSTGRES_*` ✅
  - [x] 3.2 Add tests to normalize `postgres://` -> `postgresql+psycopg2://` (if present) ✅
  - [x] 3.3 Implement config changes in `app/core/config.py` ✅

- [x] 4.0 Alembic alignment
  - [x] 4.1 Ensure Alembic uses the same resolved URL (including `DATABASE_URL`) ✅
  - [x] 4.2 Add/adjust tests (where practical) to prevent regression ✅

- [x] 5.0 Verification
  - [x] 5.1 `uv run ruff check .` ✅
  - [x] 5.2 `uv run pytest` ✅

## Success Criteria
- `services/web-service` uses Railway-provided `DATABASE_URL` in production (no `localhost:5432` attempts unless explicitly configured).
- Alembic migrations run against the same DB URL used by the application.
- `uv run pytest` passes for `services/web-service`.

## Completion Notes
- Fixed `web-service` configuration to honor Railway `DATABASE_URL` over assembled `POSTGRES_*` settings and normalized `postgres://` to `postgresql+psycopg2://`.
- Aligned startup migration checks to run against the same resolved DB URL by passing the resolved URL through `ensure_database_ready()` into `run_migrations_if_needed()`.
- Added tests to prevent regressions:
  - `tests/test_db_url_resolution.py` for precedence + normalization
  - `tests/test_db_startup_migrations.py` for migration URL alignment
- Verified: `uv run ruff check .` ✅ and `uv run pytest` ✅ in `services/web-service`.
