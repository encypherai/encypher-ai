#!/bin/sh
set -e

echo "=========================================="
echo "Enterprise API Docker Entrypoint"
echo "=========================================="

# DB migration SSOT is enforced in app startup via ensure_database_ready
# (migration strategy defaults to Alembic). Keep INIT_DB for compatibility.
if [ "${INIT_DB:-true}" = "true" ]; then
    echo "Database migration check will run on API startup (strategy: ${DB_MIGRATION_STRATEGY:-alembic})."
fi

# Start the application
echo "Starting Enterprise API..."
exec "$@"
