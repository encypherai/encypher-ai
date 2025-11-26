-- ============================================
-- ENCYPHER UNIFIED DATABASE SCHEMA
-- Version: 1.0.0
-- Date: 2025-11-25
-- ============================================
-- 
-- This is the master schema for all Encypher services:
-- - Auth Service (users, sessions)
-- - Key Service (API keys)
-- - Enterprise API (organizations, documents, C2PA)
-- - Billing Service (subscriptions, usage)
-- - Coalition Service (revenue sharing)
--
-- Design Principles:
-- 1. Organizations are the billing entity (not users)
-- 2. Users belong to organizations via memberships
-- 3. API keys belong to organizations
-- 4. All services share this schema
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
    id VARCHAR(64) PRIMARY KEY DEFAULT 'usr_' || substr(md5(random()::text), 1, 16),
    
    -- Identity
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    avatar_url VARCHAR(500),
    
    -- Authentication
    hashed_password VARCHAR(255),  -- Nullable for OAuth-only users
    
    -- OAuth
    oauth_provider VARCHAR(32),  -- google, github, etc.
    oauth_id VARCHAR(255),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    last_login TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_oauth ON users(oauth_provider, oauth_id);

-- ============================================
-- CORE: ORGANIZATION MEMBERS
-- Links users to organizations with roles
-- ============================================
CREATE TABLE IF NOT EXISTS organization_members (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'mem_' || substr(md5(random()::text), 1, 16),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Role & Permissions
    role VARCHAR(32) NOT NULL DEFAULT 'member'
        CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    
    -- Status
    status VARCHAR(32) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'invited', 'suspended')),
    
    -- Invitation tracking
    invited_by VARCHAR(64) REFERENCES users(id),
    invited_at TIMESTAMPTZ,
    accepted_at TIMESTAMPTZ,
    
    -- Activity
    last_active_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    
    UNIQUE(organization_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_org_members_org ON organization_members(organization_id);
CREATE INDEX IF NOT EXISTS idx_org_members_user ON organization_members(user_id);

-- ============================================
-- CORE: API KEYS
-- Unified API key management
-- ============================================
CREATE TABLE IF NOT EXISTS api_keys (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'key_' || substr(md5(random()::text), 1, 16),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Key Data
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE,  -- SHA-256 hash of actual key
    key_prefix VARCHAR(20) NOT NULL,  -- For display: "ency_abc..."
    
    -- Permissions
    permissions JSONB NOT NULL DEFAULT '["sign", "verify", "lookup"]'::jsonb,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_revoked BOOLEAN DEFAULT FALSE,
    
    -- Usage
    last_used_at TIMESTAMPTZ,
    usage_count INTEGER DEFAULT 0,
    
    -- Lifecycle
    created_by VARCHAR(64) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    
    -- Metadata
    description TEXT
);

CREATE INDEX IF NOT EXISTS idx_api_keys_org ON api_keys(organization_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(organization_id, is_active) WHERE is_active = TRUE;

-- ============================================
-- AUTH: REFRESH TOKENS
-- For JWT refresh token management
-- ============================================
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'rt_' || substr(md5(random()::text), 1, 16),
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    
    -- Lifecycle
    expires_at TIMESTAMPTZ NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMPTZ,
    
    -- Context
    user_agent VARCHAR(500),
    ip_address VARCHAR(45),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);

-- ============================================
-- AUTH: PASSWORD RESET TOKENS
-- ============================================
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'prt_' || substr(md5(random()::text), 1, 16),
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    
    -- Lifecycle
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_password_reset_user ON password_reset_tokens(user_id);

-- ============================================
-- AUTH: ORGANIZATION INVITES
-- Pending invitations to join organizations
-- ============================================
CREATE TABLE IF NOT EXISTS organization_invites (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'inv_' || substr(md5(random()::text), 1, 16),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'member',
    
    -- Invite Token
    invite_token VARCHAR(128) NOT NULL UNIQUE,
    
    -- Status
    status VARCHAR(32) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'accepted', 'expired', 'revoked')),
    
    -- Tracking
    invited_by VARCHAR(64) NOT NULL REFERENCES users(id),
    expires_at TIMESTAMPTZ NOT NULL,
    accepted_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_org_invites_org ON organization_invites(organization_id);
CREATE INDEX IF NOT EXISTS idx_org_invites_email ON organization_invites(email);
CREATE INDEX IF NOT EXISTS idx_org_invites_token ON organization_invites(invite_token);

-- ============================================
-- TRIGGER: Update timestamps automatically
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN SELECT table_name FROM information_schema.columns 
             WHERE column_name = 'updated_at' AND table_schema = 'public'
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS trg_updated_at ON %I', t);
        EXECUTE format('CREATE TRIGGER trg_updated_at BEFORE UPDATE ON %I 
                        FOR EACH ROW EXECUTE FUNCTION update_updated_at()', t);
    END LOOP;
END $$;

-- ============================================
-- FUNCTION: Get tier features
-- Returns default features for a given tier
-- ============================================
CREATE OR REPLACE FUNCTION get_tier_features(tier_name VARCHAR)
RETURNS JSONB AS $$
BEGIN
    RETURN CASE tier_name
        WHEN 'starter' THEN '{
            "team_management": false,
            "audit_logs": false,
            "merkle_enabled": false,
            "bulk_operations": false,
            "sentence_tracking": false,
            "streaming": false,
            "byok": false,
            "sso": false,
            "custom_assertions": false,
            "max_team_members": 1
        }'::jsonb
        WHEN 'professional' THEN '{
            "team_management": false,
            "audit_logs": false,
            "merkle_enabled": false,
            "bulk_operations": false,
            "sentence_tracking": true,
            "streaming": true,
            "byok": false,
            "sso": false,
            "custom_assertions": false,
            "max_team_members": 5
        }'::jsonb
        WHEN 'business' THEN '{
            "team_management": true,
            "audit_logs": true,
            "merkle_enabled": true,
            "bulk_operations": true,
            "sentence_tracking": true,
            "streaming": true,
            "byok": true,
            "sso": false,
            "custom_assertions": true,
            "max_team_members": 10
        }'::jsonb
        WHEN 'enterprise' THEN '{
            "team_management": true,
            "audit_logs": true,
            "merkle_enabled": true,
            "bulk_operations": true,
            "sentence_tracking": true,
            "streaming": true,
            "byok": true,
            "sso": true,
            "custom_assertions": true,
            "max_team_members": -1
        }'::jsonb
        WHEN 'demo' THEN '{
            "team_management": true,
            "audit_logs": true,
            "merkle_enabled": true,
            "bulk_operations": true,
            "sentence_tracking": true,
            "streaming": true,
            "byok": true,
            "sso": true,
            "custom_assertions": true,
            "max_team_members": -1
        }'::jsonb
        ELSE get_tier_features('starter')
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================
-- TRIGGER: Auto-set features on tier change
-- ============================================
CREATE OR REPLACE FUNCTION set_org_features_from_tier()
RETURNS TRIGGER AS $$
BEGIN
    -- Only update features if tier changed or features is empty
    IF (TG_OP = 'INSERT') OR (NEW.tier IS DISTINCT FROM OLD.tier) OR (NEW.features = '{}'::jsonb) THEN
        NEW.features = get_tier_features(NEW.tier);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_set_org_features ON organizations;
CREATE TRIGGER trg_set_org_features
    BEFORE INSERT OR UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION set_org_features_from_tier();

-- ============================================
-- VERIFICATION
-- ============================================
DO $$
BEGIN
    RAISE NOTICE 'Core schema created successfully';
END $$;
