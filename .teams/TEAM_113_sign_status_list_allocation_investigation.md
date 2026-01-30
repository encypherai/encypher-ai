# TEAM_113: Sign Status List Allocation Investigation

**Active PRD**: `PRDs/CURRENT/PRD_Enterprise_API_C2PA_Security_Launch_Audit.md`
**Working on**: Investigation (status list allocation failure)
**Started**: 2026-01-19 16:07 UTC
**Status**: in_progress

## Session Progress
- [x] Investigation — root cause identified (missing org rows for demo/user org IDs)
- [x] Implement org bootstrap for demo/user IDs — ✅ pytest

## Changes Made
- `enterprise_api/app/services/organization_bootstrap.py`: add org bootstrap helper for demo/user orgs.
- `enterprise_api/app/services/signing_executor.py`: ensure org exists before status list allocation.
- `enterprise_api/app/services/embedding_executor.py`: ensure org exists before status list allocation.
- `enterprise_api/tests/test_organization_bootstrap.py`: add regression coverage.

## Blockers
- None.

## Handoff Notes
- Root cause: status_list_metadata.organization_id FK to organizations.id fails for demo/user org IDs (e.g., user_*, org_encypher_marketing) that do not exist in core DB.
- Review key-service /validate response for user keys and demo key fallback in dependencies.
