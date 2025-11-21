-- Insert demo organization for load testing
INSERT INTO organizations (organization_id, organization_name, organization_type, email, tier, monthly_quota, created_at, updated_at)
VALUES ('org_demo', 'Encypher Demo Organization', 'demo', 'demo@encypher.ai', 'enterprise', 100000, NOW(), NOW())
ON CONFLICT (organization_id) DO NOTHING;
