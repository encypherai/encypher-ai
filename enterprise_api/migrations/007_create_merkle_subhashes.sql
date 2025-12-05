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

-- Comments are optional and may fail if table structure differs - that's OK
