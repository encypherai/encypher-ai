# PRD: Marketing Site Pricing Messaging Update

**Status:** In Progress  
**Current Goal:** Update pricing module messaging to reflect local news focus, pre-launch positioning, and similarity detection naming.

## Overview
The pricing module currently positions the Starter tier without mentioning local news, marks Professional as “Most Popular,” and labels Business features as “Plagiarism detection.” These copy changes align messaging with NMA’s local news focus and avoid premature or negative phrasing.

## Objectives
- Expand the Starter tier “Best for” messaging to include local news.
- Replace the Professional tier “Most Popular” badge text with a softer pre-launch label.
- Rename “Plagiarism detection” to “Similarity detection” in Business tier copy.

## Tasks
- [x] 1.0 Update pricing copy
  - [x] 1.1 Add “local news” to Starter tier best-for text
  - [x] 1.2 Replace “Most Popular” badge text with “Recommended”
  - [x] 1.3 Rename plagiarism detection copy to similarity detection
- [x] 2.0 Verification
  - [x] 2.1 Run marketing-site lint (targeted changed files) — ✅ next lint
  - [x] 2.2 Run marketing-site tests — ✅ npm test ✅ playwright
  - [x] 2.3 Puppeteer verification — ✅ manual browser validation

## Success Criteria
- Starter tier best-for copy mentions local news.
- Professional tier badge no longer reads “Most Popular.”
- Business tier feature copy consistently uses “Similarity detection.”
- Marketing-site checks pass.

## Completion Notes
- WordPress pricing section (`/tools/wordpress`) updated to only show **Free** and **Enterprise** plans.
- Added explicit **Minor Add-ons** panel under pricing with optional enhancement messaging.
- Added Playwright regression coverage at `apps/marketing-site/e2e/wordpress-pricing.spec.ts` to assert:
  - Free + Enterprise are present
  - Starter/Professional are absent
  - Minor Add-ons copy is visible
- Verification completed:
  - ✅ `npm run test -- --passWithNoTests`
  - ✅ `npx playwright test e2e/wordpress-pricing.spec.ts`
  - ✅ `npx next lint --file src/app/tools/wordpress/page.tsx --file e2e/wordpress-pricing.spec.ts`
  - ✅ Manual Puppeteer UI check on `/tools/wordpress`
