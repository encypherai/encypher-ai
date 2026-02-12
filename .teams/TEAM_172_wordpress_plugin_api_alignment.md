# TEAM_172 — WordPress Plugin API Alignment

## Status: COMPLETE

## Summary
Full alignment of the WordPress Provenance Plugin with the enterprise API freemium model. Three sessions:
- **Session 1**: Tier coercion (starter→free), manifest_mode defaults, verify endpoint, upsell/UI updates
- **Session 2**: Rename Encypher Assurance → Encypher Provenance, remove all merkle storage (DB handles it), remove all NMA references, fix editor sidebar panel rendering
- **Session 3**: Remove legacy backward compat (unreleased plugin), remove all coalition revenue split logic (managed externally)

## Key Changes

### Session 1 — API Alignment
1. **Tier naming**: `starter` → `free` throughout plugin
2. **Default manifest_mode**: `micro_ecc_c2pa` in all sign requests
3. **Segmentation**: `sentence` level + `index_for_attribution: true` for all tiers
4. **Verify endpoint**: Always `/verify/advanced`
5. **Upsell module**: 2-tier model (free → enterprise)
6. **Bulk signing**: Free tier limit 10 docs
7. **Trusted hosts**: Added `encypher-enterprise-api` for Docker inter-container calls

### Session 2 — Rename, Cleanup, Sidebar Fix
9. **Rename**: `EncypherAssurance` → `EncypherProvenance` namespace, `ENCYPHER_ASSURANCE_*` → `ENCYPHER_PROVENANCE_*` constants, `encypher_assurance_settings` → `encypher_provenance_settings` option
10. **Merkle removal**: Removed `persist_merkle_snapshot()`, `get_merkle_snapshot()`, all `_encypher_merkle_*` meta storage, merkle state/rendering from JS, merkle CSS from editor.css
11. **NMA removal**: Removed `render_nma_member_field()`, NMA sanitization, NMA settings field registration, `nma_member` from sign payload metadata
12. **Sidebar fix**: `wp.editPost` → `wp.editor || wp.editPost` compat for `PluginDocumentSettingPanel`, added `wp-editor` script dependency, fixed structural JS syntax errors, removed duplicate code blocks
13. **Frontend cleanup**: Removed merkle proof display from verification modal, removed legacy professional/business CSS classes, updated tier_pill to enterprise-only
14. **Docs**: README.md and readme.txt updated to free/enterprise model, no merkle/NMA/Pro references

### Session 3 — Remove Backward Compat & Revenue Splits
15. **Legacy coercion removed**: Deleted all `in_array($tier, ['starter', 'professional', 'business'])` coercion arrays from rest.php (2) and admin.php (2) — plugin is unreleased, no backward compat needed
16. **Revenue split removed**: Deleted `get_revenue_split()` and `calculate_enterprise_upgrade_roi()` from coalition.php — managed by website/internal only
17. **Coalition UI cleaned**: Removed revenue split display, payout thresholds, and ROI upgrade CTAs from coalition-widget.php, coalition-page.php, and render_coalition_enabled_field in admin.php
18. **Upsell cleaned**: Removed "85/15 revenue share" from enterprise upsell features list
19. **Docs cleaned**: Removed revenue share percentages from readme.txt tier features

## Files Modified (15 code + 2 docs)
- `encypher-provenance.php` — constants renamed
- `includes/class-encypher-provenance.php` — namespace, option name, constants
- `includes/class-encypher-provenance-rest.php` — sign payload, merkle removal, NMA removal, verify endpoint
- `includes/class-encypher-provenance-admin.php` — NMA field removal, coalition revenue split, all render methods
- `includes/class-encypher-provenance-bulk.php` — tier defaults, batch limits
- `includes/class-encypher-provenance-coalition.php` — revenue splits, upgrade ROI
- `includes/class-encypher-provenance-frontend.php` — merkle proof removal, tier_pill fix
- `includes/class-encypher-provenance-verification.php` — namespace/constants (via sed)
- `admin/partials/coalition-page.php` — enterprise upgrade CTA
- `admin/partials/coalition-widget.php` — enterprise upgrade CTA
- `assets/js/editor-sidebar.js` — full rewrite: sidebar fix, merkle removal, syntax fixes
- `assets/js/bulk-mark.js` — free tier limit 10
- `assets/css/editor.css` — merkle CSS removed
- `assets/css/frontend.css` — legacy tier CSS removed
- `assets/css/coalition-widget.css` — tier badge colors
- `assets/css/settings-page.css` — tier badge colors
- `README.md` — free/enterprise model, no merkle/NMA
- `readme.txt` — Pro+ reference removed
- `enterprise_api/app/main.py` — trusted hosts

## E2E Test Results
- **Sidebar panel**: ✅ Renders in WP editor (Puppeteer verified)
- **Pre-publish panel**: ✅ Shows C2PA signing info before publish
- **Auto-sign hook**: ✅ Fires on publish (API key expired in test env but hook confirmed)
- **Settings page**: ✅ Free tier, Enterprise CTAs
- **No Assurance refs**: ✅ grep confirmed zero matches in code files
- **No merkle refs**: ✅ grep confirmed zero matches in code files
- **No NMA refs**: ✅ grep confirmed zero matches in code files (only `minmax`/`unmarked` false positives)

## Git Commit Suggestion
```
feat(wordpress-plugin): rename to Provenance, full cleanup (TEAM_172)

Breaking changes:
- Namespace: EncypherAssurance → EncypherProvenance
- Constants: ENCYPHER_ASSURANCE_* → ENCYPHER_PROVENANCE_*
- WP option: encypher_assurance_settings → encypher_provenance_settings
- Post meta prefix: _encypher_assurance_* → _encypher_provenance_*

Removals:
- All merkle hash storage — DB handles this server-side
- All NMA references (render_nma_member_field, nma_member setting/payload)
- All legacy tier coercion arrays (starter/professional/business) — unreleased plugin
- All coalition revenue split logic (get_revenue_split, calculate_enterprise_upgrade_roi,
  revenue split UI in settings/widget/page) — managed by website/internal only

Fixes:
- Editor sidebar: wp.editor/wp.editPost compat for PluginDocumentSettingPanel
- Added wp-editor script dependency for WP 6.5+ compatibility
- Fixed structural JS syntax errors in editor-sidebar.js
- Sentence count now shown for all tiers (was gated to enterprise)

Docs:
- README.md and readme.txt updated to free/enterprise model
- No merkle, NMA, Pro tier, or revenue split references remain
```
