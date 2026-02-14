# TEAM_196: Ghost connect 401 invalid API key

**Active PRD**: `PRDs/CURRENT/PRD_Hosted_Ghost_Webhook_Endpoint.md`
**Working on**: Investigate/fix dashboard Ghost connect Step 2 unauthorized flow
**Started**: 2026-02-14 18:12 UTC
**Status**: completed

## Session Progress
- [x] 1.1 — baseline tests (pre-change) — ✅ pytest
- [x] 1.2 — identify root cause of dashboard Ghost connect 401
- [x] 2.1 — add regression tests for auth fallback path — ✅ pytest
- [x] 2.2 — implement minimal fix
- [x] 3.1 — post-change verification (pytest + ruff) — ✅ pytest ✅ ruff
- [ ] 3.2 — manual UI verification guidance (pending user-side dashboard check)

## Changes Made
- `enterprise_api/app/dependencies.py`: Added JWT access-token fallback org resolution (`_get_org_context_from_jwt_access_token`) and wired it into `get_current_organization` after key-service validation fallback.
- `enterprise_api/tests/test_demo_key_gating.py`: Added regression tests covering JWT auth with default org (success) and JWT without default org (401).

## Blockers
- Manual dashboard + Ghost connect UI verification (Step 2) still requires runtime env and user-side flow execution.

## Handoff Notes
- Root cause: Ghost integration endpoints use `require_sign_permission -> get_current_organization`, which previously only accepted API keys via key-service/demo-key fallback. Dashboard sends auth-service JWT bearer tokens (`session.user.accessToken`), causing 401 "Invalid API key" on `POST /api/v1/integrations/ghost`.
- Fix implemented by adding JWT fallback to resolve org context from `/api/v1/auth/verify` + internal org context lookup.
- Validation run:
  - `uv run pytest enterprise_api/tests/test_demo_key_gating.py` ✅
  - `uv run ruff check enterprise_api/app/dependencies.py enterprise_api/tests/test_demo_key_gating.py` ✅
  - `uv run pytest enterprise_api/tests/test_ghost_integration.py` ✅

## Suggested Commit Message
```
fix(enterprise_api): accept dashboard JWT auth for ghost integration endpoints

Root cause:
- Dashboard Ghost connect flow sends auth-service JWT bearer tokens.
- enterprise_api get_current_organization only validated API keys (key-service + demo fallback).
- POST /api/v1/integrations/ghost returned 401 "Invalid API key" during setup step 2.

Changes:
- Add _get_org_context_from_jwt_access_token() in app/dependencies.py
  - verifies bearer token via auth-service /api/v1/auth/verify
  - reads user's default_organization_id
  - fetches org context via internal auth-service organization context endpoint
  - normalizes org context for downstream permission checks
- Wire JWT fallback into get_current_organization() when key validation returns no org context
- Add regression tests in test_demo_key_gating.py:
  - accepts JWT with default organization
  - rejects JWT without default organization (401)

Verification:
- pytest enterprise_api/tests/test_demo_key_gating.py
- pytest enterprise_api/tests/test_ghost_integration.py
- ruff check enterprise_api/app/dependencies.py enterprise_api/tests/test_demo_key_gating.py
```

## 2026-02-14 Follow-up: Production Alembic idempotency hardening
- [x] 4.1 — reproduce/triage production startup failure on `add_org_certificate_metadata`
- [x] 4.2 — add regression tests first (TDD red/green) — ✅ pytest
- [x] 4.3 — implement minimal idempotent migration fix
- [x] 4.4 — verify targeted suite + lint — ✅ pytest ✅ ruff
- [x] 4.5 — push production fix to `main`

### Root Cause
- `add_org_certificate_metadata` used unconditional `op.add_column(...)` for `organizations.certificate_status` and `organizations.certificate_rotated_at`.
- In production, `certificate_status` already existed, so Alembic failed with `DuplicateColumn` during startup migration.

### Files Changed
- `enterprise_api/alembic/versions/add_org_certificate_metadata.py`
  - Added `_has_column(...)` guard using SQLAlchemy inspector.
  - Wrapped `op.add_column(...)` calls in existence checks.
  - Kept `op.alter_column(..., server_default=None)` behavior intact.
- `enterprise_api/tests/test_org_certificate_metadata_migration_idempotency.py` (new)
  - Verifies upgrade skips already existing columns.
  - Verifies upgrade adds missing columns.

