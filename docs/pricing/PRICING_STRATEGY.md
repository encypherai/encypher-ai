# Encypher Pricing & Monetization Strategy

**Version:** 3.0  
**Date:** February 13, 2026  
**Status:** Approved  
**Owner:** Product & Revenue Team

> **SSOT:** The canonical pricing configuration is defined in code at [`packages/pricing-config/src/`](../../packages/pricing-config/src/). The feature-by-feature breakdown is in [`FEATURE_MATRIX.md`](../../FEATURE_MATRIX.md). This document covers **strategy, economics, and GTM** — not feature lists.

---

## Executive Summary

Encypher operates a **dual-revenue model**:

1. **SaaS Platform Revenue** - Subscription fees for signing infrastructure
2. **Licensing Coalition Revenue** - Revenue share from AI training data licensing

This document defines the unified pricing strategy across all Encypher properties and the licensing coalition economics that create aligned incentives between Encypher and publishers.

### Key Strategic Principles

1. **Free tier builds the corpus** - Free users auto-join the licensing coalition, growing our content corpus
2. **We succeed when publishers succeed** - Revenue share model aligns incentives
3. **Merkle is the moat** - C2PA signing is commoditizing; sentence-level tracking is our differentiator
4. **AI companies pay for the corpus** - Publishers create value, AI companies pay for access

---

## Platform Tiers

Encypher has two core tiers plus optional add-ons and bundles. See [`FEATURE_MATRIX.md`](../../FEATURE_MATRIX.md) for the complete feature-by-feature breakdown.

### Tier Overview

| Tier | Price | Target Customer | Primary Value |
|------|-------|-----------------|---------------|
| **Free** | $0/month (1,000 docs/mo, $0.02/doc overage) | Bloggers, small-to-mid publishers, indie media, researchers | Full C2PA signing, verification, coalition enrollment |
| **Enterprise** | Custom (tiered by licensing potential) | Large publishers, media companies, enterprise content teams | Unlimited everything, all add-ons included, SLA, SSO, RBAC |

### Enterprise Sub-Tiers (Implementation Fee)

| Label | Licensing Potential | Implementation Fee |
|-------|--------------------|--------------------|
| Tier 1 Publisher | >$20M | $30K |
| Tier 2 Publisher | $3-20M | $20K |
| Tier 3 Publisher | <$3M | $10K |

Founding Coalition members have the implementation fee waived.

---

### Free Tier ($0/month)

**Target:** Individual bloggers, small news sites, indie publishers, WordPress owners

#### Key Features

| Category | Feature | Included |
|----------|---------|----------|
| **Signing** | C2PA 2.3-compliant document signing | ✅ 1,000/month ($0.02/doc overage) |
| **Signing** | Sentence-level Merkle tree authentication | ✅ |
| **Signing** | Invisible Unicode embeddings | ✅ |
| **Verification** | Public verification pages and API | ✅ Unlimited |
| **Distribution** | WordPress plugin, CLI, browser extension, Ghost integration | ✅ |
| **Dashboard** | Analytics, API keys, playground, integrations | ✅ |
| **Coalition** | Auto-join licensing coalition | ✅ |
| **Coalition** | Revenue share | 60% publisher / 40% Encypher |

#### Value Proposition
"Sign up to 1,000 articles/month for free. Get paid when AI companies use your content for training. Zero risk, pure upside."

---

### Enterprise Tier (Custom Pricing)

**Target:** Major digital publishers, global media companies (significant content volume)

**Examples:** New York Times, Wall Street Journal, Washington Post, BBC, Reuters, The Atlantic, Vox Media

#### Key Features (in addition to everything in Free)

