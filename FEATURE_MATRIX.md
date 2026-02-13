# Encypher Feature Matrix by Tier

**Last Updated**: February 13, 2026
**Version**: 2.0

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

## Distribution & Integrations

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| REST API with Python SDK | ✅ | ✅ |
| WordPress plugin (auto-sign on publish) | ✅ | ✅ |
| CLI tool for local signing | ✅ | ✅ |
| GitHub Action for CI/CD | ✅ | ✅ |
| Browser extension for verification | ✅ | ✅ |
| Ghost CMS integration (webhook) | ✅ | ✅ |
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
