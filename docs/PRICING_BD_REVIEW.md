# Encypher Pricing & Tiers — BD Review Document

**Purpose**: Internal document for BD team feedback on our current pricing structure.  
**Status**: DRAFT — Awaiting BD feedback  
**Date**: February 2026  
**Sources**: Website (encypherai.com/pricing), API enforcement code, feature comparison table

> **Note to BD**: This document reflects what's live on our website and enforced in our API today. We need your feedback on pricing, packaging, positioning, and the coalition revenue model. Mark up anything that doesn't land with publishers.

---

## How Encypher Works (30-Second Version)

We embed invisible, tamper-proof signatures into text using **C2PA** — the same standard Adobe, Microsoft, Google, BBC, and OpenAI use for images. We co-chair the C2PA Text Provenance Task Force.

When a publisher signs their content:
1. Every article gets a cryptographic provenance record (who wrote it, when, where)
2. Invisible watermarks travel with the text — they survive copy-paste
3. When AI companies scrape or license that content, we can prove origin
4. Publishers earn revenue through our **licensing coalition**

---

## Tier Summary

| | Starter | Professional | Business | Enterprise |
|---|---|---|---|---|
| **Price** | Free forever | $99/mo ($950/yr) | $499/mo ($4,790/yr) | Custom |
| **Coalition Rev Share** | Standard | Enhanced | Premium | Best terms available |
| **Target** | Bloggers, small publishers, WordPress users | Regional newspapers, digital magazines, trade pubs | Major digital publishers, news networks | NYT, Guardian, News Corp, major media conglomerates |
| **CTA** | Get Started Free | Start Free Trial | Start Free Trial | Contact Sales |

> **BD Question**: Annual pricing is ~20% discount. Is that competitive? Should we offer more aggressive annual discounts to lock in longer commitments?

---

## Tier Details

### Starter — "Get paid when AI uses your content"

**Free forever.** The goal is adoption — get publishers signing content so the coalition grows.

| What They Get | Limit |
|---|---|
| C2PA document signing | 1,000/month |
| Content verification | Unlimited |
| API keys | 2 |
| Rate limit | 10 req/sec |
| Analytics retention | 7 days |
| Coalition membership | Auto-join |
| WordPress plugin | Basic (with Encypher branding) |
| Support | Community (GitHub/Discord) |

**What they DON'T get**: No sentence-level tracking, no Merkle trees, no source attribution, no batch operations, no team features, no streaming API.

**Positioning**: *"Start signing your content for free. When AI companies come knocking, you'll already have proof of authorship and you'll be earning revenue through the coalition."*

**Best for**: Independent bloggers, local news sites, small WordPress publishers

> **BD Questions**:
> - Is 1K signatures/month enough for a small publisher? A daily blogger publishes ~30/month, a local news site maybe 100-300. Seems generous.
> - Is the WordPress plugin a strong enough hook? "Installs in 5 minutes" is our current callout.
> - Should we mention the 65/35 rev share split publicly, or keep it as "Standard" (current approach)?

---

### Professional — "For regional publishers and growing media companies"

**$99/month** ($950/year). This is our **recommended tier** on the website.

| What They Get | Limit |
|---|---|
| Everything in Starter | — |
| Sentence-level Merkle roots | 5,000/month |
| C2PA + Merkle encoding choice | ✓ |
| Source attribution lookups | 10,000/month |
| Invisible Unicode embeddings | ✓ |
| Streaming signing (SSE) | ✓ |
| Sentence lookup API | 50,000/month |
| Bring Your Own Keys (BYOK) | ✓ |
| C2PA signing | Unlimited |
| API keys | 10 |
| Rate limit | 50 req/sec |
| Analytics retention | 90 days |
| WordPress plugin | Pro (no Encypher branding) |
| Support | Email (48hr SLA) |

**Key upgrade drivers from Starter**:
- **Sentence-level tracking** — know *which* sentences appear in AI outputs
- **Source attribution** — "Has my content been seen elsewhere?"
- **Invisible embeddings** — watermarks that survive copy-paste across the web
- **Enhanced coalition revenue share**

**Positioning**: *"You publish hundreds of articles a month. We'll track every sentence. When an AI model regurgitates your reporting, you'll have the receipts — and a better revenue share."*

**Best for**: Regional newspapers, digital magazines, trade publications

> **BD Questions**:
> - Is $99/mo the right price point for a regional newspaper? What's their typical tech budget?
> - "Sentence-level Merkle roots" — does this language land with publishers, or do we need simpler terms? Maybe "Sentence-level content tracking"?
> - 5K Merkle encodings/month — is that enough? A regional paper with 50 articles/day × 20 sentences = 1K/day = 30K/month. They'd blow through 5K fast. **Is this a problem or an intentional upsell to Business?**
> - Source attribution at 10K lookups — who's doing the looking up? The publisher checking if their content was reused? Or is this automated?

