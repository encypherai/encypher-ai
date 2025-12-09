-- Migration: 010_alter_organizations_for_tiers
-- Description: Add tier and quota columns to organizations table for Enterprise features
-- Author: System
-- Date: 2025-10-28

-- Add tier column
ALTER TABLE organizations 
ADD COLUMN IF NOT EXISTS tier VARCHAR(50) DEFAULT 'free' 
CHECK (tier IN ('free', 'enterprise', 'custom'));

-- Add merkle_enabled flag
ALTER TABLE organizations 
ADD COLUMN IF NOT EXISTS merkle_enabled BOOLEAN DEFAULT FALSE;

-- Add monthly quota for Merkle operations
ALTER TABLE organizations 
ADD COLUMN IF NOT EXISTS monthly_merkle_quota INTEGER DEFAULT 0 
CHECK (monthly_merkle_quota >= 0);

-- Add counter for current month's usage
ALTER TABLE organizations 
ADD COLUMN IF NOT EXISTS merkle_calls_this_month INTEGER DEFAULT 0 
CHECK (merkle_calls_this_month >= 0);

-- Add timestamp for quota reset tracking
ALTER TABLE organizations 
ADD COLUMN IF NOT EXISTS quota_reset_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Create index for tier queries
CREATE INDEX IF NOT EXISTS idx_organizations_tier 
    ON organizations(tier) 
    WHERE tier != 'free';

-- Create index for quota enforcement
CREATE INDEX IF NOT EXISTS idx_organizations_merkle_enabled 
    ON organizations(merkle_enabled) 
    WHERE merkle_enabled = TRUE;

-- Add comments for documentation
COMMENT ON COLUMN organizations.tier IS 'Subscription tier: free, enterprise, or custom';
COMMENT ON COLUMN organizations.merkle_enabled IS 'Whether Merkle tree features are enabled for this organization';
COMMENT ON COLUMN organizations.monthly_merkle_quota IS 'Maximum number of Merkle operations per month (0 = unlimited for custom tier)';
COMMENT ON COLUMN organizations.merkle_calls_this_month IS 'Number of Merkle operations used this month';
COMMENT ON COLUMN organizations.quota_reset_at IS 'Timestamp of last quota reset (monthly)';

-- Update existing demo organization to enterprise tier (if it exists)
UPDATE organizations 
SET 
    tier = 'enterprise',
    merkle_enabled = TRUE,
    monthly_merkle_quota = 10000
WHERE id = 'org_demo';

-- Note: If org_demo doesn't exist yet, it will be created with enterprise tier
-- when the first demo API call is made
