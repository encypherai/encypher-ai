-- Migration: Create content_references table for minimal signed embeddings
-- Version: 011
-- Description: Stores compact reference IDs that link sentences to Merkle trees
--              Enables portable, signed embeddings that travel with content
-- Dependencies: 006_create_merkle_roots.sql, organizations table

-- ============================================================================
-- Table: content_references
-- ============================================================================

CREATE TABLE IF NOT EXISTS content_references (
    -- Primary identifier (8-byte integer for compact embeddings)
    ref_id BIGINT PRIMARY KEY,
    
    -- Link to Merkle tree system
    merkle_root_id UUID NOT NULL,
    leaf_hash VARCHAR(64) NOT NULL,
    leaf_index INTEGER NOT NULL,
    
    -- Document metadata
    organization_id VARCHAR(255) NOT NULL,
    document_id VARCHAR(255) NOT NULL,
    
    -- Content information
    text_content TEXT,
    text_preview VARCHAR(200),
    
    -- C2PA and licensing
    c2pa_manifest_url VARCHAR(500),
    c2pa_manifest_hash VARCHAR(64),
    license_type VARCHAR(100),
    license_url VARCHAR(500),
    
    -- Verification data
    signature_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Additional metadata
    embedding_metadata JSONB DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT chk_leaf_index_positive CHECK (leaf_index >= 0),
    CONSTRAINT fk_content_refs_merkle_root 
        FOREIGN KEY (merkle_root_id) 
        REFERENCES merkle_roots(root_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_content_refs_organization 
        FOREIGN KEY (organization_id) 
        REFERENCES organizations(organization_id) 
        ON DELETE CASCADE
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Primary lookup by ref_id (already indexed as PRIMARY KEY)

-- Lookup by leaf hash (for reverse verification)
CREATE INDEX idx_content_refs_leaf_hash 
    ON content_references(leaf_hash);

-- Lookup by organization and document
CREATE INDEX idx_content_refs_org_doc 
    ON content_references(organization_id, document_id);

-- Lookup by Merkle root (for batch operations)
CREATE INDEX idx_content_refs_merkle_root 
    ON content_references(merkle_root_id);

-- Lookup by creation date (for analytics and cleanup)
CREATE INDEX idx_content_refs_created 
    ON content_references(created_at DESC);

-- Composite index for organization analytics
CREATE INDEX idx_content_refs_org_created 
    ON content_references(organization_id, created_at DESC);

-- Index for expiration cleanup jobs
CREATE INDEX idx_content_refs_expires 
    ON content_references(expires_at) 
    WHERE expires_at IS NOT NULL;

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE content_references IS 
    'Stores minimal signed embeddings (28-byte references) that link text segments to Merkle trees. Enables portable content authentication.';

COMMENT ON COLUMN content_references.ref_id IS 
    '64-bit reference ID encoded as 8 hex characters in embeddings. Format: timestamp(2B) + sequence(2B) + random(2B) + checksum(2B)';

COMMENT ON COLUMN content_references.signature_hash IS 
    'HMAC-SHA256 signature (truncated to 8 bytes) for verification. Computed from ref_id + secret_key.';

COMMENT ON COLUMN content_references.text_preview IS 
    'First 200 characters of text_content for display in public verification API';

COMMENT ON COLUMN content_references.embedding_metadata IS 
    'Additional metadata: embedding_method, format, version, etc.';

-- ============================================================================
-- Verification
-- ============================================================================

-- Verify table was created
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'content_references'
    ) THEN
        RAISE EXCEPTION 'Table content_references was not created successfully';
    END IF;
    
    RAISE NOTICE 'Migration 011: content_references table created successfully';
END $$;
