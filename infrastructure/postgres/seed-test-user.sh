#!/bin/bash
# ============================================================================
# Seed Test User for Development Environment
# ============================================================================
# Creates a test user for local development:
#   Email: test@encypherai.com
#   Password: TestPassword123!
#
# This script runs after database initialization.
# ============================================================================

set -e

# Only run in development
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Skipping test user creation in production environment"
    exit 0
fi

echo "Creating test user for development..."

# Pre-hashed password for "TestPassword123!"
# Generated using: SHA-256 -> base64 -> bcrypt (12 rounds)
# This matches the auth-service's get_password_hash() function
PASSWORD_HASH='$2b$12$gag9NH0k8VWCpk6b9sadS.Qe7ho15wNK1nNYoYP5d9swQhW9UWTqq'

# Generate a UUID for the user
USER_ID=$(cat /proc/sys/kernel/random/uuid)

# Insert test user into encypher_auth database
psql -U "$POSTGRES_USER" -d encypher_auth <<EOF
-- Create users table if it doesn't exist (in case migrations haven't run yet)
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(255),
    avatar_url VARCHAR(500),
    email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP WITH TIME ZONE,
    google_id VARCHAR(255) UNIQUE,
    github_id VARCHAR(255) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert test user if not exists
INSERT INTO users (id, email, password_hash, name, email_verified, is_active, created_at, updated_at)
VALUES (
    '$USER_ID',
    'test@encypherai.com',
    '$PASSWORD_HASH',
    'Test User',
    TRUE,
    TRUE,
    NOW(),
    NOW()
)
ON CONFLICT (email) DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    name = EXCLUDED.name,
    email_verified = EXCLUDED.email_verified,
    updated_at = NOW();

EOF

echo "Test user created successfully!"
echo "  Email: test@encypherai.com"
echo "  Password: TestPassword123!"
