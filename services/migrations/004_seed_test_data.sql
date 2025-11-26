-- ============================================
-- SEED TEST DATA
-- Version: 1.0.0
-- Date: 2025-11-25
-- ============================================
-- 
-- Creates test organizations and API keys for all tiers
-- Used for local development and CI/CD testing
-- ============================================

-- ============================================
-- TEST ORGANIZATIONS
-- ============================================

-- Demo Organization (all features enabled for testing)
INSERT INTO organizations (id, name, slug, email, tier, features, monthly_api_limit, coalition_rev_share)
VALUES (
    'org_demo',
    'Demo Organization',
    'demo',
    'demo@encypher.ai',
    'demo',
    get_tier_features('demo'),
    100000,
    65
) ON CONFLICT (id) DO UPDATE SET
    tier = EXCLUDED.tier,
    features = get_tier_features('demo'),
    updated_at = NOW();

-- Starter Tier Organization
INSERT INTO organizations (id, name, slug, email, tier, features, monthly_api_limit, coalition_rev_share)
VALUES (
    'org_starter',
    'Starter Test Organization',
    'starter-test',
    'starter@test.encypher.ai',
    'starter',
    get_tier_features('starter'),
    10000,
    65
) ON CONFLICT (id) DO UPDATE SET
    tier = EXCLUDED.tier,
    features = get_tier_features('starter'),
    updated_at = NOW();

-- Professional Tier Organization
INSERT INTO organizations (id, name, slug, email, tier, features, monthly_api_limit, coalition_rev_share)
VALUES (
    'org_professional',
    'Professional Test Organization',
    'professional-test',
    'professional@test.encypher.ai',
    'professional',
    get_tier_features('professional'),
    100000,
    70
) ON CONFLICT (id) DO UPDATE SET
    tier = EXCLUDED.tier,
    features = get_tier_features('professional'),
    updated_at = NOW();

-- Business Tier Organization
INSERT INTO organizations (id, name, slug, email, tier, features, monthly_api_limit, coalition_rev_share)
VALUES (
    'org_business',
    'Business Test Organization',
    'business-test',
    'business@test.encypher.ai',
    'business',
    get_tier_features('business'),
    500000,
    80
) ON CONFLICT (id) DO UPDATE SET
    tier = EXCLUDED.tier,
    features = get_tier_features('business'),
    updated_at = NOW();

-- Enterprise Tier Organization
INSERT INTO organizations (id, name, slug, email, tier, features, monthly_api_limit, coalition_rev_share)
VALUES (
    'org_enterprise',
    'Enterprise Test Organization',
    'enterprise-test',
    'enterprise@test.encypher.ai',
    'enterprise',
    get_tier_features('enterprise'),
    -1,  -- Unlimited
    85
) ON CONFLICT (id) DO UPDATE SET
    tier = EXCLUDED.tier,
    features = get_tier_features('enterprise'),
    monthly_api_limit = -1,
    updated_at = NOW();

-- ============================================
-- TEST USERS
-- ============================================

INSERT INTO users (id, email, name, is_active, is_verified)
VALUES 
    ('usr_demo', 'demo@encypher.ai', 'Demo User', TRUE, TRUE),
    ('usr_starter', 'starter@test.encypher.ai', 'Starter User', TRUE, TRUE),
    ('usr_professional', 'professional@test.encypher.ai', 'Professional User', TRUE, TRUE),
    ('usr_business_owner', 'owner@business.test', 'Business Owner', TRUE, TRUE),
    ('usr_business_admin', 'admin@business.test', 'Business Admin', TRUE, TRUE),
    ('usr_business_member', 'member@business.test', 'Business Member', TRUE, TRUE),
    ('usr_enterprise_owner', 'owner@enterprise.test', 'Enterprise Owner', TRUE, TRUE),
    ('usr_enterprise_admin', 'admin@enterprise.test', 'Enterprise Admin', TRUE, TRUE)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- ORGANIZATION MEMBERSHIPS
-- ============================================

-- Demo org membership
INSERT INTO organization_members (id, organization_id, user_id, role, status)
VALUES ('mem_demo', 'org_demo', 'usr_demo', 'owner', 'active')
ON CONFLICT (organization_id, user_id) DO NOTHING;

-- Starter org membership
INSERT INTO organization_members (id, organization_id, user_id, role, status)
VALUES ('mem_starter', 'org_starter', 'usr_starter', 'owner', 'active')
ON CONFLICT (organization_id, user_id) DO NOTHING;

-- Professional org membership
INSERT INTO organization_members (id, organization_id, user_id, role, status)
VALUES ('mem_professional', 'org_professional', 'usr_professional', 'owner', 'active')
ON CONFLICT (organization_id, user_id) DO NOTHING;

-- Business org memberships
INSERT INTO organization_members (id, organization_id, user_id, role, status)
VALUES 
    ('mem_business_owner', 'org_business', 'usr_business_owner', 'owner', 'active'),
    ('mem_business_admin', 'org_business', 'usr_business_admin', 'admin', 'active'),
    ('mem_business_member', 'org_business', 'usr_business_member', 'member', 'active')
