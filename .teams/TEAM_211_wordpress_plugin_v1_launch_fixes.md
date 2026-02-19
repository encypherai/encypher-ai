# TEAM_211: WordPress Plugin v1 Launch Fixes

**Status**: Complete
**Started**: 2026-02-18

## Fixes
- [x] 1. auto-sign respects configured post_types (not just 'post') — ✅ 34 tests pass
- [x] 2. Content page pagination (>50 posts silently truncated) — ✅ 34 tests pass
- [x] 3. Gate error_log() behind WP_DEBUG — ✅ 34 tests pass (Rest + Coalition classes)
- [x] 4. Fix 'Signed' status guidance copy (unverified-but-signed misleading) — ✅ 34 tests pass
- [x] 5. docker-compose.yml obsolete version attribute removed — ✅
- [x] 6. Per-user error reporting — assessed (see below)
- [x] 7. Tests + verification — 34/34 contract tests pass

## Files Changed
- `integrations/wordpress-provenance-plugin/plugin/encypher-provenance/includes/class-encypher-provenance-rest.php`
  - Added `debug_log()` helper gated behind `WP_DEBUG`
  - All `error_log()` calls routed through `debug_log()`
  - `auto_sign_on_publish`: reads `$settings['post_types']` instead of hardcoding `'post'`
  - `auto_sign_on_update`: same post_types fix + removed hardcoded `'post'` check
- `integrations/wordpress-provenance-plugin/plugin/encypher-provenance/includes/class-encypher-provenance-admin.php`
  - `render_content_page`: pagination with `$paged`/`$per_page`/`$total_pages`, WP-style tablenav
  - `render_content_page`: uses `$configured_post_types` from settings
  - Status guidance: default "Provenance embedded. Run Verify to confirm integrity." for signed-not-verified; "Verified provenance is available." only when `c2pa_verified`
- `integrations/wordpress-provenance-plugin/plugin/encypher-provenance/includes/class-encypher-provenance-coalition.php`
  - Added `debug_log()` helper; routed 3 bare `error_log()` calls through it
- `integrations/wordpress-provenance-plugin/docker-compose.yml`
  - Removed obsolete `version: "3.9"` attribute
- `enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`
  - 4 new contract tests added

## Per-User Error Reporting — Implemented
Full error reporting system built across 3 layers:

### Layer 1: Per-post admin notice (all tiers)
- `_encypher_last_sign_error` post meta stores last failure (timestamp, code, message, consecutive count)
- `_encypher_consecutive_failures` post meta tracks unbroken failure streak
- `render_sign_error_notice()` in `Rest` class shows dismissible WP admin notice on post edit screen
- Notice links to Analytics error log and Settings; dismissible via AJAX with nonce
- `_encypher_sign_error_dismissed` cleared on next successful sign

### Layer 2: Site-wide error log ring buffer (all tiers, tier-gated display)
- `class-encypher-provenance-error-log.php` — new `ErrorLog` static class
- `encypher_error_log` wp_options ring buffer, max 50 entries
- Free tier: sees last 10 entries in Analytics page
- Enterprise/strategic_partner: sees all 50 + Export CSV button
- Clear log button (all tiers, admin-only, nonce-protected)
- Analytics page `#error-log` section: table with Time, Post, Context, Error code, Message, Streak columns
- Streak ≥3 shown in red, 2 in amber, 1 in neutral

### Layer 3: Outbound webhook on repeated failures (enterprise add-on)
- `error_webhook_url` setting (enterprise only, sanitized with `esc_url_raw`, free tier always cleared)
- `error_webhook_threshold` setting (1–100, default 3)
- Fires non-blocking `wp_remote_post` when consecutive failures hit threshold (and every N thereafter)
- JSON payload: event, site_name, site_url, post_id, post_title, post_url, error_code, error_message, consecutive_failures, timestamp

## Files Changed (error reporting)
- `includes/class-encypher-provenance-error-log.php` — NEW
- `includes/class-encypher-provenance.php` — require ErrorLog
- `includes/class-encypher-provenance-rest.php` — perform_signing wires ErrorLog, admin notice + dismiss handlers
- `includes/class-encypher-provenance-admin.php` — webhook setting/renderers/sanitize, AJAX clear+export, Analytics error log section
- `enterprise_api/tests/test_wordpress_provenance_plugin_contract.py` — 7 new contract tests

## Test Results
41/41 contract tests pass ✅

## Git Commit Suggestion
```
feat(wp-plugin): comprehensive per-user error reporting system

Layer 1 — Per-post admin notice (all tiers):
- Record sign failures in _encypher_last_sign_error post meta with
  timestamp, error code, message, and consecutive failure count
- Show dismissible WP admin notice on post edit screen linking to
  Analytics error log and Settings; clears on next successful sign

Layer 2 — Site-wide error log ring buffer (all tiers, tier-gated):
- New ErrorLog static class (class-encypher-provenance-error-log.php)
- encypher_error_log wp_options ring buffer, max 50 entries
- Free tier sees last 10 in Analytics; Enterprise sees all 50 + CSV export
- Analytics page gains #error-log section: Time/Post/Context/Code/Message/Streak
- Streak coloring: red ≥3, amber 2, neutral 1
- Clear log button (admin-only, nonce-protected)

Layer 3 — Outbound webhook on repeated failures (enterprise add-on):
- error_webhook_url setting (enterprise only, sanitized, free always cleared)
- error_webhook_threshold setting (1–100, default 3)
- Non-blocking wp_remote_post fires at threshold and every N thereafter
- JSON payload includes site context, post details, error info, streak count

Also: auto-sign post_types fix, content pagination, debug_log gating,
status copy fix, docker-compose version attribute removal (from prior session)

Tests: 41/41 contract tests pass
```

---

## 2026-02-19 Beta Release Prep Addendum

### Completed
- Removed Hard Binding toggle from Settings UI; hard binding is now always enforced (`add_hard_binding = true`).
- Added Dashboard support contact section with direct email CTA: `wp-support@encypherai.com`.
- Standardized full-wordmark branded headers (`logo | Page`) across Dashboard, Content, Settings, Analytics, Account, Bulk Sign, and Coalition.
- Fixed header sizing inconsistencies and validated runtime rendering with Puppeteer on Settings, Bulk Sign, and Coalition pages (computed width = `120px`).
- Bumped plugin version to `1.0.0-beta` in plugin header/constant and `readme.txt` Stable tag.
- Added `1.0.0-beta` changelog + upgrade notice entries.
- Packaged distributable zip: `integrations/wordpress-provenance-plugin/plugin/encypher-provenance-1.0.0-beta.zip`.
- Verified zip structure excludes `tests/` and top-level plugin `README.md`.
- Tagged and pushed release tag: `wp-plugin/v1.0.0-beta`.

### Validation
- `uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py -q --tb=short`
- Result: `52 passed`

### Git Commit Suggestion
```
release(wp-plugin): prepare 1.0.0-beta public beta package

- remove Hard Binding setting from admin UI and enforce add_hard_binding=true
- add Dashboard support CTA with wp-support@encypherai.com
- standardize full-wordmark page headers (logo | page name) across all Encypher admin tabs
- fix header lockup sizing regressions on Settings/Bulk Sign/Coalition (120px normalized)
- update plugin/readme versions to 1.0.0-beta and add changelog + upgrade notice
- package plugin zip for distribution and verify archive excludes dev-only files

Verification:
- contract suite: 52 passed
- puppeteer runtime checks confirm correct logo sizing on settings/bulk/coallition pages
```
