# PRD-001: Coalition Infrastructure & Auto-Onboarding

**Status**: Draft  
**Priority**: P0 (Critical)  
**Estimated Effort**: 4-6 weeks  
**Owner**: Backend Team  
**Created**: 2025-11-04  

---

## Executive Summary

Build the foundational coalition infrastructure that automatically onboards free tier users into a content licensing collective. This enables small publishers to pool their content for bulk licensing to AI companies, creating a revenue stream through an adtech-style aggregation model.

---

## Problem Statement

### Current State
- Free tier users get basic C2PA signing but no monetization path
- Small publishers lack leverage to negotiate with AI companies individually
- No infrastructure exists to aggregate content or distribute licensing revenue
- Missing the "network effect" value proposition that drives Pro tier upgrades

### Desired State
- All free tier users automatically join the coalition upon signup
- Coalition aggregates signed content from all members
- Bulk licensing deals with AI companies generate revenue
- Revenue distributed to members based on content usage (70/30 split: 70% to publishers, 30% to Encypher)
- Clear upgrade path to Pro tier for coalition benefits + additional features

---

## Goals & Success Metrics

### Primary Goals
1. **Auto-onboard 100% of free tier users** to coalition within 30 days of launch
2. **Aggregate content** from coalition members for licensing
3. **Enable bulk licensing** to AI companies with automated revenue distribution
4. **Drive Pro tier conversions** through coalition value proposition

### Success Metrics
| Metric | Target | Timeline |
|--------|--------|----------|
| Free tier coalition enrollment | 100% | Launch |
| Coalition content pool size | 1M+ signed documents | 90 days |
| First AI company licensing deal | 1 deal | 120 days |
| Revenue distributed to members | $10K+ | 180 days |
| Free → Pro conversion rate | 5% | 90 days |

---

## User Stories

### Story 1: Sarah (Small Publisher) - Auto-Onboarding
**As a** small publisher using the free tier  
**I want to** automatically join a coalition of content creators  
**So that** I can monetize my content through collective licensing without individual negotiations

**Acceptance Criteria:**
- [ ] Upon free tier signup, user is automatically enrolled in coalition
- [ ] User receives welcome email explaining coalition benefits
- [ ] User can view coalition membership status in dashboard
- [ ] User can opt-out of coalition (but loses free tier access)
- [ ] Coalition terms displayed during signup flow

### Story 2: Sarah - Revenue Tracking
**As a** coalition member  
**I want to** track my content's contribution to licensing deals  
**So that** I can see my potential revenue and understand the value

**Acceptance Criteria:**
- [ ] Dashboard shows "My Coalition Stats" widget
- [ ] Display: total signed documents, verification count, estimated value
- [ ] Show revenue share breakdown (70% to me, 30% to Encypher)
- [ ] Display pending and paid revenue
- [ ] Show which AI companies accessed my content

### Story 3: Enterprise Admin - Bulk Licensing
**As an** Encypher admin  
**I want to** create bulk licensing agreements with AI companies  
**So that** I can monetize coalition content and distribute revenue

**Acceptance Criteria:**
- [ ] Admin panel to create licensing agreements
- [ ] Define terms: price, duration, content scope, AI company
- [ ] Track content access by AI company
- [ ] Calculate revenue distribution automatically
- [ ] Generate invoices and payment records

---

## Technical Architecture

### System Components

#### 1. Coalition Service (New Microservice)
**Port**: 8009  
**Purpose**: Manage coalition membership, content aggregation, licensing agreements

**Endpoints:**
```
POST   /api/v1/coalition/join              # Auto-join on signup
POST   /api/v1/coalition/leave             # Opt-out (loses free tier)
GET    /api/v1/coalition/status            # Membership status
GET    /api/v1/coalition/stats             # User's coalition stats
GET    /api/v1/coalition/revenue           # Revenue breakdown
POST   /api/v1/coalition/agreements        # Admin: create agreement
GET    /api/v1/coalition/agreements        # List agreements
GET    /api/v1/coalition/content-pool      # Admin: view aggregated content
POST   /api/v1/coalition/track-access      # Track AI company access
```

