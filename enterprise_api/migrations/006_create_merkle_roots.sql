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

-- Add comments for documentation (only if columns exist)
DO $$
BEGIN
    -- Only add comments if the table exists with the expected columns
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'merkle_roots' AND column_name = 'id') THEN
        COMMENT ON TABLE merkle_roots IS 'Stores Merkle tree root hashes for source documents at different segmentation levels';
        COMMENT ON COLUMN merkle_roots.id IS 'Unique identifier for the Merkle root';
        COMMENT ON COLUMN merkle_roots.organization_id IS 'Organization that owns this document';
        COMMENT ON COLUMN merkle_roots.document_id IS 'Source document identifier';
        COMMENT ON COLUMN merkle_roots.root_hash IS 'SHA-256 hash of the Merkle tree root';
        COMMENT ON COLUMN merkle_roots.tree_depth IS 'Height of the Merkle tree (0 = single leaf)';
        COMMENT ON COLUMN merkle_roots.total_leaves IS 'Number of leaf nodes in the tree';
        COMMENT ON COLUMN merkle_roots.segmentation_level IS 'Level of text segmentation (sentence/paragraph/section)';
        COMMENT ON COLUMN merkle_roots.created_at IS 'Timestamp when the Merkle root was created';
        COMMENT ON COLUMN merkle_roots.metadata IS 'Additional metadata (title, author, etc.)';
    END IF;
END $$;
