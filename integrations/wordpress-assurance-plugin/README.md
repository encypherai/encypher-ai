# Encypher Assurance WordPress Plugin

This plugin brings Encypher's C2PA signing and verification workflow into the WordPress editor. It talks directly to the Enterprise API documented in [`enterprise_api/docs/API.md`](../../../enterprise_api/docs/API.md) so that every blog post can be protected with an embedded manifest and verified on publish.

## Structure

```
wordpress-assurance-plugin/
|- README.md
|- docker-compose.yml
|- plugin/
   |- encypher-assurance/
      |- assets/
      |   |- css/
      |   |   |- editor.css
      |   |- js/
      |       |- classic-meta-box.js
      |       |- editor-sidebar.js
      |- includes/
      |   |- class-encypher-assurance-admin.php
      |   |- class-encypher-assurance-rest.php
      |   |- class-encypher-assurance-verification.php
      |   |- class-encypher-assurance.php
      |- encypher-assurance.php
```

- `encypher-assurance.php` - plugin bootstrap and registration logic.
- `includes/` - PHP classes that expose REST endpoints, provide settings screens, and run verification hooks.
- `assets/js/` - Gutenberg sidebar and Classic Editor integrations for signing content.
- `assets/css/` - shared styling for WordPress admin surfaces.

## Enterprise API Integration

The plugin targets the production Enterprise API hosted at `https://api.encypherai.com`:

- `POST /api/v1/sign` signs a post by embedding a C2PA manifest. The plugin sends the post body, title, and optional URL or document type fields.
- `POST /api/v1/verify` validates stored content before display and surfaces provenance metadata in the WordPress UI.

Both endpoints and their request/response shapes are described in detail in [`API.md`](../../../enterprise_api/docs/API.md). The plugin expects JSON responses that match those schemas. API failures are surfaced in the editor so authors can retry or contact support.

## New User Onboarding (Free API Key Flow)

1. Visit `https://dashboard.encypherai.com/signup` and create a free Encypher account. The starter tier issues a sandbox key suitable for testing the plugin.
2. Verify your email, then open **Enterprise API > API Keys** in the dashboard and click **Generate Key**. Copy the issued value (`encypher_test_...`).
3. Optionally request production access from the dashboard if you need higher quotas or SSL.com certificates provisioned.
4. Store the API key securely. WordPress administrators will paste it into the plugin settings in the next step.

For local development without dashboard access you can run the Enterprise API service from this repository and use the `DEMO_API_KEY` described in [`enterprise_api/.env.example`](../../../enterprise_api/.env.example).

## Configuration & Usage

1. Copy `plugin/encypher-assurance` into a WordPress installation under `wp-content/plugins/`.
2. Activate **Encypher Assurance** in the WordPress admin dashboard.
3. Go to **Settings > Encypher Assurance** and set:
   - **API Base URL:** `https://api.encypherai.com/api/v1` (or your self-hosted Enterprise API endpoint).
   - **API Key:** paste the key generated during onboarding.
4. In the Gutenberg editor, open the **Encypher Assurance** panel to sign your draft. The Classic Editor uses the provided meta box. Each signing request produces C2PA-compliant wrapped text that replaces the post body contents.
5. When posts load on the public site the plugin replays `POST /api/v1/verify` and displays a badge summarising the verification result.

## Local Docker Environment

A `docker-compose.yml` is provided so you can run WordPress, MySQL, PostgreSQL, and the Enterprise API together for local testing.

1. Build and start the stack:
   ```bash
   cd integrations/wordpress-assurance-plugin
   docker compose up --build
   ```
   - WordPress: `http://localhost:8080`
   - Enterprise API: `http://localhost:8000`
2. Install WordPress (first run only):
   ```bash
   docker compose run --rm wp-cli core install \
     --url=http://localhost:8080 \
     --title="Encypher Local" \
     --admin_user=admin \
     --admin_password=admin \
     --admin_email=admin@example.com
   ```
3. Activate the plugin:
   ```bash
   docker compose run --rm wp-cli plugin activate encypher-assurance
   ```
4. Sign in at `http://localhost:8080/wp-admin`, choose **Settings > Encypher Assurance**, and configure:
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