---

### Business — "For major digital publishers needing enterprise features"

**$499/month** ($4,790/year).

| What They Get | Limit |
|---|---|
| Everything in Professional | — |
| Merkle tree encodings | 10,000/month |
| Similarity detection | 5,000/month |
| Source attribution lookups | 50,000/month |
| Batch operations | 100 docs per request, 1,000 ops/month |
| Sentence tracking | 500,000/month |
| Team management | 10 users |
| Audit logs | ✓ |
| API keys | 50 |
| Rate limit | 200 req/sec |
| Analytics retention | 1 year |
| Support | Priority (24hr SLA) |
| SLA | 99.5% uptime |

**Key upgrade drivers from Professional**:
- **Similarity detection** — catch paraphrased/rewritten versions of your content (not just exact matches)
- **Source attribution at scale** — 50K lookups vs 10K
- **Batch operations** — sign entire archives, not one article at a time
- **Team features** — editors, legal, tech all get their own access + audit trail
- **Premium coalition revenue share**

**Positioning**: *"Your legal team needs evidence. Your editors need alerts. Your CFO wants the revenue. Business tier gives all three."*

**Best for**: Major digital publishers, news networks, media groups with multiple properties

> **BD Questions**:
> - $499/mo is a 5x jump from Professional. Is the value gap clear enough to justify it?
> - Similarity detection is the big differentiator here — is "5K/month" enough for a major publisher?
> - Team management capped at 10 users — is that enough for a major newsroom? Or does this push them to Enterprise too early?
> - Should batch operations be available at Professional tier (smaller limit)?
> - "Audit logs" — is this a selling point for publishers, or more of a checkbox for procurement?

---

### Enterprise — "White-glove implementation"

**Custom pricing.** Contact Sales.

| What They Get | Limit |
|---|---|
| Everything in Business | — |
| All features | Unlimited |
| Custom C2PA assertion schemas | ✓ |
| C2PA schema registry | ✓ |
| Assertion templates (news, legal, academic) | ✓ |
| SSO/SCIM integration | ✓ |
| Dedicated TAM + Slack channel | ✓ |
| Custom SLAs | ✓ |
| On-premise deployment option | ✓ |
| WordPress | Unlimited sites, white-label |
| Fuzzy matching (paraphrase detection) | ✓ |
| Dual binding (enhanced security) | ✓ |
| Content fingerprinting | ✓ |
| Support | Dedicated TAM |
| SLA | 99.9% uptime |

**Key upgrade drivers from Business**:
- **Unlimited everything** — no quotas to worry about
- **Custom C2PA assertions** — define your own metadata standards for your content
- **SSO/SCIM** — integrate with corporate identity (Okta, Azure AD, etc.)
- **On-premise** — run it inside your own infrastructure
- **Best coalition revenue terms**
- **Shape industry licensing standards** — this is the current website callout

**Positioning**: *"You're a top-50 publisher. You need this running inside your infrastructure, integrated with your SSO, with a dedicated team behind it. And you want the best economics in the coalition."*

**Best for**: NYT, Guardian, News Corp, AP, Reuters, major media conglomerates

> **BD Questions**:
> - What's the realistic price floor for Enterprise? $2K/mo? $5K/mo? $10K/mo?
> - Is "Shape industry licensing standards" compelling, or too abstract?
> - Do enterprise publishers actually want on-premise, or is cloud with SOC 2 sufficient?
> - Should we have a "Strategic Partner" tier visible to prospects, or keep it as an internal negotiation lever? (It exists in our code at 85/15 rev share with co-marketing + roadmap input + dedicated engineering.)

---

## The Coalition Revenue Model

This is our **primary differentiator**. Every publisher who signs content automatically joins the licensing coalition.

### How It Works
1. Publisher signs content with Encypher → content gets cryptographic provenance
2. AI companies pay to license coalition content (or we detect unauthorized usage)
3. Revenue is distributed based on how much of each publisher's content was used
4. Higher tiers get a bigger share of the revenue

### Revenue Share (Internal — Not on Public Website)

| Tier | Publisher Keeps | Encypher Keeps |
|---|---|---|
| Starter | 65% | 35% |
| Professional | 70% | 30% |
| Business | 75% | 25% |
| Enterprise | 80% | 20% |
| Strategic Partner | 85% | 15% |

> **Current website approach**: We show "Standard / Enhanced / Premium / Best terms available" without specific percentages. Actual splits are discussed during sales.

