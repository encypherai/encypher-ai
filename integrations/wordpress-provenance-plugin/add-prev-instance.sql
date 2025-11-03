-- Add previous_instance_id column for edit provenance tracking
ALTER TABLE content_references ADD COLUMN IF NOT EXISTS previous_instance_id VARCHAR;
CREATE INDEX IF NOT EXISTS ix_content_references_previous_instance_id ON content_references(previous_instance_id);
