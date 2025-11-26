#!/bin/bash
set -e

echo "=========================================="
echo "Enterprise API Docker Entrypoint"
echo "=========================================="

# Run database initialization if INIT_DB is set
if [ "${INIT_DB:-true}" = "true" ]; then
    echo "Running database initialization..."
    python scripts/init_and_seed.py || {
        echo "Warning: Database initialization failed, but continuing..."
    }
fi

# Start the application
echo "Starting Enterprise API..."
exec "$@"
