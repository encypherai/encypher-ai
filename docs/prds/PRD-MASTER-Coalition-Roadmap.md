# Coalition & Licensing Vision - Master Roadmap

**Created**: 2025-11-04  
**Status**: Planning  
**Vision**: Enable small publishers to monetize content through collective licensing

---

## Vision Statement

Build a coalition model where free tier users are automatically onboarded into a content licensing collective. Small publishers pool their C2PA-signed content, which Encypher licenses in bulk to AI companies for training data. Revenue is distributed to members based on content contribution (65-75% to publishers, 25-35% to Encypher depending on tier).

---

## Strategic Goals

### Business Goals
1. **Monetize Free Tier**: Convert free tier from cost center to revenue generator
2. **Network Effects**: More members = more valuable content pool = better AI company deals
3. **Competitive Moat**: First-mover advantage in collective content licensing
4. **Scalable Revenue**: Automated distribution scales to 100K+ members

### Product Goals
1. **Auto-Onboarding**: 100% of free tier users join coalition
2. **Transparent Revenue**: Members see exactly how they earn
3. **Bulk Licensing**: Enable $50K-$1M deals with AI companies
4. **Automated Distribution**: Zero manual work for revenue splits

---

## PRD Overview

### Core Infrastructure (P0 - Critical)

#### PRD-001: Coalition Infrastructure & Auto-Onboarding
**Effort**: 4-6 weeks  
**Priority**: P0  
**Dependencies**: None

**Deliverables:**
- Coalition Service microservice (Port 8009)
- Auto-enrollment on free tier signup
- Coalition membership database
- Content indexing from signed documents
- Coalition stats API
- Revenue tracking infrastructure

**Key Features:**
- Automatic coalition enrollment for free tier
- Coalition membership management
- Content pool aggregation
- Member stats dashboard
- Revenue tracking foundation

---

#### PRD-002: Licensing Agreement Management
**Effort**: 3-4 weeks  
**Priority**: P0  
**Dependencies**: PRD-001

**Deliverables:**
- Licensing agreement CRUD
- AI company API key management
- Content access tracking
- Usage quota enforcement
- Revenue distribution engine
- Payment processing (Stripe)

**Key Features:**
- Create licensing agreements with AI companies
- Track content contribution to pool
- Automated revenue calculation (tiered splits: 65/35, 70/30, 75/25)
- Automated payment distribution
- Admin dashboard for agreement management

---

### User Experience (P1 - High)

#### PRD-003: WordPress Coalition Integration
**Effort**: 1-2 weeks  
**Priority**: P1  
**Dependencies**: PRD-001

**Deliverables:**
- Coalition stats widget for WordPress admin
- Revenue tracking panel
- Settings integration
- API integration

**Key Features:**
- Dashboard widget showing coalition stats
- Revenue earned display
- One-click access to full dashboard
- Auto-refresh stats

---

#### PRD-004: Dashboard Coalition Features
**Effort**: 2-3 weeks  
**Priority**: P1  
**Dependencies**: PRD-001

**Deliverables:**
- Coalition tab in dashboard
- Revenue tracking UI
- Content performance analytics
- Admin coalition management
- Access logs viewer

**Key Features:**
- Member coalition dashboard
- Revenue charts and breakdown
- Top performing content
- AI company access logs
- Admin management interface

---

### Future Enhancements (P2 - Medium)

#### PRD-005: AI Company Integration Portal (Future)
**Effort**: 3-4 weeks  
**Priority**: P2  
**Dependencies**: PRD-002

**Deliverables:**
- Self-service portal for AI companies
- Content discovery interface
- Usage analytics dashboard
- Billing and invoicing

---

#### PRD-006: Advanced Revenue Models (Future)
**Effort**: 2-3 weeks  
**Priority**: P2  
**Dependencies**: PRD-002

**Deliverables:**
- Multiple distribution algorithms (content contribution-based, quality-weighted)
- Tiered revenue splits (65/35 free, 70/30 pro, 75/25 enterprise)
- Bonus pools for high-performing content
- Referral revenue sharing

---

## Implementation Timeline

### Phase 1: Foundation (Weeks 1-6)
**Goal**: Build core coalition infrastructure

