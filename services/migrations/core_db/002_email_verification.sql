-- ============================================
-- EMAIL VERIFICATION TOKENS
-- Version: 1.0.0
-- Date: 2025-11-27
-- ============================================
-- 
-- Stores email verification tokens for user signup flow.
-- Tokens are single-use and expire after 24 hours.
-- ============================================

CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'evt_' || substr(md5(random()::text), 1, 16),
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Token (URL-safe base64, 32 bytes)
    token VARCHAR(64) NOT NULL UNIQUE,
    
    -- Expiry
    expires_at TIMESTAMPTZ NOT NULL,
    
    -- Usage tracking
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_user_id ON email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_token ON email_verification_tokens(token);
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_expires_at ON email_verification_tokens(expires_at);

-- ============================================
-- PASSWORD RESET TOKENS
-- ============================================
-- 
-- Stores password reset tokens.
-- Tokens are single-use and expire after 1 hour.
-- ============================================

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'prt_' || substr(md5(random()::text), 1, 16),
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Token (URL-safe base64, 32 bytes)
    token VARCHAR(64) NOT NULL UNIQUE,
    
    -- Expiry (shorter than verification - 1 hour)
    expires_at TIMESTAMPTZ NOT NULL,
    
    -- Usage tracking
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);
