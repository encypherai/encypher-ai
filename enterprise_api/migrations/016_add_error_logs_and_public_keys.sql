-- Migration 016: Add error_logs and public_keys tables
-- Date: 2024-12-23
-- Description: Add tables for admin error log viewing and BYOK public key registration

-- ============================================================================
-- Error Logs Table
-- Stores API errors for admin monitoring and debugging
-- ============================================================================

CREATE TABLE IF NOT EXISTS error_logs (
    id VARCHAR(64) PRIMARY KEY,
    
    -- User/org context (nullable for unauthenticated requests)
    user_id VARCHAR(64),
    organization_id VARCHAR(64),
    api_key_id VARCHAR(64),
    
    -- Request info
    endpoint VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL,
    
    -- Error details
    status_code INTEGER NOT NULL,
    error_code VARCHAR(50),
    error_message TEXT NOT NULL,
    error_details TEXT,
    
    -- Request metadata
    request_id VARCHAR(64),
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    
    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for error_logs
CREATE INDEX IF NOT EXISTS idx_error_logs_user_id ON error_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_error_logs_organization_id ON error_logs(organization_id);
CREATE INDEX IF NOT EXISTS idx_error_logs_status_code ON error_logs(status_code);
CREATE INDEX IF NOT EXISTS idx_error_logs_error_code ON error_logs(error_code);
CREATE INDEX IF NOT EXISTS idx_error_logs_request_id ON error_logs(request_id);
CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp ON error_logs(timestamp);

-- ============================================================================
-- Public Keys Table
-- Stores BYOK public keys for enterprise customers
-- ============================================================================

CREATE TABLE IF NOT EXISTS public_keys (
    id VARCHAR(64) PRIMARY KEY,
    
    -- Owner
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Key metadata
    key_name VARCHAR(255),
    key_algorithm VARCHAR(20) NOT NULL DEFAULT 'Ed25519',
    key_fingerprint VARCHAR(128) NOT NULL UNIQUE,
    
    -- The actual public key
    public_key_pem TEXT NOT NULL,
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Usage tracking
    verification_count INTEGER NOT NULL DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    
    -- Lifecycle
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_reason VARCHAR(500)
);

-- Indexes for public_keys
CREATE INDEX IF NOT EXISTS idx_public_keys_organization_id ON public_keys(organization_id);
CREATE INDEX IF NOT EXISTS idx_public_keys_fingerprint ON public_keys(key_fingerprint);
CREATE INDEX IF NOT EXISTS idx_public_keys_is_active ON public_keys(is_active);

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE error_logs IS 'API error logs for admin monitoring and debugging';
COMMENT ON TABLE public_keys IS 'BYOK public keys registered by enterprise customers for signature verification';

COMMENT ON COLUMN error_logs.status_code IS 'HTTP status code returned';
COMMENT ON COLUMN error_logs.error_code IS 'Application-specific error code (e.g., E_INTERNAL)';
COMMENT ON COLUMN error_logs.request_id IS 'Correlation ID for request tracing';

COMMENT ON COLUMN public_keys.key_fingerprint IS 'SHA-256 fingerprint of the public key for lookup';
COMMENT ON COLUMN public_keys.is_primary IS 'Whether this is the primary signing key for the organization';
COMMENT ON COLUMN public_keys.verification_count IS 'Number of times this key has been used for verification';
