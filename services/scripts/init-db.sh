#!/bin/bash
# ============================================
# Database Initialization Script
# Runs all migrations in order
# ============================================

set -e

echo "=========================================="
echo "Database Initialization"
echo "=========================================="

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until pg_isready -h ${POSTGRES_HOST:-postgres} -p ${POSTGRES_PORT:-5432} -U ${POSTGRES_USER:-encypher}; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done
echo "PostgreSQL is ready!"

# Database connection
DB_HOST=${POSTGRES_HOST:-postgres}
DB_PORT=${POSTGRES_PORT:-5432}
DB_USER=${POSTGRES_USER:-encypher}
DB_PASSWORD=${POSTGRES_PASSWORD:-encypher_dev_password}
DB_NAME=${POSTGRES_DB:-encypher}

export PGPASSWORD=$DB_PASSWORD

# Run migrations in order
MIGRATIONS_DIR="/app/migrations"

echo ""
echo "Running migrations from $MIGRATIONS_DIR..."

for migration in $(ls -1 $MIGRATIONS_DIR/*.sql 2>/dev/null | sort); do
    echo "  Running: $(basename $migration)"
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f $migration
done

echo ""
echo "=========================================="
echo "Database initialization complete!"
echo "=========================================="

# Verify
echo ""
echo "Verification:"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT id, name, tier FROM organizations ORDER BY tier;"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT id, organization_id, name FROM api_keys WHERE organization_id IS NOT NULL;"