### Verification
- `uv run pytest enterprise_api/tests/test_org_certificate_metadata_migration_idempotency.py enterprise_api/tests/test_licensing_migration_idempotency.py enterprise_api/tests/test_alembic_revision_chain.py enterprise_api/tests/test_db_startup_migration_strategy.py` ✅
- `uv run ruff check enterprise_api/alembic/versions/add_org_certificate_metadata.py enterprise_api/tests/test_org_certificate_metadata_migration_idempotency.py` ✅

### Pushed
- Commit: `55c3451c`
- Branch: `main`
- Remote: `origin/main`

### Comprehensive Commit Message Suggestion
```
fix(enterprise_api): make org certificate metadata migration idempotent

Root cause:
- Production startup runs Alembic on boot.
- Migration add_org_certificate_metadata performed unconditional ADD COLUMN on organizations.
- Environments with partially pre-provisioned schema already had certificate_status,
  causing DuplicateColumn and startup crash.

Changes:
- Add schema inspector helper in add_org_certificate_metadata migration.
- Guard certificate_status and certificate_rotated_at add_column calls with
  existence checks.
- Preserve server_default cleanup on certificate_status via alter_column.
- Add regression tests for migration idempotency:
  - skip when both columns already exist
  - add when columns are missing

Verification:
- pytest enterprise_api/tests/test_org_certificate_metadata_migration_idempotency.py
- pytest enterprise_api/tests/test_licensing_migration_idempotency.py
- pytest enterprise_api/tests/test_alembic_revision_chain.py
- pytest enterprise_api/tests/test_db_startup_migration_strategy.py
- ruff check enterprise_api/alembic/versions/add_org_certificate_metadata.py
- ruff check enterprise_api/tests/test_org_certificate_metadata_migration_idempotency.py
```

## 2026-02-14 Follow-up 2: add_kms_support DuplicateColumn hardening
- [x] 5.1 — triage startup failure at `add_kms_support` (`organizations.kms_key_id` already exists)
- [x] 5.2 — add regression tests first — ✅ pytest
- [x] 5.3 — implement idempotent guard in migration
- [x] 5.4 — verify targeted suite + lint — ✅ pytest ✅ ruff
- [x] 5.5 — push production fix to `main`

### Root Cause
- `add_kms_support` used unconditional `op.add_column(...)` calls for `kms_key_id` and `kms_region`.
- Production schema already had `kms_key_id`, triggering `DuplicateColumn` and crashing app startup during Alembic upgrade.

### Files Changed
- `enterprise_api/alembic/versions/add_kms_support.py`
  - Added `_has_column(...)` via SQLAlchemy inspector.
  - Guarded `kms_key_id` and `kms_region` column adds.
- `enterprise_api/tests/test_kms_support_migration_idempotency.py` (new)
  - Validates upgrade skips existing KMS columns.
  - Validates upgrade adds missing KMS columns.

### Verification
- `uv run pytest enterprise_api/tests/test_kms_support_migration_idempotency.py enterprise_api/tests/test_org_certificate_metadata_migration_idempotency.py enterprise_api/tests/test_licensing_migration_idempotency.py enterprise_api/tests/test_alembic_revision_chain.py enterprise_api/tests/test_db_startup_migration_strategy.py` ✅
- `uv run ruff check enterprise_api/alembic/versions/add_kms_support.py enterprise_api/tests/test_kms_support_migration_idempotency.py` ✅

### Comprehensive Commit Message Suggestion
```
fix(enterprise_api): make add_kms_support migration idempotent

Root cause:
- Production startup runs Alembic upgrades.
- add_kms_support migration unconditionally added organizations.kms_key_id.
- Some environments already had the column, causing DuplicateColumn and startup failure.

Changes:
- Add schema inspection helper to add_kms_support migration.
- Guard kms_key_id and kms_region add_column operations with existence checks.
- Add regression tests to ensure migration safely skips existing columns and adds missing ones.

Verification:
- pytest enterprise_api/tests/test_kms_support_migration_idempotency.py
- pytest enterprise_api/tests/test_org_certificate_metadata_migration_idempotency.py
- pytest enterprise_api/tests/test_licensing_migration_idempotency.py
- pytest enterprise_api/tests/test_alembic_revision_chain.py
- pytest enterprise_api/tests/test_db_startup_migration_strategy.py
- ruff check enterprise_api/alembic/versions/add_kms_support.py
- ruff check enterprise_api/tests/test_kms_support_migration_idempotency.py
```

## 2026-02-14 Follow-up 3: add_batch_requests enum idempotency + Railway log-rate hardening
- [x] 6.1 — local-first triage of `DuplicateObject` on `batch_request_type`
- [x] 6.2 — add regression tests first for batch migration idempotency — ✅ pytest
- [x] 6.3 — implement minimal enum/table/index idempotency fix
- [x] 6.4 — reduce per-request log volume with production-safe defaults
- [x] 6.5 — local verification (pytest + ruff) before push — ✅ pytest ✅ ruff

