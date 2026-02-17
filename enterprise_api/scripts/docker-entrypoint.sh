#!/bin/sh
set -e

echo "=========================================="
echo "Enterprise API Docker Entrypoint"
echo "=========================================="

# DB migration SSOT is enforced in app startup via ensure_database_ready
# (Alembic-only migration path). Keep INIT_DB for compatibility.
if [ "${INIT_DB:-true}" = "true" ]; then
    echo "Database migration check will run on API startup (strategy: alembic)."
fi

# Start the application
echo "Starting Enterprise API..."
exec "$@"
