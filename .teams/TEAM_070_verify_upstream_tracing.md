# TEAM_070 — Verify Upstream Tracing

## Goal
Expose upstream verifier trace identifiers (e.g. `X-Request-ID`, Railway request id, and `correlation_id`) through the marketing-site `/api/tools/verify` proxy so production failures can be correlated to the exact backend service + logs.

## Work Log
- Claimed TEAM_070.
- Read repo `README.md`, `agents.md`, and related PRDs.
- Implemented header passthrough for verify proxy with unit test coverage.

## Notes
- Correlating `x-railway-request-id` alone is insufficient because the marketing-site proxy can terminate the request.
