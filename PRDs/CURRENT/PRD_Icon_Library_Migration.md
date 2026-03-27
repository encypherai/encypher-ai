# PRD: Icon Library Migration + Brand Assets

**Status**: Not Started
**Current Goal**: Migrate all apps to `@encypher/icons`, serve canonical brand assets publicly, build internal brand page on dashboard

## Overview

The `@encypher/icons` package (`packages/icons/`) is built and verified with 40 generated assets (11 SVG, 28 PNG, 1 ICO), React components (`EncypherMark`, `EncypherLoader`), TypeScript color/path constants, and a build script. This PRD covers three phases: (1) migrate apps from duplicated local assets to the shared package, (2) serve canonical brand assets from marketing-site for external use with referrer tracking, and (3) build an internal brand assets browser on the dashboard locked behind auth.

## Objectives

- Replace all duplicated favicon/logo/mark files across 6+ apps with single `@encypher/icons` source
- Replace dashboard Loader.tsx (broken 1365x1365 viewBox, off-center rotation) with corrected EncypherLoader
- Replace encypher-times local EncypherMark.tsx with package version
- Serve canonical brand assets at `https://encypher.com/brand/` for external partners
- Track external brand asset usage via Referer logging
- Build internal brand assets page at `/brand` on dashboard (auth-gated, Encypher team only)
- Delete ~30+ orphaned SVG/PNG/ICO duplicates
- Zero visual regressions (Puppeteer before/after)

## Duplication Audit (Current State)

| Asset | Copies | Locations |
|-------|--------|-----------|
| favicon.ico | 5 | dashboard, marketing-site, encypher-times, ap-demo, plus `encypher_icon_nobg_color.ico` variants |
| Full logo SVGs | 13 | Every app's public/ dir, chrome extension, WordPress plugin |
| encypher-mark SVGs | 7 | marketing-site (4 color variants), encypher-times (3 variants) |
| encypher_check_*.svg | 3 | dashboard/public/assets/ |
| Local EncypherMark.tsx | 1 | encypher-times (inline SVG, ~10 import sites) |
| Loader.tsx (branded) | 1 | dashboard (broken viewBox, off-center transform-origin) |
| Loader.tsx (generic) | 1 | marketing-site (unused, generic spinner) |
| Email template logos | 12 | All services' base.html -- hardcode `https://encypherai.com/encypher_full_logo_white.png` (old domain) |

## Tasks

### 1.0 Dashboard Migration

- [ ] 1.1 Add `"@encypher/icons": "file:../../packages/icons"` to dashboard package.json
- [ ] 1.2 Replace `src/components/ui/Loader.tsx` with re-export of `EncypherLoader`
- [ ] 1.3 Update Loader import in `cdn-analytics/page.tsx` (only active consumer)
- [ ] 1.4 Replace `public/favicon.ico` with package version
- [ ] 1.5 Add `public/favicon.svg` (adaptive) from package
- [ ] 1.6 Update layout.tsx metadata to reference both SVG and ICO favicons
- [ ] 1.7 Replace `public/assets/encypher_full_logo_color.svg`, `_white.svg`, `_w.svg` with package wordmark SVGs
- [ ] 1.8 Update `DashboardLayout.tsx` logo Image srcs (3 references: sidebar, mobile, collapsed)
- [ ] 1.9 Update `signup/page.tsx`, `login/page.tsx`, `verify-domain/page.tsx`, `extension-handoff/page.tsx`, `wordpress/connect/page.tsx`, `auth/verify-email/page.tsx` logo references
- [ ] 1.10 Delete orphaned files: `encypher_check_color.svg`, `encypher_check_w.svg`, `encypher_check_white.svg`, `encypher_full_nobg.png`, `encypher-mark-corrected.svg`, `loader-preview.html`
- [ ] 1.11 Run `next build` -- zero errors
- [ ] 1.12 Puppeteer E2E: screenshot login, dashboard layout, loading states -- compare before/after

### 2.0 Encypher-Times Migration

- [ ] 2.1 Add `"@encypher/icons": "file:../../packages/icons"` to encypher-times package.json
- [ ] 2.2 Delete local `src/components/ui/EncypherMark.tsx`
- [ ] 2.3 Update 10 import sites to use `@encypher/icons` EncypherMark (verify/page, about/page, C2PABadge, ContentIntegrityBox, VerifyWidget, Footer, DemoBanner, ExtensionBanner)
- [ ] 2.4 Replace `public/encypher_icon_nobg_color.ico` with package favicon.ico
- [ ] 2.5 Update layout.tsx metadata icons reference
- [ ] 2.6 Delete local mark SVGs: `encypher-mark.svg`, `encypher-mark-azure.svg`, `encypher-mark-teal.svg`
- [ ] 2.7 Replace full logo SVGs in public/ with package wordmark versions
- [ ] 2.8 Run build -- zero errors
- [ ] 2.9 Puppeteer E2E: screenshot article page, verify page, header, footer

