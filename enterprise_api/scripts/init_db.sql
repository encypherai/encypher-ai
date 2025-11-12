-- Encypher Enterprise API Database Schema
-- PostgreSQL 15+

-- Organizations (publishers, legal/finance, AI labs)
CREATE TABLE IF NOT EXISTS organizations (
    organization_id VARCHAR(100) PRIMARY KEY,
    organization_name VARCHAR(500) NOT NULL,
    organization_type VARCHAR(50) NOT NULL, -- 'publisher', 'legal_finance', 'ai_lab', 'enterprise'
    email VARCHAR(255) NOT NULL UNIQUE,
    tier VARCHAR(50) NOT NULL DEFAULT 'free', -- 'free', 'business', 'enterprise'

    -- Certificate management (SSL.com)
    certificate_pem TEXT,
    certificate_chain TEXT,
    certificate_status VARCHAR(32) DEFAULT 'active',
    certificate_rotated_at TIMESTAMP,
    private_key_encrypted BYTEA, -- AES-256 encrypted (for Encypher-managed keys)
    certificate_expiry TIMESTAMP,
    ssl_order_id VARCHAR(100),

    -- Usage tracking
    monthly_quota INTEGER DEFAULT 1000,
    documents_signed INTEGER DEFAULT 0,
    sentences_signed INTEGER DEFAULT 0,
    api_calls_this_month INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_org_type ON organizations(organization_type);
CREATE INDEX IF NOT EXISTS idx_cert_expiry ON organizations(certificate_expiry);
CREATE INDEX IF NOT EXISTS idx_tier ON organizations(tier);

-- Documents (articles, legal briefs, AI outputs, contracts)
CREATE TABLE IF NOT EXISTS documents (
    document_id VARCHAR(100) PRIMARY KEY,
    organization_id VARCHAR(100) NOT NULL,
    title VARCHAR(500),
    url VARCHAR(1000),
    document_type VARCHAR(50) DEFAULT 'article', -- 'article', 'legal_brief', 'contract', 'ai_output'
    total_sentences INTEGER NOT NULL,

    -- C2PA manifest (from encypher-ai library)
    signed_text TEXT NOT NULL, -- Text with embedded C2PA manifest
    manifest_cbor BYTEA, -- Extracted manifest for storage/analysis
    text_hash VARCHAR(64) NOT NULL, -- SHA-256 of original text (for tamper detection)

    -- Metadata
    publication_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (organization_id) REFERENCES organizations(organization_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_org_date ON documents(organization_id, publication_date);
CREATE INDEX IF NOT EXISTS idx_doc_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_text_hash ON documents(text_hash);

-- Sentence records (for granular tracking and lookup)
CREATE TABLE IF NOT EXISTS sentence_records (
    sentence_id VARCHAR(100) PRIMARY KEY,
    document_id VARCHAR(100) NOT NULL,
    organization_id VARCHAR(100) NOT NULL,

    -- Content
    sentence_text TEXT NOT NULL,
    sentence_hash VARCHAR(64) NOT NULL, -- SHA-256 for matching
    sentence_index INTEGER NOT NULL,

    -- C2PA embedding
    embedded_in_manifest BOOLEAN DEFAULT TRUE,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE,
    FOREIGN KEY (organization_id) REFERENCES organizations(organization_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sentence_hash ON sentence_records(sentence_hash);
CREATE INDEX IF NOT EXISTS idx_document ON sentence_records(document_id);
CREATE INDEX IF NOT EXISTS idx_organization ON sentence_records(organization_id);

-- API keys (for authentication)
CREATE TABLE IF NOT EXISTS api_keys (
    api_key VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(100) NOT NULL,
    key_name VARCHAR(200), -- Optional: "Production Key", "Testing Key"

    -- Permissions
    can_sign BOOLEAN DEFAULT TRUE,
    can_verify BOOLEAN DEFAULT TRUE,
    can_lookup BOOLEAN DEFAULT TRUE,

    -- Lifecycle
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (organization_id) REFERENCES organizations(organization_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_api_key_organization ON api_keys(organization_id);
CREATE INDEX IF NOT EXISTS idx_api_key_revoked ON api_keys(revoked);

-- SSL.com certificate lifecycle tracking
CREATE TABLE IF NOT EXISTS certificate_lifecycle (
    cert_id VARCHAR(100) PRIMARY KEY,
    organization_id VARCHAR(100) NOT NULL,

    -- SSL.com integration
    ssl_order_id VARCHAR(100) UNIQUE,
    order_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'pending_validation', 'issued', 'renewed', 'expired', 'revoked'
    validation_url TEXT,

    -- Lifecycle dates
    ordered_at TIMESTAMP,
    issued_at TIMESTAMP,
    expires_at TIMESTAMP,
    renewal_initiated_at TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (organization_id) REFERENCES organizations(organization_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cert_org ON certificate_lifecycle(organization_id);
CREATE INDEX IF NOT EXISTS idx_cert_expiry ON certificate_lifecycle(expires_at);
CREATE INDEX IF NOT EXISTS idx_cert_status ON certificate_lifecycle(order_status);

-- Audit log (for compliance and debugging)
CREATE TABLE IF NOT EXISTS audit_log (
    log_id SERIAL PRIMARY KEY,
    organization_id VARCHAR(100),

    -- Event details
    event_type VARCHAR(50) NOT NULL, -- 'sign', 'verify', 'lookup', 'api_key_created', 'certificate_issued'
    event_data JSONB,

    -- Request context
    ip_address VARCHAR(45),
    user_agent TEXT,
    api_key_used VARCHAR(64),

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (organization_id) REFERENCES organizations(organization_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_organization ON audit_log(organization_id);
CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_log(created_at);

-- Merkle tree roots (for content authentication)
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
    
    CONSTRAINT fk_merkle_roots_organization 
        FOREIGN KEY (organization_id) 
        REFERENCES organizations(organization_id) 
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_merkle_roots_root_hash ON merkle_roots(root_hash);
CREATE INDEX IF NOT EXISTS idx_merkle_roots_document_id ON merkle_roots(document_id);
CREATE INDEX IF NOT EXISTS idx_merkle_roots_org_level ON merkle_roots(organization_id, segmentation_level);
CREATE INDEX IF NOT EXISTS idx_merkle_roots_created_at ON merkle_roots(created_at DESC);

-- Merkle tree subhashes (for indexing all hashes in trees)
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
    
    CONSTRAINT fk_merkle_subhashes_root 
        FOREIGN KEY (root_id) 
        REFERENCES merkle_roots(root_id) 
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_merkle_subhashes_hash_value ON merkle_subhashes(hash_value);
CREATE INDEX IF NOT EXISTS idx_merkle_subhashes_root_id ON merkle_subhashes(root_id);
CREATE INDEX IF NOT EXISTS idx_merkle_subhashes_node_type ON merkle_subhashes(node_type);
CREATE INDEX IF NOT EXISTS idx_merkle_subhashes_hash_root ON merkle_subhashes(hash_value, root_id);
CREATE INDEX IF NOT EXISTS idx_merkle_subhashes_parent ON merkle_subhashes(parent_hash) WHERE parent_hash IS NOT NULL;

-- Content references (for minimal signed embeddings)
CREATE TABLE IF NOT EXISTS content_references (
    ref_id BIGINT PRIMARY KEY,
    merkle_root_id UUID NOT NULL,
    leaf_hash VARCHAR(64) NOT NULL,
    leaf_index INTEGER NOT NULL,
    organization_id VARCHAR(255) NOT NULL,
    document_id VARCHAR(255) NOT NULL,
    text_content TEXT,
    text_preview VARCHAR(200),
    c2pa_manifest_url VARCHAR(500),
    c2pa_manifest_hash VARCHAR(64),
    license_type VARCHAR(100),
    license_url VARCHAR(500),
    signature_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    embedding_metadata JSONB DEFAULT '{}',
    
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

CREATE INDEX IF NOT EXISTS idx_content_refs_leaf_hash ON content_references(leaf_hash);
CREATE INDEX IF NOT EXISTS idx_content_refs_org_doc ON content_references(organization_id, document_id);
CREATE INDEX IF NOT EXISTS idx_content_refs_merkle_root ON content_references(merkle_root_id);
CREATE INDEX IF NOT EXISTS idx_content_refs_created ON content_references(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_refs_org_created ON content_references(organization_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_refs_expires ON content_references(expires_at) WHERE expires_at IS NOT NULL;

-- Merkle proof cache (for performance optimization)
CREATE TABLE IF NOT EXISTS merkle_proof_cache (
    cache_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_hash VARCHAR(64) NOT NULL,
    root_id UUID NOT NULL,
    proof_path JSONB NOT NULL,
    position_bits BYTEA NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
    
    CONSTRAINT fk_merkle_proof_cache_root 
        FOREIGN KEY (root_id) 
        REFERENCES merkle_roots(root_id) 
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_merkle_proof_cache_target_root ON merkle_proof_cache(target_hash, root_id);
CREATE INDEX IF NOT EXISTS idx_merkle_proof_cache_expires ON merkle_proof_cache(expires_at);

-- Attribution reports (for plagiarism detection)
CREATE TABLE IF NOT EXISTS attribution_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id VARCHAR(255) NOT NULL,
    target_document_id VARCHAR(255),
    target_text_hash VARCHAR(64),
    scan_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_segments INTEGER NOT NULL CHECK (total_segments >= 0),
    matched_segments INTEGER NOT NULL CHECK (matched_segments >= 0),
    source_documents JSONB NOT NULL DEFAULT '[]',
    heat_map_data JSONB,
    report_metadata JSONB DEFAULT '{}',
    
    CONSTRAINT fk_attribution_reports_organization 
        FOREIGN KEY (organization_id) 
        REFERENCES organizations(organization_id) 
        ON DELETE CASCADE,
    CONSTRAINT chk_matched_le_total 
        CHECK (matched_segments <= total_segments)
);

CREATE INDEX IF NOT EXISTS idx_attribution_reports_org_timestamp ON attribution_reports(organization_id, scan_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_attribution_reports_target_doc ON attribution_reports(target_document_id) WHERE target_document_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_attribution_reports_scan_timestamp ON attribution_reports(scan_timestamp DESC);