```
Week 1-2:  PRD-001 - Coalition Service (Database, API)
Week 3-4:  PRD-001 - Auto-enrollment, Content indexing
Week 5-6:  PRD-002 - Licensing agreements, AI company API
```

**Milestone**: Coalition infrastructure operational, first agreement created

---

### Phase 2: Revenue Engine (Weeks 7-10)
**Goal**: Enable revenue distribution

```
Week 7-8:  PRD-002 - Revenue calculation engine
Week 9:    PRD-002 - Payment processing integration
Week 10:   PRD-002 - Testing and refinement
```

**Milestone**: First revenue distribution completed

---

### Phase 3: User Experience (Weeks 11-14)
**Goal**: Member-facing features

```
Week 11-12: PRD-003 - WordPress plugin integration
Week 13-14: PRD-004 - Dashboard coalition features
```

**Milestone**: Members can view stats and revenue in WordPress and dashboard

---

### Phase 4: Admin Tools (Weeks 15-16)
**Goal**: Admin management interface

```
Week 15:   PRD-004 - Admin coalition management
Week 16:   PRD-002 - Admin agreement management
```

**Milestone**: Admins can fully manage coalition and agreements

---

### Phase 5: Launch (Weeks 17-18)
**Goal**: Production launch

```
Week 17:   End-to-end testing, security audit
Week 18:   Soft launch to 100 beta users
Week 19:   Full launch, marketing campaign
```

**Milestone**: Coalition live for all free tier users

---

## Technical Architecture

### Microservices

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (8000)                       │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌───────▼────────┐   ┌───────▼────────┐
│  Auth Service  │   │Coalition Service│   │Enterprise API  │
│   (Port 8001)  │   │   (Port 8009)  │   │  (Port 9000)   │
└────────────────┘   └────────────────┘   └────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   PostgreSQL      │
                    │   Redis           │
                    │   Stripe API      │
                    └───────────────────┘
```

### Data Flow

```
1. User Signup (Free Tier)
   ↓
2. Auth Service creates user
   ↓
3. Coalition Service auto-enrolls
   ↓
4. User signs content via Enterprise API
   ↓
5. Coalition Service indexes content
   ↓
6. AI Company accesses content (tracked)
   ↓
7. Monthly: Revenue calculated and distributed
   ↓
