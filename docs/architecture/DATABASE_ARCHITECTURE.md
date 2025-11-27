# EncypherAI Database Architecture

## Overview

EncypherAI uses a **two-database architecture** with Redis caching:

| Database | Purpose | Services |
|----------|---------|----------|
| **postgres-core** | Authentication, Users, Organizations, API Keys, Billing | auth-service, key-service, billing-service, user-service |
| **postgres-content** | Content operations, Verification, Analytics, Coalition | encoding-service, verification-service, analytics-service, coalition-service |
| **Redis** | Caching, Sessions, Rate Limiting | All services |

## Design Principles

1. **Database per Domain** - Not per service, but per domain boundary
2. **Shared Tables via Views** - Services that need cross-domain data use read-only views
3. **Event-Driven Sync** - Changes propagate via events, not direct DB access
4. **Each Service Owns Its Tables** - Migrations are service-specific

---

## postgres-core (Core Business Data)

### Owned by: auth-service

```sql
-- Users table (source of truth for identity)
CREATE TABLE users (
    id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),  -- NULL for OAuth-only users
    name VARCHAR(255),
    avatar_url VARCHAR(500),
    
    -- Email verification
    email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMPTZ,
    
    -- OAuth providers
    google_id VARCHAR(255) UNIQUE,
    github_id VARCHAR(255) UNIQUE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Refresh tokens (auth-service only)
CREATE TABLE refresh_tokens (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMPTZ,
    user_agent VARCHAR(500),
    ip_address VARCHAR(45)
);

-- Password reset tokens
CREATE TABLE password_reset_tokens (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMPTZ
);

-- Email verification tokens
CREATE TABLE email_verification_tokens (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
```

### Owned by: key-service (but in postgres-core)

```sql
-- Organizations (billing entity)
CREATE TABLE organizations (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    
    -- Subscription tier
    tier VARCHAR(32) NOT NULL DEFAULT 'starter',
    
    -- Stripe integration
    stripe_customer_id VARCHAR(255) UNIQUE,
    stripe_subscription_id VARCHAR(255),
    subscription_status VARCHAR(32) DEFAULT 'active',
    
    -- Feature flags (JSONB for flexibility)
    features JSONB DEFAULT '{}',
    
    -- Usage quotas
    monthly_api_limit INTEGER DEFAULT 10000,
    monthly_api_usage INTEGER DEFAULT 0,
    
    -- Coalition settings
    coalition_member BOOLEAN DEFAULT TRUE,
    coalition_rev_share INTEGER DEFAULT 65,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Organization members (links users to orgs)
CREATE TABLE organization_members (
    id VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(32) NOT NULL DEFAULT 'member',  -- owner, admin, member
    invited_by VARCHAR(64),
    invited_at TIMESTAMPTZ,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(organization_id, user_id)
);

-- API Keys
CREATE TABLE api_keys (
    id VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    key_prefix VARCHAR(20) NOT NULL,
    
    -- Permissions
    permissions JSONB DEFAULT '["sign", "verify", "lookup"]',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_revoked BOOLEAN DEFAULT FALSE,
    
    -- Usage
    last_used_at TIMESTAMPTZ,
    usage_count INTEGER DEFAULT 0,
    
    -- Lifecycle
    created_by VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    revoked_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    
    description TEXT
);

CREATE INDEX idx_api_keys_org ON api_keys(organization_id);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_org_members_org ON organization_members(organization_id);
CREATE INDEX idx_org_members_user ON organization_members(user_id);
```

### Owned by: billing-service (but in postgres-core)

```sql
-- Subscriptions
CREATE TABLE subscriptions (
    id VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    plan_id VARCHAR(64) NOT NULL,
    plan_name VARCHAR(100) NOT NULL,
    status VARCHAR(32) NOT NULL,  -- active, canceled, past_due, trialing
    
    billing_cycle VARCHAR(20) NOT NULL,  -- monthly, yearly
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    current_period_start TIMESTAMPTZ NOT NULL,
    current_period_end TIMESTAMPTZ NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    canceled_at TIMESTAMPTZ,
    
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Invoices
CREATE TABLE invoices (
    id VARCHAR(64) PRIMARY KEY,
    subscription_id VARCHAR(64) REFERENCES subscriptions(id),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id),
    
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(32) NOT NULL,  -- draft, open, paid, void
    
    amount_due DECIMAL(10,2) NOT NULL,
    amount_paid DECIMAL(10,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    due_date TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    
    stripe_invoice_id VARCHAR(255) UNIQUE,
    line_items JSONB,
    metadata JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Payments
CREATE TABLE payments (
    id VARCHAR(64) PRIMARY KEY,
    invoice_id VARCHAR(64) REFERENCES invoices(id),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id),
    
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(32) NOT NULL,  -- succeeded, failed, pending, refunded
    
    payment_method VARCHAR(50),
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    
    failure_message TEXT,
    metadata JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_org ON subscriptions(organization_id);
CREATE INDEX idx_invoices_org ON invoices(organization_id);
CREATE INDEX idx_payments_org ON payments(organization_id);
```

