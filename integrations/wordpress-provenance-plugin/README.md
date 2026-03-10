# Encypher Provenance WordPress Plugin

This plugin brings Encypher's C2PA signing and verification workflow into the WordPress editor with **full provenance chain tracking**. It talks directly to the Enterprise API so that every blog post can be protected with an embedded C2PA manifest, automatically tracking edits with ingredient references to preserve the complete content history.

## Structure

```
wordpress-provenance-plugin/
|- README.md
|- docker-compose.yml
|- docs/
|  |- wordpress-ai-integration.md   ← WordPress/ai integration guide
|  |- experiments/
|     |- content-provenance.md      ← Upstream PR spec for WordPress/ai
|     |- Content_Provenance.php     ← Draft experiment class for upstream PR
|- plugin/
   |- encypher-provenance/
      |- assets/
      |   |- css/
      |   |   |- editor.css
      |   |   |- bulk-mark.css
      |   |   |- settings-page.css
      |   |   |- frontend.css
      |   |   |- coalition-widget.css
      |   |   |- wordpress-ai-provenance.css  ← WordPress/ai sidebar panel styles
      |   |- js/
      |       |- editor-sidebar.js            ← Gutenberg provenance status panel
      |       |- wordpress-ai-provenance.js   ← WordPress/ai AI content shield badge
      |       |- bulk-mark.js
      |       |- settings-page.js
      |       |- classic-meta-box.js
      |       |- editor-embedding-nav.js
      |- includes/
      |   |- class-encypher-provenance.php              ← Main bootstrap
      |   |- class-encypher-provenance-admin.php        ← Settings UI, editor enqueue
      |   |- class-encypher-provenance-rest.php         ← REST endpoints
      |   |- class-encypher-provenance-verification.php ← Verification hooks
      |   |- class-encypher-provenance-bulk.php         ← Bulk signing
      |   |- class-encypher-provenance-frontend.php     ← Public badge
      |   |- class-encypher-provenance-coalition.php    ← Coalition dashboard + enrollment
      |   |- class-encypher-provenance-html-parser.php  ← HTML→text extraction
      |   |- class-encypher-provenance-error-log.php    ← Error log
      |   |- class-encypher-sign-ability.php            ← WordPress Abilities API: encypher/sign
      |   |- class-encypher-verify-ability.php          ← WordPress Abilities API: encypher/verify
      |   |- class-encypher-provenance-wordpress-ai.php ← WordPress/ai compat layer
      |- encypher-provenance.php
```

- `encypher-provenance.php` — plugin entry point, constants, and singleton bootstrap.
- `includes/` — PHP classes for REST endpoints, settings UI, verification, bulk signing, frontend badge, Coalition, WordPress/ai compatibility, and WordPress Abilities API registration.
- `assets/js/` — Gutenberg sidebar, WordPress/ai AI Content Provenance panel, bulk signing UI, settings page, and Classic Editor meta box.
- `assets/css/` — admin and frontend styles.
- `docs/` — integration guides and upstream PR draft for the WordPress/ai experiment framework.

## Enterprise API Integration

The plugin targets the production Enterprise API hosted at `https://api.encypherai.com`:

- `POST /api/v1/sign` - Unified signing endpoint with options-based configuration (`manifest_mode: micro`, `ecc`, `embed_c2pa`, sentence segmentation, and optional `return_embedding_plan`).
- `POST /api/v1/verify` - Public verification endpoint used by the plugin.

Both endpoints and their request/response shapes are described in detail in the [Enterprise API README](../../enterprise_api/README.md) and [C2PA Provenance Chain documentation](../../docs/c2pa/C2PA_PROVENANCE_CHAIN.md). API failures are surfaced in the editor so authors can retry or contact support.

### D2 Workflow Views

- [Publish flow](./docs/publish-flow.d2) — shows draft signing, API round-trip, signed post storage, publish, and frontend verification badge replay.
- [Onboarding connect flow](./docs/onboarding-connect-flow.d2) — shows email-based WordPress site connection from settings page through dashboard approval and API-key provisioning.
- [WordPress/ai flow](./docs/wordpress-ai-flow.d2) — shows experiment output interception, ability invocation, signing, post-meta storage, and Gutenberg sidebar status.

### C2PA Provenance Chain Features

✅ **Automatic Action Detection**: `c2pa.created` on initial publish, `c2pa.edited` on updates
✅ **Ingredient References**: Each edit includes the previous version's complete manifest
✅ **Original Creation Date**: Preserved through the entire edit history
✅ **Provenance Chain Viewer**: Visual display of complete edit history in verification modal
✅ **Copy Button**: Export full JSON manifest with one click
✅ **No Double-Signing**: Smart caching prevents unnecessary re-signing

### Advanced Features (Pro/Enterprise)

The plugin unlocks additional capabilities for licensed tiers:

*   **Whitelabeling**: Hide the "Powered by Encypher" branding in verification badges (Pro/Enterprise only).
*   **Advanced Analytics**: View "Verification Hits" directly in the WordPress dashboard, tracking how many users are verifying your content via the public API.

## Features & Tiers


The plugin adapts its capabilities based on your Encypher workspace tier:

| Feature | Free | Pro ($99/mo) | Enterprise |
|---------|------|--------------|------------|
| **Signature** | Shared (Managed) | Custom (BYOK) | Custom (HSM Option) |
| **Granularity** | Document-level | Sentence-level | Sentence-level |
| **Bulk Marking** | 100 posts / batch | Unlimited | Unlimited |
| **Coalition** | Required | Optional | Optional |
| **Support** | Community | Priority | Dedicated SLA |