| Category | Feature | Included |
|----------|---------|----------|
| **Signing** | Unlimited document signing | ✅ |
| **Signing** | Streaming LLM signing (WebSocket/SSE) | ✅ |
| **Signing** | Custom C2PA assertions and schema registry | ✅ |
| **Signing** | Batch operations (100+ docs/request) | ✅ |
| **Signing** | Document revocation (StatusList2021) | ✅ |
| **Signing** | Robust fingerprinting (survives paraphrase/translation) | ✅ |
| **Attribution** | Multi-source attribution with authority ranking | ✅ |
| **Attribution** | Plagiarism detection with Merkle proof linkage | ✅ |
| **Attribution** | Fuzzy fingerprint matching | ✅ |
| **Team** | Team management with RBAC | ✅ |
| **Team** | Audit logs | ✅ |
| **Team** | SSO (SAML, OAuth) | ✅ |
| **Team** | Organization switcher | ✅ |
| **Dashboard** | Webhooks for signing/verification/attribution events | ✅ |
| **Dashboard** | C2PA assertion templates | ✅ |
| **Support** | Dedicated SLA (99.9% uptime, 15-min incident response) | ✅ |
| **Support** | Named account manager | ✅ |
| **Add-ons** | All add-ons included (BYOK, white-label, custom signing identity, data export) | ✅ |
| **Coalition** | Revenue share | 80% publisher / 20% Encypher |
| **Coalition** | Custom terms available | ✅ |

#### Value Proposition
"Full platform access. Dedicated support. Best revenue share. Custom terms for strategic partners."

---

### Founding Coalition (Invite Only)

**Target:** First 10 major publishers to commit during the founding period

| Feature | Terms |
|---------|-------|
| Implementation fee | Waived |
| Revenue share | 80% publisher / 20% Encypher (same as Enterprise) |
| Advisory role | Syracuse Symposium seat, input on product roadmap |
| Priority positioning | Priority in all licensing negotiations |
| Early access | Beta features before GA |

**Rationale:** First movers who help establish the standard deserve the best terms. Their participation validates the coalition and attracts other publishers.

---

## Licensing Coalition Economics

### The Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LICENSING COALITION FLYWHEEL                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐       │
│   │  Publishers  │────────▶│   Encypher   │────────▶│ AI Companies │       │
│   │              │         │   Corpus     │         │              │       │
│   └──────────────┘         └──────────────┘         └──────────────┘       │
│         │                        │                        │                │
│         │ Sign content           │ Aggregate &            │ License        │
│         │ with C2PA              │ Track usage            │ training data  │
│         │                        │                        │                │
│         ▼                        ▼                        ▼                │
│   ┌──────────────────────────────────────────────────────────────┐         │
│   │                      REVENUE DISTRIBUTION                     │         │
│   │                                                               │         │
│   │   AI License Fee ──▶ Encypher ──▶ Publishers (by tier)       │         │
│   │                                                               │         │
│   └──────────────────────────────────────────────────────────────┘         │
│                                                                             │
│   VALUE EXCHANGE:                                                           │
│   • Publishers: Free/low-cost signing + NEW revenue stream                  │
│   • Encypher: Rev share + corpus growth + network effects                   │
│   • AI Companies: Licensed, attributed, compliant training data             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Revenue Share by Tier

| Model | Publisher Share | Encypher Share | Rationale |
|-------|-----------------|----------------|-----------|
| Coalition (Encypher-negotiated deals) | 60% | 40% | Encypher sources and negotiates the deal |
| Self-Service (publisher-sourced deals) | 80% | 20% | Publisher brings the relationship |
| Enterprise (custom terms) | 80% | 20% | Anchor tenants, corpus credibility |
| Founding Coalition | 80% | 20% | First movers, implementation fee waived |

### Comparison to Industry Standards

| Business Model | Take Rate | Notes |
|----------------|-----------|-------|
| **Encypher (Coalition)** | 40% | Creating entirely new revenue |
| Getty Images | 80% | Creator gets only 20% |
| Shutterstock | 70-85% | Similar B2B licensing |
| App Store | 30% | Just distribution |
| YouTube | 45% | Distribution + audience |
| Spotify | 30% | Distribution + audience |
| Music Publishers | 50% | Rights management |
| Literary Agents | 15% | Deal enablement |

**Key insight:** At 40% (coalition) or 20% (self-service), Encypher is more generous than most content licensing platforms, while providing infrastructure that enables revenue that didn't exist before.

---

## Revenue Projections by Publisher Type

### Assumptions

- AI companies pay $0.001 - $0.05 per article depending on content quality
- Premium content (NYT, WSJ) commands 10x standard rates
- High-quality content (Atlantic, Vox) commands 5x standard rates
- Standard content commands base rate
- Niche premium content commands 3x standard rates

---

