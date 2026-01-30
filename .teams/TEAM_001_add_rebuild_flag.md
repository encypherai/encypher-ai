# Team 001: Add Rebuild Flag to Start Script

## Objectives
- Add `--rebuild` flag to `start-dev.sh`.
- Allow rebuilding of application services without wiping database volumes (unlike `--clean-start`).
- Target services: auth-service, user-service, key-service, encoding-service, verification-service, coalition-service, analytics-service, billing-service, notification-service, enterprise-api.

## Tasks
- [x] Modify `start-dev.sh` to add `REBUILD_SERVICES` variable and argument parsing.
- [x] Modify `start-dev.sh` to execute `docker compose build ...` when flag is set.