8. Payments processed via Stripe
```

---

## Success Metrics

### Launch Metrics (30 Days)
| Metric | Target |
|--------|--------|
| Free tier coalition enrollment | 100% |
| Coalition content pool | 10K+ documents |
| First AI company agreement | 1 |
| System uptime | 99.9% |

### Growth Metrics (90 Days)
| Metric | Target |
|--------|--------|
| Coalition members | 1,000+ |
| Content pool | 100K+ documents |
| AI company agreements | 3 |
| Revenue distributed | $10K+ |
| Free → Pro conversion | 5% |

### Scale Metrics (180 Days)
| Metric | Target |
|--------|--------|
| Coalition members | 10,000+ |
| Content pool | 1M+ documents |
| AI company agreements | 10 |
| Revenue distributed | $100K+ |
| Member satisfaction | 80%+ |

---

## Risk Assessment

### Critical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| No AI company interest | High | Medium | Proactive outreach, pilot deals, competitive pricing |
| Low content quality | Medium | Medium | Quality filters, minimum word count, editorial review |
| Revenue disputes | Medium | Low | Transparent tracking, clear terms, audit trail |
| Scalability issues | High | Low | Design for 100K+ members, load testing |
| Payment processing failures | Medium | Low | Stripe reliability, retry logic, error handling |

---

## Dependencies

### Technical Dependencies
- **Auth Service**: User management, signup flow
- **Enterprise API**: Document signing, C2PA manifests
- **Dashboard App**: UI for coalition features
- **WordPress Plugin**: Coalition widget
- **Stripe**: Payment processing
- **PostgreSQL**: Database
- **Redis**: Caching, rate limiting

### External Dependencies
- **AI Company Partners**: Need at least 1 pilot partner
- **Legal Review**: Coalition terms, licensing agreements
- **Payment Processor**: Stripe account setup
- **Email Service**: SendGrid for notifications

---

## Open Questions & Recommendations

### Business Questions

#### 1. **Revenue Split**: What should the tiered revenue splits be?

**Recommendation: Implement 65/35, 70/30, 75/25 tiered splits (REVISED MODEL)**

**CRITICAL CLARIFICATION:**
This is **NOT a per-scrape revenue share model** (like Tollbit/Cloudflare). This is **bulk licensing for AI training data** - one-time or annual deals where AI companies pay for access to the entire coalition content pool for model training.

**Recommended Tiered Model:**
- **Free Tier: 65/35 split** (65% to publishers, 35% to Encypher)
- **Pro Tier: 70/30 split** (70% to publishers, 30% to Encypher)
- **Enterprise Tier: 75/25 split** (75% to publishers, 25% to Encypher)

**Why Higher Encypher Share Makes Sense:**

1. **Training Data Licensing ≠ Adtech**
   - Adtech (70/30 publisher-favored): Automated, low-touch, high-volume
   - Training licensing: Complex negotiations, legal frameworks, multi-million dollar deals
   - More similar to music licensing (labels 30-50%) or stock photo licensing (agencies 40-60%)

2. **Encypher's Value Add**
   - Negotiates $500K-$2M AI company deals (not automated)
   - Provides C2PA infrastructure (signing, verification, tracking)
   - Manages legal framework and formal notice capability
   - Handles payment processing and distribution
   - Bears risk of AI company non-payment
   - Maintains coalition platform, APIs, and compliance

3. **Publishers Get Something From Nothing**
   - Unmarked content has ZERO licensing value
   - Coalition enables licensing that couldn't happen otherwise
   - Not competing with existing revenue streams
   - No alternative exists for collective training data licensing

4. **Aligns with GTM Strategy**
   - Enterprise publisher deals: 25-30% to Encypher
   - Enterprise tier (75/25) = "founding member" 25% rate
   - Pro tier (70/30) = standard publisher rate
   - Free tier (65/35) = "we do more work for free users"

5. **Upgrade Incentive Remains Strong**
   - At $1,000 coalition earnings:
     - Free: $650 payout
     - Pro: $700 payout (+$50/month = 7.7% improvement)
     - Enterprise: $750 payout (+$100/month = 15.4% improvement)
   - Pro tier pays for itself at ~$200/month in coalition earnings
   - Most active publishers will hit this threshold

**Implementation:**
```sql
-- Update coalition_settings
UPDATE coalition_settings 
SET setting_value = '{"free": {"encypher": 35, "members": 65}, "pro": {"encypher": 30, "members": 70}, "enterprise": {"encypher": 25, "members": 75}}'
WHERE setting_key = 'revenue_split';
```

**Expected Impact:**
- Free → Pro conversion: 5-8% (upgrade incentive clear at scale)
- Encypher revenue: Higher margin on free tier (most users), lower on paying tiers (fair)
- Publisher satisfaction: High (getting paid for previously unmarked content)
- Competitive positioning: Strong (no alternative exists)

---

#### 2. **Minimum Payout**: $10 threshold? Or accumulate to $50?

**Recommendation: $10 threshold with smart accumulation**

**Analysis:**
- **$10 minimum aligns with Stripe's economics** ($0.30 + 2.9% fee = $0.59 on $10 payout = 5.9% overhead)
- **$50 threshold reduces payment overhead** but delays gratification and reduces engagement
- **Competitor benchmarks**: YouTube ($100), Medium ($10), Substack (immediate)

**Recommended Tiered Approach:**
- **Free Tier: $50 minimum payout**
  - Reduces payment processing costs (fewer, larger transactions)
  - Most free tier users won't hit threshold quickly (engagement driver)
  - Encourages Pro upgrade to access earnings faster
  
- **Pro Tier: $10 minimum payout**
  - Faster access to earnings (upgrade incentive)
  - Higher engagement and satisfaction
  - Pro users likely generate more content = higher payouts anyway

- **Enterprise Tier: Monthly automatic payout** (no minimum)
  - White-glove service expectation
  - Larger volumes justify processing costs

**Implementation:**
```sql
UPDATE coalition_settings 
SET setting_value = '{"free": {"amount": 50, "currency": "USD"}, "pro": {"amount": 10, "currency": "USD"}, "enterprise": {"amount": 0, "currency": "USD"}}'
WHERE setting_key = 'min_payout_threshold';
```

**Expected Impact:**
- Payment processing costs: 3-5% of total payouts (vs. 8-10% with $10 for all)
- Free → Pro conversion: +2-3% from users wanting faster payouts
- Member satisfaction: Higher (clear path to earnings)

---

#### 3. **Distribution Method**: Equal split vs. usage-based vs. quality-weighted?

**Recommendation: Content contribution-based with quality multipliers**

**IMPORTANT:** Since this is **bulk training data licensing** (not per-scrape), distribution is based on **content contribution to the pool**, not real-time access tracking.

**Phase 1 (Launch): Content Contribution-Based**
- **Metric**: Weighted content contribution to coalition pool
- **Formula**: `member_revenue = (member_content_value / total_pool_value) × member_pool`
- **Content Value Factors**:
  - Word count (more content = more value)
  - Content quality (premium content weighted higher)
  - Content freshness (newer content more valuable for training)
  - Verification count (proves content is being used/valued)

**Base Content Value Formula:**
```python
content_value = (
    word_count +                    # Raw contribution (300-10,000 words)
    quality_multiplier +            # 1.0 (standard) to 2.0 (premium)
    freshness_bonus                 # 1.5x for <30 days, 1.2x for <90 days, 1.0x otherwise
)

