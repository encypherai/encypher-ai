# PRD: Dashboard Enterprise Rev Share Removal

**Status**: Complete
**Current Goal**: Remove coalition revenue share percentage display for Enterprise tier in the dashboard billing UI.

## Overview
Enterprise pricing terms should not be displayed as explicit revenue-share percentages in the dashboard UI. The dashboard should continue to show plan and billing information, but omit enterprise rev-share details.

## Objectives
- Remove enterprise coalition revenue share percentages from the dashboard billing UI.
- Preserve non-enterprise rev-share display behavior (unless otherwise specified).
- Add automated verification to prevent regressions.

## Tasks
- [x] 1.0 Remove enterprise rev-share from Billing UI
  - [x] 1.0.1 Add e2e test coverage for enterprise rev-share removal — ✅ dashboard test:e2e
  - [x] 1.0.2 Update `apps/dashboard/src/app/billing/page.tsx` to hide enterprise rev-share display
  - [x] 1.0.3 Verification — ✅ dashboard lint ✅ dashboard test:e2e

## Success Criteria
- No instances of `80% you / 20% Encypher` are visible in the dashboard UI.
- When the current subscription tier is `enterprise`, the Current Plan card does not display coalition rev-share percentages.
- Automated checks pass.

## Completion Notes
- Removed enterprise rev-share display from the Current Plan card, Coalition Earnings header, and the Enterprise plan card.
- Added regression test to ensure `80% you / 20% Encypher` is not present in the billing page source.
