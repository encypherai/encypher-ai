# Encypher Future Partnerships and Products

**Last Updated:** March 22, 2026
**Status:** Internal Strategy
**Distribution:** Executive Team & Product Leadership

---

## Executive Summary

This document maps the strategic product and partnership landscape for Encypher as we expand
beyond the core C2PA signing SDK. Three themes drive the analysis: (1) where distribution is
gated by platform partnerships, (2) where the LLM proxy creates a lower-friction enterprise
on-ramp than the add-in, and (3) where data custody obligations will shape product architecture
as we scale.

Additionally, the Enterprise API now provides native multi-media C2PA signing (images, audio, video, live streams) and free verification across all media asset classes. This capability is production-ready and should be factored into all partnership and integration discussions -- enterprise customers can sign their entire content portfolio under one platform.

---

## 1. Microsoft Copilot Gap

### The Problem

Microsoft Copilot is the dominant AI writing assistant in the enterprise Word workflow. Our
Word add-in currently captures the full-document text after editing, but it cannot intercept
Copilot generation events -- the Office JS API does not expose Copilot's draft-complete or
suggestion-accepted events. This means:

- We cannot capture the "original AI text" at generation time from within the add-in.
- Users must paste AI output manually or use the LLM proxy path.
- The attribution workflow has a UX gap: the add-in asks the user to trust that the saved
  "original text" is the unedited AI draft, rather than capturing it cryptographically.

### Partnership Opportunity

A formal Microsoft ISV partnership or co-sell agreement could unlock:
- Access to the Copilot Extensibility SDK (currently limited preview), which would let us hook
  into Copilot draft events from within the add-in.
- Co-marketing through the Microsoft 365 App Store (AppSource) partner program, which
  accelerates enterprise IT approval cycles.
- Integration with Microsoft Purview compliance labels: attestation records could be written
  as sensitivity labels alongside C2PA metadata.

### The Wall Without Partnership

Without API access to Copilot events, our Word add-in remains a post-generation tool. This is
still valuable (human review attestation is the primary use case), but it means our AI
attribution story relies on the honor system for "what was the original AI output." The LLM
proxy path does not have this gap because it intercepts at the API call.

### Recommended Action

Engage Microsoft through the ISV Connect program. The co-sell motion is well-defined for
compliance and content authentication use cases. Target the Microsoft Purview and Information
Protection teams as primary contacts, as they own the governance narrative that aligns with
our C2PA positioning.

---

## 2. Microsoft AppSource Pathway

### Overview

AppSource is the enterprise distribution channel for Office add-ins. IT administrators can
deploy AppSource-listed add-ins to all users in a tenant without requiring individual sideload.
This removes the single biggest adoption barrier for enterprise deals.

### Timeline and Requirements

Estimated submission-to-approval timeline: 4-8 weeks.

**Technical requirements (already addressed in Priority 4):**
- Production SourceLocation URL (not a dev domain)
- All 4 icon sizes present (16x16, 32x32, 80x80, 128x128 PNG)
- SupportUrl pointing to a live support page
- Valid Category element
- Hosts restricted to supported Office apps (Word for full-document attestation)

**Business requirements (not yet complete):**
- Privacy Policy URL (public, GDPR-compliant) -- link from encypher.com/privacy
- Terms of Use URL -- link from encypher.com/terms
- AppSource listing: screenshots at 1366x768, app description (up to 2048 chars), optional
  demo video
- Microsoft Partner Center account with verified company identity

### Recommended Action

Assign a marketing resource to write the AppSource listing copy. Legal should review the
privacy policy for compliance with Microsoft's requirements. Engineering prepares the
production deployment of the add-in host (word-addin.encypher.com).

---

## 3. Future Integration Ideas

### Google Docs Add-on

Google Workspace Apps Script can read and modify document content, fire on edit events, and
communicate with external APIs. The signing and attestation flow is technically feasible.
Key difference from Office: Apps Script runs server-side (not in a browser sandbox), so
ZWC embedding in the document body requires writing to the document as text -- same model
as our current Word add-in. Attribution would face the same Gemini gap as the Copilot gap.

Priority: Medium. Google Workspace has strong SMB penetration; enterprise is growing.
Prerequisite: Google Workspace Marketplace listing (similar process to AppSource).

### Notion Integration

Notion's API exposes page content as block-level JSON. We could build a Notion integration
(OAuth app in the Notion App Gallery) that:
- Reads a page on demand
- Signs it via the Encypher API
- Writes a signed version back (ZWC in text blocks)
- Stores the attestation record linked to the page URL

Notion is used heavily by AI-native companies, making it a natural early adopter channel.
Priority: Medium-High. Notion's user base skews technical; conversion to paid likely higher.

### Slack Signing Bot

A Slack bot that intercepts messages containing AI-generated content (via a slash command or
message action) and signs them before posting. The use case is compliance: regulated firms
want a tamper-evident record of AI-generated communications.

