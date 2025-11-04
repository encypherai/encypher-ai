-- Rollback Migration 012: Drop C2PA Custom Assertions Tables
-- Date: 2025-11-03

-- Drop indexes for c2pa_assertion_templates
DROP INDEX IF EXISTS ix_c2pa_templates_category;
DROP INDEX IF EXISTS ix_c2pa_templates_is_public;
DROP INDEX IF EXISTS ix_c2pa_templates_organization_id;
DROP INDEX IF EXISTS ix_c2pa_templates_name;

-- Drop c2pa_assertion_templates table
DROP TABLE IF EXISTS c2pa_assertion_templates;

-- Drop indexes for c2pa_schemas
DROP INDEX IF EXISTS ix_c2pa_schemas_is_public;
DROP INDEX IF EXISTS ix_c2pa_schemas_organization_id;
DROP INDEX IF EXISTS ix_c2pa_schemas_label;
DROP INDEX IF EXISTS ix_c2pa_schemas_namespace;

-- Drop c2pa_schemas table
DROP TABLE IF EXISTS c2pa_schemas;
