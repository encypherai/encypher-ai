# TEAM_132: Railway healthcheck 400

**Active PRD**: `PRDs/CURRENT/PRD_Enterprise_API_Production_Readiness_Blockers.md`
**Working on**: Railway deployment readiness (/health returning 400)
**Started**: 2026-01-26 15:36 UTC
**Status**: completed

## Session Progress
- [x] 8.1.1 — Add regression test for `/health` under Railway Host header — ✅ pytest
- [x] 8.1.2 — Fix TrustedHost allowlist for Railway — ✅ pytest
- [x] 8.1.3 — Ensure Railway internal healthchecks succeed (internal Host header) — ✅ pytest
- [x] 8.1.4 — Add detailed host-rejection logs for production debugging — ✅ pytest
- [x] BillingPage — Hide coalition rev-share percentages in Change plan tiers — ✅ npm run test:e2e

## Changes Made
- `enterprise_api/app/config.py`: Allow Railway `*.up.railway.app` hosts to pass `TrustedHostMiddleware`.
- `enterprise_api/app/main.py`: Replace `TrustedHostMiddleware` with custom host validation middleware that exempts `/health` + `/readyz` and logs rejected host details.
- `enterprise_api/tests/test_healthcheck_trusted_host.py`: Regression test for Railway host header hitting `/health`.
- `apps/dashboard/src/app/billing/page.tsx`: Filter out rev-share related feature strings in Change plan tier cards; stop passing `coalition_rev_share` in fallback plan mapping.
- `apps/dashboard/src/lib/api.ts`: Make `PlanInfo.coalition_rev_share` optional.
- `apps/dashboard/tests/e2e/billing.enterprise-revshare.test.mjs`: Extend contract test to ensure self-serve tier rev-share percentages are not present in billing page source.

## Blockers
- None

## Handoff Notes
- Root cause confirmed: `TrustedHostMiddleware` rejects Railway `Host` header, resulting in `/health` returning 400 and failing readiness checks.
