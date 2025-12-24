-- Migration 017: Add webhooks and webhook_deliveries tables
-- Date: 2024-12-23
-- Description: Adds tables for webhook event notifications

-- ============================================================================
-- Webhooks Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS webhooks (
    id VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Webhook configuration
    url VARCHAR(2048) NOT NULL,
    events TEXT[] NOT NULL DEFAULT '{}',
    secret_hash VARCHAR(128),
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Delivery stats
    success_count INTEGER NOT NULL DEFAULT 0,
    failure_count INTEGER NOT NULL DEFAULT 0,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    last_success_at TIMESTAMP WITH TIME ZONE,
    last_failure_at TIMESTAMP WITH TIME ZONE,
    last_failure_reason TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for webhooks
CREATE INDEX IF NOT EXISTS idx_webhooks_organization_id ON webhooks(organization_id);
CREATE INDEX IF NOT EXISTS idx_webhooks_is_active ON webhooks(is_active) WHERE is_active = TRUE;

-- ============================================================================
-- Webhook Deliveries Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS webhook_deliveries (
    id VARCHAR(64) PRIMARY KEY,
    webhook_id VARCHAR(64) NOT NULL REFERENCES webhooks(id) ON DELETE CASCADE,
    organization_id VARCHAR(64) NOT NULL,
    
    -- Event details
    event_type VARCHAR(64) NOT NULL,
    event_id VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    
    -- Delivery status
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    
    -- Response details
    response_status_code INTEGER,
    response_body TEXT,
    response_time_ms INTEGER,
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    delivered_at TIMESTAMP WITH TIME ZONE,
    next_retry_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for webhook_deliveries
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_webhook_id ON webhook_deliveries(webhook_id);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_organization_id ON webhook_deliveries(organization_id);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_event_type ON webhook_deliveries(event_type);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_status ON webhook_deliveries(status);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_created_at ON webhook_deliveries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_next_retry ON webhook_deliveries(next_retry_at) 
    WHERE status = 'pending' AND next_retry_at IS NOT NULL;

-- ============================================================================
-- Add columns to documents table for soft delete
-- ============================================================================

ALTER TABLE documents ADD COLUMN IF NOT EXISTS deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;

-- Index for filtering out deleted documents
CREATE INDEX IF NOT EXISTS idx_documents_deleted ON documents(deleted) WHERE deleted = FALSE;

-- ============================================================================
-- Add columns to api_keys table for key management
-- ============================================================================

ALTER TABLE api_keys ADD COLUMN IF NOT EXISTS key_prefix VARCHAR(20);
ALTER TABLE api_keys ADD COLUMN IF NOT EXISTS revoked_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE api_keys ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

-- Update existing keys to have a prefix if missing
UPDATE api_keys SET key_prefix = 'ek_...' WHERE key_prefix IS NULL;

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE webhooks IS 'Webhook configurations for event notifications';
COMMENT ON TABLE webhook_deliveries IS 'Delivery attempts and history for webhooks';
COMMENT ON COLUMN webhooks.events IS 'Array of event types to subscribe to';
COMMENT ON COLUMN webhooks.secret_hash IS 'SHA256 hash of shared secret for HMAC verification';
COMMENT ON COLUMN webhook_deliveries.event_id IS 'Unique event ID for idempotency';
COMMENT ON COLUMN webhook_deliveries.max_attempts IS 'Maximum delivery attempts before giving up';