**Database Schema:**
```sql
-- Coalition Members
CREATE TABLE coalition_members (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    organization_id UUID REFERENCES organizations(id),
    joined_at TIMESTAMP NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- active, opted_out
    tier VARCHAR(20) NOT NULL, -- free, pro, enterprise
    opt_out_reason TEXT,
    opted_out_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    UNIQUE(user_id)
);

-- Coalition Content (Aggregated signed content)
CREATE TABLE coalition_content (
    id UUID PRIMARY KEY,
    member_id UUID NOT NULL REFERENCES coalition_members(id),
    document_id UUID NOT NULL REFERENCES signed_documents(id),
    content_hash VARCHAR(64) NOT NULL,
    content_type VARCHAR(50), -- article, blog, social_post
    word_count INTEGER,
    signed_at TIMESTAMP NOT NULL,
    verification_count INTEGER DEFAULT 0,
    last_verified_at TIMESTAMP,
    indexed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(document_id)
);

-- Licensing Agreements (with AI companies)
CREATE TABLE licensing_agreements (
    id UUID PRIMARY KEY,
    agreement_name VARCHAR(255) NOT NULL,
    ai_company_name VARCHAR(255) NOT NULL,
    ai_company_id VARCHAR(255), -- External ID
    agreement_type VARCHAR(50) NOT NULL, -- bulk_access, per_document, subscription
    status VARCHAR(20) NOT NULL DEFAULT 'draft', -- draft, active, expired, terminated
    
    -- Financial terms
    total_value DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_frequency VARCHAR(20), -- monthly, quarterly, annual, one_time
    
    -- Content scope
    content_types TEXT[], -- ['article', 'blog']
    min_word_count INTEGER,
    date_range_start DATE,
    date_range_end DATE,
    
    -- Dates
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    signed_date DATE,
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Content Access Tracking (AI company usage)
CREATE TABLE content_access_logs (
    id UUID PRIMARY KEY,
    agreement_id UUID NOT NULL REFERENCES licensing_agreements(id),
    content_id UUID NOT NULL REFERENCES coalition_content(id),
    member_id UUID NOT NULL REFERENCES coalition_members(id),
    accessed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    access_type VARCHAR(50), -- training, inference, verification
    ai_company_name VARCHAR(255) NOT NULL,
    metadata JSONB
);

-- Revenue Distribution
CREATE TABLE revenue_distributions (
    id UUID PRIMARY KEY,
    agreement_id UUID NOT NULL REFERENCES licensing_agreements(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_revenue DECIMAL(12,2) NOT NULL,
    encypher_share DECIMAL(12,2) NOT NULL, -- 30%
    member_pool DECIMAL(12,2) NOT NULL, -- 70%
    
    -- Distribution calculation
    total_content_count INTEGER NOT NULL,
    total_access_count INTEGER NOT NULL,
    calculation_method VARCHAR(50), -- equal_split, usage_based, weighted
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, calculated, paid
    calculated_at TIMESTAMP,
    paid_at TIMESTAMP,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Member Revenue (Individual payouts)
CREATE TABLE member_revenue (
    id UUID PRIMARY KEY,
    distribution_id UUID NOT NULL REFERENCES revenue_distributions(id),
    member_id UUID NOT NULL REFERENCES coalition_members(id),
    
    -- Content contribution
    content_count INTEGER NOT NULL,
    access_count INTEGER NOT NULL,
    contribution_percentage DECIMAL(5,2) NOT NULL,
    
    -- Revenue
    revenue_amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Payment
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, paid, failed
    payment_method VARCHAR(50),
    payment_reference VARCHAR(255),
    paid_at TIMESTAMP,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Coalition Settings
CREATE TABLE coalition_settings (
    id UUID PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Initial settings
INSERT INTO coalition_settings (id, setting_key, setting_value, description) VALUES
(gen_random_uuid(), 'revenue_split', '{"encypher": 30, "members": 70}', 'Revenue split percentage'),
(gen_random_uuid(), 'auto_onboard_free_tier', 'true', 'Automatically onboard free tier users'),
(gen_random_uuid(), 'min_payout_threshold', '{"amount": 10, "currency": "USD"}', 'Minimum payout amount');
```

#### 2. Auth Service Integration
**Changes Required:**
- Add coalition auto-enrollment to signup flow
- Create coalition membership record on free tier user creation
- Add coalition status to user profile

**Modified Endpoint:**
```python
# auth-service/app/api/v1/endpoints.py
@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Existing user creation logic
    user = AuthService.create_user(db, user_data)
    
    # NEW: Auto-enroll in coalition if free tier
    if user_data.tier == "free":
        await CoalitionService.auto_enroll_member(
            user_id=user.id,
            tier="free"
        )
    
    return user
```

#### 3. Enterprise API Integration
**Changes Required:**
- Track signed documents for coalition members
- Index content in coalition_content table
- Expose coalition stats in dashboard endpoint

