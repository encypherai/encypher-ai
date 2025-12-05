-- Migration: 006_create_merkle_roots
-- Description: Create merkle_roots table for storing Merkle tree root hashes
-- Author: System
-- Date: 2025-10-28
-- NOTE: This table is now created by services/migrations/002_enterprise_api_schema.sql
--       This migration is kept for backwards compatibility but is essentially a no-op.

-- Create merkle_roots table (uses 'id' as PK to match 002_enterprise_api_schema.sql)
CREATE TABLE IF NOT EXISTS merkle_roots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    document_id VARCHAR(64) NOT NULL,
    root_hash VARCHAR(64) NOT NULL,
    tree_depth INTEGER NOT NULL CHECK (tree_depth >= 0),
    total_leaves INTEGER NOT NULL CHECK (total_leaves > 0),
    segmentation_level VARCHAR(50) NOT NULL CHECK (segmentation_level IN ('sentence', 'paragraph', 'section')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for efficient queries (IF NOT EXISTS makes these idempotent)
CREATE INDEX IF NOT EXISTS idx_merkle_roots_hash ON merkle_roots(root_hash);
CREATE INDEX IF NOT EXISTS idx_merkle_roots_doc ON merkle_roots(document_id);
CREATE INDEX IF NOT EXISTS idx_merkle_roots_org ON merkle_roots(organization_id);

-- Comments are optional and may fail if table structure differs - that's OK