### Root Causes
- `add_batch_requests` created PostgreSQL enums explicitly and then table creation attempted implicit enum DDL again, causing `type "batch_request_type" already exists` in partially provisioned schemas.
- Enterprise API middleware logged every request/response by default, and uvicorn access logs could compound throughput, contributing to Railway 500 logs/sec limit saturation.

### Files Changed
- `enterprise_api/alembic/versions/add_batch_requests.py`
  - Switched enum definitions to `postgresql.ENUM(..., create_type=False)`.
  - Added `_has_table` / `_has_index` guards for table/index creation idempotency.
- `enterprise_api/tests/test_batch_requests_migration_idempotency.py` (new)
  - Validates enum definitions disable implicit type creation.
  - Validates upgrade skips existing tables/indexes and creates missing ones.
- `enterprise_api/app/utils/request_logging.py` (new)
  - Central request-log decision policy (`should_log_request`).
- `enterprise_api/app/main.py`
  - Request middleware now logs only 5xx, slow requests, or opt-in full request logs.
  - Health/readiness/metrics requests remain suppressed by default.
- `enterprise_api/app/config.py`
  - Added request logging controls and effective default policy.
- `enterprise_api/tests/test_request_logging_policy.py` (new)
  - Covers health suppression, 5xx logging, slow logging, and explicit opt-in logging.
- `enterprise_api/.env.example`
  - Documented request logging and uvicorn access log toggles.
- `enterprise_api/Dockerfile`
  - Disabled uvicorn access logs by default; opt-in via `UVICORN_ACCESS_LOG=true`.

### Verification
- `uv run pytest enterprise_api/tests/test_request_logging_policy.py enterprise_api/tests/test_batch_requests_migration_idempotency.py enterprise_api/tests/test_kms_support_migration_idempotency.py enterprise_api/tests/test_org_certificate_metadata_migration_idempotency.py enterprise_api/tests/test_licensing_migration_idempotency.py enterprise_api/tests/test_alembic_revision_chain.py enterprise_api/tests/test_db_startup_migration_strategy.py` ✅
- `uv run ruff check enterprise_api/app/main.py enterprise_api/app/config.py enterprise_api/app/utils/request_logging.py enterprise_api/tests/test_request_logging_policy.py enterprise_api/alembic/versions/add_batch_requests.py enterprise_api/tests/test_batch_requests_migration_idempotency.py` ✅

### Comprehensive Commit Message Suggestion
```
fix(enterprise_api): harden alembic idempotency and reduce Railway log rate

Root causes:
- add_batch_requests migration triggered DuplicateObject for enum batch_request_type
  in partially provisioned schemas.
- API emitted high log volume from per-request middleware and access logs,
  pushing Railway replica log throughput toward 500 logs/sec limits.

Changes:
- Make add_batch_requests idempotent:
  - use postgresql.ENUM(create_type=False) to avoid implicit enum create DDL
  - keep explicit enum.create(checkfirst=True)
  - guard batch_requests / batch_items table creation with has_table checks
  - guard index creation with has_index checks
- Add regression tests for batch migration idempotency.
- Add request logging policy helper and production-safe defaults:
  - log only 5xx, slow requests, or explicit opt-in request logging
  - keep health/readiness/metrics suppressed by default
- Add env/config toggles:
  - REQUEST_LOGGING_ENABLED
  - LOG_HEALTH_CHECKS
  - SLOW_REQUEST_THRESHOLD_MS
  - UVICORN_ACCESS_LOG (false by default in Docker CMD)
- Add tests for request logging policy behavior.

Verification:
- pytest enterprise_api/tests/test_request_logging_policy.py
- pytest enterprise_api/tests/test_batch_requests_migration_idempotency.py
- pytest enterprise_api/tests/test_kms_support_migration_idempotency.py
- pytest enterprise_api/tests/test_org_certificate_metadata_migration_idempotency.py
- pytest enterprise_api/tests/test_licensing_migration_idempotency.py
- pytest enterprise_api/tests/test_alembic_revision_chain.py
- pytest enterprise_api/tests/test_db_startup_migration_strategy.py
- ruff check enterprise_api/app/main.py enterprise_api/app/config.py
- ruff check enterprise_api/app/utils/request_logging.py
- ruff check enterprise_api/tests/test_request_logging_policy.py
- ruff check enterprise_api/alembic/versions/add_batch_requests.py
- ruff check enterprise_api/tests/test_batch_requests_migration_idempotency.py
```
