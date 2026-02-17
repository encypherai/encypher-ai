# TEAM_200 — Alembic Reconciliation Baseline + Stamp

## Session Summary
- Enforced Alembic-only startup migration path for `enterprise_api`.
- Added explicit reconciliation revisions to collapse historical multi-head lineage.
- Deployed `enterprise-api` to Railway production.
- Stamped content DB to unified reconciliation head.
- Verified both core and content DBs now resolve to the same Alembic head.

## Files Changed
- `enterprise_api/app/utils/db_startup.py`
- `enterprise_api/app/main.py`
- `enterprise_api/app/config.py`
- `enterprise_api/scripts/docker-entrypoint.sh`
- `enterprise_api/.env.example`
- `enterprise_api/tests/test_db_startup_migration_strategy.py`
- `enterprise_api/alembic/versions/20260216_170000_core_heads_reconciled.py`
- `enterprise_api/alembic/versions/20260216_170100_content_reconciliation_baseline.py`
- `enterprise_api/alembic/versions/20260216_170200_reconciliation_unified_head.py`

## Verification
- `uv run pytest enterprise_api/tests/test_db_startup_migration_strategy.py -q` ✅
- `uv run ruff check ...` (targeted changed files) ✅
- Railway production startup logs show Alembic upgrade to `head` ✅
- Railway production DB revisions:
  - CORE: `20260216_170200 (head) (mergepoint)` ✅
  - CONTENT: `20260216_170200 (head) (mergepoint)` ✅

## Handoff Notes
- Startup now has one migration path (Alembic).
- Reconciliation is lineage-only (no-op revisions) and intended to stop branch drift.
- Follow-up migration work should use `down_revision = "20260216_170200"`.

## Suggested Commit Message
feat(enterprise-api): reconcile alembic lineage to unified head and enforce alembic-only startup

- remove legacy sql_legacy startup migration strategy
- enforce alembic upgrade head in startup/db utilities
- add reconciliation revisions:
  - 20260216_170000 core heads merge
  - 20260216_170100 content baseline
  - 20260216_170200 unified reconciliation head
- update entrypoint/env docs to reflect alembic-only SSOT
- update db startup tests for alembic-only behavior
- deploy and stamp production content DB to unified head

## Follow-up Incident (Local Dev) — 2026-02-16
- Symptom: `./start-dev.sh --rebuild` timed out waiting for `http://localhost:9000/health`, and gateway `POST /api/v1/sign` returned `502`.
- Root cause: local `encypher_content.alembic_version` contained overlapping ancestor + descendant revisions (`003`, `add_batch_requests`, `add_kms_support`, `20260213_190000`), causing Alembic startup failure in `enterprise-api`.
- Remediation run locally:
  - `alembic stamp 20260216_170200` against `encypher_content`
  - restart `encypher-enterprise-api`
- Verification:
  - `SELECT * FROM alembic_version;` → only `20260216_170200`
  - `GET http://localhost:9000/health` → `200`
  - `POST http://localhost:8000/api/v1/sign` now routes to enterprise-api (returns `401 API key required`, expected without key)
- API keys note: key inventory in local `encypher_keys` is independent from enterprise-api readiness and can appear empty for a given org after local env resets/login org switching.

## Suggested Commit Message (if code change is later added)
chore(dev): document local alembic overlap recovery for enterprise-api startup

- record local failure mode where overlapping alembic revisions block startup
- document safe local recovery: stamp `encypher_content` to `20260216_170200`
- include verification checklist for `/health` and `/api/v1/sign`