The Slack Events API and Block Kit make this technically straightforward. The monetization
model would be per-workspace rather than per-user.

Priority: Low-Medium. The Slack distribution channel is fast but monetization is complex.
Compliance-focused firms (finance, healthcare) are the target; requires SOC2 Type II.

---

## 4. LLM Proxy as Lead Enterprise Product

### Thesis

The LLM proxy (intercept-at-API-layer) is the lowest-friction enterprise deployment:
- No browser extension to install
- No Office add-in to sideload or AppSource-approve
- No per-user setup -- one API key rotation for the whole org
- Captures original AI text cryptographically (no honor system)

The add-in is valuable for document-centric workflows (Word, Google Docs, Notion) where the
proxy is not in the call path. But for organizations whose AI usage flows through internal
tools that call OpenAI/Anthropic/Gemini directly, the proxy is the right entry point.

### Product Positioning

- **LLM Proxy:** "Zero-install AI content governance for your engineering team."
  Lead with compliance, not features. Target: CISO, General Counsel, Head of Engineering.
- **Word Add-in:** "Attestation for human reviewers of AI-generated documents."
  Lead with the human review workflow. Target: Editorial, Legal, Communications teams.
- **Multi-Media Signing:** "Provenance for your entire content portfolio -- articles, photos, podcasts, video."
  Lead with completeness. Target: Head of Content, CTO, Digital Asset Management teams.

These two motions are complementary: a proxy customer who also uses Word as their document
workflow is a natural add-in upsell, and vice versa.

### Pricing Consideration

The proxy is usage-based (per token or per request). The add-in is seat-based. Mixed
enterprise deals should be structured as a platform fee with usage components for the proxy.

---

## 5. Data Custody Roadmap

### The Problem

The LLM proxy stores (at minimum) the text of every AI prompt and response that passes
through it in order to compute Merkle hashes and support diff retrieval. This creates data
custody obligations that do not exist for the signing SDK (which is compute-only).

### Minimum Requirements Before Scaling Proxy

**Data Processing Agreement (DPA):** Required for EU customers under GDPR. Must specify:
- Categories of personal data processed (none expected in most cases, but prompts may
  contain names, email addresses, or PII)
- Retention period
- Sub-processor list (cloud provider, logging infrastructure)
- Data subject rights mechanism

**Retention Policy:**
- Proposal: 90-day default retention for stored text; configurable per organization.
- Signed Merkle hashes retained indefinitely (these are hashes, not plaintext).
- Original text deleted on schedule or on customer request.
- Implement a DELETE /api/v1/public/attest/{document_id}/data endpoint for right-to-erasure
  requests.

**Customer Controls:**
- Dashboard setting: "Do not store original text" (hash-only mode; disables diff retrieval
  but reduces custody risk)
- Per-organization retention override (Enterprise tier)
- Export endpoint for all attestation records (GDPR portability)

### Architecture Impact

The `original_text` column added in Priority 2 is the first instance of Encypher storing
customer content server-side. Before this, all content stayed on the customer's device or
in the customer's content database. This is a meaningful architectural shift and should be
communicated to enterprise customers proactively.

### Recommended Actions

1. Have legal draft a DPA before any enterprise proxy deal closes.
2. Add "hash-only mode" to the proxy roadmap (no original_text stored).
3. Publish a data practices page at encypher.com/data-practices covering retention,
   deletion, and sub-processors.
4. Target SOC2 Type II readiness within 12 months of first enterprise proxy customer.

---

## 6. Internal Engineering: Embedding Mode SSOT

### Context

The embedding mode consolidation (TEAM_247/248) reduced valid `manifest_mode` values from
8+ (full, micro, lightweight_uuid, minimal_uuid, hybrid, zw_embedding, micro_ecc, micro_c2pa,
micro_ecc_c2pa) down to 2 (`full` and `micro`), with sub-mode behavior controlled by boolean
flags (`ecc`, `embed_c2pa`, `legacy_safe`). The backend SSOT is `signing_constants.py`.

The client-side normalization logic (mapping old mode names to new API parameters) is
currently duplicated across 4 locations:
- `chrome-extension/content/editor-signer.js`
- `chrome-extension/popup/popup.js`
- `chrome-extension/background/service-worker.js`
- `ghost-provenance/src/signer.ts`

### Proposed Solution

Create `packages/signing-config/` (`@encypher/signing-config`) following the existing
`@encypher/pricing-config` pattern:

```
packages/signing-config/
  src/
    modes.ts         -- MANIFEST_MODES, EMBEDDING_STRATEGIES, SEGMENTATION_LEVELS
    normalization.ts -- normalizeEmbeddingTechnique(), normalizeManifestOptions()
    types.ts         -- ManifestMode, SignOptions interfaces
  package.json       -- zero runtime dependencies
```

### Coverage

