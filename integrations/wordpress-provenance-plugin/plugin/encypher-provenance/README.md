# Encypher C2PA - Text Authentication for WordPress

**Version:** 1.0.0  
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
- **Gutenberg Integration:** Sidebar panel in block editor
- **Classic Editor Support:** Meta box for classic editor users
- **Public Verification:** Verification links for readers to check authenticity
- **Sentence & Merkle Insights:** Pro/Enterprise tiers expose per-sentence verifier chips, upgrade prompts, and Merkle snapshot cards directly in Gutenberg.
- **Analytics Dashboard:** Built-in dashboard widget and **Encypher > Analytics** summarize coverage, sentence-level adoption, and recent signing activity.

### C2PA Compliance
- **C2PATextManifestWrapper:** Full manifest structure with magic number, version, JUMBF container
- **Unicode Variation Selectors:** Invisible embedding using U+FE00-FE0F and U+E0100-U+E01EF
- **Hard Binding:** c2pa.hash.data assertion with SHA-256 (enabled by default)
- **Soft Binding:** c2pa.soft_binding assertion for tamper detection
- **Proper Actions:** c2pa.created for new posts, c2pa.edited for updates
- **Provenance Chain:** Ingredient references for updated content

### Multi-Tier Support
- **Free Tier:** Encypher-provided shared signature
- **Pro Tier:** Bring your own key or purchase through Encypher
- **Enterprise Tier:** Advanced key management, multi-site support

### Plans & Capabilities

| Feature | Free (auto embeddings only) | Pro – $99/mo | Enterprise – Contract |
|---------|-----------------------------|--------------|------------------------|
| Auto-sign on publish/update | ✅ | ✅ | ✅ |
| Manual marking | ✅ | ✅ | ✅ |
| Bulk signing | 100 posts/batch | Unlimited | Unlimited + automation APIs |
| Invisible enhanced embeddings | ✅ (shared signer) | ✅ (BYOK or managed key) | ✅ (multi-key/HSM) |
| Bring Your Own Signature | ❌ | ✅ | ✅ (advanced rotation) |
| Verification badge | ✅ | ✅ | ✅ (custom styles) |
| Merkle + sentence visualization | Badge only | Sidebar sentence verifier + Merkle snapshot | Full visualization suite + downstream proofs |
| Dashboard access | API key & usage | Billing, BYOK wizard, analytics | Org admin, SSO, SLA dashboards |
| Support | Community forum | Email (24–48h) | Dedicated TAM + SLA |

### Dashboard & Account Management

