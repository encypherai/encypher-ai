-- Migration: 008_create_merkle_proof_cache
-- Description: Create merkle_proof_cache table for caching generated Merkle proofs
-- Author: System
-- Date: 2025-10-28
-- NOTE: This table may be created by application code or other migrations.
--       Using 'id' as PK to match the pattern in 002_enterprise_api_schema.sql.

-- Create merkle_proof_cache table (uses 'id' as PK to match schema pattern)
CREATE TABLE IF NOT EXISTS merkle_proof_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_hash VARCHAR(64) NOT NULL,
    root_id UUID NOT NULL REFERENCES merkle_roots(id) ON DELETE CASCADE,
    proof_path JSONB NOT NULL,
    position_bits BYTEA NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '24 hours')
);

-- Create indexes for cache lookups (IF NOT EXISTS makes these idempotent)
CREATE INDEX IF NOT EXISTS idx_merkle_proof_cache_target_root ON merkle_proof_cache(target_hash, root_id);
CREATE INDEX IF NOT EXISTS idx_merkle_proof_cache_expires ON merkle_proof_cache(expires_at);

-- Add comments for documentation (only if columns exist)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'merkle_proof_cache' AND column_name = 'id') THEN
        COMMENT ON TABLE merkle_proof_cache IS 'Caches generated Merkle proofs for performance optimization';
        COMMENT ON COLUMN merkle_proof_cache.id IS 'Unique identifier for the cache entry';
        COMMENT ON COLUMN merkle_proof_cache.target_hash IS 'Hash of the leaf node being proved';
        COMMENT ON COLUMN merkle_proof_cache.root_id IS 'Reference to the Merkle root';
        COMMENT ON COLUMN merkle_proof_cache.proof_path IS 'Array of sibling hashes along the path to root';
        COMMENT ON COLUMN merkle_proof_cache.position_bits IS 'Binary representation of path (0=left, 1=right)';
        COMMENT ON COLUMN merkle_proof_cache.created_at IS 'When the proof was cached';
        COMMENT ON COLUMN merkle_proof_cache.expires_at IS 'When the cache entry expires (default 24 hours)';
    END IF;
END $$;
