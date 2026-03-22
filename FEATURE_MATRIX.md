# Encypher Feature Matrix by Tier

**Last Updated**: March 21, 2026
**Version**: 2.1

This document provides a comprehensive breakdown of all Encypher features organized by subscription tier.

The pricing model has two core tiers (**Free** and **Enterprise**) plus optional **Add-Ons** and **Bundles** available to any tier.

---

## Tier Overview

| Tier | Price | Target Audience | Key Value Proposition |
|------|-------|-----------------|----------------------|
| **Free** | $0/month (1,000 docs/mo, $0.02/doc overage) | Individual bloggers, small-to-mid publishers, indie media, researchers, WordPress owners | Full C2PA signing, verification, coalition enrollment |
| **Enterprise** | Custom (tiered by licensing potential) | Large publishers, media companies, enterprise content teams | Unlimited everything, all add-ons included, SLA, SSO, RBAC |

### Enterprise Sub-Tiers (Implementation Fee)

| Label | Licensing Potential | Implementation Fee |
|-------|--------------------|--------------------|
| Tier 1 Publisher | >$20M | $30K |
| Tier 2 Publisher | $3-20M | $20K |
| Tier 3 Publisher | <$3M | $10K |

Founding Coalition members have the implementation fee waived.

---

## Content Signing

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| C2PA 2.3-compliant document signing | ✅ | ✅ |
| Sentence-level Merkle tree authentication | ✅ | ✅ (Unlimited) |
| Invisible Unicode embeddings (survive copy-paste) | ✅ | ✅ |
| Custom metadata (author, publisher, license, tags) | ✅ | ✅ |
| Streaming LLM signing (WebSocket/SSE) | ❌ | ✅ |
| OpenAI-compatible /chat/completions with auto-signing | ❌ | ✅ |
| Custom C2PA assertions and schema registry | ❌ | ✅ |
| C2PA provenance chain (full edit history) | ❌ | ✅ |
| Batch operations (100+ documents/request) | ❌ | ✅ |
| Document revocation (StatusList2021) | ❌ | ✅ |
| Robust fingerprinting (survives paraphrase/translation) | ❌ | ✅ |

---

## Verification

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| Signature verification | ✅ | ✅ |
| Tampering detection | ✅ | ✅ |
| Metadata extraction | ✅ | ✅ |
| Public verification pages with shareable URLs | ✅ | ✅ |
| Public verification API (no auth required) | ✅ | ✅ |
| Multi-source attribution with authority ranking | ❌ | ✅ |
| Fuzzy fingerprint matching | ❌ | ✅ |
| Plagiarism detection with Merkle proof linkage | ❌ | ✅ |

---

## Dashboard Features

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| Overview (usage stats, API keys, quick start) | ✅ | ✅ |
| API Keys management | ✅ | ✅ |
| API Playground | ✅ | ✅ |
| Analytics (stats, time series chart, activity feed) | ✅ | ✅ |
| Analytics CSV export (summary + time series) | ✅ | ✅ |
| Documentation hub | ✅ | ✅ |
| Integrations (CMS webhooks) | ✅ | ✅ |
| Settings (profile, password, email change) | ✅ | ✅ |
| Billing | ✅ | ✅ |
| Dark mode | ✅ | ✅ |
| Command palette (Cmd+K) | ✅ | ✅ |
| Onboarding flow | ✅ | ✅ |
| **Webhooks** | ❌ | ✅ |
| **Team management (invite, roles, org switcher)** | ❌ | ✅ |
| **Audit logs** | ❌ | ✅ |
| **C2PA assertion templates** | ❌ | ✅ |

---

## CDN Provenance Continuity

Makes C2PA provenance survive CDN image transformations (resize, reformat, recompress). When a CDN strips the embedded manifest from a transformed image, the original provenance remains verifiable via server-side pHash lookup.

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| Image signing (`POST /cdn/images/sign`) | ❌ | ✅ |
| Register pre-signed images for CDN tracking | ❌ | ✅ |
| pHash fuzzy lookup (Hamming distance ≤8) | ❌ | ✅ |
| Pre-register CDN variant transforms | ❌ | ✅ |
| Public manifest fetch (`GET /cdn/manifests/{id}`) | ✅ (read-only) | ✅ |
| Public image verification (`POST /cdn/verify`) — three states | ✅ | ✅ |
| `ORIGINAL_SIGNED` — embedded manifest present and valid | ✅ | ✅ |
| `VERIFIED_DERIVATIVE` — no embedded manifest, pHash match found | ✅ | ✅ |
| `PROVENANCE_LOST` — transform too aggressive, no match | ✅ | ✅ |
| `application/cbor` manifest response (C2PA 2.x standards-native) | ❌ | ✅ |
| `GET /.well-known/c2pa/manifests/{id}` discovery alias | ✅ | ✅ |
| Cloudflare Worker (`C2PA-Manifest-URL` header injection) | ❌ | ✅ |
| Fastly Compute@Edge handler | ❌ | ✅ |
| Lambda@Edge (CloudFront) handler | ❌ | ✅ |
| Dashboard analytics (assets protected, variants verified, % recoverable) | ❌ | ✅ |
| Logpush image attribution events | ❌ | ✅ |
| CDN image registrations/month | 0 | Unlimited |