---

## postgres-content (Content & Analytics Data)

### Owned by: encoding-service

```sql
-- Encoded documents (C2PA manifests)
CREATE TABLE encoded_documents (
    id VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL,
    
    document_id VARCHAR(64) NOT NULL UNIQUE,
    content_hash VARCHAR(64) NOT NULL,
    
    -- Signature info
    signature TEXT NOT NULL,
    signer_id VARCHAR(64) NOT NULL,
    signing_key_id VARCHAR(64),
    
    -- Manifest (C2PA)
    manifest JSONB NOT NULL,
    
    -- Metadata
    format VARCHAR(50) DEFAULT 'text',
    encoding_method VARCHAR(50) DEFAULT 'unicode',
    word_count INTEGER,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Signing operations audit log
CREATE TABLE signing_operations (
    id VARCHAR(64) PRIMARY KEY,
    document_id VARCHAR(64) NOT NULL,
    organization_id VARCHAR(64) NOT NULL,
    
    operation_type VARCHAR(50) NOT NULL,  -- sign, embed, verify
    status VARCHAR(20) NOT NULL,  -- success, failed
    error_message TEXT,
    
    processing_time_ms INTEGER,
    content_size_bytes INTEGER,
    
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_encoded_docs_org ON encoded_documents(organization_id);
CREATE INDEX idx_encoded_docs_hash ON encoded_documents(content_hash);
CREATE INDEX idx_signing_ops_doc ON signing_operations(document_id);
CREATE INDEX idx_signing_ops_created ON signing_operations(created_at);
```

### Owned by: verification-service

```sql
-- Verification results
CREATE TABLE verification_results (
    id VARCHAR(64) PRIMARY KEY,
    document_id VARCHAR(64) NOT NULL,
    organization_id VARCHAR(64),
    
    is_valid BOOLEAN NOT NULL,
    is_tampered BOOLEAN DEFAULT FALSE,
    signature_valid BOOLEAN NOT NULL,
    hash_valid BOOLEAN NOT NULL,
    
    confidence_score DECIMAL(5,4) DEFAULT 0,
    similarity_score DECIMAL(5,4),
    
    content_hash VARCHAR(64) NOT NULL,
    signature TEXT NOT NULL,
    signer_id VARCHAR(64),
    
    verification_method VARCHAR(50) DEFAULT 'signature',
    error_message TEXT,
    warnings JSONB,
    
    verification_time_ms INTEGER,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_verification_doc ON verification_results(document_id);
CREATE INDEX idx_verification_created ON verification_results(created_at);
```

### Owned by: analytics-service

```sql
-- Usage metrics (raw events)
CREATE TABLE usage_metrics (
    id VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64),
    
    metric_type VARCHAR(50) NOT NULL,  -- api_call, document_signed, verification
    service_name VARCHAR(50) NOT NULL,
    endpoint VARCHAR(255),
    
    count INTEGER DEFAULT 1,
    value DECIMAL(10,2),
    
    response_time_ms INTEGER,
    status_code INTEGER,
    
    metadata JSONB,
    
    -- Partitioning keys
    date DATE NOT NULL,
    hour INTEGER NOT NULL,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (date);

-- Aggregated metrics (pre-computed)
CREATE TABLE aggregated_metrics (
    id VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(64),
    
    metric_type VARCHAR(50) NOT NULL,
    service_name VARCHAR(50) NOT NULL,
    aggregation_period VARCHAR(20) NOT NULL,  -- hourly, daily, weekly, monthly
    
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    
    total_count INTEGER DEFAULT 0,
    total_value DECIMAL(12,2),
    avg_response_time_ms DECIMAL(10,2),
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    metadata JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_usage_metrics_org_date ON usage_metrics(organization_id, date);
CREATE INDEX idx_aggregated_org_period ON aggregated_metrics(organization_id, period_start);
```

