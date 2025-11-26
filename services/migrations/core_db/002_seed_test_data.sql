-- ============================================
-- SEED DATA FOR TESTING (CORE DATABASE)
-- ============================================

-- Demo Organization
INSERT INTO organizations (id, name, slug, email, tier, monthly_api_limit)
VALUES 
    ('org_demo', 'Demo Organization', 'demo', 'demo@encypherai.com', 'demo', -1)
ON CONFLICT (id) DO NOTHING;

-- Test Organizations for each tier
INSERT INTO organizations (id, name, slug, email, tier, monthly_api_limit)
VALUES 
    ('org_starter', 'Starter Test Org', 'starter-test', 'starter@test.encypherai.com', 'starter', 1000),
    ('org_professional', 'Professional Test Org', 'pro-test', 'pro@test.encypherai.com', 'professional', 10000),
    ('org_business', 'Business Test Org', 'business-test', 'business@test.encypherai.com', 'business', 50000),
    ('org_enterprise', 'Enterprise Test Org', 'enterprise-test', 'enterprise@test.encypherai.com', 'enterprise', -1)
ON CONFLICT (id) DO NOTHING;

-- Demo API Key (unhashed for testing - in production, store hash only)
INSERT INTO api_keys (id, organization_id, key_hash, key_prefix, name, scopes, is_active)
VALUES 
    ('key_demo', 'org_demo', 
     encode(sha256('demo-api-key-for-testing'::bytea), 'hex'),
     'demo-api-', 'Demo API Key', '["sign", "verify", "merkle", "batch"]'::jsonb, true)
ON CONFLICT (id) DO NOTHING;

-- Tier-specific API Keys
INSERT INTO api_keys (id, organization_id, key_hash, key_prefix, name, scopes, is_active)
VALUES 
    ('key_starter', 'org_starter',
     encode(sha256('starter-api-key-for-testing'::bytea), 'hex'),
     'starter-', 'Starter API Key', '["sign", "verify"]'::jsonb, true),
    ('key_professional', 'org_professional',
     encode(sha256('professional-api-key-for-testing'::bytea), 'hex'),
     'profess-', 'Professional API Key', '["sign", "verify", "streaming"]'::jsonb, true),
    ('key_business', 'org_business',
     encode(sha256('business-api-key-for-testing'::bytea), 'hex'),
     'busines-', 'Business API Key', '["sign", "verify", "merkle", "batch", "streaming"]'::jsonb, true),
    ('key_enterprise', 'org_enterprise',
     encode(sha256('enterprise-api-key-for-testing'::bytea), 'hex'),
     'enterpr-', 'Enterprise API Key', '["sign", "verify", "merkle", "batch", "streaming", "custom_assertions"]'::jsonb, true)
ON CONFLICT (id) DO NOTHING;

-- Test User
INSERT INTO users (id, email, name, email_verified)
VALUES 
    ('user_test', 'test@encypherai.com', 'Test User', true)
ON CONFLICT (id) DO NOTHING;

-- Link test user to demo org as owner
INSERT INTO organization_members (id, organization_id, user_id, role)
VALUES 
    ('mem_test_demo', 'org_demo', 'user_test', 'owner')
ON CONFLICT (organization_id, user_id) DO NOTHING;

DO $$
BEGIN
    RAISE NOTICE 'Core database seed data inserted successfully';
END $$;
