# TEAM_146: Certificate Provisioning Alignment

**Active PRD**: `PRDs/CURRENT/PRD_Enterprise_API_Production_Readiness_Blockers.md`
**Working on**: Task 8.0
**Started**: 2026-02-02
**Status**: in_progress

## Session Progress
- [ ] 8.1 — in progress
- [ ] 8.2 — in progress (local verification before push)
- [ ] 8.3 — in progress
- [ ] 8.4 — in progress
- [ ] 8.5 — in progress

## Focus
- Align auto-provisioned certificates with org signing keys in enterprise-api.
- Add internal enterprise-api endpoint for key-service to request certificate provisioning.
- Update key-service to call enterprise-api instead of generating its own certificate.

## Notes
- Local stack running via start-dev.sh; run tests before any push.
- Updated microservice/shared_libs `encypher-ai` dependency ranges to `>=3.0.4,<4.0.0`.
- Updated shared libs agent guides to reflect `encypher-ai` 3.0.4+.
- Tests: `uv run ruff check .` (repo root), `uv run pytest services/verification-service/tests/test_verify_api_key_auth.py`, `uv run pytest services/key-service/tests/test_validate_key_with_org.py`.
- Encoding-service has no `tests/` directory (pytest returned file not found).
