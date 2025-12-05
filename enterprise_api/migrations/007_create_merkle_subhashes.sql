-- Migration: 007_create_merkle_subhashes
-- Description: Create merkle_subhashes table for indexing all hashes in Merkle trees
-- Author: System
-- Date: 2025-10-28
-- NOTE: This table is now created by services/migrations/002_enterprise_api_schema.sql
--       This migration is kept for backwards compatibility but is essentially a no-op.

-- Create merkle_subhashes table (uses 'id' as PK to match 002_enterprise_api_schema.sql)
CREATE TABLE IF NOT EXISTS merkle_subhashes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    root_id UUID NOT NULL REFERENCES merkle_roots(id) ON DELETE CASCADE,
    hash_value VARCHAR(64) NOT NULL,
    node_type VARCHAR(20) NOT NULL CHECK (node_type IN ('leaf', 'branch', 'root')),
    depth_level INTEGER NOT NULL CHECK (depth_level >= 0),
    position_index INTEGER NOT NULL CHECK (position_index >= 0),
    parent_hash VARCHAR(64),
    left_child_hash VARCHAR(64),
    right_child_hash VARCHAR(64),
    text_content TEXT,
    segment_metadata JSONB DEFAULT '{}'
);

-- Create indexes for efficient hash lookups (IF NOT EXISTS makes these idempotent)
CREATE INDEX IF NOT EXISTS idx_subhashes_hash ON merkle_subhashes(hash_value);
CREATE INDEX IF NOT EXISTS idx_subhashes_root ON merkle_subhashes(root_id);

-- Add comments for documentation (only if columns exist)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'merkle_subhashes' AND column_name = 'id') THEN
        COMMENT ON TABLE merkle_subhashes IS 'Indexes all hashes (leaves and branches) in Merkle trees for efficient lookup';
        COMMENT ON COLUMN merkle_subhashes.id IS 'Unique identifier for the sub-hash entry';
        COMMENT ON COLUMN merkle_subhashes.hash_value IS 'SHA-256 hash value of the node';
        COMMENT ON COLUMN merkle_subhashes.root_id IS 'Reference to the Merkle root this hash belongs to';
        COMMENT ON COLUMN merkle_subhashes.node_type IS 'Type of node: leaf (text segment), branch (intermediate), or root';
        COMMENT ON COLUMN merkle_subhashes.depth_level IS 'Distance from root (root=0, children=1, etc.)';
        COMMENT ON COLUMN merkle_subhashes.position_index IS 'Position within the level (left-to-right, 0-indexed)';
        COMMENT ON COLUMN merkle_subhashes.parent_hash IS 'Hash of parent node (NULL for root)';
        COMMENT ON COLUMN merkle_subhashes.left_child_hash IS 'Hash of left child (NULL for leaves)';
        COMMENT ON COLUMN merkle_subhashes.right_child_hash IS 'Hash of right child (NULL for leaves)';
        COMMENT ON COLUMN merkle_subhashes.text_content IS 'Original text content (only for leaf nodes)';
        COMMENT ON COLUMN merkle_subhashes.segment_metadata IS 'Additional metadata (original index, length, etc.)';
    END IF;
END $$;
