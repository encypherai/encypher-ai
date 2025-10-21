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
