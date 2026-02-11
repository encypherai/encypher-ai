-- Migration: 022_consolidate_tiers_add_addons
-- Description: Consolidate pricing tiers to free/enterprise/strategic_partner and add add_ons column
-- Author: TEAM_166
-- Date: 2026-02-11
--
-- TEAM_145/166: Backend tier consolidation.
-- - Update tier CHECK constraint to include 'free' and 'strategic_partner'
-- - Coerce legacy tier values (starter, professional, business) to 'free'
-- - Add add_ons JSONB column to organizations table
-- - Update default coalition rev share to 60/40

-- Step 1: Drop old tier check constraint (idempotent via IF EXISTS)
ALTER TABLE organizations DROP CONSTRAINT IF EXISTS organizations_tier_check;

-- Step 2: Coerce legacy tier values to 'free' BEFORE adding new constraint
UPDATE organizations SET tier = 'free' WHERE tier IN ('starter', 'professional', 'business');

-- Step 3: Add new tier check constraint with all valid values
ALTER TABLE organizations ADD CONSTRAINT organizations_tier_check
  CHECK (tier::text = ANY(ARRAY['free', 'starter', 'professional', 'business', 'enterprise', 'strategic_partner', 'demo']::text[]));

-- Step 4: Add add_ons JSONB column (idempotent)
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS add_ons JSONB DEFAULT '{}';

-- Step 5: Update coalition rev share defaults for existing orgs still on old values
UPDATE organizations SET coalition_rev_share_publisher = 60, coalition_rev_share_encypher = 40
  WHERE coalition_rev_share_publisher = 65 AND coalition_rev_share_encypher = 35;
