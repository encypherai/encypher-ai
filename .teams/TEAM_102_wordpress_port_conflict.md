# TEAM_102 WordPress Port Conflict

## Summary
- Investigate and resolve port conflicts between WordPress plugin docker setup and start-dev.sh.

## Notes
- Session started for port conflict remediation.
- Changed wordpress-provenance-plugin docker compose host port to 8085 (avoid Traefik 8080).
- Updated WordPress URLs in README/testing guides/scripts.
- Verification: uv run ruff check .; uv run pytest (skips noted).
