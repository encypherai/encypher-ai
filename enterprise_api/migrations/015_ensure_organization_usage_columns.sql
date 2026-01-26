-- Migration: 015_ensure_organization_usage_columns
-- Description: Ensure organization usage/billing columns exist for demo/user bootstrap flows
-- Author: Cascade
-- Date: 2026-01-19
-- Note: Uses IF NOT EXISTS to remain idempotent

ALTER TABLE organizations ADD COLUMN IF NOT EXISTS monthly_api_limit INTEGER DEFAULT 10000;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS monthly_api_usage INTEGER DEFAULT 0;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS coalition_rev_share INTEGER DEFAULT 65;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50) DEFAULT 'active';
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS features JSONB DEFAULT '{}'::jsonb;

-- Usage history snapshots for billing/reporting
CREATE TABLE IF NOT EXISTS usage_history (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'usage_' || substr(md5(random()::text), 1, 16),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    c2pa_signatures INTEGER NOT NULL DEFAULT 0,
    sentences_tracked INTEGER NOT NULL DEFAULT 0,
    batch_operations INTEGER NOT NULL DEFAULT 0,
    api_calls INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_usage_history_org_period ON usage_history(organization_id, period_start DESC);
