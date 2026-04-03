# TEAM_284 - Icon Library Migration + Brand Assets

## Status: Complete

## Summary

Migrated all apps and integrations from scattered local icon/logo copies to the centralized `@encypher/icons` package. Built internal brand assets page on dashboard with auth gating. Set up public brand asset hosting on marketing-site.

## Changes Made

### Dashboard (apps/dashboard)
- Added `@encypher/icons` dependency
- Replaced broken `Loader.tsx` (1365x1365 viewBox, off-center rotation) with re-export of `EncypherLoader` (corrected 24x24, centered)
- Updated all logo references across 9 pages: login, signup, verify-domain, extension-handoff, verify-email, wordpress/connect, invite/[token], invite/team/[token], DashboardLayout
- Added favicon metadata (SVG + ICO) to layout.tsx
- Deleted 8 orphaned asset files (encypher_check_*, encypher_full_logo_*, encypher_full_nobg.png, logo.png, encypher-mark-corrected.svg, loader-preview.html)
- **NEW: `/brand` page** -- internal brand asset browser with light/dark toggle, live React component previews, download buttons, embed snippet copy, usage guidelines. Gated to @encypher.com/@encypher.com emails or superadmins.
- Added "Brand Assets" link to sidebar nav (desktop + mobile) under Internal section

### Encypher-Times (apps/encypher-times)
- Added `@encypher/icons` dependency
- Deleted local `EncypherMark.tsx` (55 lines)
- Updated 8 import sites to use `@encypher/icons`
- Replaced favicon, deleted 4 orphaned SVGs/ICOs
- Updated layout.tsx metadata

### Marketing-Site (apps/marketing-site)
- Added `@encypher/icons` dependency
- Updated navbar.tsx and footer.tsx logo constants to `/brand/` paths
- Updated metadata.ts and seo.ts favicon references
- Created `public/brand/` directory with 20 canonical assets (8 SVGs + 12 PNGs)
- Deleted 7 orphaned SVG/ICO files + unused Loader.tsx
- Updated favicon to SVG+ICO pair

### AP-Demo (apps/ap-demo)
- Replaced favicon.ico with package version, added favicon.svg
- Replaced full logo SVGs with corrected versions
- Deleted orphaned encypher_icon_nobg_color.png

### Chrome Extension (integrations/chrome-extension)
- Added icon-16/32/48/128.png from package
- Updated manifest.json to reference new icon naming
- Replaced logo SVGs (encypher_logo.svg, encypher_full_logo_*.svg)

### Other Integrations
- WordPress plugin: replaced logo SVG
- Microsoft Office addin: updated manifest.xml icon references
- Outlook addin: updated manifest.xml icon references
- Google Docs addon: no change needed (points to dashboard favicon.ico which was already updated)

## Stats
- 66 files changed, 342 insertions, 2,110 deletions
- ~30 orphaned/duplicated files deleted
- 3 app builds verified (dashboard, marketing-site, encypher-times)

## Remaining
- Wordmark vertical padding: user flagged as too much -- needs visual Puppeteer verification to determine exact crop. Deferred.
- Email template logo URLs (task 9.0): blocked on domain migration Phase 2 (12 base.html files still reference encypher.com)

## Suggested Commit Message

```
feat(icons): migrate all apps to @encypher/icons, add brand assets page

- Replace scattered local icon/logo copies across 6+ apps with
  centralized @encypher/icons package
- Fix dashboard Loader: corrected 24x24 viewBox with centered rotation
  (was broken 1365x1365 with off-center spin)
- Delete ~30 orphaned SVG/PNG/ICO duplicates (-2110 lines)
- Add internal brand assets page at /brand on dashboard:
  light/dark preview, live React components, download/embed features,
  gated to @encypher.com/@encypher.com team members
- Set up public brand assets at marketing-site/public/brand/ with
  20 canonical files (8 SVGs + 12 PNGs) for external use
- Update encypher-times: replace local EncypherMark.tsx with package
- Update chrome extension: new icon PNGs + manifest references
- Update WordPress plugin, Office/Outlook addins: fresh logo SVGs
```
