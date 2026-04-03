# WordPress C2PA Integration Plugin - Product Requirements Document

**Status:** Draft
**Version:** 1.0
**Created:** October 31, 2025
**Owner:** Product Team
**Branch:** `feature/wordpress-c2pa-plugin`

---

## Executive Summary

A WordPress plugin that enables C2PA-compliant text authentication for blog posts and pages, supporting all customer tiers from free to enterprise. The plugin programmatically embeds invisible cryptographic watermarks into WordPress content, automatically marking posts on publish and providing manual marking capabilities for archives.

### Key Features
- C2PA-Compliant: Full adherence to Manifests_Text.adoc specification
- Multi-Tier Support: Free (Encypher signature), Pro (BYOK/purchase signature)
- Auto-Mark on Publish: Automatic C2PA embedding when publishing/updating
- Bulk Archive Marking: Programmatic marking of existing content
- Update Management: Re-sign manifests when content is updated
- Standards-Based UX: Follows C2PA UX Guidance for trust and transparency

---

## Product Vision

### Problem Statement
WordPress powers 43% of the web, but blog content has no cryptographic proof of origin. When posts are copy-pasted, scraped, or used to train AI models, ownership becomes unprovable. Publishers need C2PA-compliant text authentication that works seamlessly with WordPress workflows.

### Solution
A WordPress plugin that embeds invisible C2PA-compliant cryptographic watermarks into blog posts and pages, providing:
- Proof of origin that survives copy-paste
- Automatic marking on publish/update
- Bulk archive processing for existing content
- Standards-based UX following C2PA guidance
- Multi-tier support from free to enterprise

### Value Proposition
**For Publishers:**
"Transform your WordPress blog into a C2PA-compliant content source. Every post gets cryptographic proof of origin that survives copy-paste and scraping. Serve formal notice that your content is marked and owned."

**Positioning (per Marketing Guidelines):**
- Lead with standards authority: "C2PA-compliant text authentication"
- Emphasize cryptographic certainty: "Proof embedded in text itself"
- Collaborative approach: "Built on standards we're developing with Google, BBC, OpenAI, Adobe, Microsoft"
- Economic enablement: "Transform unmarked content into provably owned assets"

---

## Feature Tiers

### Free Tier
**Target:** Individual bloggers, small publishers
**Signature:** Encypher-provided shared signature
**Features:**
- Auto-mark on publish
- Manual mark button for individual posts
- Bulk mark up to 100 posts
- C2PA-compliant manifests
- Basic status indicators
- Public verification link

**Limitations:**
- Shared Encypher signature (signer_id: "encypher_free")
- No custom branding in manifest
- Basic analytics only
- Community support

**Pricing:** Free forever

### Pro Tier
**Target:** Professional publishers, media organizations
**Signature Options:**
1. Bring Your Own Key (BYOK): Use your own Ed25519 key pair
2. Purchase Through Encypher: We generate and manage keys for you

**Features:**
- All Free features
- Custom signature (your organization)
- Unlimited bulk marking
- Advanced analytics dashboard
- Custom claim_generator branding
- Priority support
- API access for automation

**Pricing:** $99/month or $999/year

### Enterprise Tier
**Target:** Large publishers, enterprise organizations
**Signature:** Enterprise-managed keys with HSM support
**Features:**
- All Pro features
- Multi-site support
- Advanced key management
- Performance intelligence
- Custom integrations
- SLA and dedicated support
- White-label options

**Pricing:** Custom (contact sales)

### Tier Alignment & Account Flow

| Capability | Free (auto embeddings only) | Pro – $99/mo | Enterprise – Contract |
|------------|-----------------------------|--------------|------------------------|
| Auto-sign on publish/update | ✅ | ✅ | ✅ |
| Manual + bulk signing | Manual + 100 post batches | Unlimited bulk queues | Unlimited + workflow automation |
| Invisible enhanced embeddings | ✅ (Encypher shared signer) | ✅ (BYOK or managed key) | ✅ (multi-key, HSM-backed) |
| Bring Your Own Signature | ❌ | ✅ | ✅ (advanced rotation + audit) |
| Enterprise-only UX (Merkle modal, sentence verifier, verification badge) | Badge only | Badge + sentence verifier + Merkle preview | Full visualization + heatmaps |
| Dashboard access | ✅ – “Get API key” onboarding | ✅ – billing, usage, BYOK wizard | ✅ – org admin, SSO, seat control |
| Analytics | Basic coverage stats | Advanced dashboards + exports | Custom analytics + SLA reporting |
| Support | Community forum | Email (24–48h) | Dedicated TAM + SLA |

