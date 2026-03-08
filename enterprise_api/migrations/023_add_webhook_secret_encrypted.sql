ALTER TABLE webhooks
ADD COLUMN IF NOT EXISTS secret_encrypted BYTEA;

COMMENT ON COLUMN webhooks.secret_encrypted IS 'Encrypted webhook shared secret for outbound signing';
