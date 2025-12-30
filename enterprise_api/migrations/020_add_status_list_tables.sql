-- Migration 020: Add bitstring status lists for per-document revocation
-- Date: 2025-12-29
-- Description: Implements W3C StatusList2021 tables used by StatusService

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- Status List Entries
-- ============================================================================

CREATE TABLE IF NOT EXISTS status_list_entries (
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    list_index INTEGER NOT NULL,
    bit_index INTEGER NOT NULL,

    document_id VARCHAR(64) NOT NULL,

    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_reason VARCHAR(50),
    revoked_reason_detail TEXT,
    revoked_by VARCHAR(64),

    reinstated_at TIMESTAMP WITH TIME ZONE,
    reinstated_by VARCHAR(64),

    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    PRIMARY KEY (organization_id, list_index, bit_index)
);

CREATE INDEX IF NOT EXISTS idx_status_entry_document ON status_list_entries(document_id);
CREATE INDEX IF NOT EXISTS idx_status_entry_org_revoked ON status_list_entries(organization_id, revoked);
CREATE INDEX IF NOT EXISTS idx_status_entry_list ON status_list_entries(organization_id, list_index);

-- ============================================================================
-- Status List Metadata
-- ============================================================================

CREATE TABLE IF NOT EXISTS status_list_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    list_index INTEGER NOT NULL,

    next_bit_index INTEGER NOT NULL DEFAULT 0,
    is_full BOOLEAN NOT NULL DEFAULT FALSE,
    current_version INTEGER NOT NULL DEFAULT 0,

    last_generated_at TIMESTAMP WITH TIME ZONE,
    generation_duration_ms INTEGER,

    cdn_url VARCHAR(500),
    cdn_etag VARCHAR(64),

    total_documents INTEGER NOT NULL DEFAULT 0,
    revoked_count INTEGER NOT NULL DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_status_meta_org_list ON status_list_metadata(organization_id, list_index);
CREATE INDEX IF NOT EXISTS idx_status_meta_stale ON status_list_metadata(organization_id, last_generated_at);

-- ============================================================================
-- Optional link columns on content_references (used for fast verification)
-- ============================================================================

ALTER TABLE IF EXISTS content_references
    ADD COLUMN IF NOT EXISTS status_list_index INTEGER;

ALTER TABLE IF EXISTS content_references
    ADD COLUMN IF NOT EXISTS status_bit_index INTEGER;

ALTER TABLE IF EXISTS content_references
    ADD COLUMN IF NOT EXISTS status_list_url VARCHAR(500);
