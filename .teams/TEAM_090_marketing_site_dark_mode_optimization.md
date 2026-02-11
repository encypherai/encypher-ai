# TEAM_090 — Marketing Site Dark Mode Optimization

## Objective
Audit and fix the marketing site's dark mode styling. Use Puppeteer to identify visual issues, then systematically fix CSS/theme tokens across key pages.

## Status: COMPLETE ✅

## Root Cause
Tailwind v4's `@theme` block had hardcoded hex values for semantic colors (e.g. `--color-background: #ffffff`). These static values ignored the `.dark` class CSS custom property overrides, so all Tailwind utility classes like `bg-background`, `bg-card`, `text-foreground` stayed locked to light mode values.

## Changes Made

### Core Fix: `globals.css`
- Added `@custom-variant dark (&:where(.dark, .dark *));` for class-based dark mode
- Changed all semantic `@theme` tokens from hardcoded hex to `var()` references (e.g. `--color-background: var(--background)`) so they respond to `.dark` class
- Added dark mode link colors (`.dark a` uses columbia-blue)
- Added dark mode scrollbar styles for `.scrollbar-thin` and `.overflow-y-auto`

### Component Fixes
- **MetadataBackground.tsx**: All 3D elements (particles, text, wireframes, hub, lines) now switch from `#1b2f50` to `#b7d5ed` in dark mode
- **standards-compliance.tsx**: Section bg uses `dark:bg-slate-800/50`, all logos get `dark:invert`
- **page.tsx (homepage)**: C2PA/CAI hero logos get `dark:invert`
- **pricing/page.tsx**: ICP tab selectors use semantic classes instead of hardcoded inline styles; C2PA/CAI logos get `dark:invert`
- **navbar.tsx**: Dropdown menus already used semantic classes (verified)

## Verification
- Puppeteer screenshots taken for homepage, pricing, blog in both dark and light modes
- All pages render correctly in both modes
- `npm run build` passes with exit code 0
- No regressions in light mode
