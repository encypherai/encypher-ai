# Encypher C2PA - Text Authentication for WordPress

**Version:** 1.1.0
**Requires WordPress:** 6.0+
**Requires PHP:** 7.4+
**License:** GPL-2.0-or-later

C2PA-compliant text authentication for WordPress. Embed cryptographic proof of origin into your blog posts and pages. Built on standards we're developing with Google, BBC, OpenAI, Adobe, and Microsoft.

---

## Features

### Core Features
- **C2PA-Compliant:** Full adherence to C2PA Manifests_Text.adoc specification
- **Auto-Mark on Publish:** Automatically embed C2PA manifests when publishing posts
- **Auto-Mark on Update:** Re-sign manifests when content is updated
- **Manual Marking:** Mark individual posts with a button in the editor
- **Gutenberg Integration:** Sidebar panel in block editor with provenance status, sentence verification, and manifest viewer
- **Classic Editor Support:** Meta box for classic editor users
- **Public Verification:** Verification links for readers to check authenticity
- **Sentence-Level Verification:** Per-sentence verifier chips in Gutenberg sidebar for all tiers
- **Analytics Dashboard:** Built-in dashboard widget and **Encypher > Analytics** summarize coverage, sentence-level adoption, and recent signing activity
- **Bulk Signing:** Archive all existing posts via **Encypher > Bulk Sign** with real-time progress, pause/resume, and error logs
- **Coalition Dashboard:** **Encypher > Coalition** shows content pool stats, earnings, and membership status
- **WordPress/ai Integration:** Auto-signs AI-generated content from the WordPress/ai plugin experiments (title, excerpt, summary, review notes, alt text)
- **WordPress Abilities API:** Registers `encypher/sign` and `encypher/verify` as callable abilities for third-party plugins

### C2PA Compliance
- **C2PATextManifestWrapper:** Full manifest structure with magic number, version, JUMBF container
- **Unicode Variation Selectors:** Invisible embedding using U+FE00-FE0F and U+E0100-U+E01EF
- **Hard Binding:** c2pa.hash.data assertion with SHA-256 (enabled by default)
- **Soft Binding:** c2pa.soft_binding assertion for tamper detection
- **Proper Actions:** c2pa.created for new posts, c2pa.edited for updates
- **Provenance Chain:** Ingredient references for updated content

### Tier Support
- **Free Tier:** Managed signing, sentence-level embeddings, C2PA manifests, verification badges, Coalition enrollment, WordPress/ai integration
- **Enterprise Tier:** BYOK signing, advanced key management, multi-site support, custom branding, dedicated support

### Plans & Capabilities

| Feature | Free | Enterprise |
|---------|------|------------|
| Auto-sign on publish/update | ✅ | ✅ |
| Manual marking | ✅ | ✅ |
| Sentence-level embeddings | ✅ | ✅ |
| C2PA manifests | ✅ | ✅ |
| Bulk signing | 10 posts/batch | Unlimited |
| Verification badge | ✅ | ✅ (custom styles) |
| Coalition dashboard & enrollment | ✅ | ✅ |
| WordPress/ai auto-signing | ✅ | ✅ |
| WordPress Abilities API (`encypher/sign`, `encypher/verify`) | ✅ | ✅ |
| Bring Your Own Key (BYOK) | ❌ | ✅ |
| Custom branding | ❌ | ✅ |
| C2PA manifest viewer | ❌ | ✅ |
| Dashboard access | API key & usage | Org admin, billing, analytics |
| Support | Community | Dedicated + SLA |

### Dashboard & Account Management

