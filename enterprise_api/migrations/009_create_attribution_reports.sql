-- Migration: 009_create_attribution_reports
-- Description: Create attribution_reports table for storing plagiarism detection reports
-- Author: System
-- Date: 2025-10-28

-- Create attribution_reports table
CREATE TABLE IF NOT EXISTS attribution_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id VARCHAR(255) NOT NULL,
    target_document_id VARCHAR(255),
    target_text_hash VARCHAR(64),
    scan_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_segments INTEGER NOT NULL CHECK (total_segments >= 0),
    matched_segments INTEGER NOT NULL CHECK (matched_segments >= 0),
    source_documents JSONB NOT NULL DEFAULT '[]',
    heat_map_data JSONB,
    report_metadata JSONB DEFAULT '{}',
    
    -- Foreign key constraint
    CONSTRAINT fk_attribution_reports_organization 
        FOREIGN KEY (organization_id) 
        REFERENCES organizations(organization_id) 
        ON DELETE CASCADE,
    
    -- Check constraint
    CONSTRAINT chk_matched_le_total 
        CHECK (matched_segments <= total_segments)
);

-- Create indexes for report queries
CREATE INDEX IF NOT EXISTS idx_attribution_reports_org_timestamp 
    ON attribution_reports(organization_id, scan_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_attribution_reports_target_doc 
    ON attribution_reports(target_document_id) 
    WHERE target_document_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_attribution_reports_scan_timestamp 
    ON attribution_reports(scan_timestamp DESC);

-- Add comments for documentation
COMMENT ON TABLE attribution_reports IS 'Stores plagiarism detection and source attribution reports';
COMMENT ON COLUMN attribution_reports.report_id IS 'Unique identifier for the report';
COMMENT ON COLUMN attribution_reports.organization_id IS 'Organization that requested the report';
COMMENT ON COLUMN attribution_reports.target_document_id IS 'Optional identifier for the target document';
COMMENT ON COLUMN attribution_reports.target_text_hash IS 'Hash of the target text being analyzed';
COMMENT ON COLUMN attribution_reports.scan_timestamp IS 'When the scan was performed';
COMMENT ON COLUMN attribution_reports.total_segments IS 'Total number of segments scanned';
COMMENT ON COLUMN attribution_reports.matched_segments IS 'Number of segments with matches found';
COMMENT ON COLUMN attribution_reports.source_documents IS 'Array of source document matches with statistics';
COMMENT ON COLUMN attribution_reports.heat_map_data IS 'Visualization data for heat map generation';
COMMENT ON COLUMN attribution_reports.report_metadata IS 'Additional metadata (scan parameters, etc.)';
