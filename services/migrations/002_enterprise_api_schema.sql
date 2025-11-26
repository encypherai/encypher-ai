-- ============================================
-- ENTERPRISE API SCHEMA
-- Version: 1.0.0
-- Date: 2025-11-25
-- ============================================
-- 
-- Tables for C2PA signing, verification, and content tracking
-- ============================================

-- ============================================
-- DOCUMENTS
-- Signed documents with C2PA manifests
-- ============================================
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'doc_' || substr(md5(random()::text), 1, 16),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
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
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
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
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    document_id VARCHAR(64) NOT NULL,
    
    -- Tree Data
    root_hash VARCHAR(64) NOT NULL,
    tree_depth INTEGER NOT NULL CHECK (tree_depth >= 0),
    total_leaves INTEGER NOT NULL CHECK (total_leaves > 0),
    segmentation_level VARCHAR(50) NOT NULL 
        CHECK (segmentation_level IN ('sentence', 'paragraph', 'section')),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
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
-- CONTENT REFERENCES
-- Minimal signed embeddings for verification
-- ============================================
CREATE TABLE IF NOT EXISTS content_references (
    id BIGSERIAL PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
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
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
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
-- BATCH REQUESTS
-- Bulk signing/verification operations
-- ============================================
CREATE TABLE IF NOT EXISTS batch_requests (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'batch_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    api_key_id VARCHAR(64) REFERENCES api_keys(id),
    
    -- Request Details
    request_type VARCHAR(16) NOT NULL CHECK (request_type IN ('sign', 'verify')),
    mode VARCHAR(32) NOT NULL,
    segmentation_level VARCHAR(32),
    
    -- Idempotency
    idempotency_key VARCHAR(128) NOT NULL,
    payload_hash VARCHAR(64) NOT NULL,
    
    -- Status
    status VARCHAR(16) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    
    -- Counts
    item_count INTEGER NOT NULL,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    
    -- Error Info
    error_code VARCHAR(64),
    error_message TEXT,
    
    -- Metadata
    request_metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL,
    
    UNIQUE(organization_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_batch_org_status ON batch_requests(organization_id, status);
CREATE INDEX IF NOT EXISTS idx_batch_expires ON batch_requests(expires_at);

-- ============================================
-- BATCH ITEMS
-- Individual items in batch operations
-- ============================================
CREATE TABLE IF NOT EXISTS batch_items (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'bi_' || substr(md5(random()::text), 1, 12),
    batch_request_id VARCHAR(64) NOT NULL REFERENCES batch_requests(id) ON DELETE CASCADE,
    document_id VARCHAR(64) NOT NULL,
    
    -- Status
    status VARCHAR(16) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    mode VARCHAR(32) NOT NULL,
    
    -- Results
    duration_ms INTEGER,
    error_code VARCHAR(64),
    error_message TEXT,
    statistics JSONB,
    result_payload JSONB,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_batch_items_batch ON batch_items(batch_request_id);
CREATE INDEX IF NOT EXISTS idx_batch_items_doc ON batch_items(document_id);

-- ============================================
-- CERTIFICATE LIFECYCLE
-- SSL.com certificate tracking
-- ============================================
CREATE TABLE IF NOT EXISTS certificate_lifecycle (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'cert_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- SSL.com Integration
    ssl_order_id VARCHAR(100) UNIQUE,
    order_status VARCHAR(50) DEFAULT 'pending'
        CHECK (order_status IN ('pending', 'pending_validation', 'issued', 'renewed', 'expired', 'revoked')),
    validation_url TEXT,
    
    -- Lifecycle Dates
    ordered_at TIMESTAMPTZ,
    issued_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    renewal_initiated_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cert_lifecycle_org ON certificate_lifecycle(organization_id);
CREATE INDEX IF NOT EXISTS idx_cert_lifecycle_expires ON certificate_lifecycle(expires_at);

-- ============================================
-- AUDIT LOGS
-- Compliance and security tracking
-- ============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'audit_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL,
    
    -- Event
    action VARCHAR(64) NOT NULL,
    actor_id VARCHAR(64) NOT NULL,
    actor_type VARCHAR(32) NOT NULL CHECK (actor_type IN ('user', 'api_key', 'system')),
    
    -- Resource
    resource_type VARCHAR(64) NOT NULL,
    resource_id VARCHAR(64),
    
    -- Context
    details JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(512),
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_org_created ON audit_logs(organization_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(organization_id, action);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_logs(actor_id);

-- ============================================
-- C2PA CUSTOM ASSERTION SCHEMAS
-- For enterprise custom assertions
-- ============================================
CREATE TABLE IF NOT EXISTS c2pa_assertion_schemas (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'schema_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Schema Definition
    name VARCHAR(255) NOT NULL,
    label VARCHAR(255) NOT NULL,  -- C2PA assertion label
    version VARCHAR(20) NOT NULL DEFAULT '1.0',
    json_schema JSONB NOT NULL,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(organization_id, label, version)
);

CREATE INDEX IF NOT EXISTS idx_c2pa_schemas_org ON c2pa_assertion_schemas(organization_id);

-- ============================================
-- C2PA CUSTOM ASSERTION TEMPLATES
-- Reusable assertion templates
-- ============================================
CREATE TABLE IF NOT EXISTS c2pa_assertion_templates (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'tmpl_' || substr(md5(random()::text), 1, 12),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    schema_id VARCHAR(64) NOT NULL REFERENCES c2pa_assertion_schemas(id) ON DELETE CASCADE,
    
    -- Template
    name VARCHAR(255) NOT NULL,
    template_data JSONB NOT NULL,
    
    -- Status
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_c2pa_templates_org ON c2pa_assertion_templates(organization_id);
CREATE INDEX IF NOT EXISTS idx_c2pa_templates_schema ON c2pa_assertion_templates(schema_id);

-- ============================================
-- VERIFICATION
-- ============================================
DO $$
BEGIN
    RAISE NOTICE 'Enterprise API schema created successfully';
END $$;
