#!/usr/bin/env bash
# Sync shared_commercial_libs into every microservice's shared_libs/ directory.
#
# This is the local equivalent of the GitHub Actions workflow
# (.github/workflows/sync-shared-libs.yml). Run it after editing anything
# under shared_commercial_libs/ so that services pick up the change
# before you commit.
#
# Usage:
#   ./services/scripts/sync-shared-libs.sh          # sync all services
#   ./services/scripts/sync-shared-libs.sh auth-service key-service  # sync specific ones

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SOURCE="$REPO_ROOT/shared_commercial_libs"

ALL_SERVICES=(
  alert-service
  analytics-service
  auth-service
  billing-service
  coalition-service
  encoding-service
  key-service
  notification-service
  user-service
  verification-service
  web-service
)

# If args are provided, sync only those services; otherwise sync all.
if [ $# -gt 0 ]; then
  SERVICES=("$@")
else
  SERVICES=("${ALL_SERVICES[@]}")
fi

for SERVICE in "${SERVICES[@]}"; do
  TARGET="$REPO_ROOT/services/$SERVICE/shared_libs"
  if [ ! -d "$REPO_ROOT/services/$SERVICE" ]; then
    echo "  SKIP: services/$SERVICE does not exist"
    continue
  fi
  rm -rf "$TARGET"
  cp -r "$SOURCE" "$TARGET"

  # Add the same SYNC_NOTICE the GH Actions workflow creates
  cat > "$TARGET/SYNC_NOTICE.md" << 'NOTICE'
# AUTO-SYNCED - DO NOT EDIT

This directory is automatically synced from `/shared_commercial_libs/`.

**Source of Truth**: `/shared_commercial_libs/`

Any changes made here will be overwritten on the next sync.
To make changes, edit the files in `/shared_commercial_libs/` and push to main.

Synced by: GitHub Actions (sync-shared-libs.yml)
NOTICE
  echo "  OK:   $SERVICE"
done

echo "Synced ${#SERVICES[@]} service(s) from shared_commercial_libs/."
