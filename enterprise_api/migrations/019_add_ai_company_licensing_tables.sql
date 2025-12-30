-- Add AI company licensing tables (Enterprise API licensing router support)

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS ai_companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL UNIQUE,
    company_email VARCHAR(255) NOT NULL,
    api_key_hash VARCHAR(255) NOT NULL UNIQUE,
    api_key_prefix VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'suspended', 'terminated', 'expired')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_ai_companies_company_name ON ai_companies(company_name);
CREATE INDEX IF NOT EXISTS ix_ai_companies_status ON ai_companies(status);

CREATE TABLE IF NOT EXISTS licensing_agreements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agreement_name VARCHAR(255) NOT NULL,
    ai_company_id UUID NOT NULL REFERENCES ai_companies(id) ON DELETE CASCADE,
    agreement_type VARCHAR(50) NOT NULL DEFAULT 'subscription'
        CHECK (agreement_type IN ('subscription', 'one_time', 'usage_based')),
    total_value NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    content_types TEXT[] NULL,
    min_word_count INTEGER NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'suspended', 'terminated', 'expired')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_licensing_agreements_ai_company_id ON licensing_agreements(ai_company_id);
CREATE INDEX IF NOT EXISTS ix_licensing_agreements_status ON licensing_agreements(status);
CREATE INDEX IF NOT EXISTS ix_licensing_agreements_dates ON licensing_agreements(start_date, end_date);

CREATE TABLE IF NOT EXISTS content_access_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agreement_id UUID NOT NULL REFERENCES licensing_agreements(id) ON DELETE CASCADE,
    content_id BIGINT NOT NULL,
    member_id VARCHAR(64) NOT NULL,
    accessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    access_type VARCHAR(50) NULL,
    ai_company_name VARCHAR(255) NOT NULL,
    extra_metadata JSONB NULL
);

CREATE INDEX IF NOT EXISTS ix_content_access_logs_agreement_id ON content_access_logs(agreement_id);
CREATE INDEX IF NOT EXISTS ix_content_access_logs_content_id ON content_access_logs(content_id);
CREATE INDEX IF NOT EXISTS ix_content_access_logs_member_id ON content_access_logs(member_id);
CREATE INDEX IF NOT EXISTS ix_content_access_logs_accessed_at ON content_access_logs(accessed_at);

CREATE TABLE IF NOT EXISTS revenue_distributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agreement_id UUID NOT NULL REFERENCES licensing_agreements(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_revenue NUMERIC(12, 2) NOT NULL,
    encypher_share NUMERIC(12, 2) NOT NULL,
    member_pool NUMERIC(12, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ NULL
);

CREATE INDEX IF NOT EXISTS ix_revenue_distributions_agreement_id ON revenue_distributions(agreement_id);
CREATE INDEX IF NOT EXISTS ix_revenue_distributions_period ON revenue_distributions(period_start, period_end);
CREATE INDEX IF NOT EXISTS ix_revenue_distributions_status ON revenue_distributions(status);

CREATE TABLE IF NOT EXISTS member_revenue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    distribution_id UUID NOT NULL REFERENCES revenue_distributions(id) ON DELETE CASCADE,
    member_id VARCHAR(64) NOT NULL,
    content_count INTEGER NOT NULL DEFAULT 0,
    access_count INTEGER NOT NULL DEFAULT 0,
    revenue_amount NUMERIC(12, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'paid', 'failed')),
    paid_at TIMESTAMPTZ NULL,
    payment_reference VARCHAR(255) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_member_revenue_distribution_id ON member_revenue(distribution_id);
CREATE INDEX IF NOT EXISTS ix_member_revenue_member_id ON member_revenue(member_id);
CREATE INDEX IF NOT EXISTS ix_member_revenue_status ON member_revenue(status);
