-- Insert demo organization for load testing
INSERT INTO organizations (organization_id, organization_name, organization_type, email, tier, monthly_quota, created_at, updated_at)
VALUES ('org_demo', 'Encypher Demo Organization', 'demo', 'demo@encypher.ai', 'enterprise', 100000, NOW(), NOW())
ON CONFLICT (organization_id) DO NOTHING;

-- Insert demo API key
INSERT INTO api_keys (api_key, organization_id, key_name, can_sign, can_verify, can_lookup, created_at)
VALUES ('demo-key-load-test', 'org_demo', 'Load Test Key', TRUE, TRUE, TRUE, NOW())
ON CONFLICT (api_key) DO NOTHING;