### Example 1: New York Times (Enterprise - 80/20)

**Profile:**
- Tier: Enterprise
- Monthly visitors: 100M+
- Content volume: ~500 articles/day (182,500/year)
- Content quality: Premium (10x multiplier)
- Estimated rate: $0.05 per article

**Revenue Calculation:**

```
Annual articles:        182,500
Rate per article:       $0.05
Gross AI revenue:       182,500 × $0.05 = $9,125,000

NYT share (80%):        $7,300,000 / year
Encypher share (20%):   $1,825,000 / year

Enterprise SaaS fee:    ~$50,000 / year (custom)

NET TO NYT:             $7,250,000 / year (new revenue)
NET TO ENCYPHER:        $1,875,000 / year
```

**ROI for NYT:** Infinite. This revenue stream did not exist before Encypher.

---

### Example 2: Wall Street Journal (Enterprise - 80/20)

**Profile:**
- Tier: Enterprise
- Monthly visitors: 50M+
- Content volume: ~400 articles/day (146,000/year)
- Content quality: Premium (10x multiplier)
- Estimated rate: $0.05 per article

**Revenue Calculation:**

```
Annual articles:        146,000
Rate per article:       $0.05
Gross AI revenue:       146,000 × $0.05 = $7,300,000

WSJ share (80%):        $5,840,000 / year
Encypher share (20%):   $1,460,000 / year
```

---

### Example 3: The Atlantic (Enterprise - 80/20)

**Profile:**
- Tier: Enterprise
- Monthly visitors: 15M
- Content volume: ~30 articles/day (11,000/year)
- Content quality: High (5x multiplier)
- Estimated rate: $0.025 per article

**Revenue Calculation:**

```
Annual articles:        11,000
Rate per article:       $0.025
Gross AI revenue:       11,000 × $0.025 = $275,000

Atlantic share (80%):   $220,000 / year
Encipher share (20%):   $55,000 / year

Enterprise SaaS fee:    ~$20,000 / year (Tier 3)

NET TO ATLANTIC:        $200,000 / year (new revenue)
NET TO ENCYPHER:        $75,000 / year
```

---

### Example 4: Axios (Enterprise - 80/20)

**Profile:**
- Tier: Enterprise
- Monthly visitors: 10M
- Content volume: ~50 articles/day (18,250/year)
- Content quality: High (5x multiplier)
- Estimated rate: $0.025 per article

**Revenue Calculation:**

```
Annual articles:        18,250
Rate per article:       $0.025
Gross AI revenue:       18,250 × $0.025 = $456,250

Axios share (80%):      $365,000 / year
Encipher share (20%):   $91,250 / year

Enterprise SaaS fee:    ~$20,000 / year (Tier 3)

NET TO AXIOS:           $345,000 / year (new revenue)
NET TO ENCYPHER:        $111,250 / year
```

---

### Example 5: Denver Post (Free - Coalition 60/40)

**Profile:**
- Tier: Free
- Monthly visitors: 5M
- Content volume: ~75 articles/day (27,375/year)
- Content quality: Standard (1x)
- Estimated rate: $0.005 per article

**Revenue Calculation:**

```
Annual articles:        27,375
Rate per article:       $0.005
Gross AI revenue:       27,375 × $0.005 = $136,875

Denver Post share (60%): $82,125 / year
Encipher share (40%):    $54,750 / year

SaaS fee:                $0

NET TO DENVER POST:      $82,125 / year (new revenue)
NET TO ENCYPHER:         $54,750 / year
```

---

### Example 6: Seattle Times (Free - Coalition 60/40)

**Profile:**
- Tier: Free
- Monthly visitors: 4M
- Content volume: ~60 articles/day (21,900/year)
- Content quality: Standard (1x)
- Estimated rate: $0.005 per article

**Revenue Calculation:**

```
Annual articles:        21,900
Rate per article:       $0.005
Gross AI revenue:       21,900 × $0.005 = $109,500

Seattle Times share (60%): $65,700 / year
Encipher share (40%):      $43,800 / year

SaaS fee:                  $0

NET TO SEATTLE TIMES:      $65,700 / year (new revenue)
NET TO ENCYPHER:           $43,800 / year
```

---