### 3.0 Marketing-Site Migration

- [ ] 3.1 Add `"@encypher/icons": "file:../../packages/icons"` to marketing-site package.json
- [ ] 3.2 Replace `public/favicon.ico` and `public/encypher_icon_nobg_color.ico` with package version
- [ ] 3.3 Add `public/favicon.svg` (adaptive) from package
- [ ] 3.4 Update `src/app/metadata.ts` and `src/lib/seo.ts` favicon references
- [ ] 3.5 Update `navbar.tsx` and `footer.tsx` LOGO_COLOR/LOGO_WHITE constants to use package wordmark SVGs
- [ ] 3.6 Delete orphaned public/ files: `encypher-mark.svg`, `encypher-mark-azure.svg`, `encypher-mark-teal.svg`, `encypher-mark-white.svg`, `encypher_check_color.svg`, `encypher_check_white.svg`, `encypher_full_logo_color.svg`, `encypher_full_logo_white.svg`, `encypher_full_logo_white.png`, `encypher_full_nobg.png`, `encypher_icon_nobg_color.png`
- [ ] 3.7 Run build -- zero errors
- [ ] 3.8 Puppeteer E2E: screenshot homepage, navbar, footer, pricing page

### 4.0 AP-Demo + NMA-Demo Migration

- [ ] 4.1 Replace favicon.ico and logo SVGs in ap-demo public/
- [ ] 4.2 Update `ap-demo/src/app/page.tsx` and `merkle/page.tsx` logo references
- [ ] 4.3 Run build -- zero errors

### 5.0 Chrome Extension Migration

- [ ] 5.1 Copy PNG sizes (16, 32, 48, 128) from package to extension icons/
- [ ] 5.2 Replace `encypher_logo.svg` (mislabeled wordmark) with package `wordmark-white-nobg.svg`
- [ ] 5.3 Replace `encypher_full_logo_color.svg` with package version
- [ ] 5.4 Update `manifest.json` icon references if paths changed
- [ ] 5.5 Update `popup.html` and `options.html` logo img srcs
- [ ] 5.6 Run extension test suite

### 6.0 Other Integrations

- [ ] 6.1 WordPress plugin: replace `assets/images/encypher_full_logo_color.svg`
- [ ] 6.2 Google Docs addon: update `appsscript.json` logoUrl (currently `https://dashboard.encypher.com/favicon.ico`)
- [ ] 6.3 Microsoft Office addin: update logo references in manifest.xml
- [ ] 6.4 Outlook addin: update logo references in manifest.xml

### 7.0 Public Brand Assets on Marketing-Site

Serve canonical brand assets at `https://encypher.com/brand/` so external partners, press, and integrators have a SSOT URL for our logo. Track who uses them.

- [ ] 7.1 Create `apps/marketing-site/public/brand/` directory
- [ ] 7.2 Copy key assets from `@encypher/icons` into `public/brand/`:
  - `mark-navy-nobg.svg`, `mark-white-nobg.svg`
  - `mark-navy-bg.svg`, `mark-white-bg.svg`
  - `wordmark-navy-nobg.svg`, `wordmark-white-nobg.svg`
  - `wordmark-navy-bg.svg`, `wordmark-white-bg.svg`
  - PNGs at 128, 256, 512 for each variant
- [ ] 7.3 Create API route `apps/marketing-site/src/app/api/brand/[...asset]/route.ts` that:
  - Serves the asset from `public/brand/`
  - Logs the `Referer` header, asset name, timestamp, and IP to an analytics event
  - Sets proper `Cache-Control`, `Access-Control-Allow-Origin: *` (public assets)
  - Returns 404 with a helpful message for invalid paths
- [ ] 7.4 Alternative approach: if overhead of API route is undesirable, serve from `public/brand/` directly and rely on infrastructure-level (Cloudflare/Nginx) access logs for Referer tracking. Decision point: discuss with user.
- [ ] 7.5 Add `Cache-Control` header override in `next.config.js` for `/brand/*` assets (public, max-age=86400 -- shorter than immutable so we can update brand assets)
- [ ] 7.6 Create simple `https://encypher.com/brand` landing page (public, unauthenticated) with:
  - Usage guidelines (brief: "Use our logo as-is, don't modify, minimum clear space")
  - Direct download links for each variant
  - Copy-pasteable `<img>` embed snippets pointing to `https://encypher.com/brand/...`
  - Note: This is the external-facing page, minimal, no auth required

### 8.0 Internal Brand Assets Page on Dashboard

Build an internal brand asset browser at `/brand` on the dashboard, locked behind auth, for Encypher team members. Based on the preview.html built during package development but integrated into the dashboard UI.

