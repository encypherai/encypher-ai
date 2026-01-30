# Team 001: Enable Hot Reload for Microservices

## Objectives
- Enable hot reloading (volumes + `--reload`) for all microservices in `docker-compose.full-stack.yml`.
- Ensure development changes are reflected immediately without rebuilding containers.

## Tasks
- [x] Modify `docker-compose.full-stack.yml` to add `volumes` mounting the source code for:
    - `auth-service`
    - `user-service`
    - `key-service`
    - `encoding-service`
    - `verification-service`
    - `coalition-service`
    - `analytics-service`
    - `billing-service`
    - `notification-service`
- [x] Modify `docker-compose.full-stack.yml` to override `command` with `--reload` flag for all above services plus `enterprise-api`.
