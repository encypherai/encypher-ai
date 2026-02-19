=== Encypher Provenance - Text Authorship Verification ===
Contributors: encypherai
Tags: content authenticity, provenance, verification, proof of origin, authorship verification, misinformation, plagiarism, copyright, digital signature
Requires at least: 6.0
Tested up to: 6.5
Requires PHP: 7.4
Stable tag: 1.0.0-beta
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Protect your content with cryptographic proof of authorship. Invisible signatures prove when content was created, by whom, and whether it was tampered with.

== Description ==

**Encypher Provenance** brings C2PA (Coalition for Content Provenance and Authenticity) compliance to WordPress. Automatically embed invisible cryptographic signatures into your blog posts and pages that prove when content was created, by whom, and whether it has been modified.

= Why Content Authenticity Matters =

In an era of rapid content reuse and misinformation, proving the authenticity of your content is more important than ever. Encypher Provenance helps you:

* **Prove Original Authorship** - Cryptographic signatures tied to your organization
* **Detect Tampering** - Know if content has been modified after signing
* **Build Trust** - Show readers your content is verified and authentic
* **Protect Against Misquotes** - Track sentence-level provenance

= Key Features =

* **Auto-Sign on Publish** - Content is automatically signed when you publish
* **Auto-Sign on Update** - Re-signs with edit history when content changes
* **Invisible Embeddings** - C2PA manifests are embedded using invisible Unicode characters
* **Public Verification** - Readers can verify content authenticity with one click
* **Gutenberg Integration** - Full sidebar panel in the block editor
* **Verification Badge** - Optional floating badge shows content is protected

= C2PA Compliance =

Built on the same standards used by Google, BBC, OpenAI, Adobe, and Microsoft:

* Full C2PA 2.3 text manifest specification compliance
* Unicode variation selector embedding (invisible, copy-safe)
* SHA-256 hard binding for tamper detection
* Provenance chain tracking for edit history

= Tier Features =

**Free**
* Auto-sign on publish/update
* Sentence-level C2PA signing (micro_ecc_c2pa)
* Attribution indexing
* Batch signing (up to 10 docs)
* Encypher-managed certificates
* Coalition membership

**Enterprise (Custom)**
* All Free features
* Bring Your Own Key (BYOK)
* Word-level segmentation
* Dual binding & fingerprinting
* Batch signing (up to 100 docs)
* SSO/SCIM integration
* Dedicated support & SLA
* Coalition membership (priority placement)

== Installation ==

1. Upload the `encypher-provenance` folder to `/wp-content/plugins/`
2. Activate the plugin through the 'Plugins' menu in WordPress
3. Go to **Encypher > Settings** to configure your API key
4. Get your free API key at [dashboard.encypherai.com](https://dashboard.encypherai.com)

== Frequently Asked Questions ==

= Do I need an API key? =

Yes, you need a free API key from [dashboard.encypherai.com](https://dashboard.encypherai.com). The free tier includes unlimited document signing.

= Are the embeddings visible? =

No. C2PA manifests are embedded using invisible Unicode variation selectors. They don't affect how your content looks but can be extracted for verification.

= Does this work with the Classic Editor? =

Yes, the plugin supports both Gutenberg (block editor) and Classic Editor.

= What happens if I edit a signed post? =

The plugin automatically re-signs the content with a `c2pa.edited` action and maintains a provenance chain linking to the previous version.

= Can readers verify my content? =

Yes! A verification badge can be displayed on your posts. Clicking it shows verification details including signer information and timestamp.

= Is my content sent to external servers? =

Yes, content is sent to Encypher's API for signing. The API creates cryptographic signatures but does not store your full content. See our [Privacy Policy](https://encypherai.com/privacy) for details.

== Screenshots ==

1. Settings page with API configuration
2. Gutenberg sidebar showing signing status
3. Frontend verification badge
4. Verification modal with content details
5. Analytics dashboard

== Changelog ==

= 1.0.0-beta =
* Public beta release for Encypher Provenance
* Settings UI streamlined: hard binding is always on and no longer configurable
* Added dashboard support contact section with direct email CTA
* Unified branded full-wordmark headers across Dashboard, Content, Settings, Analytics, Account, Bulk Sign, and Coalition pages
* Improved analytics cards/status presentation and coalition early-rollout placeholder experience

= 1.2.0 =
* Migrated verify calls from deprecated POST /verify to POST /verify/advanced
* Added per-post admin notice on auto-sign failure (dismissible, links to error log)
* Added site-wide error log ring buffer (last 50 entries) on Analytics page
* Added verification hits counter (30d + lifetime) on Analytics page
* Added outbound webhook alerting on repeated failures (enterprise add-on)
* Fixed auto-sign to respect configured post_types setting
* Added content page pagination (50 posts/page)
* Fixed status guidance copy: distinguishes embedded vs verified provenance
* Removed debug console.log calls from frontend JS
* All debug logging now gated behind WP_DEBUG

= 1.1.0 =
* Updated API endpoints to use unified /sign and /verify
* Improved C2PA compliance validation
* Enhanced error handling and logging
* Updated documentation

= 1.0.1 =
* Fixed C2PA wrapper compliance (single wrapper per document)
* Added provenance chain support for edits
* Improved tier-based feature gating

= 1.0.0 =
* Initial release
* C2PA-compliant text signing
* Auto-sign on publish/update
* Gutenberg and Classic Editor support
* Public verification badge
* Bulk signing tool

== Upgrade Notice ==

= 1.0.0-beta =
Public beta with polished admin UX and production-ready signing/verification defaults. Hard binding is enforced by default.

= 1.2.0 =
This version migrates verification to the /verify/advanced endpoint (requires API key). All existing signed content remains valid. Error reporting and analytics improvements included.

= 1.1.0 =
This version updates API endpoints for improved compatibility. All existing signed content remains valid.

== Privacy Policy ==

Encypher Provenance sends your post content to Encypher's API (api.encypherai.com) for cryptographic signing. We do not store your full content - only metadata needed for verification. See [encypherai.com/privacy](https://encypherai.com/privacy) for our complete privacy policy.