- [ ] 8.1 Create `apps/dashboard/src/app/brand/page.tsx`
- [ ] 8.2 Gate access: require authenticated session with email ending in `@encypher.com` or `@encypherai.com`, OR `isSuperAdmin` check (matching existing admin page pattern)
- [ ] 8.3 Build page UI:
  - Light/dark mode toggle (or respect dashboard theme)
  - Contrast preview section (dark bg + light bg side by side)
  - SVG mark variants grid (4 variants: navy/white x bg/nobg)
  - Animated loader preview (both color variants, multiple sizes)
  - Wordmark variants grid (4 variants)
  - Favicon preview (adaptive SVG + ICO)
  - PNG size ladder (16..512px for each variant)
  - Download buttons for each asset
  - Copy-to-clipboard for `<img>` embed snippets
- [ ] 8.4 Import React components (`EncypherMark`, `EncypherLoader`) from `@encypher/icons` to render live previews
- [ ] 8.5 Serve static assets (SVGs, PNGs) from dashboard's public/brand/ or reference marketing-site URLs
- [ ] 8.6 Add "Brand Assets" link in dashboard sidebar nav (visible only to gated users)
- [ ] 8.7 If Referer tracking API exists (7.3), add a "Usage Analytics" section showing which external domains are embedding our assets
- [ ] 8.8 Puppeteer E2E: screenshot brand page in both light and dark mode

### 9.0 Email Template Logo URLs (Domain Migration Dependency)

These are tracked separately under the domain migration project but noted here for completeness.

- [ ] 9.1 Update ~12 `base.html` files across services from `https://encypherai.com/encypher_full_logo_white.png` to `https://encypher.com/brand/wordmark-white-nobg.png` (or appropriate hosted URL)
- [ ] 9.2 Depends on: DNS migration Phase 2 (domain migration PRD) and task 7.x (public brand assets)

### 10.0 Cleanup

- [ ] 10.1 Delete `apps/dashboard/public/encypher-mark-corrected.svg` (canonical source is now in packages/icons)
- [ ] 10.2 Delete `apps/dashboard/public/loader-preview.html` (dev artifact, replaced by dashboard /brand page)
- [ ] 10.3 Audit all apps for remaining orphaned icon/logo files
- [ ] 10.4 Run full monorepo build across all apps
- [ ] 10.5 Delete marketing-site unused `src/components/ui/Loader.tsx` (generic spinner, never imported)

## Architecture Notes

### Public brand asset URLs (proposed)
```
https://encypher.com/brand/mark-navy-nobg.svg
https://encypher.com/brand/mark-white-nobg.svg
https://encypher.com/brand/wordmark-navy-nobg.svg
https://encypher.com/brand/wordmark-white-nobg.svg
https://encypher.com/brand/mark-navy-nobg-128.png
https://encypher.com/brand/mark-navy-nobg-256.png
https://encypher.com/brand/mark-navy-nobg-512.png
... (etc)
```

### Referer tracking approach
Option A: API route proxy -- more control, can log to DB/analytics, but adds latency and server load for what should be static files.

Option B: Serve from `public/brand/` directly, track via Cloudflare analytics or access logs at infra layer. Simpler, faster, but less granular.

Recommendation: Start with Option B (direct static serving). If Referer analytics become a product requirement, add a lightweight logging middleware or Cloudflare Worker in front of the `/brand/` path.

### Dashboard brand page auth
```ts
// Gating pattern (matches existing admin page approach)
const session = useSession();
const isEncypherTeam =
  session?.data?.user?.email?.endsWith('@encypher.com') ||
  session?.data?.user?.email?.endsWith('@encypherai.com');
const { data: isSuperAdmin } = useQuery(['is-super-admin'], ...);
const hasAccess = isEncypherTeam || isSuperAdmin;
```

## Verification Protocol

For each app migration (tasks 1.0-6.0):
1. **Before screenshot**: Puppeteer captures key pages before changes
2. **Migrate**: Apply changes per task list
3. **Build**: `next build` (or equivalent) must pass with zero errors
4. **After screenshot**: Puppeteer captures same pages after changes
5. **Diff**: Visual comparison confirms no regressions
6. **Commit**: One commit per app migration

## Success Criteria

- All duplicated favicon/logo/mark files eliminated (single source in `@encypher/icons`)
- All app builds pass
- Dashboard loader uses corrected 24x24 viewBox with centered rotation
- Puppeteer before/after screenshots show no visual regressions
- `https://encypher.com/brand/` serves canonical assets with proper caching
- Dashboard `/brand` page accessible to Encypher team, shows all variants with download/embed functionality
- Email templates point to hosted brand asset URLs (blocked on domain migration Phase 2)

## Completion Notes

(To be filled upon completion)
