-- Make merkle_root_id nullable for free tier support
ALTER TABLE content_references ALTER COLUMN merkle_root_id DROP NOT NULL;