All users authenticate via [dashboard.encypherai.com](https://dashboard.encypherai.com) to:
- Create and manage a workspace for WordPress signing and verification
- Upgrade to Enterprise for BYOK, custom branding, and advanced features
- Manage billing and organization settings

The plugin settings page surfaces direct links:
- **Open Dashboard / Manage Account** – opens the dashboard for workspace management and credential fallback
- **Bring Your Own Key** – launches the dashboard wizard to upload a public key and obtain a signing profile ID (Enterprise only)
- **Enterprise Support** – pre-filled contact form to reach your CSM

The recommended onboarding path now starts directly in WordPress:
- Enter a work email on the settings page
- Receive a secure magic link from Encypher
- Approve the site in the browser
- Let the plugin poll and store the provisioned API key automatically

The API key contains a `tier` claim that the plugin reads to automatically enable or limit functionality (e.g., bulk batch size, BYOK controls). If billing lapses, the plugin gracefully reverts to Free limits but preserves previously signed manifests.

---

## Installation

### From WordPress Admin
1. Download `encypher-provenance.zip` from the Encypher dashboard
2. Go to **Plugins → Add New → Upload Plugin**
3. Upload the ZIP file and click **Install Now**
4. Click **Activate Plugin**

### Manual Installation
1. Upload the `encypher-provenance` folder to `/wp-content/plugins/`
2. Activate the plugin through the **Plugins** menu in WordPress

### Configuration
1. Go to **Encypher > Settings**
2. Enter your work email and click **Email me a secure connect link**
3. Open the secure email from Encypher and approve the WordPress connection
4. Return to the settings page and wait a few seconds while the plugin polls for completion and stores the provisioned API key automatically
5. Review or adjust your settings:
   - **API Base URL:** `https://api.encypherai.com/api/v1` (default)
   - **API Key:** Auto-provisioned by the email connect flow, or entered manually if you already manage credentials
   - **Bring Your Own Signature (Pro/Enterprise):** Paste the Signing Profile ID generated in the dashboard BYOK wizard
   - **Auto-mark on publish/update:** Enable to automatically mark content (recommended)
   - **Metadata Format:** C2PA (default) or Basic
   - **Hard Binding:** Enabled by default for `c2pa.hash.data`

### Manual API Key Setup
1. Go to **Encypher > Settings**
2. Paste an existing Encypher API key
3. Click **Test Connection** to confirm the workspace and site metadata resolve correctly

---

## Usage

### Auto-Mark on Publish (Recommended)

The plugin automatically embeds C2PA manifests when you publish or update posts:

1. **Write your post** as usual in WordPress
2. **Click Publish** - the plugin automatically embeds the C2PA manifest
3. **Done!** Your content now has cryptographic proof of origin

**What happens:**
- New posts get `c2pa.created` actions
- Updated posts get `c2pa.edited` actions with the previous instance captured as an ingredient
- Invisible Unicode embeddings are added to the content body
- Sentence metadata is stored for later inspection

### Verification Sidebar (Gutenberg)

- The **Encypher Provenance** panel summarizes signing status, document ID, and verification URLs.
- Sentence-level verifier chips are available for all tiers.
- Enterprise users can view the full C2PA manifest JSON directly in the sidebar.
- The manifest viewer streams the exact JSON wrapper so editors can inspect every assertion without leaving WordPress.

### Public Extract & Verify Endpoint

The plugin now exposes a public REST endpoint for third-party verification without a WordPress login:

```
POST /wp-json/encypher-provenance/v1/extract
{
  "text": "C2PA-protected content…"
}
```

The route proxies to Encypher's `POST /api/v1/verify` so publishers can embed interactive checkers or build custom workflows around invisible embeddings.

### Analytics & Dashboard Coverage

- WordPress Dashboard now includes an **Encypher Provenance Coverage** widget showing signed counts, coverage percentage, and quick access links.
- **Encypher > Analytics** provides a detailed view with sentence-level adoption, tampering alerts, and the five most recently signed posts.
- Editors can use the analytics page during audits to prove that enterprise tiers are meeting their provenance SLAs.


### Manual Marking

You can also manually mark posts using the editor panel:

**Gutenberg (Block Editor):**
1. Open a post in the editor
2. Look for the **Encypher C2PA** panel in the sidebar
3. Click **Mark with C2PA**
4. Wait for confirmation

**Classic Editor:**
1. Open a post in the editor
2. Look for the **Encypher C2PA** meta box
3. Click **Sign Content**
4. Wait for confirmation

### Bulk Archive Marking

Mark existing WordPress archives programmatically:

1. Go to **Encypher > Bulk Sign**
2. Select post types to mark (Posts, Pages, etc.)
3. Choose filters:
   - Date range (all time, last month, 3/6/12 months, custom)
   - Status (unmarked only, all posts)
   - Batch size (1-50 posts per batch)
4. Review total count
5. Click **Start Bulk Marking**
6. Monitor progress with real-time updates
7. Pause/resume or cancel as needed

**Features:**
- Real-time progress tracking
- Error handling with detailed logs
- Pause/resume capability
- Free tier: 10 posts per batch
- Enterprise tier: Unlimited

### Frontend Badge

Optional C2PA badge on marked posts:

1. Go to **Encypher > Settings**
2. Enable **Show C2PA badge**
3. Choose badge position:
   - Top of post
   - Bottom of post (default)
   - Floating (bottom-right corner)
4. Badge displays:
   - C2PA protection status
   - Verification link
   - Marked date
   - Powered by Encypher

**Customization:**
- Brand colors (Deep Navy, Azure Blue)
- Responsive design
- Print-friendly styles
- Accessible markup

### Status Indicators

The plugin shows the current C2PA status:
- **C2PA Protected:** Content is marked and up-to-date
- **Outdated:** Content changed since last marking (re-mark recommended)
- **Failed:** Marking failed (check API key and try again)
- **Processing:** Marking in progress

### Per-Post Control

You can override auto-marking for specific posts:
- Add custom field `_encypher_skip_marking` with value `1`
- The plugin will skip auto-marking for that post

---

## Settings

### General Settings

**Auto-mark on publish** (default: ON)
- Automatically embed C2PA manifests when publishing new posts
- Recommended for all users

**Auto-mark on update** (default: ON)
- Re-sign manifests when content is updated
- Preserves provenance chain through ingredient references

**Post types to auto-mark**
- Select which post types should be auto-marked
- Default: Posts and Pages

### C2PA Settings

**Metadata Format** (default: C2PA)
- **C2PA:** Full C2PA-compliant manifests (recommended)
- **Basic:** Minimal metadata for testing

**Hard Binding** (default: ON)
- Include c2pa.hash.data assertion
- Provides content hash for tamper detection
- Recommended for maximum security

### WordPress/ai Integration Settings

**Enable WordPress/ai Integration** (`wordpress_ai_enabled`, default: OFF)
- When ON: hooks into all WordPress/ai experiment output filters and auto-signs AI-generated content before it's committed to the post
- Requires the WordPress/ai plugin to be active; admin shows a notice if it isn't detected

**Coalition Auto-Enrollment** (`coalition_auto_enroll`, default: OFF)
- When first toggled ON: POSTs site URL and name to `/coalition/enroll`
- Stores `encypher_coalition_enrolled` + `encypher_coalition_enrolled_at` options
- Shows a WP admin notice confirming enrollment (or error details on failure)
- Rising-edge trigger — re-saving settings without changing the toggle does not re-enroll

### Workspace Connection & API Settings

**API Base URL**
- Default: `https://api.encypherai.com/api/v1`
- Only change if using self-hosted Enterprise API

**API Key**
- Usually provisioned automatically by secure email connect
- Can still be pasted manually if your team manages credentials outside WordPress

---

## Tier Comparison

### Free Tier
**Perfect for:** Individual bloggers, small publishers
**Features:**
- ✅ Auto-sign on publish/update
- ✅ Sentence-level embeddings
- ✅ C2PA-compliant manifests
- ✅ Public verification links
- ✅ Gutenberg & Classic Editor support
- ✅ Verification badge
- ✅ Bulk signing (10 posts/batch)

**Limitations:**
- Managed Encypher signature
- Community support

**Price:** Free forever

### Enterprise Tier
**Perfect for:** Professional publishers, media organizations, enterprises
**Features:**
- ✅ All Free features
- ✅ Bring Your Own Key (BYOK)
- ✅ Custom branding (removable Encypher badge)
- ✅ C2PA manifest viewer in editor
- ✅ Unlimited bulk signing
- ✅ Multi-site support
- ✅ Advanced key management
- ✅ Dedicated support + SLA

**Price:** Contact sales

---

## Technical Details

### C2PA Compliance

The plugin implements the full C2PA specification for text:

**C2PATextManifestWrapper Structure:**
```
Magic: C2PATXT\0 (0x4332504154585400)
Version: 1
Manifest Length: [calculated]
JUMBF Container: [full C2PA manifest]
```

**Unicode Encoding:**
- Bytes 0-15: U+FE00 to U+FE0F (VS1-VS16)
- Bytes 16-255: U+E0100 to U+E01EF (VS17-VS256)
- Prefix: U+FEFF (Zero-Width No-Break Space)

**Required Assertions:**
- `c2pa.actions.v1`: Creation/edit actions
- `c2pa.hash.data.v1`: Hard binding (optional, default ON)
- `c2pa.soft_binding.v1`: Soft binding

**Actions:**
- `c2pa.created`: New posts with digitalSourceType
- `c2pa.edited`: Updated posts with ingredient reference

### API Integration

The plugin communicates with the Encypher Enterprise API:

**Endpoints:**
- `POST /api/v1/sign` (unified signing — all tiers, features gated server-side)
- `POST /api/v1/verify` (unified verification via verification-service — all tiers)

**Request:**
```json
{
  "document_id": "wp_post_123",
  "text": "Blog post text...",
  "options": {
    "manifest_mode": "micro",
    "ecc": true,
    "embed_c2pa": true,
    "segmentation_level": "sentence",
    "action": "c2pa.created",
    "return_embedding_plan": true
  },
  "metadata": {
    "title": "My Blog Post",
    "author": "John Doe",
    "url": "https://example.com/my-post",
    "wordpress_post_id": 123
  }
}
```

**Response:**
```json
{
  "success": true,
  "document_id": "wp_post_123",
  "embedded_content": "Blog post text with invisible C2PA manifest...",
}
```

### Database Schema

Post meta keys written by the plugin:

```
_encypher_provenance_status         // string: c2pa_protected | tampered | not_signed | modified
_encypher_provenance_signature      // string: raw C2PA signature
_encypher_provenance_document_id    // string: document UUID
_encypher_provenance_instance_id    // string: signing instance UUID
_encypher_provenance_total_sentences// int: number of signed sentences
_encypher_provenance_last_signed    // datetime: last successful sign
_encypher_provenance_verification   // array: cached verify result
_encypher_provenance_needs_verify   // bool: dirty flag
_encypher_skip_marking              // bool: user override to skip auto-signing
_encypher_wpai_experiments          // array: keyed by experiment slug — records of WP/ai signed content
                                    //   { name, generator, signed_at }
```

WordPress options written by the plugin:

```
encypher_provenance_settings        // main settings array (api_key, api_base_url, tier, wordpress_ai_enabled, coalition_auto_enroll, …)
encypher_coalition_enrolled         // bool: true when Coalition enrollment confirmed
encypher_coalition_enrolled_at      // datetime: when enrollment was confirmed
```

---

## Troubleshooting

### Plugin not marking content

**Check:**
1. Is auto-mark enabled in settings?
2. Is the API key configured correctly?
3. Is the post type enabled for auto-marking?
4. Check the post meta for `_encypher_skip_marking`

**Debug:**
- Enable WordPress debug logging
- Check PHP error logs
- Look for "Encypher:" messages

### API connection errors

**Check:**
1. Is the API base URL correct?
2. Is the API key valid?
3. Is your server able to make outbound HTTPS requests?
4. Check firewall settings

**Test:**
- Try manual marking from the editor
- Check network tab in browser dev tools
- Contact support if issues persist

### Content not displaying correctly

**Check:**
1. Are you using a caching plugin? Clear cache
2. Is the content being modified by another plugin?
3. Check for JavaScript errors in browser console

---

## Support

### Free Tier
- Documentation: [encypherai.com/docs](https://encypherai.com/docs)
- Community Forum: [community.encypherai.com](https://community.encypherai.com)

### Enterprise Tier
- Dedicated Support: enterprise@encypherai.com
- SLA: Custom
- Phone Support: Available

---

## Privacy & Security

### Data Collection
The plugin sends the following data to the Encypher API:
- Post content (for embedding)
- Post title
- Post author name
- Post URL
- Post ID

**No personal information** is embedded in the C2PA manifest unless you explicitly include it in your post content.

### Security
- API keys are stored encrypted in WordPress database
- All API communication uses HTTPS
- No credentials are logged
- Private keys (Pro/Enterprise) are never transmitted

---

## REST Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/encypher-provenance/v1/sign` | Editor | Sign a post by ID |
| `GET` | `/encypher-provenance/v1/status` | Editor | Post signing status + sentence segments |
| `POST` | `/encypher-provenance/v1/verify` | Public | Verify post content against Encypher API |
| `GET` | `/encypher-provenance/v1/provenance` | Public | Provenance report by post/instance ID |
| `POST` | `/encypher-provenance/v1/extract` | Public | Verify arbitrary text (no post required) |
| `POST` | `/encypher-provenance/v1/test-connection` | Admin | Test API key + base URL |
| `POST` | `/encypher-provenance/v1/quick-connect` | Admin | Store API key from email connect flow |
| `POST` | `/encypher-provenance/v1/connect/start` | Admin | Initiate email connect flow |
| `GET` | `/encypher-provenance/v1/wordpress-ai-status` | Editor | AI content provenance status for a post |

---

## Changelog

### 1.2.0 (2026-03-10)
- **WordPress/ai Integration:** Auto-sign AI-generated content from all 5 WordPress/ai experiments (title, excerpt, summary, review notes, alt text) via `class-encypher-provenance-wordpress-ai.php`
- **WordPress Abilities API:** Register `encypher/sign` and `encypher/verify` as first-class abilities callable via `wp_do_ability()` (`class-encypher-sign-ability.php`, `class-encypher-verify-ability.php`)
- **AI Content Provenance sidebar panel:** New Gutenberg panel (`assets/js/wordpress-ai-provenance.js`) with shield badge (green/yellow/red/grey) and signed experiment list
- **New REST endpoint:** `GET /encypher-provenance/v1/wordpress-ai-status` returning provenance status per post
- **Coalition auto-enrollment:** Rising-edge settings toggle POSTs to `/coalition/enroll` and stores confirmation with WP admin notice
- **Admin settings:** New "WordPress/ai Integration" section with `wordpress_ai_enabled` and `coalition_auto_enroll` toggles; enrollment status display

### 1.1.0
- Coalition dashboard and widget (`class-encypher-provenance-coalition.php`)
- Bulk signing UI (`class-encypher-provenance-bulk.php`) with pause/resume, error log
- Frontend C2PA badge (`class-encypher-provenance-frontend.php`)
- Sentence-level verifier chips in Gutenberg sidebar
- Pre-publish panel in block editor
- C2PA verification page at `/c2pa-verify/{instance_id}`
- Email connect flow for API key provisioning
- Provenance chain ingredient references

### 1.0.0 (2025-10-31)
- Initial release
- C2PA-compliant text authentication
- Auto-mark on publish/update
- Manual marking in Gutenberg and Classic Editor
- Two-tier support (Free, Enterprise)
- Public verification links

---

## Credits

**Developed by:** Encypher Corporation
**Website:** [encypherai.com](https://encypherai.com)
**Standards:** Co-Chair of C2PA Text Provenance Task Force
**License:** GPL-2.0-or-later

Built on standards we're developing with Google, BBC, OpenAI, Adobe, and Microsoft.

---

## License

This plugin is licensed under the GPL-2.0-or-later license.

Copyright (C) 2025 Encypher Corporation

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
