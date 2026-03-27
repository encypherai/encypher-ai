=== Encypher Provenance - Text Authorship Verification ===
Contributors: encypherai
Tags: content authenticity, provenance, verification, proof of origin, authorship verification, misinformation, plagiarism, copyright, digital signature
Requires at least: 6.0
Tested up to: 6.5
Requires PHP: 7.4
Stable tag: 1.2.0
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

* **Email Connect Setup** - Start from a work email and auto-provision the plugin API key with a secure magic link
* **Auto-Sign on Publish** - Content is automatically signed when you publish
* **Auto-Sign on Update** - Re-signs with edit history when content changes
* **Invisible Embeddings** - C2PA manifests are embedded using invisible Unicode characters
* **Public Verification** - Readers can verify content authenticity with one click
* **Gutenberg Integration** - Full sidebar panel in the block editor
* **Verification Badge** - Optional badge shows readers that content is signed and verifiable

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
3. Go to **Encypher > Settings**
4. Enter your work email and click **Email me a secure connect link**
5. Open the email from Encypher and approve the WordPress connection
6. Return to WordPress and wait a few seconds while the plugin stores the provisioned API key automatically

You can still paste an existing API key manually if you already manage Encypher credentials outside the guided connect flow.

== Frequently Asked Questions ==

= Do I need an API key? =

Yes, the plugin ultimately uses an API key to call Encypher. The recommended path is the built-in email connect flow, which verifies your email and provisions the key automatically. Advanced users can still paste an existing key manually.

= How does the email connect flow work? =

Enter your work email on the plugin settings page, approve the secure link sent by Encypher, and keep the WordPress settings page open while it polls for completion. Once approved, the plugin stores the provisioned API key and connects the site automatically.

= Are the embeddings visible? =

No. C2PA manifests are embedded using invisible Unicode variation selectors. They don't affect how your content looks but can be extracted for verification.

= Does this work with the Classic Editor? =

Yes, the plugin supports both Gutenberg (block editor) and Classic Editor.

= What happens if I edit a signed post? =

The plugin automatically re-signs the content with a `c2pa.edited` action and maintains a provenance chain linking to the previous version.

= Can readers verify my content? =

Yes! A verification badge can be displayed on your posts. Clicking it shows verification details including signer information and timestamp.

= Is my content sent to external servers? =

Yes, content is sent to Encypher's API for signing. The API creates cryptographic signatures but does not store your full content. See our [Privacy Policy](https://encypher.com/privacy) for details.

== Screenshots ==

1. Settings page with workspace connection and signing defaults
2. Gutenberg sidebar showing signing status
3. Frontend verification badge
4. Verification modal with content details
5. Analytics dashboard

== Changelog ==

= 1.2.0 =
* Added WordPress/ai integration: auto-signs AI-generated content from all five WordPress/ai experiments (Title Generation, Excerpt Generation, Summarization, Review Notes, Alt Text) before it is committed to the post
* Added WordPress Abilities API support: registers `encypher/sign` and `encypher/verify` as first-class abilities callable by any plugin via `wp_do_ability()`
* Added "AI Content Provenance" Gutenberg sidebar panel with shield badge (green/yellow/red/grey) showing per-post AI provenance status and signed experiment list
* Added `GET encypher-provenance/v1/wordpress-ai-status` REST endpoint powering the new sidebar panel
* Added Coalition auto-enrollment: enabling the toggle in settings automatically enrolls the site in the Encypher Coalition via `/coalition/enroll`
* Added WordPress/ai Integration settings section with enable toggle and Coalition auto-enroll toggle
* AI-signed experiment records are stored in post meta (`_encypher_wpai_experiments`) for audit trail and REST lookups

= 1.1.0 =
* Added email-based secure connect flow with automatic API key provisioning
* Added WordPress approval page flow for emailed connect links
* Added session polling and automatic connection completion in plugin settings
* Updated dashboard and plugin documentation for guided WordPress onboarding

= 1.0.0-beta =
* Public beta release for Encypher Provenance
* Settings UI streamlined: hard binding is always on and no longer configurable
* Added dashboard support contact section with direct email CTA
* Unified branded full-wordmark headers across Dashboard, Content, Settings, Analytics, Account, Bulk Sign, and Coalition pages
* Improved analytics cards/status presentation and coalition early-rollout placeholder experience

== Upgrade Notice ==

= 1.2.0 =
Adds WordPress/ai integration, WordPress Abilities API support, and Coalition auto-enrollment. No breaking changes. If you use the WordPress/ai plugin, enable the new integration toggle in Encypher > Settings to auto-sign AI-generated content.

= 1.1.0 =
This release adds secure email-based connection and automatic API key provisioning for WordPress installs while preserving manual API key setup for existing workspaces.

= 1.0.0-beta =
Public beta with polished admin UX and production-ready signing/verification defaults. Hard binding is enforced by default.

== Privacy Policy ==

Encypher Provenance sends your post content to Encypher's API (api.encypher.com) for cryptographic signing. We do not store your full content - only metadata needed for verification. See [encypher.com/privacy](https://encypher.com/privacy) for our complete privacy policy.