### Owned by: coalition-service

```sql
-- Coalition members
CREATE TABLE coalition_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id VARCHAR(64) NOT NULL UNIQUE,
    
    status VARCHAR(20) DEFAULT 'active',  -- active, opted_out
    tier VARCHAR(20) NOT NULL,
    
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    opted_out_at TIMESTAMPTZ,
    opt_out_reason TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Coalition content index
CREATE TABLE coalition_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID NOT NULL REFERENCES coalition_members(id),
    document_id VARCHAR(64) NOT NULL UNIQUE,
    content_hash VARCHAR(64) NOT NULL,
    
    content_type VARCHAR(50),
    word_count INTEGER,
    
    signed_at TIMESTAMPTZ NOT NULL,
    verification_count INTEGER DEFAULT 0,
    last_verified_at TIMESTAMPTZ,
    
    indexed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Licensing agreements
CREATE TABLE licensing_agreements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agreement_name VARCHAR(255) NOT NULL,
    ai_company_name VARCHAR(255) NOT NULL,
    agreement_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    
    total_value DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Revenue distributions
CREATE TABLE revenue_distributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agreement_id UUID NOT NULL REFERENCES licensing_agreements(id),
    
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    total_revenue DECIMAL(12,2) NOT NULL,
    encypher_share DECIMAL(12,2) NOT NULL,
    member_pool DECIMAL(12,2) NOT NULL,
    
    status VARCHAR(20) DEFAULT 'pending',
    calculated_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Member revenue (payouts)
CREATE TABLE member_revenue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    distribution_id UUID NOT NULL REFERENCES revenue_distributions(id),
    member_id UUID NOT NULL REFERENCES coalition_members(id),
    
    content_count INTEGER NOT NULL,
    access_count INTEGER NOT NULL,
    contribution_percentage DECIMAL(5,2) NOT NULL,
    
    revenue_amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    status VARCHAR(20) DEFAULT 'pending',
    paid_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_coalition_members_org ON coalition_members(organization_id);
CREATE INDEX idx_coalition_content_member ON coalition_content(member_id);
CREATE INDEX idx_coalition_content_hash ON coalition_content(content_hash);
```

---

## Redis Cache Structure

```
# Session tokens (auth-service)
session:{user_id} -> JWT token (TTL: 15min)

# Rate limiting
ratelimit:{api_key_id}:{endpoint} -> count (TTL: 1min)
ratelimit:org:{org_id}:{endpoint} -> count (TTL: 1min)

# API key cache
apikey:{key_hash} -> {org_id, permissions, is_active} (TTL: 5min)

# Organization cache
org:{org_id} -> {tier, features, quotas} (TTL: 5min)

# Verification cache
verification:{content_hash} -> {is_valid, signer_id, verified_at} (TTL: 1hour)

# Usage counters (real-time)
usage:{org_id}:{date}:api_calls -> count
usage:{org_id}:{date}:documents -> count
```

---

## Migration Strategy

Each service manages its own migrations via Alembic:

```
services/
├── auth-service/
│   └── alembic/
│       └── versions/
│           ├── 001_initial_schema.py
│           ├── 002_add_tier_to_users.py
│           └── 003_add_token_column.py
├── key-service/
│   └── alembic/
│       └── versions/
│           ├── 001_organizations.py
│           └── 002_api_keys.py
├── billing-service/
│   └── alembic/
│       └── versions/
│           └── 001_subscriptions_invoices.py
...
```

### Running Migrations

```bash
# Each service runs migrations on startup
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app ..."]
```

---

## Environment Variables

```bash
# postgres-core
DATABASE_URL=postgresql://user:pass@postgres-core:5432/core

# postgres-content  
CONTENT_DATABASE_URL=postgresql://user:pass@postgres-content:5432/content

# Redis
REDIS_URL=redis://redis:6379/0
```

---

## Cross-Service Data Access

Services should **NOT** directly query other services' tables. Instead:

1. **API Calls** - Call the owning service's API
2. **Events** - Publish/subscribe via Redis or message queue
3. **Read Replicas** - For analytics, use read-only views

Example: `encoding-service` needs organization tier:
```python
# ❌ Wrong - direct DB access
org = db.query(Organization).filter_by(id=org_id).first()

# ✅ Right - API call to key-service
org = await key_service_client.get_organization(org_id)

# ✅ Right - Cached lookup
org = await redis.get(f"org:{org_id}")
```
