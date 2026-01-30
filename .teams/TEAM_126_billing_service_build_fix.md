# TEAM_126: billing_service_build_fix

**Active PRD**: `PRDs/CURRENT/PRD_Billing_Service_Build_Fix.md`
**Working on**: Task 3.3
**Started**: 2026-01-22 15:48
**Status**: in_progress

## Session Progress
Reference PRD task numbers. Mark with test verification:
- [x] 1.1 — ✅ updated
- [x] 1.2 — ✅ updated
- [x] 3.1 — ✅ ruff
- [x] 3.2 — ✅ pytest
- [ ] 3.3 — pending container build verification

## Changes Made
- `services/billing-service/pyproject.toml`: removed UV workspace config and added local `tool.uv.sources` path for shared library.
- `services/billing-service/Dockerfile`: aligned shared_libs install path with local UV source.
- `start-dev.sh`: added optional Stripe CLI webhook listener with skip flag and env override.
- `docs/STRIPE_SETUP_GUIDE.md`: documented start-dev Stripe listener behavior.

## Blockers
- None.

## Handoff Notes
- Run container build to verify task 3.3 and update PRD status.
