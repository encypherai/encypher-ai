# TEAM_213 — WordPress Marketing Pricing Audit

## Session Summary
- Audited `apps/marketing-site` WordPress marketing pricing content.
- Updated `/tools/wordpress` pricing UI to only show **Free** and **Enterprise** plans.
- Added a dedicated **Minor Add-ons** block under pricing.
- Removed legacy plan labels and copy references (`Starter`, `Professional`, `Pro+`) from the WordPress pricing section.
- Added a Playwright regression spec for WordPress pricing assertions.

## Verification
- ✅ `npm run test -- --passWithNoTests` (marketing-site)
- ✅ `npx playwright test e2e/wordpress-pricing.spec.ts`
- ✅ Manual UI verification via Puppeteer (`/tools/wordpress`) + screenshot
- ⚠️ `npm run lint` has pre-existing global lint failures unrelated to this change set.
- ✅ Targeted lint for changed files: `npx next lint --file src/app/tools/wordpress/page.tsx --file e2e/wordpress-pricing.spec.ts`

## Files Changed
- `apps/marketing-site/src/app/tools/wordpress/page.tsx`
- `apps/marketing-site/e2e/wordpress-pricing.spec.ts`
- `PRDs/CURRENT/PRD_MarketingSite_Pricing_Messaging_Update.md`

## Handoff Notes
- WordPress pricing module now reflects the requested model: Free + Enterprise + minor add-ons.
- Added test coverage to prevent regressions back to Starter/Professional labels.

## Suggested Commit Message
feat(marketing-site): align WordPress pricing to Free + Enterprise with add-ons and add e2e regression

- update /tools/wordpress pricing cards to Free and Enterprise only
- remove legacy Starter/Professional references from pricing copy
- add Minor Add-ons section in WordPress pricing module
- add Playwright e2e contract to assert Free+Enterprise only and add-ons visibility
- verify with jest suite, playwright spec, and manual Puppeteer check
