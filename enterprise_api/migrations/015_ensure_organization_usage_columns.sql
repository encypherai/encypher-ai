-- Migration: 015_ensure_organization_usage_columns
-- Description: Ensure organization usage/billing columns exist for demo/user bootstrap flows
-- Author: Cascade
-- Date: 2026-01-19
-- Note: Uses IF NOT EXISTS to remain idempotent

ALTER TABLE organizations ADD COLUMN IF NOT EXISTS monthly_api_limit INTEGER DEFAULT 10000;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS monthly_api_usage INTEGER DEFAULT 0;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS coalition_rev_share INTEGER DEFAULT 65;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(32) DEFAULT 'active';
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS features JSONB DEFAULT '{}'::jsonb;