### Example 7: Stratechery (Free - Coalition 60/40)

**Profile:**
- Tier: Free
- Subscribers: 50,000 paid
- Content volume: ~3 articles/week (156/year)
- Content quality: Niche premium (3x multiplier)
- Estimated rate: $0.015 per article

**Revenue Calculation:**

```
Annual articles:        156
Rate per article:       $0.015
Gross AI revenue:       156 × $0.015 = $2,340

Stratechery share (60%): $1,404 / year
Encipher share (40%):    $936 / year

SaaS fee:                $0

NET TO STRATECHERY:      $1,404 / year (free money)
NET TO ENCYPHER:         $936 / year
```

---

### Example 8: Local News Blog (Free - Coalition 60/40)

**Profile:**
- Tier: Free
- Monthly visitors: 50,000
- Content volume: ~5 articles/week (260/year)
- Content quality: Standard (1x)
- Estimated rate: $0.005 per article

**Revenue Calculation:**

```
Annual articles:        260
Rate per article:       $0.005
Gross AI revenue:       260 × $0.005 = $1,300

Blog share (60%):       $780 / year
Encipher share (40%):   $520 / year

SaaS fee:               $0

NET TO BLOG:            $780 / year (free money)
NET TO ENCYPHER:        $520 / year
```

---

## Revenue Summary by Publisher Segment

### Publisher Economics

| Publisher Type | Example | Tier | Rev Share | Gross AI Rev | Publisher Net | Encypher Net |
|----------------|---------|------|-----------|--------------|---------------|--------------|
| Global Giant | NYT | Enterprise | 80/20 | $9.1M | $7.25M | $1.88M |
| Global Giant | WSJ | Enterprise | 80/20 | $7.3M | $5.84M | $1.46M |
| Major Digital | Atlantic | Enterprise | 80/20 | $275K | $220K | $75K |
| Major Digital | Axios | Enterprise | 80/20 | $456K | $365K | $111K |
| Regional News | Denver Post | Free | 60/40 | $137K | $82K | $55K |
| Regional News | Seattle Times | Free | 60/40 | $110K | $66K | $44K |
| Indie Premium | Stratechery | Free | 60/40 | $2.3K | $1.4K | $0.9K |
| Local Blog | Various | Free | 60/40 | $1.3K | $0.8K | $0.5K |

### Encypher Revenue Projections (Year 1)

| Segment | Count | Avg Encypher Rev | Total Rev |
|---------|-------|------------------|-----------|
| Enterprise (Tier 1) | 10 | $1,500,000 | $15,000,000 |
| Enterprise (Tier 2) | 15 | $500,000 | $7,500,000 |
| Enterprise (Tier 3) | 50 | $100,000 | $5,000,000 |
| Free (active, coalition) | 10,000 | $500 | $5,000,000 |
| **Total Coalition Revenue** | | | **$32,500,000** |

| SaaS Subscriptions | Count | ARPU | Total ARR |
|--------------------|-------|------|-----------|
| Enterprise | 75 | $25,000 | $1,875,000 |
| **Total SaaS ARR** | | | **$1,875,000** |

**Total Year 1 Revenue Target: $34,375,000**

*Note: Coalition revenue depends on AI company licensing deals. SaaS revenue is more predictable. Free tier has no SaaS fee — revenue comes entirely from coalition rev share.*

---

## Feature Availability Matrix

> For the complete feature-by-feature breakdown, see [`FEATURE_MATRIX.md`](../../FEATURE_MATRIX.md). This is the SSOT for what's included in each tier.

---

## WordPress Plugin Strategy

### Free Plugin (WordPress.org)

**Features:**
- C2PA signing on publish
- Verification badge on posts
- Basic analytics
- Auto-joins licensing coalition (60/40 rev share)

**Limits:**
- Same as Free tier (1,000 docs/month, $0.02/doc overage)

**Purpose:**
- Distribution channel (WordPress.org marketplace)
- Corpus growth
- Brand awareness
- Upgrade funnel

### Enterprise Plugin Features

**Unlocked with Enterprise tier:**
- White-label verification pages (via White-Label Verification add-on)
- Custom signing identity
- Unlimited sites
- Team access and RBAC
- Custom integration support

---

## AI Company Pricing (Enterprise Sales)

