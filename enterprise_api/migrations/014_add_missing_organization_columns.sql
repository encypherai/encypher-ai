-- Migration: 014_add_missing_organization_columns
-- Description: Add all missing columns to organizations table to match SQLAlchemy model
-- Author: System
-- Date: 2025-12-05
-- Note: Uses IF NOT EXISTS to be idempotent

-- Feature flags
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS merkle_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS advanced_analytics_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS bulk_operations_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS sentence_tracking_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS streaming_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS byok_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS team_management_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS audit_logs_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS sso_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS custom_assertions_enabled BOOLEAN DEFAULT FALSE;

-- Coalition settings
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS coalition_member BOOLEAN DEFAULT TRUE;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS coalition_rev_share_publisher INTEGER DEFAULT 65;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS coalition_rev_share_encypher INTEGER DEFAULT 35;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS coalition_opted_out BOOLEAN DEFAULT FALSE;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS coalition_opted_out_at TIMESTAMP WITH TIME ZONE;

-- Usage tracking / quotas
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS monthly_quota INTEGER DEFAULT 1000;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS documents_signed INTEGER DEFAULT 0;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS sentences_signed INTEGER DEFAULT 0;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS sentences_tracked_this_month INTEGER DEFAULT 0;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS api_calls_this_month INTEGER DEFAULT 0;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS merkle_encoding_calls_this_month INTEGER DEFAULT 0;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS merkle_attribution_calls_this_month INTEGER DEFAULT 0;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS merkle_plagiarism_calls_this_month INTEGER DEFAULT 0;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS batch_operations_this_month INTEGER DEFAULT 0;

-- Certificate metadata (if not already present)
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS certificate_pem TEXT;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS certificate_chain TEXT;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS certificate_status VARCHAR(20) DEFAULT 'none';
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS certificate_rotated_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS certificate_expiry TIMESTAMP WITH TIME ZONE;

-- AWS KMS Support
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS kms_key_id VARCHAR(255);
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS kms_region VARCHAR(50);

-- Timestamps (if not already present)
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_organizations_tier ON organizations(tier);
CREATE INDEX IF NOT EXISTS idx_organizations_merkle_enabled ON organizations(merkle_enabled) WHERE merkle_enabled = TRUE;
CREATE INDEX IF NOT EXISTS idx_organizations_coalition_member ON organizations(coalition_member) WHERE coalition_member = TRUE;