### CDN Quota

| Metric | Free | Enterprise |
|--------|:----:|:----------:|
| Image registrations/month | 0 | Unlimited |

---

## Audio C2PA Signing

Embed C2PA manifests directly into audio files. Uses `c2pa-python` (wrapping `c2pa-rs`) for container-specific embedding (RIFF chunk for WAV, ID3 GEOB frame for MP3, BMFF uuid box for M4A/AAC).

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| Audio C2PA signing (WAV, MP3, M4A/AAC) | ❌ | ✅ |
| Audio C2PA verification | ✅ | ✅ |
| C2PA v2.3 audio actions (created, dubbed, mixed, mastered, remixed) | ❌ | ✅ |
| Per-org signing credentials (SSL.com / BYOK) | ❌ | ✅ |
| Passthrough mode (provenance metadata without JUMBF embedding) | ❌ | ✅ |

---

## Video C2PA Signing

Embed C2PA manifests directly into video files. Uses `c2pa-python` (wrapping `c2pa-rs`) for container-specific embedding (ISO BMFF uuid box for MP4/MOV/M4V, RIFF C2PA chunk for AVI). Video endpoints use multipart upload (not base64) to handle files up to 500 MB.

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| Video C2PA signing (MP4, MOV, M4V, AVI) | ❌ | ✅ |
| Video C2PA verification | ✅ | ✅ |
| Multipart upload (up to 500 MB) | ❌ | ✅ |
| Large file download endpoint (files > 50 MB) | ❌ | ✅ |
| Per-org signing credentials (SSL.com / BYOK) | ❌ | ✅ |
| Passthrough mode (provenance metadata without JUMBF embedding) | ❌ | ✅ |

---

## Live Video Stream Signing (C2PA 2.3 Section 19)

Per-segment C2PA manifest signing for live video streams. Each CMAF/fMP4 segment gets its own C2PA manifest with backwards-linked provenance chain. REST-based session lifecycle with Merkle root computation on finalize.

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| Per-segment C2PA manifest signing | ❌ | ✅ |
| Manifest chaining (backwards-linked provenance via `com.encypher.stream.chain.v1`) | ❌ | ✅ |
| Merkle root computation over segment manifest hashes | ❌ | ✅ |
| Session-cached signing credentials (1-hour TTL) | ❌ | ✅ |
| Session status monitoring | ❌ | ✅ |

---

## Distribution & Integrations

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| REST API with Python SDK | ✅ | ✅ |
| WordPress plugin (auto-sign on publish) | ✅ | ✅ |
| WordPress plugin — image signing on publish | ❌ | ✅ |
| CLI tool for local signing | ✅ | ✅ |
| GitHub Action for CI/CD | ✅ | ✅ |
| Browser extension for verification | ✅ | ✅ |
| Ghost CMS integration (webhook + image signing) | ✅ | ✅ |
| Custom integrations | ❌ | ✅ |

---

## AI Licensing & Coalition

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| Auto-enrolled in Encypher Coalition | ✅ | ✅ |
| Content indexed for coalition licensing | ✅ | ✅ |
| Basic attribution view | ✅ | ✅ |
| Coalition dashboard with content stats | ✅ | ✅ |
| AI Company Licensing API | ❌ | ✅ |
| Content access APIs for AI models | ❌ | ✅ |
| Revenue distribution and payouts | ❌ | ✅ |
| Licensing usage and attribution reports | ❌ | ✅ |

---

## Authentication & Access

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| Email/password login | ✅ | ✅ |
| OAuth (Google, GitHub) | ✅ | ✅ |
| Password reset | ✅ | ✅ |
| Session management | ✅ | ✅ |
| SSO (SAML, OAuth) | ❌ | ✅ |
| Team management with RBAC | ❌ | ✅ |

---

## API Limits

| Metric | Free | Enterprise |
|--------|:----:|:----------:|
| Documents signed/month | 1,000 ($0.02/doc overage) | Unlimited |
| Verification requests | Unlimited | Unlimited |
| Public API lookups | Unlimited | Unlimited |

---

## Support

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| Documentation | ✅ | ✅ |
| Email support | ✅ | ✅ |
| Priority support (4-hour SLA) | ❌ | ✅ |
| Dedicated account manager | ❌ | ✅ |
| SLA guarantee (99.9% uptime, 15-min incident response) | ❌ | ✅ |

