# TEAM_060 — API Sign/Verify Consolidation

## Session Goal
Consolidate API surface to `/sign` (+ `/sign/advanced`) and `/verify`; migrate marketing site off `/encode` and `/decode`; verify with tests.

## Work Completed (this session)
- Marketing-site dev server hang resolved by restarting `next dev`.
- Installed Playwright Chromium runtime needed for e2e.
- Fixed Playwright smoke test to correctly validate `/tools` and then `/tools/encode-decode`.
- Deprecated legacy marketing-site API route `/api/tools/decode` to return `410 Gone` (direct callers to `/api/tools/verify`).
- Verified:
  - `apps/marketing-site`: `npm test` ✅
  - `apps/marketing-site`: Playwright e2e ✅

## Next Steps
- Inventory backend `/encode` + `/decode` endpoints and references.
- Implement backend consolidation so `/sign` + `/verify` are canonical; hard-deprecate/remove legacy endpoints with tests.

## Notes / Risks
- Keep internal API key server-only (Next route handlers) and avoid exposing to browser.