AI companies are handled through enterprise sales, not self-serve. This section provides guidance for sales conversations.

### Licensing Models

#### 1. Training Data License

**For:** AI labs licensing corpus for model training

| Volume | Annual Price | Per-Article Rate |
|--------|--------------|------------------|
| Up to 1M articles | $500,000 | $0.50 |
| Up to 10M articles | $2,000,000 | $0.20 |
| Up to 100M articles | $10,000,000 | $0.10 |
| Unlimited | Custom | Negotiated |

**Includes:**
- Full corpus access
- Attribution metadata
- Provenance verification
- Compliance documentation
- Quarterly usage reports

#### 2. Attribution API License

**For:** AI products displaying content attribution

| API Calls/Month | Monthly Price |
|-----------------|---------------|
| 1M | $5,000 |
| 10M | $25,000 |
| 100M | $100,000 |
| Unlimited | Custom |

**Includes:**
- Real-time attribution lookup
- Source verification
- Publisher metadata
- 99.9% SLA

### Revenue Distribution to Publishers

AI licensing revenue flows back to publishers based on:
1. Content volume in corpus
2. Content quality signals
3. Usage in AI training/inference
4. Publisher tier (rev share %)

---

## Backend Features Roadmap

### Currently Implemented ✅

- C2PA signing and verification
- Sentence-level tracking with invisible embeddings
- Merkle tree encoding
- Source attribution
- Plagiarism detection
- Batch operations
- Streaming (WebSocket/SSE)
- Public verification API
- Custom C2PA assertions
- API key management
- Usage analytics

### Needs Implementation 🚧

| Feature | Priority | Effort | Required For |
|---------|----------|--------|--------------|
| Tier enforcement in API | P0 | 1 week | Monetization |
| Audit logs | P1 | 1 week | Enterprise tier |
| Team management | P1 | 2-3 weeks | Enterprise tier |
| BYOK completion | P2 | 1-2 weeks | Enterprise tier (add-on) |
| SSO/SCIM | P3 | 3-4 weeks | Enterprise tier |
| Coalition revenue tracking | P1 | 2 weeks | All tiers |
| Publisher payout system | P1 | 3 weeks | All tiers |

---

## GTM Strategy: Dashboard as the Gateway

### The Unified Approach

All customers—from indie bloggers to the New York Times—use the same infrastructure:

```
Publisher → Dashboard → Enterprise API → C2PA Signing + Coalition
```

The **dashboard is the source of truth** for pricing and the primary entry point for all customers. The marketing site mirrors the dashboard pricing and directs users to sign up.

### Customer Journey by Segment

| Segment | Entry Point | Conversion Path |
|---------|-------------|-----------------|
| **Long Tail** (bloggers) | Marketing site → Dashboard signup | Self-serve, credit card |
| **Mid-Market** (regional news) | Marketing site → Dashboard signup | Self-serve or sales assist |
| **Enterprise** (major publishers) | Marketing site → Dashboard → Contact Sales | Enterprise contract |
| **Strategic** (NYT, WSJ) | Direct outreach → Dashboard demo → Custom contract | White-glove sales |

### Why Dashboard-First Works

1. **Try Before You Buy**: Publishers can test the tech immediately
2. **Self-Serve Scale**: Long tail signs up without sales involvement
3. **Qualified Leads**: Enterprise prospects who contact sales already understand the product
4. **Unified Codebase**: One platform to maintain, not separate enterprise tools
5. **Network Effects**: Every publisher on the platform grows the coalition corpus

### Enterprise Sales Flow

1. Publisher discovers Encypher (marketing, referral, outreach)
2. Signs up for Free tier on dashboard
3. Tests C2PA signing, sees coalition revenue potential
4. Clicks "Contact Sales" for Enterprise features
5. Sales negotiates custom contract (pricing, rev share, SLA)
6. Account upgraded to Enterprise tier in dashboard
7. Publisher manages keys, users, analytics through same dashboard

### Pricing Alignment

The dashboard tiers align with GTM pricing:

