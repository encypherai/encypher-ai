=== Encypher Provenance - C2PA Content Authentication ===
Contributors: encypherai
Tags: c2pa, content authenticity, provenance, verification, ai detection, misinformation, plagiarism, copyright, digital signature, blockchain
Requires at least: 6.0
Tested up to: 6.5
Requires PHP: 7.4
Stable tag: 1.1.0
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Protect your content with cryptographic proof of authorship. C2PA-compliant digital signatures prove when content was created, by whom, and detect AI-generated or tampered text. Fight misinformation, plagiarism, and content theft.

== Description ==

**Encypher Provenance** brings C2PA (Coalition for Content Provenance and Authenticity) compliance to WordPress. Automatically embed invisible cryptographic signatures into your blog posts and pages that prove when content was created, by whom, and whether it has been modified.

= Why Content Authenticity Matters =

In an era of AI-generated content and misinformation, proving the authenticity of your content is more important than ever. Encypher Provenance helps you:

* **Prove Original Authorship** - Cryptographic signatures tied to your organization
* **Detect Tampering** - Know if content has been modified after signing
* **Build Trust** - Show readers your content is verified and authentic
* **Protect Against Misquotes** - Track sentence-level provenance (Pro+)

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

**Free (Starter)**
* Auto-sign on publish/update
* Document-level C2PA manifests
* Public verification badge
* Coalition membership (65/35 revenue share)

**Professional ($99/month)**
* Sentence-level attribution
* Merkle tree encoding
* Advanced verification options
* BYOK (Bring Your Own Key)
* Coalition membership (70/30 revenue share)

**Enterprise (Custom)**
* All Professional features
* Custom branding options
* SSO integration
* Dedicated support
* Coalition membership (80/20 revenue share)

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

= 1.1.0 =
This version updates API endpoints for improved compatibility. All existing signed content remains valid.

== Privacy Policy ==

Encypher Provenance sends your post content to Encypher's API (api.encypherai.com) for cryptographic signing. We do not store your full content - only metadata needed for verification. See [encypherai.com/privacy](https://encypherai.com/privacy) for our complete privacy policy.
