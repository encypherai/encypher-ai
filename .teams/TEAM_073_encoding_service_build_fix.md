# TEAM_073 — Encoding Service Build Fix

## Status
- In progress

## Goal
Fix Railway build failure for `services/encoding-service`.

## Notes
- Investigating `services/encoding-service/Dockerfile` and build/install steps.
- Suspect current Dockerfile’s UV installation / `uv pip install --system` steps.
