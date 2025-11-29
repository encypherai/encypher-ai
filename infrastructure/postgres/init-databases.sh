#!/bin/bash
# ============================================================================
# Encypher Per-Service Database Initialization
# ============================================================================
# Creates all databases needed for the microservices architecture.
# Each service gets its own isolated database.
# ============================================================================

set -e

# Connect to the default database (encypher_auth, set as POSTGRES_DB)
PGDATABASE="$POSTGRES_DB"

# Function to create database if it doesn't exist
create_db_if_not_exists() {
    local db_name=$1
    if psql -U "$POSTGRES_USER" -d "$PGDATABASE" -lqt | cut -d \| -f 1 | grep -qw "$db_name"; then
        echo "Database $db_name already exists, skipping..."
    else
        echo "Creating database $db_name..."
        psql -U "$POSTGRES_USER" -d "$PGDATABASE" -c "CREATE DATABASE $db_name;"
        psql -U "$POSTGRES_USER" -d "$PGDATABASE" -c "GRANT ALL PRIVILEGES ON DATABASE $db_name TO $POSTGRES_USER;"
    fi
}

echo "Creating Encypher per-service databases..."

# Create remaining databases (encypher_auth is created automatically as POSTGRES_DB)
create_db_if_not_exists "encypher_users"
create_db_if_not_exists "encypher_keys"
create_db_if_not_exists "encypher_billing"
create_db_if_not_exists "encypher_notifications"
create_db_if_not_exists "encypher_encoding"
create_db_if_not_exists "encypher_verification"
create_db_if_not_exists "encypher_analytics"
create_db_if_not_exists "encypher_coalition"
create_db_if_not_exists "encypher_content"

echo "All Encypher databases created successfully!"
