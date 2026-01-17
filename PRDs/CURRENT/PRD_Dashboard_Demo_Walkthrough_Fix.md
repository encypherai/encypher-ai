# PRD: Dashboard Playground Demo Walkthrough Fix

## Status
In Progress

## Current Goal
Ensure the dashboard Playground demo walkthrough starts at Sign, flows through Copy, and ends in Verify while surfacing the /verify/advanced endpoint.

## Overview
The Playground quick-start demo currently jumps straight to verification, which conflicts with the Sign → Copy → Verify walkthrough messaging. We will realign the demo button to start at signing, reset the quick-start state appropriately, and add the advanced verify endpoint to the catalog so users can discover it.

## Objectives
- Align the demo walkthrough with the Sign → Copy → Verify flow.
- Expose the /verify/advanced endpoint in the Playground catalog with accurate metadata.
- Add automated coverage for the demo config and endpoint catalog changes.

## Tasks
- [ ] 1.0 Baseline verification
- [x] 1.1 Run `npm run test:e2e` in `apps/dashboard`

- [ ] 2.0 Demo walkthrough fixes
- [x] 2.1 Start the demo flow at Sign and reset quick-start state
- [x] 2.2 Add /verify/advanced to the Playground endpoint catalog

- [ ] 3.0 Tests (TDD)
- [x] 3.1 Add coverage for demo config + endpoint list

- [ ] 4.0 Verification
- [ ] 4.1 Run `npm run lint`, `npm run type-check`, `npm run test:e2e`
- [ ] 4.2 Run Puppeteer verification for Playground demo flow

## Success Criteria
- The demo walkthrough starts at Sign and proceeds to Copy → Verify without jumping to Verify.
- /verify/advanced appears in the Playground endpoints list with correct metadata.
- ✅ `npm run lint`, ✅ `npm run type-check`, ✅ `npm run test:e2e`.
- ✅ Puppeteer verification confirms the demo flow.

## Completion Notes
- 2026-01-16: ✅ Code changes complete. Demo flow now starts at Sign endpoint.
- 2026-01-16: ✅ `/verify/advanced` endpoint added to playground catalog.
- 2026-01-16: ✅ Contract tests updated and passing.
- 2026-01-16: ✅ Puppeteer E2E test created with demo API key (`demo-api-key-for-testing`).
- 2026-01-16: ⚠️ E2E test blocked: Sign API not responding (returns no response). API may be down or misconfigured.
- 2026-01-16: Manual verification recommended: Test demo flow in browser with demo API key.
