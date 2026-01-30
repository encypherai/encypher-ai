# TEAM_134 — Key-service validate fallback on schema drift

## Status
- **In Progress** (key-service fix complete; advanced verification work underway)

## Goal
Prevent production `401 Invalid API key` errors caused by key-service querying `organizations.certificate_pem` when the column does not exist (schema drift), which aborts the transaction and breaks fallback validation.

## Changes
- `services/key-service/app/services/key_service.py`
  - Roll back the DB transaction before retrying the fallback query when `certificate_pem` is missing.
- `services/key-service/tests/conftest.py`
  - Strengthen test double to simulate Postgres `InFailedSqlTransaction` behavior unless `rollback()` is called.
- `services/key-service/pyproject.toml`
  - Add missing runtime deps required by shared libs test import path (`rich`, `encypher-ai`).

## Verification
- `uv run pytest -q tests/test_validate_key_with_org.py::test_validate_key_missing_certificate_column_returns_none` ✅
- `uv run pytest -q` (services/key-service) ✅
- `uv run ruff check app tests` (services/key-service) ✅

## Handoff Notes
- Deploy **key-service** with this fix to unblock production signing via `/api/v1/sign/advanced`.
- After deploy, re-run `scripts/example_lightweight_sign.py` against `https://api.encypherai.com` with a valid API key.

---

## 2026-01-27 — Advanced Verification (Hashes-Only) Focus

### Goal
Align Enterprise API verification with hashes-only storage: public/basic endpoints verify signer+manifest integrity without returning DB-stored text, while advanced verification adds strict tamper detection, localization, and soft-match (snippets derived only from request text).

### Planned Changes
- Remove DB-sourced `text_preview` from public verification responses.
- Stop persisting `text_content`, `text_preview`, and `manifest_data` in `content_references` (and `text_content` in `merkle_subhashes`).
- Implement advanced verification: strict Merkle root match, localization diff, and soft-match scoring.
- Update logging to avoid request text previews.
- Add tests + documentation for new verification behaviors.
