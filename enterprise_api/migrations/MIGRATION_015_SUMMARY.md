# Migration 015: Fix Old Content Verification

## Problem Summary

Old content signed using the website encode/decode tool fails verification with:

```
⚠️ Tampered Content Detected (Manifest Found)
Warning: A valid C2PA manifest was found, but the content text has been modified since signing.
Error Details: Verification failed - signature invalid or content modified
```

**Root Cause**: Database error shows `column "public_key" does not exist`

```
ERROR: column "public_key" does not exist at character 8
STATEMENT: SELECT public_key FROM organizations WHERE id = $1
```

## Technical Analysis

### What Went Wrong

1. **Missing Column**: The `organizations` table never had a `public_key` column added
2. **Trust Anchor Verification**: Code at `app/utils/crypto_utils.py:116` tries to look up public keys from the database
3. **Old Signed Content**: Content signed with `demo-signer-id` cannot be verified because the signer's public key isn't in the database

### Why This Matters

The Enterprise API implements a **Trust Anchor** model for C2PA verification:
- **Identity**: Extract `signer_id` from manifest
- **Lookup**: Query `organizations.public_key` for the signer
- **Verify**: Use the trusted public key to verify the signature

Without the `public_key` column, all Trust Anchor lookups fail.

## Solution

### Step 1: Run Migration

Run `015_add_public_key_to_organizations.sql` to add the missing columns:

```sql
-- Add public_key column (32 bytes for Ed25519 public key)
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS public_key BYTEA;

-- Add private_key_encrypted column if not exists (for BYOK customers)
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS private_key_encrypted BYTEA;
```

### Step 2: Populate Demo Keys

Run the Python script to populate public keys for demo organizations:

```bash
# From enterprise_api directory
uv run python scripts/populate_demo_public_key.py
```

This script will:
1. ✅ Populate `org_demo` with the demo public key
2. ✅ Create/update legacy signer IDs (`demo-signer-id`, `c2pa-demo-signer-001`)
3. ✅ Verify all keys are stored correctly

### Step 3: Verify Fix

Test with old signed content:
1. Go to https://encypherai.com/tools/decode
2. Paste old signed content
3. Should now verify successfully

## Files Created

1. **`migrations/015_add_public_key_to_organizations.sql`** - Database migration
2. **`migrations/RUN_MIGRATION_015.md`** - Detailed instructions for running migration on Railway
3. **`scripts/populate_demo_public_key.py`** - Script to populate demo public keys
4. **`migrations/MIGRATION_015_SUMMARY.md`** - This file

## Railway Deployment Steps

### Quick Steps

```bash
# 1. Connect to Railway database
railway run psql $DATABASE_URL

# 2. Run migration
\i enterprise_api/migrations/015_add_public_key_to_organizations.sql

# 3. Exit psql
\q

# 4. Run population script (requires Railway environment variables)
railway run uv run python enterprise_api/scripts/populate_demo_public_key.py
```

### Alternative: Manual SQL

If you prefer to run SQL directly in Railway dashboard:

```sql
-- 1. Add columns
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS public_key BYTEA;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS private_key_encrypted BYTEA;
CREATE INDEX IF NOT EXISTS idx_organizations_public_key ON organizations(id) WHERE public_key IS NOT NULL;

-- 2. Populate demo org (replace HEX_VALUE with actual demo public key hex)
-- Get the hex value by running: railway run uv run python -c "from app.utils.crypto_utils import get_demo_private_key, serialize_public_key; print(serialize_public_key(get_demo_private_key().public_key()).hex())"
UPDATE organizations 
SET public_key = decode('HEX_VALUE', 'hex')
WHERE id = 'org_demo';

-- 3. Create legacy signer orgs if they don't exist
INSERT INTO organizations (id, name, email, tier, public_key, monthly_quota, created_at, updated_at)
VALUES 
  ('demo-signer-id', 'Legacy Demo Signer (demo-signer-id)', 'demo-signer-id@encypherai.com', 'starter', decode('HEX_VALUE', 'hex'), 1000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('c2pa-demo-signer-001', 'Legacy Demo Signer (c2pa-demo-signer-001)', 'c2pa-demo-signer-001@encypherai.com', 'starter', decode('HEX_VALUE', 'hex'), 1000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (id) DO UPDATE SET public_key = EXCLUDED.public_key;
```

## Expected Behavior After Fix

### Before Fix
```
❌ Verification Status: Failure
❌ Error: column "public_key" does not exist
❌ Signer: Unknown
```

### After Fix
```
✅ Verification Status: Success
✅ Signer: demo-signer-id (Verified via Trust Anchor)
✅ Signature: Valid
✅ Content: Unmodified
```

## Code References

### Where Public Key is Used

1. **`app/utils/crypto_utils.py:115-127`** - `load_organization_public_key()` function
2. **`app/routers/tools.py:325`** - Decode endpoint calls this for Trust Anchor lookup
3. **`app/api/v1/public/c2pa.py:283-289`** - Trust Anchor API endpoint

### Fallback Logic

The code has fallback logic for demo signers:

```python
# If signer_id is demo-related, use demo key
if signer_id in (_demo_signer_id, "org_demo", "c2pa-demo-signer-001"):
    return public_key  # Use demo key

# If signer_id starts with "user_", use demo key (free tier)
if signer_id.startswith("user_"):
    return public_key
```

However, the database lookup happens **before** this fallback, so the SQL error prevents verification.

## Future Improvements

1. **Graceful Degradation**: Catch database errors and fall back to demo key
2. **Public Key Caching**: Cache public keys in Redis to reduce database load
3. **Key Rotation**: Add `public_key_version` column for key rotation support
4. **Audit Trail**: Log all Trust Anchor lookups for security auditing

## Testing Checklist

- [ ] Migration runs successfully on Railway
- [ ] Demo organization has public key populated
- [ ] Legacy signer IDs have public keys populated
- [ ] Old signed content verifies successfully
- [ ] New signed content still works
- [ ] User-level orgs (user_*) still use demo key fallback
- [ ] BYOK customers can still use their own keys

## Rollback Plan

If issues occur, rollback with:

```sql
ALTER TABLE organizations DROP COLUMN IF EXISTS public_key;
ALTER TABLE organizations DROP COLUMN IF EXISTS private_key_encrypted;
DROP INDEX IF EXISTS idx_organizations_public_key;
```

Then redeploy previous version of the API.

## Related Issues

- Trust Anchor verification was implemented but database schema was never updated
- Old content signed before this fix will now verify correctly
- BYOK feature requires `private_key_encrypted` column (also added in this migration)
