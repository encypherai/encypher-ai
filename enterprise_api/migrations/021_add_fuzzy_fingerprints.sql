-- Migration 021: Add fuzzy fingerprint index + org quota columns
-- Date: 2026-01-17
-- Description: Adds fuzzy fingerprint indexing table and org feature/quota columns

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Organization feature flag + quota tracking
ALTER TABLE organizations
    ADD COLUMN IF NOT EXISTS fuzzy_fingerprint_enabled BOOLEAN DEFAULT FALSE;

ALTER TABLE organizations
    ADD COLUMN IF NOT EXISTS fuzzy_index_calls_this_month INTEGER DEFAULT 0;

ALTER TABLE organizations
    ADD COLUMN IF NOT EXISTS fuzzy_search_calls_this_month INTEGER DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_organizations_fuzzy_enabled
    ON organizations(fuzzy_fingerprint_enabled)
    WHERE fuzzy_fingerprint_enabled = TRUE;

-- Fuzzy fingerprints table
CREATE TABLE IF NOT EXISTS fuzzy_fingerprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    document_id VARCHAR(64) NOT NULL,
    merkle_root_id UUID REFERENCES merkle_roots(id) ON DELETE SET NULL,
    segmentation_level VARCHAR(20) NOT NULL,
    segment_index INTEGER,
    leaf_hash VARCHAR(64),
    fingerprint_type VARCHAR(20) NOT NULL DEFAULT 'simhash',
    fingerprint_value BIGINT NOT NULL,
    fingerprint_bits INTEGER NOT NULL DEFAULT 64,
    fingerprint_bucket INTEGER NOT NULL,
    text_preview VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fuzzy_fingerprints_segmentation_level_check
        CHECK (segmentation_level IN ('sentence', 'paragraph', 'document'))
);

CREATE INDEX IF NOT EXISTS idx_fuzzy_fingerprints_org ON fuzzy_fingerprints(organization_id);
CREATE INDEX IF NOT EXISTS idx_fuzzy_fingerprints_doc_level ON fuzzy_fingerprints(document_id, segmentation_level);
CREATE INDEX IF NOT EXISTS idx_fuzzy_fingerprints_bucket ON fuzzy_fingerprints(fingerprint_bucket);
CREATE INDEX IF NOT EXISTS idx_fuzzy_fingerprints_root ON fuzzy_fingerprints(merkle_root_id);