**New Endpoint:**
```python
# enterprise_api/app/api/v1/endpoints/coalition.py
@router.get("/coalition/stats", response_model=CoalitionStatsResponse)
async def get_coalition_stats(
    org: Organization = Depends(require_permission("can_view_stats"))
):
    """Get user's coalition statistics"""
    stats = await CoalitionService.get_member_stats(org.id)
    return stats
```

#### 4. Dashboard App Integration
**Frontend Changes:**
- Add "Coalition" tab to dashboard
- Display coalition stats widget on home page
- Show revenue tracking panel
- Add coalition settings page

**Backend Changes:**
- Proxy coalition API calls
- Add coalition revenue endpoints
- Display coalition membership status

---

## Data Flow

### 1. Auto-Onboarding Flow
```
User Signup (Free Tier)
    ↓
Auth Service creates user
    ↓
Coalition Service auto-enrolls
    ↓
Welcome email sent
    ↓
Coalition membership active
```

### 2. Content Indexing Flow
```
User signs document via Enterprise API
    ↓
Document stored in signed_documents table
    ↓
Coalition Service indexes document
    ↓
Document added to coalition_content pool
    ↓
Content available for licensing
```

### 3. Revenue Distribution Flow
```
AI Company accesses content
    ↓
Access logged in content_access_logs
    ↓
Monthly: Calculate revenue distribution
    ↓
Split: 30% Encypher, 70% member pool
    ↓
Distribute to members based on usage
    ↓
Generate payment records
    ↓
Process payouts (>$10 threshold)
```

---

## API Specifications

### Coalition Service API

#### POST /api/v1/coalition/join
**Description**: Manually join coalition (or auto-join on signup)

**Request:**
```json
{
  "user_id": "uuid",
  "tier": "free",
  "accept_terms": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "member_id": "uuid",
    "joined_at": "2025-01-04T10:00:00Z",
    "status": "active",
    "tier": "free"
  }
}
```

#### GET /api/v1/coalition/stats
**Description**: Get member's coalition statistics

**Response:**
```json
{
  "success": true,
  "data": {
    "member_id": "uuid",
    "status": "active",
    "joined_at": "2025-01-04T10:00:00Z",
    "content_stats": {
      "total_documents": 42,
      "total_word_count": 15000,
      "verification_count": 128,
      "last_signed": "2025-01-04T09:30:00Z"
    },
    "revenue_stats": {
      "total_earned": 487.50,
      "pending": 125.00,
      "paid": 362.50,
      "currency": "USD",
      "next_payout_date": "2025-02-01"
    },
    "coalition_stats": {
      "total_members": 1250,
      "total_content_pool": 125000,
      "active_agreements": 3
    }
  }
}
```

#### GET /api/v1/coalition/revenue
**Description**: Get detailed revenue breakdown

**Response:**
```json
{
  "success": true,
  "data": {
    "total_earned": 487.50,
    "currency": "USD",
    "distributions": [
      {
        "period": "2024-12",
        "amount": 125.00,
        "status": "pending",
        "agreement_name": "OpenAI Training License",
        "content_accessed": 15,
        "access_count": 45
      },
      {
        "period": "2024-11",
        "amount": 362.50,
        "status": "paid",
        "paid_at": "2024-12-05T10:00:00Z",
        "payment_method": "stripe",
        "payment_reference": "pi_abc123"
      }
    ]
  }
}
```

---

## WordPress Plugin Integration

### Coalition Widget
Add coalition stats widget to WordPress admin dashboard:

```php
// includes/class-encypher-provenance-coalition.php
class Encypher_Provenance_Coalition {
    public function render_coalition_widget() {
        $stats = $this->get_coalition_stats();
        ?>
        <div class="encypher-coalition-widget">
            <h3>Coalition Membership</h3>
            <div class="coalition-stats">
                <div class="stat">
                    <span class="label">Signed Posts:</span>
                    <span class="value"><?php echo $stats['total_documents']; ?></span>
                </div>
                <div class="stat">
                    <span class="label">Verifications:</span>
                    <span class="value"><?php echo $stats['verification_count']; ?></span>
                </div>
                <div class="stat">
                    <span class="label">Revenue Earned:</span>
                    <span class="value">$<?php echo number_format($stats['total_earned'], 2); ?></span>
                </div>
            </div>
            <a href="<?php echo admin_url('admin.php?page=encypher-coalition'); ?>" class="button">
                View Coalition Dashboard
            </a>
        </div>
        <?php
    }
}
```

---

## Security & Privacy

