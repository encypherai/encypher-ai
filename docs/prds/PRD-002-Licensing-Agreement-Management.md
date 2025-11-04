# PRD-002: Licensing Agreement Management System

**Status**: Draft  
**Priority**: P0 (Critical)  
**Estimated Effort**: 3-4 weeks  
**Owner**: Backend Team  
**Created**: 2025-11-04  
**Depends On**: PRD-001 (Coalition Infrastructure)

---

## Executive Summary

Build a comprehensive licensing agreement management system that enables Encypher to create, manage, and track bulk licensing deals with AI companies. This system automates revenue tracking, content access monitoring, and payment distribution to coalition members.

---

## Problem Statement

### Current State
- No infrastructure to create licensing agreements with AI companies
- No way to track which AI companies access which content
- No automated revenue calculation or distribution
- Manual negotiation and tracking would not scale

### Desired State
- Self-service agreement creation for admins
- Automated content access tracking via API
- Real-time revenue calculation based on usage
- Automated payment distribution to coalition members
- Transparent reporting for all stakeholders

---

## Goals & Success Metrics

### Primary Goals
1. **Enable bulk licensing** to AI companies with clear terms
2. **Track content access** in real-time for accurate revenue attribution
3. **Automate revenue distribution** to eliminate manual calculations
4. **Provide transparency** to coalition members on their earnings

### Success Metrics
| Metric | Target | Timeline |
|--------|--------|----------|
| First licensing agreement created | 1 | 30 days |
| AI companies onboarded | 3 | 90 days |
| Content access events tracked | 100K+ | 90 days |
| Revenue distributions processed | 1 | 60 days |

---

## Technical Architecture

### System Components

#### 1. Licensing Service (Part of Coalition Service)
**Purpose**: Manage licensing agreements, track access, calculate revenue

**Key Endpoints:**
```
# Agreement Management (Admin only)
POST   /api/v1/licensing/agreements          # Create agreement
GET    /api/v1/licensing/agreements          # List agreements
GET    /api/v1/licensing/agreements/:id      # Get agreement details
PATCH  /api/v1/licensing/agreements/:id      # Update agreement
DELETE /api/v1/licensing/agreements/:id      # Terminate agreement

# AI Company Access (AI company API key)
GET    /api/v1/licensing/content             # List available content
GET    /api/v1/licensing/content/:id         # Get content details
POST   /api/v1/licensing/track-access        # Track content access

# Revenue Management (Admin only)
POST   /api/v1/licensing/distributions       # Create revenue distribution
GET    /api/v1/licensing/distributions       # List distributions
POST   /api/v1/licensing/payouts             # Process payouts
```

#### 2. Database Schema

**Key Tables:**
```sql
-- AI Company Profiles
CREATE TABLE ai_companies (
    id UUID PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL UNIQUE,
    company_email VARCHAR(255) NOT NULL,
    api_key_hash VARCHAR(255) NOT NULL UNIQUE,
    api_key_prefix VARCHAR(20),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Licensing Agreements
CREATE TABLE licensing_agreements (
    id UUID PRIMARY KEY,
    agreement_name VARCHAR(255) NOT NULL,
    ai_company_id UUID REFERENCES ai_companies(id),
    agreement_type VARCHAR(50) NOT NULL,
    total_value DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    content_types TEXT[],
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Content Access Tracking
CREATE TABLE content_access_logs (
    id UUID PRIMARY KEY,
    agreement_id UUID NOT NULL REFERENCES licensing_agreements(id),
    content_id UUID NOT NULL REFERENCES coalition_content(id),
    member_id UUID NOT NULL REFERENCES coalition_members(id),
    accessed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    access_type VARCHAR(50),
    ai_company_name VARCHAR(255) NOT NULL
);

-- Revenue Distribution
CREATE TABLE revenue_distributions (
    id UUID PRIMARY KEY,
    agreement_id UUID NOT NULL REFERENCES licensing_agreements(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_revenue DECIMAL(12,2) NOT NULL,
    encypher_share DECIMAL(12,2) NOT NULL,
    member_pool DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Member Revenue (Individual payouts)
CREATE TABLE member_revenue (
    id UUID PRIMARY KEY,
    distribution_id UUID NOT NULL REFERENCES revenue_distributions(id),
    member_id UUID NOT NULL REFERENCES coalition_members(id),
    content_count INTEGER NOT NULL,
    access_count INTEGER NOT NULL,
    revenue_amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    paid_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

#### 3. Revenue Distribution Algorithm

**Method**: Usage-Based Distribution

```python
def calculate_revenue_distribution(period_start, period_end):
    # 1. Get all active agreements for period
    agreements = get_active_agreements(period_start, period_end)
    total_revenue = sum(a.monthly_value for a in agreements)
    
    # 2. Calculate split
    encypher_share = total_revenue * 0.30  # 30%
    member_pool = total_revenue * 0.70     # 70%
    
    # 3. Get all content access logs
    access_logs = get_access_logs(period_start, period_end)
    total_access_count = len(access_logs)
    
    # 4. Calculate member contributions
    member_contributions = {}
    for log in access_logs:
        member_id = log.member_id
        if member_id not in member_contributions:
            member_contributions[member_id] = {
                "access_count": 0,
                "content_ids": set()
            }
        member_contributions[member_id]["access_count"] += 1
        member_contributions[member_id]["content_ids"].add(log.content_id)
    
    # 5. Distribute based on usage
    for member_id, contribution in member_contributions.items():
        contribution_percentage = (
            contribution["access_count"] / total_access_count * 100
        )
        revenue_amount = member_pool * (contribution_percentage / 100)
        
        create_member_revenue(
            member_id=member_id,
            revenue_amount=revenue_amount,
            access_count=contribution["access_count"],
            content_count=len(contribution["content_ids"])
        )
