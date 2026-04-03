# Migration 015: Add public_key Column

## Problem
Old signed content fails verification with error:
```
column "public_key" does not exist
```

The `organizations` table is missing the `public_key` column needed for Trust Anchor verification.

## Solution
Run migration `015_add_public_key_to_organizations.sql` to add the missing columns.

## How to Run on Railway

### Option 1: Railway CLI (Recommended)

```bash
# 1. Install Railway CLI if not already installed
npm i -g @railway/cli

# 2. Login to Railway
railway login

# 3. Link to your project
railway link

# 4. Connect to the database
railway run psql $DATABASE_URL

# 5. Run the migration
\i enterprise_api/migrations/015_add_public_key_to_organizations.sql

# 6. Verify the columns were added
\d organizations

# 7. Exit psql
\q
```

### Option 2: Railway Dashboard

1. Go to Railway Dashboard → Your Project → PostgreSQL Service
2. Click "Data" tab
3. Click "Query" button
4. Copy the contents of `015_add_public_key_to_organizations.sql`
5. Paste into the query editor
6. Click "Run Query"
7. Verify success

### Option 3: Direct psql Connection

```bash
# Get DATABASE_URL from Railway dashboard (Settings → Variables)
export DATABASE_URL="postgresql://..."

# Run migration
psql $DATABASE_URL -f enterprise_api/migrations/015_add_public_key_to_organizations.sql

# Verify
psql $DATABASE_URL -c "\d organizations"
```

## Verification

After running the migration, verify the columns exist:

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'organizations'
  AND column_name IN ('public_key', 'private_key_encrypted')
ORDER BY column_name;
```

Expected output:
```
     column_name      | data_type | is_nullable
----------------------+-----------+-------------
 private_key_encrypted | bytea     | YES
 public_key            | bytea     | YES
```

## Testing

After migration, test with old signed content:
1. Go to https://encypher.com/tools/decode
2. Paste old signed content
3. Should now verify successfully (or show proper verification status)

## Rollback (if needed)

```sql
ALTER TABLE organizations DROP COLUMN IF EXISTS public_key;
ALTER TABLE organizations DROP COLUMN IF EXISTS private_key_encrypted;
DROP INDEX IF EXISTS idx_organizations_public_key;
```

## Notes

- This migration is idempotent (safe to run multiple times)
- Existing rows will have NULL values for these columns
- Demo organization will need its public key populated programmatically
- For BYOK customers, keys will be populated when they upload their keys
