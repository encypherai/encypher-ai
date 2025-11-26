-- ============================================
-- Test Data Seed Script for Enterprise API
-- Creates organizations and API keys for all tiers
-- ============================================

-- ============================================
-- DEMO ORGANIZATION (General Testing)
-- ============================================
INSERT INTO organizations (
    organization_id, organization_name, organization_type, email, tier,
    monthly_quota, documents_signed, sentences_signed, api_calls_this_month,
    sentences_tracked_this_month, batch_operations_this_month,
    merkle_enabled, advanced_analytics_enabled, bulk_operations_enabled,
    sentence_tracking_enabled, streaming_enabled, byok_enabled,
    team_management_enabled, audit_logs_enabled, sso_enabled, custom_assertions_enabled,
    coalition_member, coalition_rev_share_publisher, coalition_rev_share_encypher,
    created_at, updated_at
)
VALUES (
    'org_demo', 'Encypher Demo Organization', 'demo', 'demo@encypher.ai', 'demo',
    10000, 0, 0, 0, 0, 0,
    TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,
    TRUE, 65, 35,
    NOW(), NOW()
)
ON CONFLICT (organization_id) DO UPDATE SET
    tier = 'demo',
    monthly_quota = 10000,
    updated_at = NOW();

-- Note: Enterprise API uses demo key bypass in dependencies.py
-- The demo API key is configured via DEMO_API_KEY environment variable
-- For tier-specific testing, we rely on the organization's tier field

-- ============================================
-- STARTER TIER ORGANIZATION
-- ============================================
INSERT INTO organizations (
    organization_id, organization_name, organization_type, email, tier,
    monthly_quota, documents_signed, sentences_signed, api_calls_this_month,
    sentences_tracked_this_month, batch_operations_this_month,
    merkle_enabled, advanced_analytics_enabled, bulk_operations_enabled,
    sentence_tracking_enabled, streaming_enabled, byok_enabled,
    team_management_enabled, audit_logs_enabled, sso_enabled, custom_assertions_enabled,
    coalition_member, coalition_rev_share_publisher, coalition_rev_share_encypher,
    created_at, updated_at
)
VALUES (
    'org_starter', 'Starter Test Organization', 'publisher', 'starter@test.encypher.ai', 'starter',
    10000, 0, 0, 0, 0, 0,
    FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE,
    TRUE, 65, 35,
    NOW(), NOW()
)
ON CONFLICT (organization_id) DO UPDATE SET
    tier = 'starter',
    merkle_enabled = FALSE,
    sentence_tracking_enabled = FALSE,
    team_management_enabled = FALSE,
    audit_logs_enabled = FALSE,
    updated_at = NOW();

INSERT INTO api_keys (api_key, organization_id, key_name, can_sign, can_verify, can_lookup, created_at)
VALUES ('starter-api-key-for-testing', 'org_starter', 'Starter API Key', TRUE, TRUE, TRUE, NOW())
ON CONFLICT (api_key) DO NOTHING;

-- ============================================
-- PROFESSIONAL TIER ORGANIZATION
-- ============================================
INSERT INTO organizations (
    organization_id, organization_name, organization_type, email, tier,
    monthly_quota, documents_signed, sentences_signed, api_calls_this_month,
    sentences_tracked_this_month, batch_operations_this_month,
    merkle_enabled, advanced_analytics_enabled, bulk_operations_enabled,
    sentence_tracking_enabled, streaming_enabled, byok_enabled,
    team_management_enabled, audit_logs_enabled, sso_enabled, custom_assertions_enabled,
    coalition_member, coalition_rev_share_publisher, coalition_rev_share_encypher,
    created_at, updated_at
)
VALUES (
    'org_professional', 'Professional Test Organization', 'publisher', 'professional@test.encypher.ai', 'professional',
    100000, 0, 0, 0, 0, 0,
    FALSE, TRUE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE,
    TRUE, 70, 30,
    NOW(), NOW()
)
ON CONFLICT (organization_id) DO UPDATE SET
    tier = 'professional',
    sentence_tracking_enabled = TRUE,
    streaming_enabled = TRUE,
    team_management_enabled = FALSE,
    audit_logs_enabled = FALSE,
    coalition_rev_share_publisher = 70,
    updated_at = NOW();

INSERT INTO api_keys (api_key, organization_id, key_name, can_sign, can_verify, can_lookup, created_at)
VALUES ('professional-api-key-for-testing', 'org_professional', 'Professional API Key', TRUE, TRUE, TRUE, NOW())
ON CONFLICT (api_key) DO NOTHING;

