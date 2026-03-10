# Changelog

All notable changes to the Encypher Provenance WordPress plugin are documented here.

## [1.2.0] — 2026-03-10

### Added
- **WordPress/ai integration** (`class-encypher-provenance-wordpress-ai.php`): detects the WordPress/ai plugin and hooks into all five experiment output filters — Title Generation, Excerpt Generation, Summarization, Review Notes, Alt Text — auto-signing AI-generated content via `/api/v1/sign` before it is committed to the post. Signed experiment records stored in `_encypher_wpai_experiments` post meta.
- **WordPress Abilities API** (`class-encypher-sign-ability.php`, `class-encypher-verify-ability.php`): registers `encypher/sign` and `encypher/verify` as first-class abilities. Third-party plugins can call `wp_do_ability('encypher/sign', ['text' => …])`. Abilities registered on both `wp_abilities_api_init` and `init` priority 20 for load-order safety.
- **AI Content Provenance Gutenberg sidebar panel** (`assets/js/wordpress-ai-provenance.js`): new panel titled "AI Content Provenance" with a shield badge (green = verified, yellow = unverified, red = tampered, grey = no AI content), signed experiment list with timestamps, and a "Check Provenance" button. Gracefully degrades when the WordPress/ai integration is disabled.
- **REST endpoint** `GET encypher-provenance/v1/wordpress-ai-status?post_id=N`: returns `{ status, details: { experiments } }` based on `_encypher_wpai_experiments` meta and overall post signing status.
- **Coalition auto-enrollment**: new `coalition_auto_enroll` settings toggle. On rising edge (first enable), POSTs site URL and name to `/coalition/enroll`, stores `encypher_coalition_enrolled` and `encypher_coalition_enrolled_at` options, and surfaces a WP admin settings notice with the result.
- **Admin settings**: new "WordPress/ai Integration" section with `wordpress_ai_enabled` toggle (shows a notice if the WordPress/ai plugin is not detected) and `coalition_auto_enroll` toggle (shows enrollment date when enrolled).
- **Docs**: `docs/wordpress-ai-integration.md` integration guide, `docs/experiments/content-provenance.md` upstream PR spec, `docs/experiments/Content_Provenance.php` draft experiment class for contribution to the WordPress/ai repo.

### Changed
- Bootstrap (`class-encypher-provenance.php`) loads three new classes and wires them in `boot()`.
- Admin (`class-encypher-provenance-admin.php`) adds `wordpress_ai_enabled` and `settings_url` to `EncypherProvenanceConfig` JS global; enqueues new sidebar JS/CSS.
- `readme.txt` stable tag bumped to 1.2.0.

---

## [1.1.0]

### Added
- Email-based secure connect flow with automatic API key provisioning via magic link.
- WordPress approval page flow for emailed connect links with polling.
- Coalition dashboard (`class-encypher-provenance-coalition.php`): widget, submenu page, stats from `/coalition/dashboard`, 1-hour transient cache.
- Bulk signing UI (`class-encypher-provenance-bulk.php`): pause/resume, real-time progress, error log, batch-size gated by tier.
- Frontend C2PA badge (`class-encypher-provenance-frontend.php`): optional badge on public posts with configurable position.
- HTML parser (`class-encypher-provenance-html-parser.php`): byte-level text fragment extraction preserving invisible Unicode characters for accurate verification.
- Error log (`class-encypher-provenance-error-log.php`): persistent error log in WP admin.
- Sentence-level verifier chips in the Gutenberg sidebar for all tiers.
- Pre-publish panel in the block editor.
- C2PA verification page at `/c2pa-verify/{instance_id}` (rewrite rule + template).
- Provenance chain ingredient references for updated posts (`c2pa.edited` with previous instance).

---

## [1.0.0-beta]

### Added
- Initial public beta.
- C2PA-compliant text authentication (full manifest: magic number, JUMBF container, Unicode variation selector embedding).
- Auto-sign on publish (`c2pa.created`) and update (`c2pa.edited`).
- Manual marking in Gutenberg sidebar and Classic Editor meta box.
- Public verification links via `/api/v1/verify`.
- SHA-256 hard binding (`c2pa.hash.data`) enforced by default.
- Two-tier support: Free (managed key) and Enterprise (BYOK).
- Dashboard widget for provenance coverage stats.
- Settings UI: API key, API base URL, auto-mark toggles, metadata format.
