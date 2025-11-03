-- Add manifest storage for ingredient references
ALTER TABLE content_references ADD COLUMN IF NOT EXISTS instance_id VARCHAR;
ALTER TABLE content_references ADD COLUMN IF NOT EXISTS manifest_data JSONB;
CREATE INDEX IF NOT EXISTS ix_content_references_instance_id ON content_references(instance_id);
