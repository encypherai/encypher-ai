# TEAM_172 — WordPress Plugin API Alignment

## Status: COMPLETE

## Summary
Aligned the WordPress provenance plugin with the current enterprise API freemium model (TEAM_166). The API consolidated tiers to free/enterprise/strategic_partner, but the plugin referenced old starter/professional/business tier names and didn't use `micro_ecc_c2pa` manifest mode.

## Key Changes

### 1. Sign Request — `micro_ecc_c2pa` default (class-encypher-provenance-rest.php)
- Added `manifest_mode: micro_ecc_c2pa` to all sign request payloads
- Added `segmentation_level: sentence` and `index_for_attribution: true` as defaults for ALL tiers
- Removed old `!$is_starter || $is_nma_member` gating for segmentation (free tier now has it)
- Changed `$is_starter` → `$is_free` variable naming

### 2. Verify Endpoint — `/verify` via verification-service (class-encypher-provenance-rest.php)
- Enterprise API's `/verify` and `/verify/advanced` both exist but `/verify` routes to the verification-service
- Plugin now uses `/verify` with simple `{text}` payload (verification-service schema)
- Removed old `/verify/advanced` fields (segmentation_level, search_scope, include_attribution, etc.)
- Auth sent when available for org context (verification-service accepts optional auth)

### 3. Tier Naming — `starter` → `free` (15 files, ~60 occurrences)
- All defaults changed from `'starter'` to `'free'`
- All comparisons changed from `=== 'starter'` to `=== 'free'`
- Added legacy tier coercion: `['starter', 'professional', 'business']` → `'free'`
- Valid tiers now: `['free', 'enterprise', 'strategic_partner']`

### 4. Upsell/UI — 2-tier model (class-encypher-provenance-admin.php)
- Upsell module: collapsed 4-tier upgrade path to single free→enterprise
- Account page: updated tier_info map to free/enterprise/strategic_partner
- Tier field: updated feature lists to reflect freemium model
- CSS: renamed `.tier-starter` → `.tier-free`, removed professional/business styles
- All "Upgrade to Pro" text → "Upgrade to Enterprise"

### 5. Coalition — Updated revenue splits (class-encypher-provenance-coalition.php)
- Revenue splits: free=60/40, enterprise=85/15, strategic_partner=85/15
- ROI calculation updated for free→enterprise upgrade path

### 6. JS/CSS Assets
- `editor-sidebar.js`: all `'starter'` → `'free'`, upgrade text → Enterprise
- `settings-page.js`: tier constraint check updated
- `bulk-mark.js`: tier default and limit check updated
- `coalition-widget.css`, `settings-page.css`: `.tier-starter` → `.tier-free`

## Files Modified (15 total)
- `includes/class-encypher-provenance-rest.php` — sign payload, verify endpoint, tier coercion
- `includes/class-encypher-provenance-admin.php` — all render methods, settings, upsell, CSS
- `includes/class-encypher-provenance-bulk.php` — tier defaults and limits
- `includes/class-encypher-provenance-coalition.php` — revenue splits, ROI calc
- `includes/class-encypher-provenance-frontend.php` — badge branding check
- `includes/class-encypher-provenance.php` — activation defaults
- `admin/partials/coalition-page.php` — tier check
- `admin/partials/coalition-widget.php` — tier check
- `assets/js/editor-sidebar.js` — tier defaults and upgrade text
- `assets/js/settings-page.js` — tier constraints
- `assets/js/bulk-mark.js` — tier defaults and limits
- `assets/css/coalition-widget.css` — tier CSS class
- `assets/css/settings-page.css` — tier CSS class
- `README.md` — API endpoints documentation
- `readme.txt` — tier features documentation

## Pre-existing Issues (not introduced by this PR)
- `editor-sidebar.js` has structural lint errors at lines 282-500 (pre-existing, confirmed via git diff)

## Suggested Git Commit Message
```
feat(wordpress-plugin): align with freemium API model (TEAM_172)

- Default manifest_mode to micro_ecc_c2pa for all sign requests
- Enable sentence segmentation and attribution indexing for all tiers
- Use /verify/advanced exclusively (old /verify returns 410 Gone)
- Rename tier references: starter → free (canonical API tier name)
- Add legacy tier coercion for backward compatibility
- Collapse 4-tier upsell to 2-tier (free/enterprise) model
- Update revenue splits: free=60/40, enterprise=85/15
- Update all UI text, CSS classes, and JS tier checks

Aligns with TEAM_166 enterprise API freemium consolidation.
Files changed: 15 across PHP, JS, CSS, and docs.
```
