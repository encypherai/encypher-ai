-- ============================================================================
-- Encypher Per-Service Database Initialization
-- ============================================================================
-- This script creates all databases needed for the microservices architecture.
-- Each service gets its own isolated database.
--
-- Run by PostgreSQL on first container startup via docker-entrypoint-initdb.d
-- ============================================================================

-- Use a DO block to handle "IF NOT EXISTS" for CREATE DATABASE
-- (PostgreSQL doesn't support CREATE DATABASE IF NOT EXISTS directly)

DO $$
BEGIN
    -- User Service Database
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'encypher_users') THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE encypher_users');
    END IF;
END
$$;

-- Since we can't use dblink without extension, use a simpler approach:
-- Create databases, ignore errors if they exist

-- Note: encypher_auth is created as POSTGRES_DB, so skip it

-- Create remaining databases using template0
SELECT 'CREATE DATABASE encypher_users' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'encypher_users')\gexec
SELECT 'CREATE DATABASE encypher_keys' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'encypher_keys')\gexec
SELECT 'CREATE DATABASE encypher_billing' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'encypher_billing')\gexec
SELECT 'CREATE DATABASE encypher_notifications' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'encypher_notifications')\gexec
SELECT 'CREATE DATABASE encypher_encoding' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'encypher_encoding')\gexec
SELECT 'CREATE DATABASE encypher_verification' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'encypher_verification')\gexec
SELECT 'CREATE DATABASE encypher_analytics' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'encypher_analytics')\gexec
SELECT 'CREATE DATABASE encypher_coalition' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'encypher_coalition')\gexec
SELECT 'CREATE DATABASE encypher_content' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'encypher_content')\gexec

-- Grant all privileges to the encypher user on all databases
GRANT ALL PRIVILEGES ON DATABASE encypher_auth TO encypher;
GRANT ALL PRIVILEGES ON DATABASE encypher_users TO encypher;
GRANT ALL PRIVILEGES ON DATABASE encypher_keys TO encypher;
GRANT ALL PRIVILEGES ON DATABASE encypher_billing TO encypher;
GRANT ALL PRIVILEGES ON DATABASE encypher_notifications TO encypher;
GRANT ALL PRIVILEGES ON DATABASE encypher_encoding TO encypher;
GRANT ALL PRIVILEGES ON DATABASE encypher_verification TO encypher;
GRANT ALL PRIVILEGES ON DATABASE encypher_analytics TO encypher;
GRANT ALL PRIVILEGES ON DATABASE encypher_coalition TO encypher;
GRANT ALL PRIVILEGES ON DATABASE encypher_content TO encypher;

\echo 'All Encypher databases created successfully!'
