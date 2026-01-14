# PRD: Marketing Site Button Color Alignment

**Status**: Complete
**Current Goal**: Replace blue/purple gradient buttons with design-system color tokens in the marketing site publisher demo.

## Overview
The marketing site currently includes CTA buttons in the publisher demo that use a blue/purple gradient scheme. All buttons should use the canonical Encypher design-system color palette and styling.

## Objectives
- Remove the blue/purple gradient button styling from `apps/marketing-site/src/app/publisher-demo`.
- Ensure buttons use design-system color tokens (e.g. `blue-ncs`) and consistent focus/hover states.
- Add automated verification to prevent reintroducing blue/purple gradient CTA buttons.

## Tasks
- [x] 1.0 Align publisher-demo buttons with design-system
  - [x] 1.0.1 Add e2e test coverage to detect forbidden gradient button classes — ✅ marketing-site test:e2e
  - [x] 1.0.2 Update publisher-demo CTA button styles to design-system tokens
  - [x] 1.0.3 Update publisher-demo modal submit button styles to design-system tokens
  - [x] 1.0.4 Verification — ✅ marketing-site lint ✅ marketing-site test:e2e ✅ puppeteer

## Success Criteria
- No publisher-demo buttons render with `bg-gradient-to-r from-blue-600 to-purple-600` (or equivalent).
- Publisher-demo CTA and modal submit buttons use design-system token-based colors.
- Automated checks pass.

## Completion Notes
- Updated publisher-demo CTA and modal submit button styling to use design-system token colors (no blue/purple gradients).
- Added Playwright regression test to prevent reintroduction of gradient CTA buttons.
- Repaired corrupted `src/app/dashboard/UserOnboardingGate.tsx` (all null bytes) to unblock ESLint.
