# TEAM_150 — Dark Mode Fixes & UX Improvements

## Objective
1. Fix C2PA text standard SVGs in dark mode (logos invisible on dark bg)
2. Fix /solutions/enterprise company slider dark mode to match homepage
3. Fix /demo page duplicate headers
4. Improve WordPress plugin page UX/UI to match design system

## Status: COMPLETE ✅

## Changes Made

### 1. C2PA Hero Logos Dark Mode (`src/app/page.tsx`)
- Added `dark:brightness-200` to both C2PA and CAI logo `<Image>` elements in the hero section
- Logos now render bright white against the dark 3D background instead of faint/invisible

### 2. Enterprise Company Slider
- Verified the `StandardsCompliance` component already handles dark mode correctly with `dark:invert` on all company logos and `dark:bg-slate-800/50` background
- No changes needed — already matches homepage pattern

### 3. Demo Page Duplicate Headers (`src/app/demo/page.tsx`)
- **Root cause**: Page rendered its own `<Navbar />` and `<Footer />` while `ConditionalLayoutWrapper` in root layout already provides them
- Removed `import { Navbar }` and `import { Footer }` 
- Replaced `<main className="min-h-screen flex flex-col bg-background"><Navbar />...<Footer /></main>` with `<section className="py-20 px-4 bg-background">...</section>`
- Single navbar now rendered by layout wrapper

### 4. WordPress Plugin Page UX (`src/app/tools/wordpress/page.tsx`)
Replaced all hardcoded colors with design system tokens:
- **Hero**: `bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900` → `bg-muted/30 border-b border-border`
- **Hero text**: `text-slate-300` → `text-muted-foreground`; gradient span → `text-primary`
- **Buttons**: `bg-blue-600 hover:bg-blue-700` → default Button; `border-slate-500 bg-slate-700/50` → `variant="outline"`
- **Trust bar**: `bg-slate-100 dark:bg-slate-800` → `bg-muted/50 border-y border-border`; `text-slate-600 dark:text-slate-400` → `text-foreground`
- **Feature cards**: `text-blue-600` → `text-primary`; `hover:border-blue-500/50` → `hover:border-primary/50`
- **How It Works**: `bg-slate-50 dark:bg-slate-900` → `bg-muted/30 border-y border-border`; `bg-blue-600` circles → `bg-primary text-primary-foreground`
- **Pricing**: `border-blue-500` → `border-primary`; `bg-blue-600` badge → default Badge; `text-green-500` checks → `text-primary`
- **Use Cases**: `bg-slate-50 dark:bg-slate-900` → `bg-muted/30 border-y border-border`
- **CTA**: `bg-gradient-to-r from-blue-600 to-cyan-600` → `bg-primary text-primary-foreground`
- **FAQ**: Plain `<div>` items → `bg-card border border-border rounded-lg p-6` cards with spacing

## Verification
- ✅ `npx next build` — all pages compiled, exit code 0
- ✅ Puppeteer: /demo — single navbar, clean layout
- ✅ Puppeteer: /tools/wordpress — dark mode uses design system tokens throughout
- ✅ Puppeteer: / (homepage) — C2PA logos bright and visible in dark mode
- ✅ Puppeteer: /solutions/enterprises — company slider working in dark mode
