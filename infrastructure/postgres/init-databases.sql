-- ============================================================================
-- Encypher Per-Service Database Initialization
-- ============================================================================
-- This script creates all databases needed for the microservices architecture.
-- Each service gets its own isolated database.
--
-- Run by PostgreSQL on first container startup via docker-entrypoint-initdb.d
-- ============================================================================

-- Auth Service Database
-- Tables: users, refresh_tokens, password_reset_tokens, email_verification_tokens
CREATE DATABASE encypher_auth;

-- User Service Database  
-- Tables: user_profiles, user_preferences, teams, team_members
CREATE DATABASE encypher_users;

-- Key Service Database
-- Tables: organizations, organization_members, api_keys
CREATE DATABASE encypher_keys;

-- Billing Service Database
-- Tables: subscriptions, invoices, payments, usage_records
CREATE DATABASE encypher_billing;

-- Notification Service Database
-- Tables: notification_logs, email_templates, notification_preferences
CREATE DATABASE encypher_notifications;

-- Encoding Service Database
-- Tables: encoded_documents, signing_operations
CREATE DATABASE encypher_encoding;

-- Verification Service Database
-- Tables: verification_results, verification_cache
CREATE DATABASE encypher_verification;

-- Analytics Service Database
-- Tables: usage_metrics, aggregated_metrics
CREATE DATABASE encypher_analytics;

-- Coalition Service Database
-- Tables: coalition_members, coalition_content, licensing_agreements, revenue_distributions
CREATE DATABASE encypher_coalition;

-- Enterprise API Content Database
-- Tables: documents, merkle_trees, signatures (C2PA content)
CREATE DATABASE encypher_content;

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

-- Log completion
\echo 'All Encypher databases created successfully!'
