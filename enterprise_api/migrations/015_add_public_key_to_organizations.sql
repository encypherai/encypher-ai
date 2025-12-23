-- Migration: 015_add_public_key_to_organizations
-- Description: Add public_key and private_key_encrypted columns for Trust Anchor verification
-- Author: System
-- Date: 2025-12-23
-- Note: Fixes verification failure for old signed content

-- Add public_key column (32 bytes for Ed25519 public key)
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS public_key BYTEA;

-- Add private_key_encrypted column if not exists (for BYOK customers)
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS private_key_encrypted BYTEA;

-- Create index for public key lookups (used during verification)
CREATE INDEX IF NOT EXISTS idx_organizations_public_key ON organizations(id) WHERE public_key IS NOT NULL;

-- Add comment for documentation
COMMENT ON COLUMN organizations.public_key IS 'Ed25519 public key (32 bytes raw format) for signature verification via Trust Anchor';
COMMENT ON COLUMN organizations.private_key_encrypted IS 'AES-256-GCM encrypted Ed25519 private key (32 bytes) for Encypher-managed keys';

-- Update demo organization with demo public key (if it exists and doesn't have a key yet)
-- Note: The demo key will be set programmatically when the demo org is created/updated
-- This is just a placeholder to ensure the column exists
