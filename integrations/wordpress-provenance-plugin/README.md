# Encypher Provenance WordPress Plugin

This plugin brings Encypher's C2PA signing and verification workflow into the WordPress editor with **full provenance chain tracking**. It talks directly to the Enterprise API so that every blog post can be protected with an embedded C2PA manifest, automatically tracking edits with ingredient references to preserve the complete content history.

## Structure

```
wordpress-provenance-plugin/
|- README.md
|- docker-compose.yml
|- plugin/
   |- encypher-provenance/
      |- assets/
      |   |- css/
      |   |   |- editor.css
      |   |- js/
      |       |- classic-meta-box.js
      |       |- editor-sidebar.js
      |- includes/
      |   |- class-encypher-provenance-admin.php
      |   |- class-encypher-provenance-rest.php
      |   |- class-encypher-provenance-verification.php
      |   |- class-encypher-provenance.php
      |- encypher-provenance.php
```

- `encypher-provenance.php` - plugin bootstrap and registration logic.
- `includes/` - PHP classes that expose REST endpoints, provide settings screens, and run verification hooks.
- `assets/js/` - Gutenberg sidebar and Classic Editor integrations for signing content.
- `assets/css/` - shared styling for WordPress admin surfaces.

## Enterprise API Integration

The plugin targets the production Enterprise API hosted at `https://api.encypherai.com`:

- `POST /api/v1/sign` - Unified signing endpoint with options-based configuration (`manifest_mode: micro`, `ecc`, `embed_c2pa`, sentence segmentation, and optional `return_embedding_plan`).
- `POST /api/v1/verify` - Public verification endpoint used by the plugin.

Both endpoints and their request/response shapes are described in detail in the [Enterprise API README](../../enterprise_api/README.md) and [C2PA Provenance Chain documentation](../../docs/c2pa/C2PA_PROVENANCE_CHAIN.md). API failures are surfaced in the editor so authors can retry or contact support.

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

## New User Onboarding (Free API Key Flow)

1. Visit `https://dashboard.encypherai.com/signup` and create a free Encypher account. The starter tier issues a sandbox key suitable for testing the plugin.
2. Verify your email, then open **Enterprise API > API Keys** in the dashboard and click **Generate Key**. Copy the issued value (`encypher_test_...`).
3. Optionally request production access from the dashboard if you need higher quotas or SSL.com certificates provisioned.
4. Store the API key securely. WordPress administrators will paste it into the plugin settings in the next step.

For local development without dashboard access you can run the Enterprise API service from this repository and use the `DEMO_API_KEY` described in [`enterprise_api/.env.example`](../../../enterprise_api/.env.example).

## Configuration & Usage

1. Copy `plugin/encypher-provenance` into a WordPress installation under `wp-content/plugins/`.
2. Activate **Encypher Provenance** in the WordPress admin dashboard.
3. Go to **Encypher > Settings** and set:
   - **API Base URL:** `https://api.encypherai.com/api/v1` (or your self-hosted Enterprise API endpoint).
   - **API Key:** paste the key generated during onboarding.
4. In the Gutenberg editor, open the **Encypher Provenance** panel to sign your draft. The Classic Editor uses the provided meta box. Each signing request produces C2PA-compliant wrapped text that replaces the post body contents.
5. When posts load on the public site the plugin replays `POST /api/v1/verify` and displays a badge summarising the verification result.

## Local Docker Environment

A `docker-compose.yml` is provided so you can run WordPress, MySQL, PostgreSQL, and the Enterprise API together for local testing.

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
4. Sign in at `http://localhost:8085/wp-admin`, choose **Encypher > Settings**, and configure:
   - **API Base URL:** `http://enterprise-api:8000/api/v1`
   - **API Key:** `demo-local-key`
   - Enable automatic verification if desired.
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
