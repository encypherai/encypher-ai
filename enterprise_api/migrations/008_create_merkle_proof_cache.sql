-- Migration: 008_create_merkle_proof_cache
-- Description: Create merkle_proof_cache table for caching generated Merkle proofs
-- Author: System
-- Date: 2025-10-28

-- Create merkle_proof_cache table
CREATE TABLE IF NOT EXISTS merkle_proof_cache (
    cache_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_hash VARCHAR(64) NOT NULL,
    root_id UUID NOT NULL,
    proof_path JSONB NOT NULL,
    position_bits BYTEA NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
    
    -- Foreign key constraint
    CONSTRAINT fk_merkle_proof_cache_root 
        FOREIGN KEY (root_id) 
        REFERENCES merkle_roots(root_id) 
        ON DELETE CASCADE
);

-- Create indexes for cache lookups
CREATE INDEX IF NOT EXISTS idx_merkle_proof_cache_target_root 
    ON merkle_proof_cache(target_hash, root_id);

CREATE INDEX IF NOT EXISTS idx_merkle_proof_cache_expires 
    ON merkle_proof_cache(expires_at);

-- Add comments for documentation
COMMENT ON TABLE merkle_proof_cache IS 'Caches generated Merkle proofs for performance optimization';
COMMENT ON COLUMN merkle_proof_cache.cache_id IS 'Unique identifier for the cache entry';
COMMENT ON COLUMN merkle_proof_cache.target_hash IS 'Hash of the leaf node being proved';
COMMENT ON COLUMN merkle_proof_cache.root_id IS 'Reference to the Merkle root';
COMMENT ON COLUMN merkle_proof_cache.proof_path IS 'Array of sibling hashes along the path to root';
COMMENT ON COLUMN merkle_proof_cache.position_bits IS 'Binary representation of path (0=left, 1=right)';
COMMENT ON COLUMN merkle_proof_cache.created_at IS 'When the proof was cached';
COMMENT ON COLUMN merkle_proof_cache.expires_at IS 'When the cache entry expires (default 24 hours)';
