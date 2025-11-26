-- ============================================
-- ENCYPHER CORE DATABASE SCHEMA
-- Version: 1.0.0
-- Date: 2025-11-26
-- ============================================
-- 
-- This database stores sensitive customer/billing data:
-- - Organizations (billing entities)
-- - Users and authentication
-- - API keys
-- - Subscriptions and billing
-- - Audit logs
--
-- This data is SENSITIVE and requires authentication.
-- Separate from content/verification data for security.
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- CORE: ORGANIZATIONS
-- The primary billing and subscription entity
-- ============================================
CREATE TABLE IF NOT EXISTS organizations (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'org_' || substr(md5(random()::text), 1, 16),
    
    -- Identity
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    
    -- Subscription & Tier
    tier VARCHAR(32) NOT NULL DEFAULT 'starter'
        CHECK (tier IN ('starter', 'professional', 'business', 'enterprise', 'demo')),
    
    -- Stripe Integration
    stripe_customer_id VARCHAR(255) UNIQUE,
    stripe_subscription_id VARCHAR(255),
    subscription_status VARCHAR(32) DEFAULT 'active'
        CHECK (subscription_status IN ('active', 'past_due', 'canceled', 'trialing', 'paused')),
    
    -- Feature Flags (JSONB for flexibility, derived from tier)
    features JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Usage Limits (per billing period)
    monthly_api_limit INTEGER DEFAULT 10000,  -- -1 = unlimited
    monthly_api_usage INTEGER DEFAULT 0,
    usage_reset_at TIMESTAMPTZ DEFAULT (date_trunc('month', NOW()) + INTERVAL '1 month'),
    
    -- Coalition Revenue Sharing
    coalition_member BOOLEAN DEFAULT TRUE,
    coalition_rev_share INTEGER DEFAULT 65 CHECK (coalition_rev_share BETWEEN 0 AND 100),
    coalition_opted_out BOOLEAN DEFAULT FALSE,
    coalition_opted_out_at TIMESTAMPTZ,
    
    -- Certificate Management (for C2PA signing)
    certificate_pem TEXT,
    certificate_chain TEXT,
    certificate_status VARCHAR(32) DEFAULT 'none'
        CHECK (certificate_status IN ('none', 'pending', 'active', 'expired', 'revoked')),
    certificate_expiry TIMESTAMPTZ,
    certificate_rotated_at TIMESTAMPTZ,  -- Last certificate rotation timestamp
    private_key_encrypted BYTEA,  -- AES-256 encrypted
    ssl_order_id VARCHAR(100),
    
    -- KMS Support (for BYOK)
    kms_key_id VARCHAR(255),
    kms_region VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_organizations_tier ON organizations(tier);
CREATE INDEX IF NOT EXISTS idx_organizations_stripe ON organizations(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_organizations_slug ON organizations(slug);

-- ============================================
-- CORE: USERS
-- Individual user accounts
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'user_' || substr(md5(random()::text), 1, 16),
    
    -- Identity
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),  -- NULL for OAuth-only users
    
    -- Profile
    name VARCHAR(255),
    avatar_url VARCHAR(500),
    
    -- Auth
    email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMPTZ,
    
    -- OAuth Providers
    google_id VARCHAR(255) UNIQUE,
    github_id VARCHAR(255) UNIQUE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================
-- CORE: ORGANIZATION MEMBERS
-- Links users to organizations with roles
-- ============================================
CREATE TABLE IF NOT EXISTS organization_members (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'mem_' || substr(md5(random()::text), 1, 16),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Role
    role VARCHAR(32) NOT NULL DEFAULT 'member'
        CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    
    -- Timestamps
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(organization_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_org_members_org ON organization_members(organization_id);
CREATE INDEX IF NOT EXISTS idx_org_members_user ON organization_members(user_id);

-- ============================================
-- CORE: ORGANIZATION INVITES
-- Pending invitations to join organizations
-- ============================================
CREATE TABLE IF NOT EXISTS organization_invites (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'inv_' || substr(md5(random()::text), 1, 16),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Invite Details
    email VARCHAR(255) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'member'
        CHECK (role IN ('admin', 'member', 'viewer')),
    invited_by VARCHAR(64) NOT NULL,  -- Can be user_id or api_key_owner_id
    
    -- Token
    token VARCHAR(255) NOT NULL UNIQUE,
    
    -- Status
    status VARCHAR(32) DEFAULT 'pending'
        CHECK (status IN ('pending', 'accepted', 'expired', 'revoked')),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '7 days',
    accepted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_org_invites_org ON organization_invites(organization_id);
CREATE INDEX IF NOT EXISTS idx_org_invites_email ON organization_invites(email);
CREATE INDEX IF NOT EXISTS idx_org_invites_token ON organization_invites(token);

-- ============================================
-- CORE: API KEYS
-- Organization API keys for programmatic access
-- ============================================
CREATE TABLE IF NOT EXISTS api_keys (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'key_' || substr(md5(random()::text), 1, 16),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Key Data
    key_hash VARCHAR(255) NOT NULL,  -- SHA-256 of the actual key
    key_prefix VARCHAR(12) NOT NULL,  -- First 8 chars for identification
    name VARCHAR(255) NOT NULL,
    
    -- Permissions
    scopes JSONB DEFAULT '["sign", "verify"]'::jsonb,
    
    -- Rate Limiting
    rate_limit_per_minute INTEGER DEFAULT 60,
    rate_limit_per_day INTEGER DEFAULT 10000,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_api_keys_org ON api_keys(organization_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_prefix ON api_keys(key_prefix);
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);

-- ============================================
-- CORE: SESSIONS
-- User sessions for web authentication
-- ============================================
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'sess_' || substr(md5(random()::text), 1, 16),
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Session Data
    token_hash VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(512),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    last_active_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token_hash);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);

-- ============================================
-- CORE: REFRESH TOKENS
-- Long-lived tokens for session refresh
-- ============================================
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'rt_' || substr(md5(random()::text), 1, 16),
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(64) REFERENCES sessions(id) ON DELETE CASCADE,
    
    -- Token Data
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    
    -- Status
    is_revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_hash ON refresh_tokens(token_hash);

-- ============================================
-- BILLING: SUBSCRIPTION HISTORY
-- Track subscription changes
-- ============================================
CREATE TABLE IF NOT EXISTS subscription_history (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'subhist_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Change Details
    previous_tier VARCHAR(32),
    new_tier VARCHAR(32) NOT NULL,
    change_type VARCHAR(32) NOT NULL
        CHECK (change_type IN ('upgrade', 'downgrade', 'cancel', 'reactivate', 'trial_start', 'trial_end')),
    
    -- Stripe
    stripe_event_id VARCHAR(255),
    
    -- Timestamps
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sub_history_org ON subscription_history(organization_id);

-- ============================================
-- BILLING: USAGE RECORDS
-- Detailed API usage tracking
-- ============================================
CREATE TABLE IF NOT EXISTS usage_records (
    id BIGSERIAL PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    api_key_id VARCHAR(64) REFERENCES api_keys(id) ON DELETE SET NULL,
    
    -- Usage Details
    endpoint VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    
    -- Request Info
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Partition by month for efficient queries and cleanup
CREATE INDEX IF NOT EXISTS idx_usage_org_created ON usage_records(organization_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_created ON usage_records(created_at DESC);

-- ============================================
-- BILLING: KEY USAGE
-- Track API key usage for billing
-- ============================================
CREATE TABLE IF NOT EXISTS key_usage (
    id BIGSERIAL PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    api_key_id VARCHAR(64) NOT NULL REFERENCES api_keys(id) ON DELETE CASCADE,
    
    -- Usage
    operation VARCHAR(32) NOT NULL,
    count INTEGER NOT NULL DEFAULT 1,
    
    -- Timestamp (hourly buckets)
    hour_bucket TIMESTAMPTZ NOT NULL,
    
    UNIQUE(api_key_id, operation, hour_bucket)
);

CREATE INDEX IF NOT EXISTS idx_key_usage_org ON key_usage(organization_id);
CREATE INDEX IF NOT EXISTS idx_key_usage_bucket ON key_usage(hour_bucket);

-- ============================================
-- BILLING: KEY ROTATIONS
-- Track API key rotation history
-- ============================================
CREATE TABLE IF NOT EXISTS key_rotations (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'rot_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    old_key_id VARCHAR(64),
    new_key_id VARCHAR(64) REFERENCES api_keys(id) ON DELETE SET NULL,
    
    -- Rotation Details
    reason VARCHAR(100),
    rotated_by VARCHAR(64),
    
    -- Timestamp
    rotated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_key_rotations_org ON key_rotations(organization_id);

-- ============================================
-- ENTERPRISE: CERTIFICATE LIFECYCLE
-- SSL.com certificate tracking
-- ============================================
CREATE TABLE IF NOT EXISTS certificate_lifecycle (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'cert_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- SSL.com Integration
    ssl_order_id VARCHAR(100) UNIQUE,
    order_status VARCHAR(50) DEFAULT 'pending'
        CHECK (order_status IN ('pending', 'pending_validation', 'issued', 'renewed', 'expired', 'revoked')),
    validation_url TEXT,
    
    -- Lifecycle Dates
    ordered_at TIMESTAMPTZ,
    issued_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    renewal_initiated_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cert_lifecycle_org ON certificate_lifecycle(organization_id);
CREATE INDEX IF NOT EXISTS idx_cert_lifecycle_expires ON certificate_lifecycle(expires_at);

-- ============================================
-- ENTERPRISE: BATCH REQUESTS
-- Bulk signing/verification operations
-- ============================================
CREATE TABLE IF NOT EXISTS batch_requests (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'batch_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    api_key_id VARCHAR(64) REFERENCES api_keys(id),
    
    -- Request Details
    request_type VARCHAR(16) NOT NULL CHECK (request_type IN ('sign', 'verify')),
    mode VARCHAR(32) NOT NULL,
    segmentation_level VARCHAR(32),
    
    -- Idempotency
    idempotency_key VARCHAR(128) NOT NULL,
    payload_hash VARCHAR(64) NOT NULL,
    
    -- Status
    status VARCHAR(16) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    
    -- Counts
    item_count INTEGER NOT NULL,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    
    -- Error Info
    error_code VARCHAR(64),
    error_message TEXT,
    
    -- Metadata
    request_metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL,
    
    UNIQUE(organization_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_batch_org_status ON batch_requests(organization_id, status);
CREATE INDEX IF NOT EXISTS idx_batch_expires ON batch_requests(expires_at);

-- ============================================
-- ENTERPRISE: BATCH ITEMS
-- Individual items in batch operations
-- ============================================
CREATE TABLE IF NOT EXISTS batch_items (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'bi_' || substr(md5(random()::text), 1, 12),
    batch_request_id VARCHAR(64) NOT NULL REFERENCES batch_requests(id) ON DELETE CASCADE,
    document_id VARCHAR(64) NOT NULL,
    
    -- Status
    status VARCHAR(16) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    mode VARCHAR(32) NOT NULL,
    
    -- Results
    duration_ms INTEGER,
    error_code VARCHAR(64),
    error_message TEXT,
    statistics JSONB,
    result_payload JSONB,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_batch_items_batch ON batch_items(batch_request_id);
CREATE INDEX IF NOT EXISTS idx_batch_items_doc ON batch_items(document_id);

-- ============================================
-- ENTERPRISE: C2PA CUSTOM ASSERTION SCHEMAS
-- For enterprise custom assertions
-- ============================================
CREATE TABLE IF NOT EXISTS c2pa_assertion_schemas (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'schema_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Schema Definition
    name VARCHAR(255) NOT NULL,
    label VARCHAR(255) NOT NULL,  -- C2PA assertion label
    version VARCHAR(20) NOT NULL DEFAULT '1.0',
    json_schema JSONB NOT NULL,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT FALSE,  -- Allow sharing across organizations
    
    -- Metadata
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(organization_id, label, version)
);

CREATE INDEX IF NOT EXISTS idx_c2pa_schemas_org ON c2pa_assertion_schemas(organization_id);
CREATE INDEX IF NOT EXISTS idx_c2pa_schemas_public ON c2pa_assertion_schemas(is_public) WHERE is_public = TRUE;

-- ============================================
-- ENTERPRISE: C2PA CUSTOM ASSERTION TEMPLATES
-- Reusable assertion templates
-- ============================================
CREATE TABLE IF NOT EXISTS c2pa_assertion_templates (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'tmpl_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    schema_id VARCHAR(64) NOT NULL REFERENCES c2pa_assertion_schemas(id) ON DELETE CASCADE,
    
    -- Template
    name VARCHAR(255) NOT NULL,
    template_data JSONB NOT NULL,
    category VARCHAR(100),  -- news, legal, academic, publisher
    
    -- Status
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT FALSE,  -- Allow sharing across organizations
    
    -- Metadata
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_c2pa_templates_org ON c2pa_assertion_templates(organization_id);
CREATE INDEX IF NOT EXISTS idx_c2pa_templates_schema ON c2pa_assertion_templates(schema_id);

-- ============================================
-- AUDIT: AUDIT LOGS
-- Compliance and security tracking
-- ============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'audit_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL,
    
    -- Event
    action VARCHAR(64) NOT NULL,
    actor_id VARCHAR(64) NOT NULL,
    actor_type VARCHAR(32) NOT NULL CHECK (actor_type IN ('user', 'api_key', 'system')),
    
    -- Resource
    resource_type VARCHAR(64) NOT NULL,
    resource_id VARCHAR(64),
    
    -- Context
    details JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(512),
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_org_created ON audit_logs(organization_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(organization_id, action);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_logs(actor_id);

-- ============================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to relevant tables
CREATE TRIGGER trg_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_updated_at BEFORE UPDATE ON api_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_updated_at BEFORE UPDATE ON batch_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_updated_at BEFORE UPDATE ON batch_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_updated_at BEFORE UPDATE ON certificate_lifecycle
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_updated_at BEFORE UPDATE ON c2pa_assertion_schemas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_updated_at BEFORE UPDATE ON c2pa_assertion_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================
-- FUNCTIONS: Set organization features from tier
-- ============================================
CREATE OR REPLACE FUNCTION set_org_features_from_tier()
RETURNS TRIGGER AS $$
BEGIN
    NEW.features = CASE NEW.tier
        WHEN 'starter' THEN '{
            "team_management": false,
            "audit_logs": false,
            "merkle_enabled": false,
            "bulk_operations": false,
            "sentence_tracking": false,
            "streaming": false,
            "custom_assertions": false,
            "priority_support": false,
            "sla": false
        }'::jsonb
        WHEN 'professional' THEN '{
            "team_management": false,
            "audit_logs": false,
            "merkle_enabled": false,
            "bulk_operations": false,
            "sentence_tracking": true,
            "streaming": true,
            "custom_assertions": false,
            "priority_support": false,
            "sla": false
        }'::jsonb
        WHEN 'business' THEN '{
            "team_management": true,
            "audit_logs": true,
            "merkle_enabled": true,
            "bulk_operations": true,
            "sentence_tracking": true,
            "streaming": true,
            "custom_assertions": false,
            "priority_support": true,
            "sla": false
        }'::jsonb
        WHEN 'enterprise' THEN '{
            "team_management": true,
            "audit_logs": true,
            "merkle_enabled": true,
            "bulk_operations": true,
            "sentence_tracking": true,
            "streaming": true,
            "custom_assertions": true,
            "priority_support": true,
            "sla": true
        }'::jsonb
        WHEN 'demo' THEN '{
            "team_management": true,
            "audit_logs": true,
            "merkle_enabled": true,
            "bulk_operations": true,
            "sentence_tracking": true,
            "streaming": true,
            "custom_assertions": true,
            "priority_support": false,
            "sla": false
        }'::jsonb
        ELSE '{}'::jsonb
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_set_org_features BEFORE INSERT OR UPDATE OF tier ON organizations
    FOR EACH ROW EXECUTE FUNCTION set_org_features_from_tier();

-- ============================================
-- COALITION: Content Stats
-- Aggregated content statistics for revenue sharing
-- ============================================
CREATE TABLE IF NOT EXISTS coalition_content_stats (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'stats_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Stats
    documents_count INTEGER NOT NULL DEFAULT 0,
    sentences_count INTEGER NOT NULL DEFAULT 0,
    total_characters BIGINT NOT NULL DEFAULT 0,
    unique_content_hash_count INTEGER NOT NULL DEFAULT 0,
    content_categories JSONB,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(organization_id, period_start, period_end)
);

CREATE INDEX IF NOT EXISTS idx_coalition_stats_org ON coalition_content_stats(organization_id);
CREATE INDEX IF NOT EXISTS idx_coalition_stats_period ON coalition_content_stats(period_start, period_end);

-- ============================================
-- COALITION: Earnings
-- Revenue sharing earnings records
-- ============================================
CREATE TABLE IF NOT EXISTS coalition_earnings (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'earn_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Deal info
    deal_id VARCHAR(64) NOT NULL,
    deal_name VARCHAR(256),
    ai_company VARCHAR(256),
    
    -- Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Revenue
    gross_revenue_cents INTEGER NOT NULL DEFAULT 0,
    publisher_share_percent INTEGER NOT NULL DEFAULT 70,
    publisher_earnings_cents INTEGER NOT NULL DEFAULT 0,
    
    -- Attribution
    attribution_method VARCHAR(64),
    attribution_weight DECIMAL(5, 4),
    
    -- Status
    status VARCHAR(32) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'confirmed', 'paid', 'disputed')),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_coalition_earnings_org ON coalition_earnings(organization_id);
CREATE INDEX IF NOT EXISTS idx_coalition_earnings_period ON coalition_earnings(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_coalition_earnings_status ON coalition_earnings(status);

-- ============================================
-- COALITION: Payouts
-- Payout records for publishers
-- ============================================
CREATE TABLE IF NOT EXISTS coalition_payouts (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'payout_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Amount
    total_earnings_cents INTEGER NOT NULL DEFAULT 0,
    payout_amount_cents INTEGER NOT NULL DEFAULT 0,
    currency VARCHAR(8) NOT NULL DEFAULT 'USD',
    
    -- Status
    status VARCHAR(32) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    
    -- Payment details
    payment_method VARCHAR(64),
    payment_reference VARCHAR(256),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_coalition_payouts_org ON coalition_payouts(organization_id);
CREATE INDEX IF NOT EXISTS idx_coalition_payouts_status ON coalition_payouts(status);

-- ============================================
-- VERIFICATION
-- ============================================
DO $$
BEGIN
    RAISE NOTICE 'Core database schema created successfully';
END $$;
