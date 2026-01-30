# TEAM_074: Dashboard demo walkthrough fix

**Active PRD**: `PRDs/CURRENT/PRD_Dashboard_Demo_Walkthrough_Fix.md`
**Working on**: Task 4.0
**Started**: 2026-01-16 17:14
**Status**: in_progress

## Session Progress
Reference PRD task numbers. Mark with test verification:
- [x] 1.1 — ✅ test:e2e
- [x] 2.1 — demo flow reset to sign
- [x] 2.2 — /verify/advanced added
- [x] 3.1 — contract tests updated
- [ ] 4.1 — ⚠️ type-check blocked by missing @playwright/test
- [ ] 4.2 — pending

## Changes Made
- `apps/dashboard/src/app/playground/page.tsx`: Demo flow starts at sign; add verify/advanced endpoint.
- `apps/dashboard/src/lib/playgroundRequestBuilder.mjs`: Add verify-advanced support and stricter verify validation.
- `apps/dashboard/tests/e2e/playground.request-builder.contract.test.mjs`: Update contract coverage for verify-advanced.

## Blockers
- `npm run type-check` fails because `@playwright/test` is not installed in `apps/dashboard`.

## Handoff Notes
- Need approval to add `@playwright/test` dev dependency (likely via `npm install --save-dev`).
