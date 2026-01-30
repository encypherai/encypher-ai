# TEAM_075: Marketing Site Pricing Copy

**Active PRD**: `PRDs/CURRENT/PRD_MarketingSite_Pricing_Messaging_Update.md`
**Working on**: Task 2.0
**Started**: 2026-01-16 17:46
**Status**: in_progress

## Session Progress
- [x] 1.1 — local news added to Starter best-for copy
- [x] 1.2 — Recommended badge applied
- [x] 1.3 — similarity detection naming updated
- [x] 2.1 — ✅ lint
- [x] 2.2 — ✅ npm test
- [ ] 2.3 — blocked (Playwright browsers not installed)

## Changes Made
- `apps/marketing-site/src/app/pricing/page.tsx`: Updated best-for copy, badge label, and Business highlight messaging.
- `apps/marketing-site/src/components/pricing/pricing-table.tsx`: Adjusted badge text and Business description.
- `apps/marketing-site/src/components/pricing/FeatureComparisonTable.tsx`: Renamed plagiarism detection feature and badge label.
- `packages/pricing-config/src/tiers.ts`: Updated Business tier feature copy.
- `packages/pricing-config/src/coalition.ts`: Updated coalition subheadline copy.
- `apps/marketing-site/src/lib/pricing-config/tiers.ts`: Synced pricing-config from package source.
- `apps/marketing-site/src/lib/pricing-config/coalition.ts`: Synced pricing-config from package source.

## Blockers
- Playwright browsers missing; `npm run test:e2e` fails until `npx playwright install` runs.

## Handoff Notes
- None yet.
