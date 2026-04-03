# PRD — Marketing Site: Verify Upstream Tracing

## Status
In Progress

## Current Goal
Expose upstream verifier trace identifiers through the marketing-site `/api/tools/verify` proxy response so production verification failures can be correlated to the exact backend service instance and logs.

## Overview
The marketing-site Encode/Decode tool calls its own Next.js API route (`/api/tools/verify`), which then proxies to `https://api.encypher.com/api/v1/verify`. Railway adds `x-railway-request-id` to the proxy response, but the verifier service also emits its own request ID (`X-Request-ID`) and includes a `correlation_id` field in JSON. Without propagating those upstream identifiers, debugging `SIGNATURE_INVALID` in production cannot reliably confirm which service processed the request.

## Objectives
- Surface upstream `X-Request-ID` from the verifier as a response header on `/api/tools/verify`.
- Surface upstream Railway request id (if present) separately from the proxy’s request id.
- Surface upstream `correlation_id` (from JSON) as a response header.
- Add unit test coverage for header derivation logic.

## Tasks
- [x] 1.0 Baseline: confirm current proxy does not forward upstream IDs
- [x] 2.0 Add tests (TDD) for upstream trace header derivation
- [x] 2.1 Task — ✅ npm test
- [x] 3.0 Implement upstream trace header passthrough in `/api/tools/verify`
- [x] 3.1 Task — ✅ npm test
- [ ] 4.0 Manual verification
- [ ] 4.1 Confirm response includes `x-upstream-request-id` and `x-upstream-correlation-id`
- [ ] 4.2 Use IDs to find matching Railway logs in verification-service

## Success Criteria
- `/api/tools/verify` includes upstream tracing headers when upstream returns them.
- Unit tests pass (`npm test`) for marketing-site.

## Completion Notes
( заполнить при завершении )