ON CONFLICT (organization_id, user_id) DO NOTHING;

-- Enterprise org memberships
INSERT INTO organization_members (id, organization_id, user_id, role, status)
VALUES 
    ('mem_enterprise_owner', 'org_enterprise', 'usr_enterprise_owner', 'owner', 'active'),
    ('mem_enterprise_admin', 'org_enterprise', 'usr_enterprise_admin', 'admin', 'active')
ON CONFLICT (organization_id, user_id) DO NOTHING;

-- ============================================
-- TEST API KEYS
-- ============================================
-- Note: These are plaintext test keys. In production, keys are hashed.
-- The key_hash values here are SHA-256 hashes of the test key strings.

-- Demo API Key
INSERT INTO api_keys (id, organization_id, name, key_hash, key_prefix, permissions, is_active, created_by)
VALUES (
    'key_demo',
    'org_demo',
    'Demo API Key',
    encode(sha256('demo-api-key-for-testing'::bytea), 'hex'),
    'demo-api-k',
    '["sign", "verify", "lookup"]'::jsonb,
    TRUE,
    'usr_demo'
) ON CONFLICT (id) DO UPDATE SET
    key_hash = encode(sha256('demo-api-key-for-testing'::bytea), 'hex'),
    is_active = TRUE;

-- Starter API Key
INSERT INTO api_keys (id, organization_id, name, key_hash, key_prefix, permissions, is_active, created_by)
VALUES (
    'key_starter',
    'org_starter',
    'Starter API Key',
    encode(sha256('starter-api-key-for-testing'::bytea), 'hex'),
    'starter-ap',
    '["sign", "verify"]'::jsonb,
    TRUE,
    'usr_starter'
) ON CONFLICT (id) DO UPDATE SET
    key_hash = encode(sha256('starter-api-key-for-testing'::bytea), 'hex'),
    is_active = TRUE;

-- Professional API Key
INSERT INTO api_keys (id, organization_id, name, key_hash, key_prefix, permissions, is_active, created_by)
VALUES (
    'key_professional',
    'org_professional',
    'Professional API Key',
    encode(sha256('professional-api-key-for-testing'::bytea), 'hex'),
    'profession',
    '["sign", "verify", "lookup"]'::jsonb,
    TRUE,
    'usr_professional'
) ON CONFLICT (id) DO UPDATE SET
    key_hash = encode(sha256('professional-api-key-for-testing'::bytea), 'hex'),
    is_active = TRUE;

-- Business API Key
INSERT INTO api_keys (id, organization_id, name, key_hash, key_prefix, permissions, is_active, created_by)
VALUES (
    'key_business',
    'org_business',
    'Business API Key',
    encode(sha256('business-api-key-for-testing'::bytea), 'hex'),
    'business-a',
    '["sign", "verify", "lookup"]'::jsonb,
    TRUE,
    'usr_business_owner'
) ON CONFLICT (id) DO UPDATE SET
    key_hash = encode(sha256('business-api-key-for-testing'::bytea), 'hex'),
    is_active = TRUE;

-- Enterprise API Key
INSERT INTO api_keys (id, organization_id, name, key_hash, key_prefix, permissions, is_active, created_by)
VALUES (
    'key_enterprise',
    'org_enterprise',
    'Enterprise API Key',
    encode(sha256('enterprise-api-key-for-testing'::bytea), 'hex'),
    'enterprise',
    '["sign", "verify", "lookup"]'::jsonb,
    TRUE,
    'usr_enterprise_owner'
) ON CONFLICT (id) DO UPDATE SET
    key_hash = encode(sha256('enterprise-api-key-for-testing'::bytea), 'hex'),
    is_active = TRUE;

-- ============================================
-- VERIFICATION
-- ============================================
DO $$
DECLARE
    org_count INTEGER;
    user_count INTEGER;
    key_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO org_count FROM organizations;
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*) INTO key_count FROM api_keys;
    
    RAISE NOTICE 'Test data seeded successfully:';
    RAISE NOTICE '  Organizations: %', org_count;
    RAISE NOTICE '  Users: %', user_count;
    RAISE NOTICE '  API Keys: %', key_count;
END $$;

-- ============================================
-- TEST API KEYS REFERENCE
-- ============================================
-- 
-- Organization     | API Key                          | Tier
-- -----------------|----------------------------------|-------------
-- org_demo         | demo-api-key-for-testing         | demo (all features)
-- org_starter      | starter-api-key-for-testing      | starter
-- org_professional | professional-api-key-for-testing | professional
-- org_business     | business-api-key-for-testing     | business
-- org_enterprise   | enterprise-api-key-for-testing   | enterprise
--
-- Usage in tests:
--   Authorization: Bearer demo-api-key-for-testing
--   Authorization: Bearer business-api-key-for-testing
-- ============================================
