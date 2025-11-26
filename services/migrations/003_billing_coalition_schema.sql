-- ============================================
-- BILLING & COALITION SCHEMA
-- Version: 1.0.0
-- Date: 2025-11-25
-- ============================================
-- 
-- Tables for usage tracking, billing, and coalition revenue sharing
-- ============================================

-- ============================================
-- USAGE RECORDS
-- Monthly usage tracking for billing
-- ============================================
CREATE TABLE IF NOT EXISTS usage_records (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'usage_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Metrics
    api_calls INTEGER DEFAULT 0,
    documents_signed INTEGER DEFAULT 0,
    sentences_signed INTEGER DEFAULT 0,
    sentences_tracked INTEGER DEFAULT 0,
    batch_operations INTEGER DEFAULT 0,
    verifications INTEGER DEFAULT 0,
    lookups INTEGER DEFAULT 0,
    
    -- Billing
    billable_amount_cents INTEGER DEFAULT 0,
    overage_amount_cents INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(organization_id, period_start, period_end)
);

CREATE INDEX IF NOT EXISTS idx_usage_org ON usage_records(organization_id);
CREATE INDEX IF NOT EXISTS idx_usage_period ON usage_records(period_start, period_end);

-- ============================================
-- API KEY USAGE
-- Per-key usage tracking
-- ============================================
CREATE TABLE IF NOT EXISTS key_usage (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'ku_' || substr(md5(random()::text), 1, 12),
    key_id VARCHAR(64) NOT NULL REFERENCES api_keys(id) ON DELETE CASCADE,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Request Info
    endpoint VARCHAR(255),
    method VARCHAR(10),
    status_code INTEGER,
    
    -- Client Info
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_key_usage_key ON key_usage(key_id);
CREATE INDEX IF NOT EXISTS idx_key_usage_org ON key_usage(organization_id);
CREATE INDEX IF NOT EXISTS idx_key_usage_created ON key_usage(created_at DESC);

-- ============================================
-- KEY ROTATIONS
-- API key rotation history
-- ============================================
CREATE TABLE IF NOT EXISTS key_rotations (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'kr_' || substr(md5(random()::text), 1, 12),
    old_key_id VARCHAR(64) NOT NULL,
    new_key_id VARCHAR(64) NOT NULL,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Rotation Info
    reason VARCHAR(255),
    rotated_by VARCHAR(64),  -- user_id or 'system'
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_key_rotations_org ON key_rotations(organization_id);

-- ============================================
-- COALITION CONTENT STATS
-- Content contribution tracking for revenue sharing
-- ============================================
CREATE TABLE IF NOT EXISTS coalition_content_stats (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'ccs_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Content Metrics
    documents_count INTEGER DEFAULT 0,
    sentences_count INTEGER DEFAULT 0,
    total_characters BIGINT DEFAULT 0,
    unique_content_hash_count INTEGER DEFAULT 0,
    
    -- Categories
    content_categories JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(organization_id, period_start, period_end)
);

CREATE INDEX IF NOT EXISTS idx_coalition_stats_org ON coalition_content_stats(organization_id);
CREATE INDEX IF NOT EXISTS idx_coalition_stats_period ON coalition_content_stats(period_start, period_end);

-- ============================================
-- COALITION EARNINGS
-- Revenue attribution from AI licensing deals
-- ============================================
CREATE TABLE IF NOT EXISTS coalition_earnings (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'ce_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Deal Info
    deal_id VARCHAR(64) NOT NULL,
    deal_name VARCHAR(255),
    ai_company VARCHAR(255),
    
    -- Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Revenue
    gross_revenue_cents BIGINT DEFAULT 0,
    publisher_share_percent INTEGER NOT NULL CHECK (publisher_share_percent BETWEEN 0 AND 100),
    publisher_earnings_cents BIGINT DEFAULT 0,
    encypher_share_cents BIGINT DEFAULT 0,
    
    -- Attribution
    attribution_method VARCHAR(32) NOT NULL 
        CHECK (attribution_method IN ('corpus_size', 'usage_based', 'flat_rate', 'hybrid')),
    attribution_weight FLOAT,
    
    -- Status
    status VARCHAR(32) DEFAULT 'pending'
        CHECK (status IN ('pending', 'confirmed', 'paid', 'disputed')),
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_coalition_earnings_org ON coalition_earnings(organization_id);
CREATE INDEX IF NOT EXISTS idx_coalition_earnings_deal ON coalition_earnings(deal_id);
CREATE INDEX IF NOT EXISTS idx_coalition_earnings_period ON coalition_earnings(period_start, period_end);

-- ============================================
-- COALITION PAYOUTS
-- Payout records to publishers
-- ============================================
CREATE TABLE IF NOT EXISTS coalition_payouts (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'cp_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Amounts
    total_earnings_cents BIGINT NOT NULL,
    payout_amount_cents BIGINT NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Status
    status VARCHAR(32) DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    
    -- Payment Info
    payment_method VARCHAR(32),
    payment_reference VARCHAR(255),
    paid_at TIMESTAMPTZ,
    
    -- Related Earnings
    earnings_ids JSONB DEFAULT '[]',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_coalition_payouts_org ON coalition_payouts(organization_id);
CREATE INDEX IF NOT EXISTS idx_coalition_payouts_status ON coalition_payouts(status);

-- ============================================
-- LICENSING AGREEMENTS
-- Content licensing deals with AI companies
-- ============================================
CREATE TABLE IF NOT EXISTS licensing_agreements (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'lic_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Agreement Details
    agreement_name VARCHAR(255) NOT NULL,
    licensee_name VARCHAR(255) NOT NULL,  -- AI company name
    licensee_contact_email VARCHAR(255),
    
    -- Terms
    license_type VARCHAR(50) NOT NULL 
        CHECK (license_type IN ('exclusive', 'non_exclusive', 'limited')),
    content_types TEXT[] DEFAULT '{}',  -- ['articles', 'reports', etc.]
    
    -- Dates
    effective_date DATE NOT NULL,
    expiration_date DATE,
    
    -- Financial
    revenue_share_percent INTEGER CHECK (revenue_share_percent BETWEEN 0 AND 100),
    minimum_guarantee_cents BIGINT DEFAULT 0,
    
    -- Status
    status VARCHAR(32) DEFAULT 'draft'
        CHECK (status IN ('draft', 'pending_approval', 'active', 'expired', 'terminated')),
    
    -- Documents
    agreement_document_url VARCHAR(500),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_licensing_org ON licensing_agreements(organization_id);
CREATE INDEX IF NOT EXISTS idx_licensing_status ON licensing_agreements(status);

-- ============================================
-- SUBSCRIPTION HISTORY
-- Track subscription changes
-- ============================================
CREATE TABLE IF NOT EXISTS subscription_history (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'sh_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Change Details
    previous_tier VARCHAR(32),
    new_tier VARCHAR(32) NOT NULL,
    change_type VARCHAR(32) NOT NULL 
        CHECK (change_type IN ('upgrade', 'downgrade', 'cancel', 'reactivate', 'trial_start', 'trial_end')),
    
    -- Stripe
    stripe_subscription_id VARCHAR(255),
    stripe_event_id VARCHAR(255),
    
    -- Metadata
    change_reason TEXT,
    changed_by VARCHAR(64),  -- user_id or 'system'
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sub_history_org ON subscription_history(organization_id);
CREATE INDEX IF NOT EXISTS idx_sub_history_created ON subscription_history(created_at DESC);

-- ============================================
-- VERIFICATION
-- ============================================
DO $$
BEGIN
    RAISE NOTICE 'Billing & Coalition schema created successfully';
END $$;