```

#### 4. API Key Management

**Generation:**
- Cryptographically secure random keys (32 bytes)
- Prefix: `lic_` for easy identification
- Stored as bcrypt hash in database
- Only shown once during creation

**Authentication:**
```python
async def verify_ai_company_api_key(authorization: str):
    # Extract key from "Bearer lic_abc123..."
    api_key = authorization.replace("Bearer ", "")
    
    # Hash and lookup
    for company in ai_companies:
        if bcrypt.verify(api_key, company.api_key_hash):
            return company
    
    raise HTTPException(status_code=401, detail="Invalid API key")
```

#### 5. Content Access Flow

```
AI Company Request
    ↓
Verify API Key
    ↓
Check Agreement Status (active?)
    ↓
Check Usage Quota (not exceeded?)
    ↓
Query Coalition Content Pool
    ↓
Return Content Metadata
    ↓
Log Access Event (async)
    ↓
Update Usage Quota
```

---

## API Specifications

### Create Licensing Agreement

**POST /api/v1/licensing/agreements**

**Request:**
```json
{
  "agreement_name": "OpenAI Training License Q1 2025",
  "ai_company_name": "OpenAI",
  "ai_company_email": "licensing@openai.com",
  "agreement_type": "subscription",
  "total_value": 50000.00,
  "currency": "USD",
  "start_date": "2025-01-01",
  "end_date": "2025-03-31",
  "content_types": ["article", "blog"],
  "min_word_count": 500
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "agreement_name": "OpenAI Training License Q1 2025",
    "api_key": "lic_abc123...",
    "api_key_prefix": "lic_abc1",
    "status": "active",
    "created_at": "2025-01-04T10:00:00Z"
  }
}
```

### List Available Content (AI Company)

**GET /api/v1/licensing/content**

**Headers:**
```
Authorization: Bearer lic_abc123...
```

**Query Parameters:**
- `content_type`: Filter by type
- `min_word_count`: Minimum word count
- `limit`: Results per page (default: 100)
- `offset`: Pagination offset

**Response:**
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "id": "uuid",
        "content_type": "article",
        "word_count": 1500,
        "signed_at": "2025-01-03T10:00:00Z",
        "content_hash": "sha256:abc123...",
        "verification_url": "https://api.encypherai.com/verify/abc123"
      }
    ],
    "total": 1250,
    "quota_remaining": 95000
  }
}
```

---

## Security Considerations

### API Key Security
- Keys hashed with bcrypt (never stored in plaintext)
- Only shown once during creation
- Automatic rotation support
- Immediate revocation on agreement termination

### Access Control
- Admin-only agreement management
- AI company access limited to licensed content
- Rate limiting per agreement
- All access logged with timestamps

### Data Privacy
- Only metadata exposed via API (not full content)
- AI companies see aggregated pool, not individual publishers
- GDPR-compliant data handling

---

## Rollout Plan

### Week 1-2: Core Infrastructure
- [ ] Database schema implementation
- [ ] Agreement CRUD endpoints
- [ ] AI company profile management
- [ ] API key generation and authentication

### Week 3: Content Access
- [ ] Content listing endpoint
- [ ] Access tracking system
- [ ] Usage quota enforcement
- [ ] Rate limiting implementation

### Week 4: Revenue Distribution
- [ ] Revenue calculation engine
- [ ] Distribution algorithm implementation
- [ ] Stripe payment integration
- [ ] Email notifications

---

## Related PRDs
- **PRD-001**: Coalition Infrastructure
- **PRD-003**: AI Company Integration Portal
- **PRD-004**: Revenue Distribution Engine
