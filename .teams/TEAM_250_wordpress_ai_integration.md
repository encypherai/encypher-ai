# TEAM_250 — WordPress/ai Integration

## Session
- Date: 2026-03-10
- Team: TEAM_250
- Focus: WordPress/ai integration epics (1–5)

## Status
- [x] Epic 1: WordPress/ai compatibility layer
- [x] Epic 2: Encypher Ability registration
- [x] Epic 3: Gutenberg sidebar WordPress/ai panel
- [x] Epic 4: Coalition auto-enrollment
- [x] Epic 5: Docs + upstream PR draft

## Files Created/Modified

### New PHP files
- `includes/class-encypher-provenance-wordpress-ai.php` — WordPress_AI_Compat class; detects WP/ai by class/function/plugin file; hooks 5 experiment output filters; signs content via /api/v1/sign
- `includes/class-encypher-sign-ability.php` — Encypher_Sign_Ability; registers encypher/sign in WP Abilities API
- `includes/class-encypher-verify-ability.php` — Encypher_Verify_Ability; registers encypher/verify (no API key needed)

### Modified PHP files
- `includes/class-encypher-provenance.php` — requires 3 new classes, adds properties, instantiates, wires to boot()
- `includes/class-encypher-provenance-coalition.php` — adds enroll_site(), maybe_enroll_on_settings_save(), rising-edge enrollment trigger
- `includes/class-encypher-provenance-admin.php` — adds WP/ai settings section + coalition_auto_enroll checkbox; adds wordpress_ai_enabled + settings_url to EncypherProvenanceConfig; enqueues new JS/CSS

### New JS/CSS files
- `assets/js/wordpress-ai-provenance.js` — Gutenberg sidebar panel with shield badge, provenance status, experiment list, Check Provenance button
- `assets/css/wordpress-ai-provenance.css` — Minimal panel styles

### New documentation
- `docs/experiments/content-provenance.md` — Experiment spec + upstream PR checklist
- `docs/experiments/Content_Provenance.php` — Draft class for WordPress/ai upstream PR
- `docs/wordpress-ai-integration.md` — Integration guide

## Key Decisions
- WordPress/ai detection uses 3 strategies (class, function, plugin file) for resilience
- Coalition enrollment is rising-edge only (no re-enrollment on every save)
- Ability registration fires on both wp_abilities_api_init AND init priority 20 (load-order safety)
- New JS sidebar does NOT modify existing editor-sidebar.js
- Upstream PR draft lives in docs/ (not shipped as runtime code)

## Open Items
- REST endpoint `encypher-provenance/v1/wordpress-ai-status` needs to be implemented in the REST class (sidebar JS calls it; currently falls back gracefully to 'unverified' on 404)
- Needs WP dev environment testing (`.wp-env.json` from WordPress/ai repo)
- Upstream PR to WordPress/ai repo pending human review of Content_Provenance.php draft

## Suggested Commit Message
```
feat(wordpress-plugin): add WordPress/ai integration layer

- Add WordPress_AI_Compat class: auto-signs content from all 5 WP/ai
  experiments (title, excerpt, summary, review notes, alt text) via
  Encypher /api/v1/sign before content is committed to post

- Add Encypher_Sign_Ability and Encypher_Verify_Ability: register
  encypher/sign and encypher/verify as first-class WordPress Abilities
  API citizens callable by any plugin via wp_do_ability()

- Add Gutenberg sidebar panel (wordpress-ai-provenance.js): shield badge
  (green/yellow/red/grey) showing AI content provenance status inline
  in the block editor

- Add Coalition auto-enrollment: rising-edge trigger on settings save,
  POSTs to /coalition/enroll, surfaces WP admin notice on result

- Add docs/experiments/content-provenance.md + Content_Provenance.php
  draft class for upstream contribution to WordPress/ai repo

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```