> **BD Questions**:
> - Should we publish the actual percentages? Transparency could build trust. Or does ambiguity give us negotiation room?
> - Is the 5% increment between tiers meaningful enough to drive upgrades?
> - Is 65/35 for free-tier publishers competitive? What are publishers used to from other licensing deals?
> - The subscription + rev share model means publishers pay us twice (subscription fee + our cut of licensing revenue). Is this a hard sell, or does the "subscription pays for itself" narrative work?

---

## Full Feature Comparison (As Shown on Website)

### Core API
| Feature | Starter | Professional | Business | Enterprise |
|---|---|---|---|---|
| C2PA Document Signing | 1K/mo | Unlimited | Unlimited | Unlimited |
| Advanced Signing Options | ✗ | ✓ | ✓ | ✓ |
| Content Verification | Unlimited | Unlimited | Unlimited | Unlimited |
| Sentence Lookup | ✗ | 50K/mo | 500K/mo | Unlimited |
| Usage Statistics | 7 days | 90 days | 1 year | Unlimited |

### Invisible Embeddings
| Feature | Starter | Professional | Business | Enterprise |
|---|---|---|---|---|
| Unicode VS Embeddings | ✓ | ✓ | ✓ | ✓ |
| Public Verification API | ✓ | ✓ | ✓ | ✓ |
| Batch Embedding Verification | ✓ | ✓ | ✓ | ✓ |

### Enterprise Features
| Feature | Starter | Professional | Business | Enterprise |
|---|---|---|---|---|
| Merkle Tree Encoding | ✗ | 5K/mo | 10K/mo | Unlimited |
| Source Attribution | ✗ | 10K/mo | 50K/mo | Unlimited |
| Similarity Detection | ✗ | ✗ | 5K/mo | Unlimited |
| Batch Operations | ✗ | ✗ | 1K/mo | Unlimited |
| Custom C2PA Assertions | ✗ | ✗ | ✗ | ✓ |
| C2PA Schema Registry | ✗ | ✗ | ✗ | ✓ |
| Assertion Templates | ✗ | ✗ | ✗ | ✓ |

### Streaming API
| Feature | Starter | Professional | Business | Enterprise |
|---|---|---|---|---|
| Streaming Signing (SSE) | ✗ | ✓ | ✓ | ✓ |
| Chat Application Wrapper | ✗ | ✓ | ✓ | ✓ |
| Server-Sent Events | ✗ | ✓ | ✓ | ✓ |

### Platform & Limits
| Feature | Starter | Professional | Business | Enterprise |
|---|---|---|---|---|
| API Keys | 2 | 10 | 50 | Unlimited |
| Rate Limit | 10/s | 50/s | 200/s | Unlimited |
| WordPress Plugin | Basic | Pro (no branding) | Pro (no branding) | White-label |
| Team Management | ✗ | ✗ | 10 users | Unlimited |
| Audit Logs | ✗ | ✗ | ✓ | ✓ |
| BYOK | ✗ | ✓ | ✓ | ✓ |

### Support & SLA
| Feature | Starter | Professional | Business | Enterprise |
|---|---|---|---|---|
| Support Level | Community | Email (48hr) | Priority (24hr) | Dedicated TAM |
| SLA Guarantee | ✗ | ✗ | 99.5% | 99.9% |
| SSO/SCIM | ✗ | ✗ | ✗ | ✓ |
| On-Premise Option | ✗ | ✗ | ✗ | ✓ |

---

## Open Questions for BD

### Pricing
1. Is the Free → $99 → $499 → Custom progression right?
2. Should there be a tier between $99 and $499? (e.g., $249 "Growth" tier)
3. Are annual discounts (20%) competitive?
4. What's the realistic Enterprise price floor?

### Packaging
5. Are the right features gated at the right tiers?
6. Is the Starter→Professional upgrade path compelling enough?
7. Is the Professional→Business jump too steep (5x price)?
8. Should batch operations start at Professional?
9. Are the quota limits (5K Merkle, 10K attribution, etc.) realistic for target customers?

### Coalition & Revenue
10. Should we publish actual rev share percentages?
11. Is the "subscription + rev share" double-dip a concern?
12. Is 65/35 competitive for free-tier publishers?
13. Is the 5% increment between tiers enough to drive upgrades?

### Positioning
14. Does "sentence-level Merkle roots" make sense to a publisher, or do we need plainer language?
15. Is "Shape industry licensing standards" compelling for Enterprise?
16. Should Strategic Partner be visible externally?
17. Is the WordPress plugin a strong enough hook for Starter?

### Competitive
18. What are publishers paying for similar tools today?
19. What rev share splits are publishers used to from existing licensing deals?
20. Who do publishers compare us to? (CCC, AP, NLA, individual AI licensing deals?)

---

**Please mark up this document with your feedback and return it. Highlight anything that doesn't match what you're hearing from publishers in conversations.**