-- ============================================
-- BUSINESS TIER ORGANIZATION
-- ============================================
INSERT INTO organizations (
    organization_id, organization_name, organization_type, email, tier,
    monthly_quota, documents_signed, sentences_signed, api_calls_this_month,
    sentences_tracked_this_month, batch_operations_this_month,
    merkle_enabled, advanced_analytics_enabled, bulk_operations_enabled,
    sentence_tracking_enabled, streaming_enabled, byok_enabled,
    team_management_enabled, audit_logs_enabled, sso_enabled, custom_assertions_enabled,
    coalition_member, coalition_rev_share_publisher, coalition_rev_share_encypher,
    created_at, updated_at
)
VALUES (
    'org_business', 'Business Test Organization', 'enterprise', 'business@test.encypher.ai', 'business',
    500000, 0, 0, 0, 0, 0,
    TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, FALSE, TRUE,
    TRUE, 80, 20,
    NOW(), NOW()
)
ON CONFLICT (organization_id) DO UPDATE SET
    tier = 'business',
    merkle_enabled = TRUE,
    bulk_operations_enabled = TRUE,
    team_management_enabled = TRUE,
    audit_logs_enabled = TRUE,
    coalition_rev_share_publisher = 80,
    updated_at = NOW();

INSERT INTO api_keys (api_key, organization_id, key_name, can_sign, can_verify, can_lookup, created_at)
VALUES ('business-api-key-for-testing', 'org_business', 'Business API Key', TRUE, TRUE, TRUE, NOW())
ON CONFLICT (api_key) DO NOTHING;

-- Business Admin user (for team management tests)
INSERT INTO team_members (
    id, organization_id, user_id, email, name, role, status, created_at
)
VALUES (
    'mem_business_owner', 'org_business', 'user_business_owner', 'owner@business.test', 'Business Owner', 'owner', 'active', NOW()
)
ON CONFLICT (organization_id, user_id) DO NOTHING;

INSERT INTO team_members (
    id, organization_id, user_id, email, name, role, status, created_at
)
VALUES (
    'mem_business_admin', 'org_business', 'user_business_admin', 'admin@business.test', 'Business Admin', 'admin', 'active', NOW()
)
ON CONFLICT (organization_id, user_id) DO NOTHING;

-- ============================================
-- ENTERPRISE TIER ORGANIZATION
-- ============================================
INSERT INTO organizations (
    organization_id, organization_name, organization_type, email, tier,
    monthly_quota, documents_signed, sentences_signed, api_calls_this_month,
    sentences_tracked_this_month, batch_operations_this_month,
    merkle_enabled, advanced_analytics_enabled, bulk_operations_enabled,
    sentence_tracking_enabled, streaming_enabled, byok_enabled,
    team_management_enabled, audit_logs_enabled, sso_enabled, custom_assertions_enabled,
    coalition_member, coalition_rev_share_publisher, coalition_rev_share_encypher,
    created_at, updated_at
)
VALUES (
    'org_enterprise', 'Enterprise Test Organization', 'enterprise', 'enterprise@test.encypher.ai', 'enterprise',
    -1, 0, 0, 0, 0, 0,  -- -1 = unlimited
    TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,
    TRUE, 85, 15,
    NOW(), NOW()
)
ON CONFLICT (organization_id) DO UPDATE SET
    tier = 'enterprise',
    monthly_quota = -1,
    merkle_enabled = TRUE,
    bulk_operations_enabled = TRUE,
    team_management_enabled = TRUE,
    audit_logs_enabled = TRUE,
    sso_enabled = TRUE,
    coalition_rev_share_publisher = 85,
    updated_at = NOW();

INSERT INTO api_keys (api_key, organization_id, key_name, can_sign, can_verify, can_lookup, created_at)
VALUES ('enterprise-api-key-for-testing', 'org_enterprise', 'Enterprise API Key', TRUE, TRUE, TRUE, NOW())
ON CONFLICT (api_key) DO NOTHING;

-- Enterprise team members
INSERT INTO team_members (
    id, organization_id, user_id, email, name, role, status, created_at
)
VALUES (
    'mem_enterprise_owner', 'org_enterprise', 'user_enterprise_owner', 'owner@enterprise.test', 'Enterprise Owner', 'owner', 'active', NOW()
)
ON CONFLICT (organization_id, user_id) DO NOTHING;

-- ============================================
-- SUMMARY
-- ============================================
-- Organizations created:
--   org_demo        - Demo tier (all features for testing)
--   org_starter     - Starter tier (basic features only)
--   org_professional - Professional tier (sentence tracking, streaming)
--   org_business    - Business tier (team mgmt, audit logs, merkle)
--   org_enterprise  - Enterprise tier (all features, unlimited)
--
-- API Keys:
--   demo-api-key-for-testing
--   starter-api-key-for-testing
--   professional-api-key-for-testing
--   business-api-key-for-testing
--   enterprise-api-key-for-testing
