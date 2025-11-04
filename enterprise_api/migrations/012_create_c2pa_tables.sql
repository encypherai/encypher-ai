-- Migration 012: Create C2PA Custom Assertions Tables
-- Date: 2025-11-03
-- Description: Creates tables for C2PA custom assertion schemas and templates

-- Create c2pa_schemas table
CREATE TABLE IF NOT EXISTS c2pa_schemas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    namespace VARCHAR(255) NOT NULL,
    label VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    schema JSONB NOT NULL,
    description TEXT,
    organization_id VARCHAR(255),
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_schema_namespace_label_version UNIQUE (namespace, label, version)
);

-- Create indexes for c2pa_schemas
CREATE INDEX IF NOT EXISTS ix_c2pa_schemas_namespace ON c2pa_schemas(namespace);
CREATE INDEX IF NOT EXISTS ix_c2pa_schemas_label ON c2pa_schemas(label);
CREATE INDEX IF NOT EXISTS ix_c2pa_schemas_organization_id ON c2pa_schemas(organization_id);
CREATE INDEX IF NOT EXISTS ix_c2pa_schemas_is_public ON c2pa_schemas(is_public);

-- Create c2pa_assertion_templates table
CREATE TABLE IF NOT EXISTS c2pa_assertion_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    assertions JSONB NOT NULL,
    organization_id VARCHAR(255),
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    category VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for c2pa_assertion_templates
CREATE INDEX IF NOT EXISTS ix_c2pa_templates_name ON c2pa_assertion_templates(name);
CREATE INDEX IF NOT EXISTS ix_c2pa_templates_organization_id ON c2pa_assertion_templates(organization_id);
CREATE INDEX IF NOT EXISTS ix_c2pa_templates_is_public ON c2pa_assertion_templates(is_public);
CREATE INDEX IF NOT EXISTS ix_c2pa_templates_category ON c2pa_assertion_templates(category);

-- Add comments
COMMENT ON TABLE c2pa_schemas IS 'Custom C2PA assertion schemas with JSON Schema validation';
COMMENT ON TABLE c2pa_assertion_templates IS 'Reusable C2PA assertion templates for common use cases';