**Dashboard Requirements**
- Every user must authenticate via [dashboard.encypher.com](https://dashboard.encypher.com) to obtain API keys, manage billing, and configure BYOK profiles.
- Plugin settings include contextual actions: “Get API Key”, “Manage Account & Billing”, and (enterprise) “Contact Customer Success”.
- Tokens returned by the dashboard carry a `tier` claim that the plugin uses to toggle UI controls and enforce limits (e.g., bulk batch size, sentence highlighting panel).
- If an account downgrades, the plugin gracefully reverts to Free limits but keeps previously signed content intact (read-only mode).

---

## Core Features

### 1. Auto-Mark on Publish

Automatically embed C2PA-compliant manifests when publishing or updating posts/pages.

**Behavior:**
- New Post: Embed manifest with c2pa.created action on first publish
- Update: Re-sign manifest with c2pa.edited action, preserving provenance chain
- Draft to Publish: Embed on transition to published state
- Scheduled Posts: Embed when scheduled post goes live

**User Control:**
- Global setting: "Auto-mark new posts" (default: ON)
- Per-post override: Checkbox in editor sidebar
- Post type selection: Choose which post types to auto-mark

**C2PA Compliance:**
- Full C2PATextManifestWrapper structure
- Proper c2pa.actions assertions
- Hard binding via c2pa.hash.data (enabled by default)
- Soft binding via c2pa.soft_binding

### 2. Manual Mark Button

Allow editors to manually mark individual posts with a button in the editor.

**UI Location:**
- Block Editor (Gutenberg): Sidebar panel "Encypher C2PA"
- Classic Editor: Meta box below editor

**Button States:**
- Not Marked: "Mark with C2PA" (primary button)
- Marked: "Re-mark with C2PA" (secondary button) + status badge
- Processing: "Marking..." (disabled with spinner)
- Error: "Mark Failed - Retry" (error state)

**Status Indicators:**
- Marked: Green checkmark + "C2PA Protected"
- Outdated: Yellow warning + "Content changed - re-mark recommended"
- Failed: Red X + "Marking failed"
- Processing: Spinner + "Marking in progress..."

### 3. Bulk Archive Marking

Programmatically mark existing WordPress archives (posts, pages, custom post types).

**UI Location:** Tools → Encypher C2PA → Bulk Mark

**Features:**
- Post Type Selection: Choose which post types to mark
- Date Range Filter: Mark posts from specific date range
- Category/Tag Filter: Mark posts by taxonomy
- Status Filter: Published, draft, scheduled
- Batch Processing: Process in batches to avoid timeouts
- Progress Tracking: Real-time progress bar
- Error Handling: Skip failed posts, log errors, continue processing

**Free Tier Limitation:**
- Maximum 100 posts per bulk operation
- Show upgrade prompt when limit reached
- Allow multiple 100-post batches with manual restart

### 4. Update Management

Intelligently handle C2PA manifests when content is updated.

**Behavior:**

**Scenario 1: Content Changed**
- Detect content changes (compare hash)
- Re-sign manifest with new c2pa.edited action
- Update hard binding hash
- Preserve original manifest in provenance chain
- Add ingredient reference to previous version

**Scenario 2: Metadata Changed (title, author, etc.)**
- Update manifest metadata
- Re-sign with updated information
- Maintain content hash if text unchanged

**Scenario 3: Minor Edit (typo fix)**
- User can choose: "Minor edit - update manifest" or "Major edit - create new manifest"
- Minor: Update existing manifest
- Major: Create new manifest with ingredient reference

**C2PA Compliance:**
- Follow C2PA guidance on update manifests
- Preserve provenance chain through ingredients
- Use appropriate action types (c2pa.edited, c2pa.updated)
- Maintain hard binding integrity

---

## C2PA Compliance

### Manifests_Text.adoc Adherence

**1. C2PATextManifestWrapper Structure**
- Magic: C2PATXT\0 (0x4332504154585400)
- Version: 1
- Manifest Length: calculated
- JUMBF Container: full C2PA manifest

**2. Unicode Variation Selector Encoding**
- Bytes 0-15: U+FE00 to U+FE0F (VS1-VS16)
- Bytes 16-255: U+E0100 to U+E01EF (VS17-VS256)
- Prefix: U+FEFF (Zero-Width No-Break Space)

**3. Placement Strategy**
- Embedded at end of visible text content
- Single contiguous block
- Not split across multiple locations

**4. Content Binding**
- Hard Binding: c2pa.hash.data assertion with SHA-256
- Exclusions: Byte offsets for wrapper itself
- NFC Normalization: Text normalized before hashing
- Soft Binding: c2pa.soft_binding assertion with manifest hash

**5. Required Assertions**
- c2pa.actions.v1: Creation/edit actions
- c2pa.hash.data.v1: Hard binding (optional but default ON)
- c2pa.soft_binding.v1: Soft binding

**6. Actions**
- New Post: c2pa.created with digitalSourceType
- Update: c2pa.edited with ingredient reference
- Claim Generator: "WordPress/Encypher Plugin v{version}"

---

## Success Metrics

### Adoption Metrics
- Plugin installations (target: 10,000 in first year)
- Active installations (target: 70% retention)
- Posts marked per month (target: 1M+ after 6 months)
- Free to Pro conversion rate (target: 5%)

### Engagement Metrics
- Auto-mark adoption rate (target: 80% enable auto-mark)
- Bulk marking usage (target: 50% of users mark archives)
- Average posts marked per site (target: 100+)
- Re-marking frequency (content updates)

### Quality Metrics
- C2PA compliance rate (target: 100%)
- Verification success rate (target: 99%+)
- Error rate during marking (target: <1%)
- User satisfaction (target: 4.5+ stars)

---

## Implementation Plan

### Phase 1: MVP (Months 1-2)
- Core plugin architecture
- Auto-mark on publish
- Manual mark button
- Free tier with Encypher signature
- Basic settings page
- WordPress.org submission

### Phase 2: Pro Features (Month 3)
- BYOK support
- Purchase signature flow
- Unlimited bulk marking
- Advanced analytics dashboard
- Pro tier billing integration

### Phase 3: Enterprise (Month 4)
- Multi-site support
- HSM integration
- Advanced key management
- Custom integrations
- White-label options

### Phase 4: Polish & Scale (Month 5-6)
- Performance optimization
- Internationalization
- Advanced UX improvements
- Marketing and growth
- Enterprise sales enablement

---

## Technical Requirements

### WordPress Compatibility
- Minimum WordPress version: 6.0
- PHP version: 7.4+
- Gutenberg support: Required
- Classic Editor support: Optional
- Multisite compatible: Yes (Enterprise)

### Dependencies
- encypher-ai PHP SDK
- WordPress REST API
- AJAX for bulk operations
- Cron for scheduled tasks

### Security
- API key encryption at rest
- Private key storage (Pro/Enterprise)
- Nonce verification for all actions
- Capability checks (edit_posts minimum)
- Input sanitization and validation

### Performance
- Async marking to avoid blocking
- Batch processing for bulk operations
- Caching for verification results
- Minimal frontend impact
- Database query optimization

---

## Marketing & Distribution

### WordPress.org Listing
**Plugin Name:** Encypher C2PA - Text Authentication
**Short Description:** "C2PA-compliant text authentication. Embed cryptographic proof of origin into your WordPress content."
**Tags:** c2pa, content-authentication, provenance, watermarking, copyright

### Positioning (per Marketing Guidelines)
- Lead with: "C2PA-compliant text authentication"
- Emphasize: "Cryptographic proof embedded in text"
- Highlight: "Built on standards we're developing with industry leaders"
- Avoid: AI detection comparisons, accuracy percentages

### Launch Strategy
1. WordPress.org submission
2. Publisher outreach (Eleanor persona)
3. Content marketing (blog posts, case studies)
4. Partnership announcements
5. Conference presentations (WordCamp, C2PA events)

---

## Support & Documentation

### Documentation
- Installation guide
- Quick start tutorial
- C2PA explainer
- BYOK setup guide
- Bulk marking walkthrough
- Troubleshooting guide
- API documentation

### Support Channels
- Free: Community forum, documentation
- Pro: Email support (24-48h response)
- Enterprise: Dedicated support, SLA

---

## Appendix

### Glossary
- **C2PA:** Coalition for Content Provenance and Authenticity
- **Manifest:** Cryptographic container with content provenance
- **Hard Binding:** Content hash that detects tampering
- **Soft Binding:** Manifest hash for integrity verification
- **BYOK:** Bring Your Own Key
- **Signer ID:** Identifier for the signing key

### References
- C2PA Specification 2.2
- Manifests_Text.adoc
- C2PA Implementation Guidance
- C2PA UX Guidance
- Encypher Marketing Guidelines

---

**Document Control**
**Created:** October 31, 2025
**Last Updated:** October 31, 2025
**Next Review:** November 15, 2025
**Owner:** Product Team
**Approvers:** CEO, CTO, Head of Product

---

## Implementation Status

### ✅ Completed Features (October 31, 2025)

#### Core Auto-Signing Workflow
- ✅ Auto-sign on publish (draft → published)
- ✅ Auto-re-sign on update (content change detection)
- ✅ Editor sidebar with C2PA status display
- ✅ Pre-publish panel notification
- ✅ Badge display on frontend
- ✅ Disabled classic meta box

#### C2PA Spec Compliance
- ✅ **CRITICAL**: Fixed to create ONE `C2PATextManifestWrapper` per document
- ✅ Compliant with Manifests_Text.adoc specification
- ✅ Validates exactly 1 wrapper (spec requirement: "Quantity: Zero or one")
- ✅ Compatible with all standard C2PA validators

#### Enterprise API
- ✅ Sentence-level content tracking
- ✅ Document-level C2PA wrapper (spec compliant)
- ✅ Unique ref_id generation (timestamp-based)
- ✅ Delete-before-insert for re-signing
- ✅ Merkle tree integration

#### Database & Infrastructure
- ✅ Docker Compose setup for local testing
- ✅ PostgreSQL database with content_references table
- ✅ WordPress + Enterprise API integration
- ✅ Auto-signing hooks (transition_post_status, save_post)

### Status / Next Steps
- [x] Frontend badge styling improvements (tier-aware UI + upgrade callouts)
- [x] Settings page enhancements (dashboard stats caching, BYOK gating)
- [x] Verification API public endpoint
- [x] Admin console (dashboard user/permission management)
- [ ] Bulk signing interface

### 📋 Future Features
See `FUTURE_FEATURES.md` for detailed roadmap including:
- Manifest chaining with WordPress revisions
- Bulk signing for archives
- Advanced analytics dashboard
- Multi-site support