*   **Free Tier**: Perfect for personal blogs. Uses a shared Encypher key and standard document-level signing.
*   **Pro Tier**: For professional publishers. Connect your own signing key (BYOK), enable sentence-level attribution (Merkle trees), and process large archives.
*   **Enterprise Tier**: For large organizations. High-volume API limits, HSM-backed keys, and multi-site support.

## New User Onboarding (Email Connect Flow)

1. Visit `https://dashboard.encypherai.com/signup` and create an Encypher account if you do not already have one.
2. Install and activate the WordPress plugin.
3. Open **Encypher > Settings** in WordPress, enter your work email, and click **Email me a secure connect link**.
4. Open the secure email from Encypher and approve the WordPress site connection in the browser.
5. Return to WordPress and keep the settings page open for a few seconds while the plugin polls for completion and stores the provisioned API key automatically.

If your team already manages Encypher API credentials outside the guided onboarding flow, the plugin still supports manual API key entry.

## Configuration & Usage

1. Copy `plugin/encypher-provenance` into a WordPress installation under `wp-content/plugins/`.
2. Activate **Encypher Provenance** in the WordPress admin dashboard.
3. Go to **Encypher > Settings** and either:
   - enter your work email and use the secure email connect flow to provision the API key automatically, or
   - paste an existing API key manually.
4. Confirm the **API Base URL** is `https://api.encypherai.com/api/v1` (or your self-hosted Enterprise API endpoint).
5. In the Gutenberg editor, open the **Encypher Provenance** panel to sign your draft. The Classic Editor uses the provided meta box. Each signing request produces C2PA-compliant wrapped text that replaces the post body contents.
6. When posts load on the public site the plugin replays `POST /api/v1/verify` and displays a badge summarising the verification result.

## WordPress/ai Integration

The plugin integrates with the [WordPress/ai plugin](https://github.com/WordPress/ai) ("AI Experiments") — the official canonical WordPress AI framework on a path toward WordPress core.

When both plugins are active and **WordPress/ai Integration** is enabled in Encypher settings, all AI-generated content is automatically signed with C2PA provenance before it's committed to a post:

| WordPress/ai Experiment | Signed? |
|---|---|
| Title Generation | ✅ |
| Excerpt Generation | ✅ |
| Summarization | ✅ |
| Review Notes | ✅ |
| Alt Text | ✅ |

### Components

- **Compat layer** (`class-encypher-provenance-wordpress-ai.php`) — hooks into all 5 experiment output filters, calls `/api/v1/sign`, stores signed experiment records in post meta.
- **WordPress Abilities API** (`class-encypher-sign-ability.php`, `class-encypher-verify-ability.php`) — registers `encypher/sign` and `encypher/verify` as first-class abilities callable by any plugin via `wp_do_ability()`.
- **AI Content Provenance sidebar** (`assets/js/wordpress-ai-provenance.js`) — Gutenberg panel with a shield badge (green/yellow/red/grey) showing provenance status for AI-generated content in the current post.
- **REST endpoint** `GET encypher-provenance/v1/wordpress-ai-status?post_id=N` — returns `{ status, details: { experiments } }` consumed by the sidebar panel.
- **Coalition auto-enrollment** — when the Coalition toggle is enabled in settings, the site is automatically enrolled in the Encypher Coalition on the first save.

### Setup

1. Install and activate the WordPress/ai plugin.
2. Go to **Encypher > Settings** and enable **WordPress/ai Integration**.
3. Optionally enable **Coalition Auto-Enrollment**.
4. AI-generated content is now auto-signed. The "AI Content Provenance" sidebar panel in the block editor shows live status.

See [`docs/wordpress-ai-integration.md`](./docs/wordpress-ai-integration.md) for full details and [`docs/experiments/content-provenance.md`](./docs/experiments/content-provenance.md) for the upstream PR spec.

---

## Local Docker Environment

A `docker-compose.yml` is provided so you can run WordPress, MySQL, PostgreSQL, and the Enterprise API together for local testing.

For the full internal local-development setup, testing credentials, and Docker workflow, use [`LOCAL_TESTING_GUIDE.md`](./LOCAL_TESTING_GUIDE.md). The steps below are a lightweight overview only.

1. Build and start the stack:
   ```bash
   cd integrations/wordpress-provenance-plugin
   docker compose up --build
   ```
   - WordPress: `http://localhost:8085`
   - Enterprise API: `http://localhost:8001`
2. Install WordPress (first run only):
   ```bash
   docker compose run --rm wp-cli core install \
     --url=http://localhost:8085 \
     --title="Encypher Local" \
     --admin_user=admin \
     --admin_password=admin \
     --admin_email=admin@example.com
   ```
3. Activate the plugin:
   ```bash
   docker compose run --rm wp-cli plugin activate encypher-provenance
   ```
4. Sign in at `http://localhost:8085/wp-admin`, choose **Encypher > Settings**, and configure the local API endpoint described in [`LOCAL_TESTING_GUIDE.md`](./LOCAL_TESTING_GUIDE.md).
5. Create or edit posts as usual. Signing requests now hit the containerised Enterprise API service.

Stop the stack with:
```bash
docker compose down
```
Add `-v` to also remove the MySQL and PostgreSQL volumes for a clean slate.

## Testing

Automated tests are not yet wired up for the WordPress code. To validate changes manually:

- Run the Docker stack described above or point the plugin at the hosted preview environment.
- Create or edit posts in WordPress and confirm that signed content embeds invisible manifests.
- Publish a signed post and ensure the verification badge reflects the API response.

Please open issues or pull requests if you encounter problems while onboarding or integrating with the Enterprise API.
