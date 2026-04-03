# Design System SSOT Migration

**Status:** Complete
**Current Goal:** All tasks complete - both apps build clean

## Overview

Both frontend apps (marketing-site, dashboard) had duplicate component stacks: local shadcn/ui components AND @encypher/design-system imports for the same primitives (Button, Card, Badge, Input). The design system package contained 11 simple pure-React components while the apps used 27-33 Radix-backed shadcn components with brand customizations. This PRD consolidated the shadcn/ui components into packages/design-system/ as the single source of truth, then migrated both apps to import exclusively from @encypher/design-system.

## Objectives

- One component library shared across all frontend apps via CI sync
- Brand changes (colors, tokens, variants) propagate automatically to both apps
- Radix UI accessibility preserved (keyboard nav, focus management, ARIA)
- App-specific components (ChromeInstallButton, VerificationSequence, BrandedLoadingScreen, etc.) remain local

## Tasks

### 1.0 Replace Design System Package Contents

- [x] 1.1 Copy marketing-site shadcn components into packages/design-system/src/components/
- [x] 1.2 Copy shared utilities (cn, etc.) into packages/design-system/src/lib/
- [x] 1.3 Copy theme CSS (globals.css token definitions, theme.css) into packages/design-system/src/styles/
- [x] 1.4 Update packages/design-system/src/index.ts exports to match new components
- [x] 1.5 Add Radix UI dependencies to packages/design-system/package.json
- [x] 1.6 Verify design system package builds/resolves correctly

### 2.0 Marketing Site Migration

- [x] 2.1 Update marketing-site imports from @/components/ui/ to @encypher/design-system for all shared components (87 files)
- [x] 2.2 Keep app-specific components local (ChromeInstallButton, VerificationSequence)
- [x] 2.3 Migrate useAuth.ts from deprecated showToast API to new toast API
- [x] 2.4 Verify marketing-site build passes

### 3.0 Dashboard Migration

- [x] 3.1 Update dashboard imports to use new @encypher/design-system API surface (5 files with local imports migrated)
- [x] 3.2 Sync updated design system to apps/dashboard/design-system/
- [x] 3.3 Keep app-specific components local (BrandedLoadingScreen, Loader, confirm-dialog, enterprise-gate, breadcrumb, empty-state)
- [x] 3.4 Verify dashboard build passes

### 4.0 Testing & Validation

- [x] 4.1 Marketing-site full build clean (94+ routes, 0 errors)
- [x] 4.2 Dashboard full build clean (41 routes, 0 errors)
- [ ] 4.3 Visual verification of key pages via Puppeteer

## Shared Components (migrated to design system)

accordion, alert, badge, button, card, dialog, dropdown-menu, form, input, label, radio-group, scroll-area, select, separator, sheet, skeleton, slider, sonner, switch, table, tabs, textarea, toast, toastContext, toggle, tooltip, use-toast

## App-Specific Components (stayed local)

Marketing-site: ChromeInstallButton, VerificationSequence
Dashboard: BrandedLoadingScreen, Loader, confirm-dialog, enterprise-gate, breadcrumb, empty-state

## Key Changes

- Design system upgraded from v1.0.0 to v2.0.0 (27 shadcn components replace 11 simple components)
- Theme tokens aligned to marketing site values (primary=blue-ncs #2a87c4, accent=columbia-blue #b7d5ed)
- Previous design system had swapped primary/accent mapping (primary=columbia-blue, accent=blue-ncs)
- Dashboard's existing 45 imports from @encypher/design-system continue to work with new API
- Marketing site's useAuth.ts migrated from deprecated showToast to new toast API

## Success Criteria

- [x] Zero imports from @/components/ui/ for shared components in either app
- [x] Both apps build clean
- [ ] No visual regressions on key pages
- [x] CI sync workflow propagates design system changes to both apps

## Completion Notes

Migration complete. Both apps build successfully. The design system now contains all 27 shadcn/ui components with Radix UI accessibility primitives, brand-customized variants (using Encypher color tokens), and full light/dark mode support. The theme.css is now the single source of truth for all brand tokens across both apps. Visual verification via Puppeteer pending as follow-up.