| Dashboard Tier | GTM Tier | Annual Value |
|----------------|----------|--------------|
| Free | Long tail (self-serve) | $0 + 40% coalition rev share |
| Enterprise (Tier 3) | <$3M licensing potential | $10K impl + custom annual + 20% rev share |
| Enterprise (Tier 2) | $3-20M licensing potential | $20K impl + custom annual + 20% rev share |
| Enterprise (Tier 1) | >$20M licensing potential | $30K impl + custom annual + 20% rev share |

---

## Competitive Positioning

### vs. No Solution (Status Quo)

> "Your content is being scraped and used to train AI models right now. You're getting $0. With Encypher, you get paid for every article in our corpus. The question isn't whether you can afford Encypher—it's whether you can afford NOT to join."

### vs. Building Internal

> "Building C2PA infrastructure takes 18 months and $5M minimum. We co-chair the C2PA task force. We have relationships with every major AI company. You could build the tech, but you can't build the corpus or the relationships."

### vs. Other Watermarking

> "Watermarking proves you created content. We do that AND get you paid. Our licensing coalition is the only way to monetize your content in AI training. Watermarking alone is a cost center. Encypher is a profit center."

---

## Implementation Checklist

### Phase 1: Foundation (Week 1-2)
- [ ] Implement tier enforcement in API
- [ ] Update dashboard billing page with new tiers
- [ ] Update marketing site pricing page
- [ ] Create tier comparison documentation

### Phase 2: Coalition Infrastructure (Week 3-4)
- [ ] Build coalition revenue tracking
- [ ] Implement publisher payout system
- [ ] Create coalition terms of service
- [ ] Build coalition dashboard for publishers

### Phase 3: Team Features (Week 5-7)
- [ ] Implement team management
- [ ] Build audit logs
- [ ] Create role-based permissions
- [ ] Update dashboard UI

### Phase 4: Enterprise Features (Week 8-10)
- [ ] Complete BYOK implementation
- [ ] Build SSO/SCIM integration
- [ ] Create enterprise onboarding flow
- [ ] Develop custom reporting

---

## Future Cohort Pricing Policy

### Founding Coalition Members

Publishers who join the coalition during the **founding period** (prior to first major AI licensing deal) receive the best available terms:

- **Revenue share:** 80% publisher / 20% Encypher (Enterprise tier)
- **Lock-in:** These terms are **grandfathered** for the life of the contract
- **Benefits:** Input on product roadmap, early access to features, co-marketing opportunities

### Future Cohort Terms

After the founding period closes, new coalition members may receive different terms:

- Coalition rev share may be adjusted (e.g., 55/45 instead of 60/40)
- Self-service rev share may be adjusted (e.g., 75/25 instead of 80/20)
- Founding members retain their original terms regardless of future changes
- Any changes to standard terms will be announced with at least 90 days notice

**Rationale:** Early adopters who help establish the standard and validate the model deserve the best terms. Later entrants benefit from an established corpus and proven AI licensing deals, justifying a higher platform take.

---

## OEM / Non-Publisher Pricing

For customers who want to integrate Encypher APIs but do not participate in the Licensing Coalition (e.g., SaaS platforms, internal enterprise use), see:

**[OEM Pricing Guidelines](./OEM_PRICING_GUIDELINES.md)**

Key differences from publisher tiers:
- No coalition revenue share (they pay platform fees instead)
- Sales-driven (not self-serve)
- Base platform fee + usage-based component

---

## Document Control

**Version:** 3.0  
**Last Updated:** February 13, 2026  
**Next Review:** March 15, 2026  
**Approved By:** [Pending Executive Review]

### Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Nov 25, 2025 | Initial draft |
| 2.0 | Nov 25, 2025 | Complete rewrite with coalition economics, publisher examples, feature matrix |
| 2.1 | Nov 29, 2025 | Added GTM Strategy section: Dashboard as the Gateway. Aligned dashboard, marketing site, and internal docs. |
| 2.2 | Dec 3, 2025 | Added Future Cohort Pricing Policy and OEM/Non-Publisher section. Clarified founding member grandfathering. |
| 3.0 | Feb 13, 2026 | Consolidated to 2-tier model (Free + Enterprise). Removed stale Professional/Business tiers. Updated rev share to match pricing-config SSOT (60/40 coalition, 80/20 self-service). Replaced inline feature matrix with pointer to FEATURE_MATRIX.md. Updated all revenue projections. |
