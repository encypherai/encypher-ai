ALTER TABLE organizations
ADD COLUMN IF NOT EXISTS default_c2pa_template_id VARCHAR(64);

CREATE INDEX IF NOT EXISTS idx_organizations_default_c2pa_template_id
ON organizations(default_c2pa_template_id);