- Chrome extension: direct ES module import (has build step)
- Ghost provenance: npm reference (TypeScript, has build step)
- Microsoft Office add-in: not applicable (hardcoded `micro`, no build step; add webpack if
  mode selection is ever added)
- WordPress plugin: not applicable (PHP backend; JS assets lack build step)
- Python backend: not applicable (`signing_constants.py` remains the Python SSOT

### Print-Survivable Micro ECC (April 2026, TEAM_297)

A third embedding channel, `enable_print_micro_ecc`, was added as a parallel layer alongside
the `full`/`micro` manifest modes. It is not a `manifest_mode` value; it is a boolean flag
on `SignOptions` (Enterprise tier, mutually exclusive with `enable_print_fingerprint`). It
encodes the same `log_id` + HMAC payload as the digital micro channel in inter-word spacing
width variations (4-symbol base-4 encoding, RS(48,32) error correction). This channel
survives printing and scanning at 300-600 DPI.

The `@encypher/signing-config` package (when created) should include `enable_print_micro_ecc`
as a named boolean option alongside `ecc`, `legacy_safe`, and `embed_c2pa`.

### Why Deferred

Low urgency -- the 4 duplicate sites are consistent today and the normalization logic is
small. Worth doing when the next mode-level change requires touching all 4 sites anyway,
or when the Chrome extension gains a build step refactor.

---

## 7. CDN Edge Signing & Distribution Leak Detection

### Concept

Partner with CDNs (Fastly, Cloudflare, Akamai) or ad-tech delivery platforms to sign content
on demand at the delivery edge, embedding per-session/per-subscriber context via invisible
fingerprinting. When content leaks, the publisher traces the leak back to the exact user
session, subscriber account, referral path, and timestamp.

This extends the existing Enterprise-tier fingerprint service (`fingerprint_service.py`) from a
single-document tool into a distribution-layer forensic infrastructure.

### Why It Matters

- Upgrades Tier 1 detection from "what leaked" to "who leaked it" -- forensic-grade attribution
- Unlocks a new buyer (Head of Subscriptions / VP Revenue) and budget (paywall enforcement)
- No competitor can replicate: requires both ENC0100 patent-pending embedding AND delivery-layer integration
- Natural Enterprise add-on at $1,500-3,000/mo per publisher domain

### Technical Approach

Two-phase signing: pre-sign at publish time (document-level C2PA, cached normally), then apply
only the lightweight fingerprint layer at the CDN edge via WASM SDK. Hierarchical key derivation
(master -> doc -> session) avoids per-session key storage. Zero latency impact on content delivery.

### Partner Sequencing

1. Freestar/PubOS (seed concept in current partnership, Phase 2 capability)
2. **Prebid.js RTD Module (Phase 1 complete):** Backend signing service live at `/api/v1/public/prebid/sign`. RTD module (`encypherRtdProvider.js`, 3.79 KiB minified) with three execution paths (Path A: CDN/CMS meta tag, Path B: cache lookup, Path C: auto-sign). 23 unit + 7 E2E tests passing. Upstream PR to `prebid/Prebid.js` pending. Aditude relationship provides bridge into Prebid.org AI working group for distribution and standards influence.
3. Fastly (first CDN -- media vertical, least competitive overlap)
4. Cloudflare (after reference implementation exists -- competitive risk if approached too early)

### Prerequisites

- Patent CIP for per-session dynamic embedding claims (P0)
- Privacy framework: pseudonymous tokens only, mandatory publisher ToS disclosure, DPIA template (P0)
- Lightweight fingerprint-only API endpoint + identification endpoint (P1)

### Full Concept Document

See `future_product_concepts/CDN_Edge_Signing_Leak_Detection.md` for complete technical
architecture, privacy/legal analysis, partnership strategy, and risk register.

---

## Summary: Priority Matrix

| Initiative | Impact | Friction | Timeline |
|---|---|---|---|
| AppSource submission | High | Medium | 4-8 weeks |
| Microsoft ISV Connect | Very High | High | 3-6 months |
| LLM proxy as primary enterprise motion | Very High | Low | Now |
| CDN edge signing / leak detection | Very High | High | Q2-Q3 2026 |
| Google Docs add-on | Medium | Medium | 2-3 months |
| Notion integration | Medium-High | Low | 1-2 months |
| Slack signing bot | Low-Medium | Low | 2-3 months |
| DPA + data custody roadmap | High (blocker) | Medium | 4-6 weeks |
| @encypher/signing-config SSOT | Low | Low | When next mode change lands |
| Multi-media signing GTM messaging | High | Low | Now (capability exists) |

The highest-leverage near-term action is positioning the LLM proxy as the enterprise lead
product while pursuing AppSource for the add-in distribution channel. The Copilot gap and
data custody roadmap are medium-term blockers that require partnership conversations and
legal preparation respectively. CDN edge signing is a Q2-Q3 capability expansion with Very
High impact but requires patent (CIP) and privacy framework prerequisites before any pilot.