---

## Add-Ons (Available to Any Tier)

Add-ons are purchased separately. Enterprise tier includes all add-ons at no additional charge.

### Enforcement (Coming Soon)

| Add-On | Price | Description |
|--------|-------|-------------|
| Attribution Analytics | TBD | Full dashboard: where your content appears in AI outputs, frequency, context |
| Formal Notice Package | TBD | Cryptographically-backed formal notice to AI companies |
| Evidence Package | TBD | Court-ready evidence bundle for infringement claims |

### Infrastructure

| Add-On | Price | Description |
|--------|-------|-------------|
| Custom Signing Identity | $499/mo | Sign as your brand instead of "Encypher Coalition Member" |
| White-Label Verification | $299/mo | Verification pages on your domain with your branding (requires Custom Signing Identity) |
| Custom Verification Domain | $29/mo | Point a custom domain to verification pages (no full white-label) |
| BYOK (Bring Your Own Keys) | $499/mo | Use your organization's PKI infrastructure and signing certificates |

### Operations

| Add-On | Price | Description |
|--------|-------|-------------|
| Bulk Archive Backfill | $0.01/doc | One-time batch signing of existing content archives |
| Data Export (Full) | $49/export | Full export of all attribution and analytics data as CSV/JSON |
| Priority Support | $199/mo | 4-hour response SLA, dedicated onboarding, priority bug fixes |

---

## Bundles

| Bundle | Price | Includes | Savings |
|--------|-------|----------|---------|
| Enforcement Bundle | TBD (Coming Soon) | Attribution Analytics, 2 Formal Notices/mo, 1 Evidence Package/mo | 57% |
| Publisher Identity | $749/mo | Custom Signing Identity, White-Label Verification, Custom Verification Domain | 7% |
| Full Stack | TBD (Coming Soon) | Enforcement Bundle + Publisher Identity | 51% |

---

## Revenue Share (Coalition Licensing)

| Model | Publisher Share | Encypher Share |
|-------|:--------------:|:--------------:|
| Coalition (Encypher-negotiated deals) | 60% | 40% |
| Self-Service (publisher-sourced deals) | 80% | 20% |

---

## Platform Partner Tier (Strategic Partner)

The `strategic_partner` tier is a non-public, integration-partnership tier assigned to platform partners (e.g. Freestar) who onboard publishers en masse on behalf of Encypher. It is not purchasable through the dashboard.

| Feature | strategic_partner |
|---------|:-----------------:|
| All Enterprise signing features | Yes |
| Unlimited quota and rate limits | Yes |
| Proxy signing (`publisher_org_id` on `POST /sign`) | Yes - signs on behalf of provisioned publishers; publisher pays quota |
| Bulk publisher provisioning (`POST /api/v1/partner/publishers/provision`) | Yes - creates orgs, rights profiles, and claim emails in one call |
| Delegated rights setup (`POST /api/v1/rights/profile/delegated-setup`) | Yes |
| Publisher dashboard claim flow (existing `/invite/[token]` page) | Yes - publishers claim via email link |

Publishers provisioned by a strategic partner receive:
- A `free`-tier organization created on their behalf
- A `news_publisher_default` rights profile with `notice_status=active` and `coalition_member=True`
- A partner-branded claim email linking to their dashboard

---

## Dashboard Feature Gating (Implementation)

The dashboard uses `userTier` from the session JWT to gate features. The sidebar hides enterprise-only pages for free users.

| Gating Mechanism | Location | Behavior |
|-----------------|----------|----------|
| Sidebar nav filtering | `DashboardLayout.tsx` | Enterprise nav group hidden for free users |
| Page-level tier check | `audit-logs/page.tsx`, `team/page.tsx` | Shows upgrade prompt for non-enterprise users |
| Playground endpoint gating | `playground/page.tsx` | `minTier` per endpoint (currently unused) |
| Template selector | `TemplateSelector.tsx` | Shows "Enterprise tier required" on error |
| Billing tier normalization | `billing/page.tsx` | Maps legacy tier names (`starter`, `basic`) to `free` |

**Source of truth for pricing**: `packages/pricing-config/src/` (auto-generated to `apps/dashboard/src/lib/pricing-config/tiers.ts`)

---

## Legend

- ✅ = Included
- ❌ = Not available at this tier (upgrade or add-on required)
- "Unlimited" = No monthly cap
- "TBD" = Pricing not yet finalized
- "Coming Soon" = Feature announced but not yet available

---

## Related Documentation

- [README.md](./README.md) - Repository overview
- [MICROSERVICES_FEATURES.md](./MICROSERVICES_FEATURES.md) - Detailed microservice features
- [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) - Full documentation index
- [packages/pricing-config/](./packages/pricing-config/) - Pricing config source of truth

---

**Document End**
