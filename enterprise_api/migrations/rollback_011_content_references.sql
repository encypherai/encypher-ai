-- Rollback Migration 011: Drop content_references table
-- WARNING: This will delete all embedding reference data

-- Drop indexes first
DROP INDEX IF EXISTS idx_content_refs_expires;
DROP INDEX IF EXISTS idx_content_refs_org_created;
DROP INDEX IF EXISTS idx_content_refs_created;
DROP INDEX IF EXISTS idx_content_refs_merkle_root;
DROP INDEX IF EXISTS idx_content_refs_org_doc;
DROP INDEX IF EXISTS idx_content_refs_leaf_hash;

-- Drop table
DROP TABLE IF EXISTS content_references CASCADE;

-- Verification
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'content_references'
    ) THEN
        RAISE EXCEPTION 'Table content_references still exists after rollback';
    END IF;
    
    RAISE NOTICE 'Rollback 011: content_references table dropped successfully';
END $$;
