# TEAM_125: Marketing Site Sign Verify Payload

**Active PRD**: `PRDs/CURRENT/PRD_MarketingSite_Tools_Sign_Logging.md`
**Working on**: Tasks 2.1, 3.1
**Started**: 2026-01-22 14:50 UTC
**Status**: completed

## Session Progress
- [x] 2.1 — ✅ npm test
- [x] 3.1 — ✅ pytest ✅ ruff

## Changes Made
- `apps/marketing-site/src/components/tools/EncodeDecodeTool.tsx`: Remove claim generator field and send provenance-only ai_info without target override.
- `apps/marketing-site/src/lib/enterpriseApiTools.ts`: Send provenance as custom assertion for base sign.
- `apps/marketing-site/src/lib/enterpriseApiTools.test.ts`: Update tests for provenance assertions.
- `enterprise_api/app/models/request_models.py`: Allow custom assertions on base /sign.
- `enterprise_api/app/services/signing_executor.py`: Enforce starter-tier custom assertion limit and embed custom assertions.
- `enterprise_api/tests/test_sign_basic_template_usage.py`: Add tests for starter custom assertions and limits.
- `enterprise_api/README.md`: Document custom assertion support on /sign.

## Blockers
- None.

## Handoff Notes
- Manual production verification for `/api/tools/sign` still pending (PRD task 4.2).
