-- Rollback script for Merkle tree tables
-- Description: Removes all Merkle-related tables and columns
-- Author: System
-- Date: 2025-10-28
-- WARNING: This will delete all Merkle tree data!

-- Drop tables in reverse order (respecting foreign key constraints)
DROP TABLE IF EXISTS attribution_reports CASCADE;
DROP TABLE IF EXISTS merkle_proof_cache CASCADE;
DROP TABLE IF NOT EXISTS merkle_subhashes CASCADE;
DROP TABLE IF EXISTS merkle_roots CASCADE;

-- Remove columns from organizations table
ALTER TABLE organizations DROP COLUMN IF EXISTS tier;
ALTER TABLE organizations DROP COLUMN IF EXISTS merkle_enabled;
ALTER TABLE organizations DROP COLUMN IF EXISTS monthly_merkle_quota;
ALTER TABLE organizations DROP COLUMN IF EXISTS merkle_calls_this_month;
ALTER TABLE organizations DROP COLUMN IF EXISTS quota_reset_at;

-- Note: Indexes are automatically dropped with their tables