All users authenticate via [dashboard.encypherai.com](https://dashboard.encypherai.com) to:
- Create a workspace and retrieve API keys (Free tier)
- Upgrade to Pro ($99/mo) for BYOK, partial Enterprise features, and billing management
- Provision enterprise licenses, seats, and SLA contacts

The plugin settings page surfaces direct links:
- **Get API Key / Manage Account** – opens the dashboard to copy keys or update billing
- **Bring Your Own Key** – launches the dashboard wizard to upload a public key and obtain a signing profile ID
- **Enterprise Support** – pre-filled contact form to reach your CSM

Tokens issued by the dashboard contain a `tier` claim that the plugin reads to automatically enable or limit functionality (e.g., bulk batch size, visualization controls). If billing lapses, the plugin gracefully reverts to Free limits but preserves previously signed manifests.

---

## Installation

### From WordPress Admin
1. Download the plugin ZIP file
2. Go to **Plugins → Add New → Upload Plugin**
3. Upload the ZIP file and click **Install Now**
4. Click **Activate Plugin**

### Manual Installation
1. Upload the `encypher-provenance` folder to `/wp-content/plugins/`
2. Activate the plugin through the **Plugins** menu in WordPress

### Configuration
1. Go to **Encypher > Settings**
2. Click **Get API Key / Manage Account** to open [dashboard.encypherai.com](https://dashboard.encypherai.com) and either create a free workspace or sign in to your Pro/Enterprise account
3. Configure your settings:
   - **API Base URL:** `https://api.encypherai.com/api/v1` (default)
   - **API Key:** Get your free key from [dashboard.encypherai.com](https://dashboard.encypherai.com)
   - **Bring Your Own Signature (Pro/Enterprise):** Paste the Signing Profile ID generated in the dashboard BYOK wizard
   - **Auto-mark on publish/update:** Enable to automatically mark content (recommended)
   - **Metadata Format:** C2PA (default) or Basic
   - **Hard Binding:** Enable for c2pa.hash.data assertion (recommended)

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
- Merkle trees and sentence metadata are stored for later inspection

### Verification Sidebar (Gutenberg)

- The **Encypher Provenance** panel summarizes signing status, document ID, and verification URLs.
- **Pro/Enterprise** tiers unlock sentence-level verifier chips (linking to `POST /api/v1/public/extract-and-verify` results) plus a Merkle snapshot card with one-click copy buttons.
- Free tier users see inline upgrade prompts instead of the advanced UI.
- The manifest viewer streams the exact JSON wrapper so editors can inspect every assertion without leaving WordPress.

### Public Extract & Verify Endpoint

The plugin now exposes a public REST endpoint for third-party verification without a WordPress login:

```
POST /wp-json/encypher-provenance/v1/extract
{
  "text": "C2PA-protected content…"
}
```

The route proxies to Encypher's `POST /api/v1/public/extract-and-verify` so publishers can embed interactive checkers or build custom workflows around invisible embeddings.

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
- Free tier: 100 posts per operation
- Pro tier: Unlimited marking

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

### API Configuration

**API Base URL**
- Default: `https://api.encypherai.com/api/v1`
- Only change if using self-hosted Enterprise API

**API Key**
- Get your free key from [dashboard.encypherai.com](https://dashboard.encypherai.com)
- Required for all tiers

---

## Tier Comparison

### Free Tier
**Perfect for:** Individual bloggers, small publishers  
**Features:**
- ✅ Auto-mark on publish
- ✅ Manual mark button
- ✅ C2PA-compliant manifests
- ✅ Public verification links
- ✅ Gutenberg & Classic Editor support

**Limitations:**
- Shared Encypher signature
- Community support

**Price:** Free forever

### Pro Tier
**Perfect for:** Professional publishers, media organizations  
**Features:**
- ✅ All Free features
- ✅ Custom signature (your organization)
- ✅ Bring your own key (BYOK)
- ✅ Or purchase signature through Encypher
- ✅ Advanced analytics
- ✅ Priority support

**Price:** $99/month or $999/year

### Enterprise Tier
**Perfect for:** Large publishers, enterprise organizations  
**Features:**
- ✅ All Pro features
- ✅ Multi-site support
- ✅ Advanced key management
- ✅ HSM integration
- ✅ Custom integrations
- ✅ SLA and dedicated support

**Price:** Custom (contact sales)

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
- `POST /api/v1/sign` (Starter tier)
- `POST /api/v1/sign/advanced` (Professional+ tiers)
- `POST /api/v1/verify` (public verification)
- `POST /api/v1/verify/advanced` (authenticated verification with tier-gated options)

**Request:**
```json
{
  "document_id": "wp_post_123",
  "text": "Blog post text...",
  "segmentation_level": "sentence",
  "action": "c2pa.created",
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
  "merkle_tree": { "root_hash": "..." }
}
```

### Database Schema

The plugin stores metadata in WordPress post meta:

```
_encypher_marked           // boolean: true if marked
_encypher_marked_date      // datetime: when marked
_encypher_manifest_id      // string: manifest UUID
_encypher_content_hash     // string: SHA-256 of content
_encypher_skip_marking     // boolean: user override to skip
_encypher_verification_url // string: public verification URL
_encypher_action_type      // string: c2pa.created or c2pa.edited
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

### Pro Tier
- Email Support: support@encypherai.com
- Response Time: 24-48 hours

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

## Changelog

### 1.0.0 (2025-10-31)
- Initial release
- C2PA-compliant text authentication
- Auto-mark on publish/update
- Manual marking in Gutenberg and Classic Editor
- Multi-tier support (Free, Pro, Enterprise)
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