member_total_value = sum(content_value for all member's content)
member_revenue = (member_total_value / total_pool_value) × member_pool
```

**Rationale:**
- **Fair**: Publishers with more/better content get more revenue
- **Simple**: Easy to calculate and explain
- **Transparent**: Members see exactly how their content contributes
- **Predictable**: Revenue doesn't fluctuate based on AI company access patterns

**Phase 2 (3-6 months): Quality-Weighted Contribution**
- Add quality tiers (Premium/Standard/Archive)
- Premium content gets 2x multiplier
- Standard content gets 1x multiplier
- Archive content gets 0.5x multiplier

**Quality Score Formula:**
```python
quality_multiplier = (
    word_count_factor × 0.3 +      # >1000 words = 1.5, 300-1000 = 1.0
    verification_factor × 0.2 +     # >10 verifications = 1.3, >5 = 1.1
    freshness_factor × 0.3 +        # <30 days = 1.5, <90 days = 1.2, <1yr = 1.0
    content_type_factor × 0.2       # Article = 1.2, Blog = 1.0, Social = 0.8
)
```

**Phase 3 (Future): Advanced Models**
- **Category premiums**: Investigative journalism, technical content worth more
- **Bonus pools**: Top 10% contributors get 20% bonus from separate pool
- **Referral revenue**: Invite publishers, earn 5% of their revenue for 12 months
- **Exclusivity bonus**: Exclusive content (not published elsewhere) gets 1.5x multiplier

**Optional: Hybrid Model (If AI Companies Provide Access Data)**
If AI companies share which content they actually used in training:
- 70% distributed by content contribution (predictable)
- 30% distributed by actual usage (performance bonus)
- Best of both worlds: base revenue + performance upside

**Implementation Priority:**
1. **Launch**: Content contribution-based (simple, no AI company data needed)
2. **Month 3**: Add quality multipliers (after data collection)
3. **Month 6**: Bonus pools and advanced features
4. **Month 12**: Hybrid model if AI companies share usage data

**Expected Impact:**
- Member satisfaction: High (fair, transparent, predictable)
- Content quality: Improves over time (incentivized)
- Gaming resistance: Quality multipliers prevent spam
- Publisher engagement: Clear path to increase earnings (create more/better content)

---

#### 4. **AI Company Pricing**: How to price bulk licensing deals?

**Recommendation: Annual bulk licensing for training data access**

**CRITICAL DISTINCTION:**
- **Coalition Content Licensing**: Bulk training data access (this section)
- **Enterprise API**: Separate product ($35-50M/year for C2PA infrastructure + performance intelligence)

**Coalition Training Data Licensing Model:**

**Tier 1: Major AI Labs** ($1M - $3M/year)
- **Target**: OpenAI, Anthropic, Google DeepMind, Meta AI
- **What They Get**: 
  - Full coalition content pool (1M+ documents) for training
  - Annual license, unlimited training runs
  - Attribution data (optional, for performance intelligence)
  - Legal indemnification (formal licensing = no litigation risk)
- **Pricing Model**: 
  - Base: $1M/year for pool access
  - Volume tier: +$0.50 per 1K documents in pool (scales with coalition growth)
  - Example: 1M documents = $1M base + $500K volume = $1.5M/year
- **Justification**: 
  - Avoids $10M+ litigation risk per case
  - Access to high-quality, C2PA-verified training data
  - Formal licensing relationship with publisher ecosystem
  - Supports C2PA standards (they're already members)

**Tier 2: Mid-Size AI Companies** ($250K - $750K/year)
- **Target**: Cohere, Mistral AI, Stability AI, AI21 Labs, Inflection
- **What They Get**:
  - Full coalition pool for training
  - Annual license with refresh rights (quarterly updates)
  - Standard attribution data
  - Legal indemnification
- **Pricing Model**:
  - Base: $250K/year for pool access
  - Volume tier: +$0.25 per 1K documents in pool
  - Example: 1M documents = $250K base + $250K volume = $500K/year
- **Justification**:
  - Growing companies need diverse training data
  - Budget-conscious but willing to pay for quality + legal clarity
  - Ecosystem building (future Tier 1 customers)

**Tier 3: Startups & Research** ($25K - $100K/year)
- **Target**: AI startups (<$50M funding), academic institutions, research labs
- **What They Get**:
  - Limited pool (100K-500K documents) or category-specific
  - Annual license, training only (no commercial inference)
  - Basic attribution data
  - Limited indemnification
- **Pricing Model**:
  - Base: $25K/year for 100K documents
  - Volume tier: +$0.10 per 1K additional documents
  - Example: 500K documents = $25K base + $40K volume = $65K/year
- **Justification**:
  - Ecosystem building and goodwill
  - Academic research supports standards adoption
  - Future commercial customers

**Pricing Justification (Sales Conversations):**

1. **Litigation Risk Avoidance** ($10M+ per case)
   - NYT vs. OpenAI: Billions at stake
   - Formal licensing eliminates risk entirely
   - Coalition represents growing publisher ecosystem

2. **Publisher Relations**
   - Collaborative vs. adversarial relationships
   - Publishers get paid, AI companies get legal clarity
   - Win-win through C2PA standards

3. **Content Quality**
   - C2PA-verified, tamper-proof content
   - High-quality publisher content (not scraped web data)
   - Sentence-level tracking for attribution

4. **Standards Compliance**
   - C2PA co-chair authority (we wrote the standard)
   - Industry leaders already implementing (Google SynthID, OpenAI participation)
   - Future-proof as standards become mandatory

**Expected Revenue (Year 1):**
- 2 Tier 1 deals × $1.5M = $3M
- 5 Tier 2 deals × $500K = $2.5M
- 10 Tier 3 deals × $50K = $500K
- **Total**: $6M licensing revenue

**Revenue Distribution (with 65/35, 70/30, 75/25 splits):**
- Assuming 80% free tier, 15% pro tier, 5% enterprise tier
- Free tier pool: $6M × 80% × 65% = $3.12M to publishers
- Pro tier pool: $6M × 15% × 70% = $630K to publishers
- Enterprise tier pool: $6M × 5% × 75% = $225K to publishers
- **Total to publishers**: $3.975M (66.25% average)
- **Total to Encypher**: $2.025M (33.75% average)

**Note:** This is SEPARATE from Enterprise API revenue ($35-50M/year for infrastructure + performance intelligence)

---

#### 5. **Pro Tier Incentive**: What coalition benefits drive upgrades?

**Recommendation: Multi-faceted value proposition**

**Primary Incentives (Ranked by Impact):**

1. **Better Revenue Split** (70/30 vs. 65/35) - **HIGHEST IMPACT**
   - Direct financial benefit
   - Pays for itself at ~$200/month in coalition earnings
   - Clear ROI calculation for publishers
   - Example: $1,000 coalition earnings → Free tier gets $650, Pro gets $700 (+$50/month = half of $99 plan cost)
   - At $2,000 earnings: Free gets $1,300, Pro gets $1,400 (+$100/month = pays for plan + profit)

2. **Lower Payout Threshold** ($10 vs. $50) - **HIGH IMPACT**
   - Faster access to earnings
   - Psychological benefit (see money sooner)
   - Reduces "locked earnings" frustration
   - Particularly valuable for smaller publishers

3. **Priority Content Placement** - **MEDIUM IMPACT**
   - Pro content shown first to AI companies
   - Higher likelihood of access = more revenue
   - "Featured publisher" badge in coalition pool
   - Estimated 20-30% more accesses than free tier

4. **Advanced Analytics** - **MEDIUM IMPACT**
   - See which AI companies accessed your content
   - Content performance insights (what types perform best)
   - Revenue forecasting based on trends
   - Competitive intelligence (how you compare to others)

5. **Coalition Governance** - **LOW-MEDIUM IMPACT**
   - Vote on coalition policies
   - Suggest AI company targets
   - Influence distribution algorithm changes
   - "Founding member" status for early adopters

6. **Exclusive Features** - **LOW IMPACT (but valuable for retention)**
   - Early access to new coalition features
   - Beta test new AI company integrations
   - Custom content categories
   - White-label coalition branding

**Messaging Framework:**
```
Free Tier: "Join the coalition, start earning from your content"
Pro Tier: "Keep 70% instead of 65% - maximize your coalition earnings"
Enterprise Tier: "Keep 75% + custom licensing deals + coalition network effects"
```

**Expected Conversion Funnel:**
- Month 1: User joins free tier, sees $20 pending (65% of $30)
- Month 2: Sees $65 pending (65% of $100), realizes Pro would give $70 (+$5)
- Month 3: Sees $130 pending (65% of $200), Pro would give $140 (+$10)
- Month 4: Hits $50 threshold, gets first payout of $195 (65% of $300)
- Month 5: Sees $325 pending (65% of $500), Pro would give $350 (+$25)
- Month 6: **Upgrades to Pro** (ROI clear: at $2K earnings, extra $100/month > $99/month cost)
- Month 12: Earning $1,500/month, Pro gives $1,050 vs Free $975 (+$75/month profit after plan cost)

**Implementation:**
- Dashboard shows "Pro Upgrade Calculator" widget
- Real-time ROI calculation based on actual earnings
- "You would have earned $X more with Pro this month" messaging

---

### Technical Questions

#### 1. **Content Quality**: Filter low-quality content from pool?

**Recommendation: YES - Implement quality filters with transparency**

**Minimum Quality Standards:**
- **Word Count**: Minimum 300 words (filters out spam, low-effort content)
- **Verification Count**: At least 1 verification (proves content is being used)
- **Content Type**: Must be article, blog, or social_post (no test files, lorem ipsum)
- **Tamper Detection**: No tampering detected (maintains C2PA integrity)
- **Freshness**: Content <2 years old (unless high verification count)

**Quality Tiers (for AI company filtering):**
- **Premium Pool**: >1000 words, >10 verifications, <90 days old
- **Standard Pool**: >300 words, >1 verification, <1 year old
- **Archive Pool**: All other qualifying content

**AI companies can choose:**
- Premium only (higher price)
- Premium + Standard (standard price)
- All pools (discounted price)

**Transparency:**
- Dashboard shows content quality score
- Explains why content is/isn't in premium pool
- Provides tips to improve quality score
- No content is excluded entirely (just tiered)

**Expected Impact:**
- AI company satisfaction: Higher (better content quality)
- Member engagement: Higher (gamification of quality)
- Coalition reputation: Stronger (known for quality)

---

#### 2. **Scalability**: Can we handle 100K+ members at launch?

**Recommendation: YES - With proper architecture**

**Database Optimization:**
- **Partitioning**: Partition `content_access_logs` by month (prevents table bloat)
- **Indexing**: Composite indexes on `(member_id, accessed_at)`, `(agreement_id, accessed_at)`
- **Archiving**: Move logs >6 months to cold storage (S3/Glacier)

**Caching Strategy:**
- **Redis**: Cache coalition stats (TTL: 5 minutes)
- **CDN**: Cache public coalition data (member count, pool size)
- **Materialized Views**: Pre-calculate revenue distributions

**API Rate Limiting:**
- **Member API**: 100 requests/minute per user
- **AI Company API**: 10,000 requests/minute per agreement
- **Admin API**: 1,000 requests/minute

**Load Testing Targets:**
- **100K members**: 1,000 concurrent users
- **1M documents**: 10,000 accesses/second
- **Revenue calculation**: <30 seconds for 100K members

**Infrastructure:**
- **Database**: PostgreSQL with read replicas (3 replicas)
- **Application**: Horizontal scaling (10+ instances)
- **Queue**: Redis/RabbitMQ for async tasks (revenue calculation)

**Expected Performance:**
- API response time: <200ms P95
- Revenue calculation: <5 minutes for 100K members
- Dashboard load time: <2 seconds

---

#### 3. **Payment Methods**: Stripe only? PayPal? Bank transfer?

**Recommendation: Stripe primary, expand based on demand**

**Phase 1 (Launch): Stripe Only**
- **Rationale**: 
  - Fastest to implement
  - Best API/developer experience
  - Handles international payments
  - Supports ACH, cards, bank transfers
  - 2.9% + $0.30 fee (acceptable for $10+ payouts)

**Phase 2 (Month 3): Add PayPal**
- **Rationale**:
  - International users prefer PayPal
  - Lower fees for international transfers
  - Familiar to publishers
  - Easy integration (Stripe supports PayPal)

**Phase 3 (Month 6): Direct Bank Transfer**
- **Rationale**:
  - Large publishers want ACH/wire
  - Lower fees for $1,000+ payouts
  - Enterprise tier expectation
  - Requires more compliance work

**Phase 4 (Future): Cryptocurrency**
- **Rationale**:
  - International publishers avoid currency conversion
  - Lower fees for cross-border
  - Tech-savvy audience
  - Regulatory complexity (wait for clarity)

**Implementation Priority:**
1. Stripe (launch)
2. PayPal (if >20% of users request)
3. Bank transfer (if >10 enterprise users request)
4. Crypto (if regulatory clarity + demand)

---

#### 4. **API Rate Limits**: What limits for AI company access?

**Recommendation: Tiered rate limits based on agreement**

**Tier 1 (Major AI Labs): High Limits**
- **Rate Limit**: 100,000 requests/minute
- **Daily Quota**: 10M accesses/day
- **Burst**: 200,000 requests/minute for 1 minute
- **Rationale**: Massive training pipelines, need high throughput

**Tier 2 (Mid-Size): Medium Limits**
- **Rate Limit**: 10,000 requests/minute
- **Daily Quota**: 1M accesses/day
- **Burst**: 20,000 requests/minute for 1 minute
- **Rationale**: Smaller scale but still production workloads

**Tier 3 (Startups): Low Limits**
- **Rate Limit**: 1,000 requests/minute
- **Daily Quota**: 100K accesses/day
- **Burst**: 2,000 requests/minute for 1 minute
- **Rationale**: Research/development use cases

**Overage Handling:**
- **Soft Limit**: Warning at 80% of quota
- **Hard Limit**: 429 Too Many Requests (with retry-after header)
- **Overage Pricing**: $0.20 per 1K requests over quota (vs. $0.10 in plan)

**Monitoring:**
- Real-time dashboard showing usage
- Alerts at 50%, 80%, 100% of quota
- Automatic scaling recommendations

---

#### 5. **Data Retention**: How long to keep access logs?

**Recommendation: Tiered retention based on data type**

**Access Logs (content_access_logs):**
- **Hot Storage (PostgreSQL)**: 6 months
  - Fast queries for revenue calculation
  - Member analytics
  - Dispute resolution
  
- **Warm Storage (S3)**: 6 months - 2 years
  - Compressed JSON/Parquet
  - Queryable via Athena
  - Audit trail
  
- **Cold Storage (Glacier)**: 2-7 years
  - Compliance requirements
  - Legal discovery
  - Historical analysis

**Revenue Distributions:**
- **Forever** (legal requirement)
- Compressed after 2 years
- Archived to S3 after 5 years

**Member Data:**
- **Active Members**: Forever
- **Opted-Out Members**: 90 days (GDPR right to be forgotten)
- **Deleted Accounts**: 30 days (recovery period), then purged

**Content Metadata:**
- **Active Content**: Forever (while in pool)
- **Removed Content**: 90 days (dispute window)
- **Deleted Content**: Immediate purge (GDPR compliance)

**Compliance:**
- **GDPR**: Right to be forgotten (30-90 day purge)
- **CCPA**: Data export on request
- **SOX/Financial**: 7 years for revenue records
- **Legal Hold**: Indefinite retention if litigation

**Storage Costs (estimated):**
- Hot: $0.023/GB/month (PostgreSQL)
- Warm: $0.004/GB/month (S3 Standard)
- Cold: $0.001/GB/month (Glacier)

**Expected Volume:**
- 100K members × 1M accesses/month = 100B logs/month
- ~10GB/month hot storage
- ~100GB/year warm storage
- **Cost**: ~$50/month storage (negligible)

---

## Go/No-Go Criteria

### Launch Criteria
- [ ] Coalition Service deployed and tested
- [ ] Auto-enrollment working for free tier
- [ ] Content indexing operational
- [ ] Revenue calculation tested with 10K+ members
- [ ] Payment processing integrated (Stripe)
- [ ] Security audit passed
- [ ] Legal terms reviewed and approved
- [ ] At least 1 AI company pilot partner committed
- [ ] WordPress plugin coalition widget working
- [ ] Dashboard coalition tab functional

### Success Criteria (Post-Launch)
- [ ] 100% free tier enrollment within 30 days
- [ ] <2% opt-out rate
- [ ] First revenue distribution completed
- [ ] Member satisfaction >80%
- [ ] System uptime >99.9%
- [ ] <10 support tickets/week

---

## Resource Requirements

### Engineering
- **Backend**: 2 engineers (Coalition Service, Revenue Engine)
- **Frontend**: 1 engineer (Dashboard, WordPress)
- **DevOps**: 0.5 engineer (Deployment, monitoring)
- **QA**: 1 engineer (Testing, security)

### Product & Design
- **Product Manager**: 1 (Roadmap, requirements)
- **Designer**: 0.5 (UI/UX for dashboard and WordPress)

### Business
- **BD**: 1 (AI company partnerships)
- **Legal**: 0.5 (Terms, agreements)
- **Marketing**: 1 (Launch campaign)

---

## Related Documentation

### PRDs
- [PRD-001: Coalition Infrastructure](./PRD-001-Coalition-Infrastructure.md)
- [PRD-002: Licensing Agreement Management](./PRD-002-Licensing-Agreement-Management.md)
- [PRD-003: WordPress Coalition Integration](./PRD-003-WordPress-Coalition-Integration.md)
- [PRD-004: Dashboard Coalition Features](./PRD-004-Dashboard-Coalition-Features.md)

### Technical Docs
- [Enterprise API Documentation](../../enterprise_api/README.md)
- [Services Architecture](../../services/README.md)
- [Dashboard App Documentation](../../dashboard_app/README.md)
- [WordPress Plugin Documentation](../../integrations/wordpress-provenance-plugin/README.md)

### Business Docs
- Customer Journey: Small Publisher (TechCurrent)
- Customer Journey: Large Publisher (MetroDaily)
- Competitive Analysis: Content Licensing Platforms
- Market Research: AI Company Content Needs

---

## Appendix: Customer Journey Alignment

### Sarah's Journey (Small Publisher)
**Current Gap**: No coalition, no revenue, no value prop for Pro upgrade

**After Implementation**:
- ✅ Week 1: Auto-enrolled in coalition on signup (free tier, 65/35 split)
- ✅ Month 2: Sees $65 pending revenue in WordPress widget (65% of $100 pool contribution)
- ✅ Month 4: First $195 payout received (hit $50 threshold, 65% of $300)
- ✅ Month 6: Upgrades to Pro for better revenue split (70/30 vs 65/35)
- ✅ Year 1: Earns $16.8K from coalition licensing (70% of $24K pool contribution as Pro member)

### Jennifer's Journey (Large Publisher)
**Current Gap**: No formal notice system, no proactive licensing

**After Implementation**:
- ✅ Month 1: Uses Enterprise API for court case (existing)
- ✅ Month 8: Encypher proactively identifies AI company usage
- ✅ Month 9: Formal notice sent via coalition system
- ✅ Month 10: Licensing agreement negotiated
- ✅ Year 1: $30.5M benefit (legal savings + licensing revenue)

---

**Last Updated**: 2025-11-04  
**Next Review**: 2025-11-11  
**Status**: Ready for Engineering Review - Revenue Model Revised
