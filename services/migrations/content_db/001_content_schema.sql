-- ============================================
-- ENCYPHER CONTENT DATABASE SCHEMA
-- Version: 1.0.0
-- Date: 2025-11-26
-- ============================================
-- 
-- This database stores verification/content data:
-- - Documents and signed content
-- - Merkle trees for content authentication
-- - Attribution reports
-- - Sentence records for plagiarism detection
--
-- This data is semi-public (verification queries don't require auth)
-- and can be scaled independently from customer data.
--
-- IMPORTANT: This database does NOT have foreign keys to the core
-- database. Organization IDs are stored as strings for reference
-- but not enforced at the database level.
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- DOCUMENTS
-- Signed documents with C2PA manifests
-- ============================================
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'doc_' || substr(md5(random()::text), 1, 16),
    organization_id VARCHAR(64) NOT NULL,  -- Reference to core.organizations (not enforced)
    
    -- Content
    title VARCHAR(500),
    url VARCHAR(1000),
    document_type VARCHAR(50) DEFAULT 'article'
        CHECK (document_type IN ('article', 'legal_brief', 'contract', 'ai_output', 'report', 'other')),
    total_sentences INTEGER NOT NULL DEFAULT 0,
    
    -- C2PA Manifest
    signed_text TEXT NOT NULL,
    manifest_cbor BYTEA,
    text_hash VARCHAR(64) NOT NULL,  -- SHA-256 of original text
    
    -- Metadata
    publication_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_org ON documents(organization_id);
CREATE INDEX IF NOT EXISTS idx_documents_org_date ON documents(organization_id, publication_date DESC);
CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(text_hash);

-- ============================================
-- SENTENCE RECORDS
-- Individual sentences for granular tracking
-- ============================================
CREATE TABLE IF NOT EXISTS sentence_records (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'sent_' || substr(md5(random()::text), 1, 16),
    document_id VARCHAR(64) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    organization_id VARCHAR(64) NOT NULL,  -- Reference to core.organizations (not enforced)
    
    -- Content
    sentence_text TEXT NOT NULL,
    sentence_hash VARCHAR(64) NOT NULL,  -- SHA-256 for matching
    sentence_index INTEGER NOT NULL,
    
    -- C2PA
    embedded_in_manifest BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sentences_hash ON sentence_records(sentence_hash);
CREATE INDEX IF NOT EXISTS idx_sentences_doc ON sentence_records(document_id);
CREATE INDEX IF NOT EXISTS idx_sentences_org ON sentence_records(organization_id);

-- ============================================
-- MERKLE ROOTS
-- Root hashes for content authentication trees
-- ============================================
CREATE TABLE IF NOT EXISTS merkle_roots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id VARCHAR(64) NOT NULL,  -- Reference to core.organizations (not enforced)
    document_id VARCHAR(64) NOT NULL,
    
    -- Tree Data
    root_hash VARCHAR(64) NOT NULL,
    algorithm VARCHAR(20) NOT NULL DEFAULT 'sha256',
    leaf_count INTEGER NOT NULL CHECK (leaf_count > 0),
    tree_depth INTEGER NOT NULL DEFAULT 0 CHECK (tree_depth >= 0),
    segmentation_level VARCHAR(50) NOT NULL DEFAULT 'sentence'
        CHECK (segmentation_level IN ('sentence', 'paragraph', 'section')),
    
    -- Metadata
    doc_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_merkle_roots_hash ON merkle_roots(root_hash);
CREATE INDEX IF NOT EXISTS idx_merkle_roots_doc ON merkle_roots(document_id);
CREATE INDEX IF NOT EXISTS idx_merkle_roots_org ON merkle_roots(organization_id);

-- ============================================
-- MERKLE SUBHASHES
-- All nodes in merkle trees for verification
-- ============================================
CREATE TABLE IF NOT EXISTS merkle_subhashes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    root_id UUID NOT NULL REFERENCES merkle_roots(id) ON DELETE CASCADE,
    
    -- Node Data
    hash_value VARCHAR(64) NOT NULL,
    node_type VARCHAR(20) NOT NULL CHECK (node_type IN ('leaf', 'branch', 'root')),
    depth_level INTEGER NOT NULL CHECK (depth_level >= 0),
    position_index INTEGER NOT NULL CHECK (position_index >= 0),
    
    -- Tree Structure
    parent_hash VARCHAR(64),
    left_child_hash VARCHAR(64),
    right_child_hash VARCHAR(64),
    
    -- Content (for leaves)
    text_content TEXT,
    segment_metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_subhashes_hash ON merkle_subhashes(hash_value);
CREATE INDEX IF NOT EXISTS idx_subhashes_root ON merkle_subhashes(root_id);

-- ============================================
-- MERKLE PROOF CACHE
-- Cached proofs for fast verification
-- ============================================
CREATE TABLE IF NOT EXISTS merkle_proof_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    root_id UUID NOT NULL REFERENCES merkle_roots(id) ON DELETE CASCADE,
    
    -- Proof Data
    leaf_hash VARCHAR(64) NOT NULL,
    proof_path JSONB NOT NULL,  -- Array of {hash, position} objects
    
    -- Cache Management
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '7 days'
);

CREATE INDEX IF NOT EXISTS idx_proof_cache_leaf ON merkle_proof_cache(leaf_hash);
CREATE INDEX IF NOT EXISTS idx_proof_cache_root ON merkle_proof_cache(root_id);
CREATE INDEX IF NOT EXISTS idx_proof_cache_expires ON merkle_proof_cache(expires_at);

-- ============================================
-- CONTENT REFERENCES
-- Minimal signed embeddings for verification
-- ============================================
CREATE TABLE IF NOT EXISTS content_references (
    id BIGSERIAL PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL,  -- Reference to core.organizations (not enforced)
    document_id VARCHAR(64) NOT NULL,
    merkle_root_id UUID REFERENCES merkle_roots(id) ON DELETE CASCADE,
    
    -- Reference Data
    leaf_hash VARCHAR(64) NOT NULL,
    leaf_index INTEGER NOT NULL CHECK (leaf_index >= 0),
    signature_hash VARCHAR(64) NOT NULL,
    
    -- Content
    text_content TEXT,
    text_preview VARCHAR(200),
    
    -- C2PA
    c2pa_manifest_url VARCHAR(500),
    c2pa_manifest_hash VARCHAR(64),
    manifest_data JSONB,
    
    -- Licensing
    license_type VARCHAR(100),
    license_url VARCHAR(500),
    
    -- Instance Tracking
    instance_id VARCHAR(100),
    previous_instance_id VARCHAR(100),
    
    -- Metadata
    embedding_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_content_refs_hash ON content_references(leaf_hash);
CREATE INDEX IF NOT EXISTS idx_content_refs_org_doc ON content_references(organization_id, document_id);
CREATE INDEX IF NOT EXISTS idx_content_refs_created ON content_references(created_at DESC);

-- ============================================
-- ATTRIBUTION REPORTS
-- Plagiarism detection and content matching
-- ============================================
CREATE TABLE IF NOT EXISTS attribution_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id VARCHAR(64) NOT NULL,  -- Reference to core.organizations (not enforced)
    
    -- Target
    target_document_id VARCHAR(64),
    target_text_hash VARCHAR(64),
    
    -- Results
    total_segments INTEGER NOT NULL CHECK (total_segments >= 0),
    matched_segments INTEGER NOT NULL CHECK (matched_segments >= 0),
    source_documents JSONB DEFAULT '[]',
    heat_map_data JSONB,
    
    -- Metadata
    report_metadata JSONB DEFAULT '{}',
    scan_timestamp TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT chk_matched_le_total CHECK (matched_segments <= total_segments)
);

CREATE INDEX IF NOT EXISTS idx_attribution_org ON attribution_reports(organization_id);
CREATE INDEX IF NOT EXISTS idx_attribution_scan ON attribution_reports(scan_timestamp DESC);

-- ============================================
-- VERIFICATION
-- ============================================
DO $$
BEGIN
    RAISE NOTICE 'Content database schema created successfully';
END $$;
