-- Migration: 009_create_attribution_reports
-- Description: Create attribution_reports table for storing plagiarism detection reports
-- Author: System
-- Date: 2025-10-28
-- NOTE: This table is now created by services/migrations/002_enterprise_api_schema.sql
--       This migration is kept for backwards compatibility but is essentially a no-op.

-- Create attribution_reports table (uses 'id' as PK to match 002_enterprise_api_schema.sql)
CREATE TABLE IF NOT EXISTS attribution_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    target_document_id VARCHAR(64),
    target_text_hash VARCHAR(64),
    scan_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    total_segments INTEGER NOT NULL CHECK (total_segments >= 0),
    matched_segments INTEGER NOT NULL CHECK (matched_segments >= 0),
    source_documents JSONB NOT NULL DEFAULT '[]',
    heat_map_data JSONB,
    report_metadata JSONB DEFAULT '{}',
    
    -- Check constraint
    CONSTRAINT chk_matched_le_total CHECK (matched_segments <= total_segments)
);

-- Create indexes for report queries (IF NOT EXISTS makes these idempotent)
CREATE INDEX IF NOT EXISTS idx_attribution_org ON attribution_reports(organization_id);
CREATE INDEX IF NOT EXISTS idx_attribution_scan ON attribution_reports(scan_timestamp);
CREATE INDEX IF NOT EXISTS idx_attribution_target ON attribution_reports(target_document_id) WHERE target_document_id IS NOT NULL;

-- Add comments for documentation (only if columns exist)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'attribution_reports' AND column_name = 'id') THEN
        COMMENT ON TABLE attribution_reports IS 'Stores plagiarism detection and source attribution reports';
        COMMENT ON COLUMN attribution_reports.id IS 'Unique identifier for the report';
        COMMENT ON COLUMN attribution_reports.organization_id IS 'Organization that requested the report';
        COMMENT ON COLUMN attribution_reports.target_document_id IS 'Optional identifier for the target document';
        COMMENT ON COLUMN attribution_reports.target_text_hash IS 'Hash of the target text being analyzed';
        COMMENT ON COLUMN attribution_reports.scan_timestamp IS 'When the scan was performed';
        COMMENT ON COLUMN attribution_reports.total_segments IS 'Total number of segments scanned';
        COMMENT ON COLUMN attribution_reports.matched_segments IS 'Number of segments with matches found';
        COMMENT ON COLUMN attribution_reports.source_documents IS 'Array of source document matches with statistics';
        COMMENT ON COLUMN attribution_reports.heat_map_data IS 'Visualization data for heat map generation';
        COMMENT ON COLUMN attribution_reports.report_metadata IS 'Additional metadata (scan parameters, etc.)';
    END IF;
END $$;
