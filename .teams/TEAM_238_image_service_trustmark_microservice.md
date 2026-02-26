# TEAM_238 - TrustMark Image Service Microservice (Track D)

**Session:** 2026-02-26
**Branch:** feat/image-signing-c2pa
**PRD:** PRDs/CURRENT/PRD_Image_Signing_C2PA.md (Tasks 5.1-5.7)

## Goal

Implement services/image-service/ -- a standalone FastAPI microservice that wraps
Adobe Research's TrustMark neural watermarking library. Enterprise-only. PyTorch
is isolated here to avoid inflating the main enterprise_api container.

## Tasks

- [x] 5.1 Scaffold services/image-service/ directory structure
- [x] 5.2 Schemas (watermark_schemas.py)
- [x] 5.3 TrustMarkService (trustmark_service.py)
- [x] 5.4 Routers (health.py, watermark.py)
- [x] 5.5 Dockerfile
- [x] 5.6 Add to docker-compose.dev.yml (enterprise profile, port 8010)
- [x] 5.7 Tests (mocked, since torch may not be installed in CI) -- all passing

## Status

COMPLETE. All tests pass. docker-compose.dev.yml updated.

## Handoff

The image-service is fully scaffolded. TrustMark/torch are NOT in pyproject.toml
(they are installed via Dockerfile only). Tests run without torch installed using
mocks. Start with: `docker-compose --profile enterprise up image-service`

Next: Task 5.5 in PRD (image_service_client.py in enterprise_api) to wire the
HTTP client that calls this microservice from the main API.

## Suggested Commit Message

```
feat(image-service): scaffold TrustMark neural watermarking microservice

Add services/image-service/ as a standalone FastAPI microservice for
Enterprise-tier image watermarking using Adobe Research TrustMark
(Apache 2.0). PyTorch is isolated here to avoid inflating enterprise_api.

- pyproject.toml with FastAPI/uvicorn/Pillow (no torch in toml, installed
  in Dockerfile only for platform flexibility)
- TrustMarkService with graceful fallback when torch not installed
- POST /api/v1/watermark and POST /api/v1/detect endpoints
- GET /health endpoint with model_loaded status
- Dockerfile using python:3.11-slim + CPU torch wheels
- docker-compose.dev.yml: image-service on port 8010 under 'enterprise' profile
- Full pytest suite (mocked) passing without torch installed
```
