# PRD: Metrics Parsing and API Docs Routing

**Status:** 📋 Planning
**Current Goal:** Fix analytics metric ingestion type handling and restore publicly accessible API docs at `api.encypherai.com/docs`.

## Overview

We currently emit fractional latency metrics into Redis Streams, but the Analytics Service stream consumer parses these fields as integers and logs errors. Separately, requests to `api.encypherai.com/docs` return 404, blocking prospective customers from viewing interactive API documentation.

This PRD defines the work to:
- Make metrics ingestion robust and type-correct (industry best practices)
- Ensure API docs are reachable at the intended public hostname/path, with secure production defaults

## Objectives

- Ensure `response_time_ms` and other numeric metrics are parsed and stored correctly without log spam
- Maintain efficient ingestion (batching, minimal overhead)
- Ensure `/docs` is served correctly via Traefik gateway for production hostnames
- Align documentation (README links/hostnames) with actual deployed routing

## Tasks

### 1.0 Metrics Parsing Hardening (Analytics Service)

- [x] 1.1 Add unit tests for `StreamConsumer._parse_metric` handling:
  - [x] 1.1.1 `response_time_ms` accepts float strings and stores correctly
  - [x] 1.1.2 `status_code` handles int strings and rejects invalid values safely
  - [x] 1.1.3 Missing/invalid fields do not crash the consumer
- [x] 1.2 Implement parsing fix and ensure it is type-correct and efficient
- [x] 1.3 Run `uv run pytest` — ✅ pytest

### 2.0 Public API Docs Routing (Traefik + Enterprise API)

- [x] 2.1 Identify which hostname should serve docs (`api.encypherai.com`) and align routing
- [x] 2.2 Update Traefik routing rules to serve `/docs`, `/redoc`, `/openapi.json` at the chosen public hostname
- [x] 2.3 Ensure Enterprise API configuration allows docs in production only when explicitly enabled (secure default)
- [ ] 2.4 Verify in the target environment and document the correct URL(s)

## Success Criteria

- Metrics consumer emits no `Error parsing metric` logs for valid float latency inputs
- Automated tests pass:
  - [ ] 1.3 — ✅ pytest
- `api.encypherai.com/docs` returns a non-404 response in the target environment

## Completion Notes

( заполнить по завершению )
