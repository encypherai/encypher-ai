-- Migration: 006_create_merkle_roots
-- Description: Create merkle_roots table for storing Merkle tree root hashes
-- Author: System
-- Date: 2025-10-28

-- Create merkle_roots table
CREATE TABLE IF NOT EXISTS merkle_roots (
    root_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id VARCHAR(255) NOT NULL,
    document_id VARCHAR(255) NOT NULL,
    root_hash VARCHAR(64) NOT NULL,
    tree_depth INTEGER NOT NULL CHECK (tree_depth >= 0),
    total_leaves INTEGER NOT NULL CHECK (total_leaves > 0),
    segmentation_level VARCHAR(50) NOT NULL CHECK (segmentation_level IN ('sentence', 'paragraph', 'section')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    
    -- Foreign key constraint
    CONSTRAINT fk_merkle_roots_organization 
        FOREIGN KEY (organization_id) 
        REFERENCES organizations(organization_id) 
        ON DELETE CASCADE
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_merkle_roots_root_hash 
    ON merkle_roots(root_hash);

CREATE INDEX IF NOT EXISTS idx_merkle_roots_document_id 
    ON merkle_roots(document_id);

CREATE INDEX IF NOT EXISTS idx_merkle_roots_org_level 
    ON merkle_roots(organization_id, segmentation_level);

CREATE INDEX IF NOT EXISTS idx_merkle_roots_created_at 
    ON merkle_roots(created_at DESC);

-- Add comment for documentation
COMMENT ON TABLE merkle_roots IS 'Stores Merkle tree root hashes for source documents at different segmentation levels';
COMMENT ON COLUMN merkle_roots.root_id IS 'Unique identifier for the Merkle root';
COMMENT ON COLUMN merkle_roots.organization_id IS 'Organization that owns this document';
COMMENT ON COLUMN merkle_roots.document_id IS 'Source document identifier';
COMMENT ON COLUMN merkle_roots.root_hash IS 'SHA-256 hash of the Merkle tree root';
COMMENT ON COLUMN merkle_roots.tree_depth IS 'Height of the Merkle tree (0 = single leaf)';
COMMENT ON COLUMN merkle_roots.total_leaves IS 'Number of leaf nodes in the tree';
COMMENT ON COLUMN merkle_roots.segmentation_level IS 'Level of text segmentation (sentence/paragraph/section)';
COMMENT ON COLUMN merkle_roots.created_at IS 'Timestamp when the Merkle root was created';
COMMENT ON COLUMN merkle_roots.metadata IS 'Additional metadata (title, author, etc.)';