### Data Protection
- **Content Privacy**: Only metadata indexed, not full content
- **Anonymization**: AI companies see aggregated pool, not individual publishers
- **Opt-out**: Users can leave coalition (but lose free tier)
- **Data Retention**: Content removed from pool if user opts out

### Access Control
- **Member Access**: View own stats only
- **Admin Access**: View all coalition data, create agreements
- **AI Company Access**: Only licensed content, tracked access

### Compliance
- **GDPR**: Right to be forgotten (opt-out removes content)
- **CCPA**: Disclosure of data sharing with AI companies
- **Terms of Service**: Coalition terms in signup flow

---

## Rollout Plan

### Phase 1: Foundation (Weeks 1-2)
- [ ] Create coalition-service microservice
- [ ] Implement database schema
- [ ] Build core API endpoints (join, stats, revenue)
- [ ] Add auto-enrollment to auth-service

### Phase 2: Content Indexing (Weeks 3-4)
- [ ] Integrate with enterprise_api signing flow
- [ ] Index signed documents in coalition_content
- [ ] Build content aggregation logic
- [ ] Create admin panel for content pool view

### Phase 3: Licensing Infrastructure (Weeks 5-6)
- [ ] Build licensing agreement management
- [ ] Implement content access tracking
- [ ] Create revenue distribution calculator
- [ ] Build payout processing

### Phase 4: UI Integration (Weeks 7-8) ✅ COMPLETE
- [x] Add coalition tab to dashboard (PRD-004 implemented)
- [x] Build coalition stats widgets (dashboard_app/frontend)
- [x] Create revenue tracking UI (RevenueChart, ContentPerformanceTable, AccessLogsTable)
- [x] WordPress plugin coalition widget (PRD-003 implemented)

### Phase 5: Testing & Launch (Weeks 9-10) 🚧 IN PROGRESS
- [x] End-to-end testing (test_coalition_flow.py created)
- [x] Backend API tests (test_coalition_api_async.py created)
- [x] Frontend component tests (CoalitionPage.test.tsx created)
- [x] Load testing preparation (test_coalition_load.py created)
- [x] Security audit checklist (COALITION_SECURITY_AUDIT.md created)
- [ ] Run load tests with 10K+ members (requires infrastructure)
- [ ] Complete security audit (checklist ready)
- [ ] Soft launch to 100 beta users (pending backend deployment)
- [ ] Full launch (pending all tests passing)

---

## Dependencies

### Technical Dependencies
- **auth-service**: User management, signup flow
- **enterprise_api**: Document signing, content tracking
- **dashboard_app**: UI for coalition stats
- **wordpress-plugin**: Coalition widget

### External Dependencies
- **Payment Processor**: Stripe/PayPal for payouts
- **Email Service**: SendGrid for notifications
- **Analytics**: Track coalition engagement

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Low adoption rate | High | Medium | Auto-enrollment ensures 100% free tier participation |
| No AI company deals | High | Medium | Proactive outreach, competitive pricing, start with pilot deals |
| Revenue distribution disputes | Medium | Low | Transparent tracking, clear terms, audit trail |
| Opt-out rate too high | Medium | Low | Demonstrate value early, show revenue potential |
| Scalability issues | Medium | Low | Design for 100K+ members from start |

---

## Open Questions

1. **Revenue Split**: Is 70/30 the right split? Should Pro tier get better split (e.g., 80/20)?
2. **Distribution Method**: Equal split vs. usage-based vs. weighted by content quality?
3. **Minimum Payout**: $10 threshold? Or accumulate until $50?
4. **Payment Methods**: Stripe only? PayPal? Crypto?
5. **AI Company Onboarding**: How do we attract first AI company partner?
6. **Content Quality**: Should we filter low-quality content from coalition pool?

---

## Success Criteria

### Launch Criteria (Go/No-Go)
- [ ] 100% of new free tier signups auto-enrolled
- [ ] Coalition stats API returns data in <200ms
- [ ] Revenue distribution calculator tested with 10K+ members
- [ ] WordPress plugin displays coalition widget
- [ ] Security audit passed
- [ ] Legal terms reviewed and approved

### Post-Launch Success (90 Days)
- [ ] 1,000+ coalition members
- [ ] 50,000+ signed documents in pool
- [ ] 1 AI company licensing agreement signed
- [ ] First revenue distribution completed
- [ ] 5% free → Pro conversion rate
- [ ] <2% opt-out rate

---

## Related PRDs
- **PRD-002**: Licensing Agreement Management
- **PRD-003**: AI Company Integration Portal
- **PRD-004**: Revenue Distribution Engine
- **PRD-005**: Coalition Analytics Dashboard
