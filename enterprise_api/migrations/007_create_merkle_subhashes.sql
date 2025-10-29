-- Migration: 007_create_merkle_subhashes
-- Description: Create merkle_subhashes table for indexing all hashes in Merkle trees
-- Author: System
-- Date: 2025-10-28

-- Create merkle_subhashes table
CREATE TABLE IF NOT EXISTS merkle_subhashes (
    subhash_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hash_value VARCHAR(64) NOT NULL,
    root_id UUID NOT NULL,
    node_type VARCHAR(20) NOT NULL CHECK (node_type IN ('leaf', 'branch', 'root')),
    depth_level INTEGER NOT NULL CHECK (depth_level >= 0),
    position_index INTEGER NOT NULL CHECK (position_index >= 0),
    parent_hash VARCHAR(64),
    left_child_hash VARCHAR(64),
    right_child_hash VARCHAR(64),
    text_content TEXT,
    segment_metadata JSONB DEFAULT '{}',
    
    -- Foreign key constraint
    CONSTRAINT fk_merkle_subhashes_root 
        FOREIGN KEY (root_id) 
        REFERENCES merkle_roots(root_id) 
        ON DELETE CASCADE
);

-- Create indexes for efficient hash lookups (CRITICAL for performance)
CREATE INDEX IF NOT EXISTS idx_merkle_subhashes_hash_value 
    ON merkle_subhashes(hash_value);

CREATE INDEX IF NOT EXISTS idx_merkle_subhashes_root_id 
    ON merkle_subhashes(root_id);

CREATE INDEX IF NOT EXISTS idx_merkle_subhashes_node_type 
    ON merkle_subhashes(node_type);

-- Composite index for combined queries
CREATE INDEX IF NOT EXISTS idx_merkle_subhashes_hash_root 
    ON merkle_subhashes(hash_value, root_id);

-- Index for tree traversal queries
CREATE INDEX IF NOT EXISTS idx_merkle_subhashes_parent 
    ON merkle_subhashes(parent_hash) 
    WHERE parent_hash IS NOT NULL;

-- Add comments for documentation
COMMENT ON TABLE merkle_subhashes IS 'Indexes all hashes (leaves and branches) in Merkle trees for efficient lookup';
COMMENT ON COLUMN merkle_subhashes.subhash_id IS 'Unique identifier for the sub-hash entry';
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
