-- Migration: 013_add_user_id_to_organizations
-- Description: Add user_id to organizations table for coalition tracking
-- Author: System
-- Date: 2025-11-04

-- Add user_id column to link organizations to users (from auth-service)
ALTER TABLE organizations
ADD COLUMN IF NOT EXISTS user_id UUID;

-- Create index for user lookups
CREATE INDEX IF NOT EXISTS idx_organizations_user_id
    ON organizations(user_id);

-- Add comment for documentation
COMMENT ON COLUMN organizations.user_id IS 'User ID from auth-service who owns this organization';

-- Note: Existing organizations will have NULL user_id until they are claimed
-- New organizations should be created with a user_id when the user signs up
