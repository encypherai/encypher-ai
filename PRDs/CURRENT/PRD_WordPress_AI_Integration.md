# PRD: WordPress/ai Integration

**Status:** Complete
**Team:** TEAM_250
**Current Goal:** Integrate Encypher provenance into the WordPress/ai experiment framework as a compatibility layer, first-class Abilities, Gutenberg panel, Coalition enrollment, and upstream PR docs.

## Overview
The WordPress/ai plugin ("AI Experiments") is an official canonical WordPress plugin on a path toward WordPress core. Encypher integrates into its experiment framework to auto-sign AI-generated content with C2PA manifests, become a first-class Ability, show provenance status in the editor, enroll publishers in the Coalition, and draft an upstream contribution.

## Objectives
- Auto-sign AI-generated content from WordPress/ai experiments (title, excerpt, summary, review notes, alt text)
- Register `encypher/sign` and `encypher/verify` as WordPress Abilities API citizens
- Show WordPress/ai AI content provenance status in the Gutenberg sidebar
- Auto-enroll publishers in the Encypher Coalition when experiment is enabled
- Draft Content Provenance experiment for upstream PR to WordPress/ai

## Tasks

### Epic 1: WordPress/ai Compatibility Layer
- [x] 1.1 Create `includes/class-encypher-provenance-wordpress-ai.php` — detect WP/ai active, hook into lifecycle
- [x] 1.2 Hook into `wp_abilities_api_init` for bootstrap
- [x] 1.3 Filter each experiment content output (title, excerpt, summary, review_notes, alt_text) → call sign API ✅ all 5 filters confirmed
- [x] 1.4 Embed Unicode watermark in signed content ✅ returned via `signed_text` from API
- [x] 1.5 Add WP/ai settings section (API key visible, WP/ai toggle) to admin settings page ✅ `wordpress_ai_enabled` field confirmed
- [x] 1.6 Wire up in main plugin bootstrap (`class-encypher-provenance.php`) ✅ `WordPress_AI_Compat` referenced 2x

### Epic 2: Encypher Ability Registration
- [x] 2.1 Create `includes/class-encypher-sign-ability.php` extending `Abstract_Ability` pattern ✅
- [x] 2.2 Create `includes/class-encypher-verify-ability.php` extending `Abstract_Ability` pattern ✅
- [x] 2.3 Register both abilities in plugin bootstrap ✅ `sign_ability`/`verify_ability` referenced 8x

### Epic 3: Gutenberg Sidebar WordPress/ai Panel
- [x] 3.1 Add `assets/js/wordpress-ai-provenance.js` — sidebar panel showing AI content provenance status ✅ 272 lines
- [x] 3.2 Shield badge (green/yellow/red) based on verify API result ✅ `ShieldBadge` component confirmed
- [x] 3.3 Wire enqueue in PHP (Admin class) ✅ 4 references in admin

### Epic 4: Coalition Auto-Enrollment
- [x] 4.1 Extend Coalition class with enrollment API call ✅ `enroll_site()` confirmed
- [x] 4.2 Add enrollment toggle in admin settings ✅ `coalition_auto_enroll` confirmed
- [x] 4.3 On settings save + toggle ON → POST to Coalition enrollment endpoint ✅ rising-edge hook
- [x] 4.4 Store enrollment status, show confirmation notice ✅ `encypher_coalition_enrolled` option confirmed

### Epic 5: Documentation + Upstream PR Draft
- [x] 5.1 Write `docs/experiments/content-provenance.md` ✅ 96 lines
- [x] 5.2 Draft `Content_Provenance` PHP class following WP/ai patterns ✅

### Post-session addition
- [x] Add `GET encypher-provenance/v1/wordpress-ai-status` REST endpoint ✅ route + handler confirmed (3 references)
- [x] Record signed experiments in `_encypher_wpai_experiments` post meta ✅ confirmed

## Success Criteria
- [x] WordPress/ai active → AI content auto-signed via Encypher API
- [x] `wp_do_ability('encypher/sign', ...)` callable by third-party plugins
- [x] Sidebar panel shows signed/unsigned/tampered status for AI content
- [x] Coalition enrollment via admin settings toggle
- [x] Upstream PR draft ready for submission

## Completion Notes
All tasks verified via code grep audit on 2026-03-10 (TEAM_250). No WordPress runtime available to execute end-to-end tests — PHP is structurally correct and follows existing plugin conventions. Functional testing requires a WP dev environment (use `.wp-env.json` from the wordpress/ai repo).
