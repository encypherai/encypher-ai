# Encypher API Gateway

Minimal FastAPI-based gateway that exposes a single base URL for the frontend and forwards requests to internal services.

## Features
- CORS allowlist
- Health endpoint (`/health`)
- Prometheus metrics (`/metrics`)
- Structured logging with correlation IDs (`X-Request-ID`)
- Proxy routes:
  - `/api/v1/auth/*` → auth-service
  - `/api/v1/analytics/*` → analytics-service
  - `/api/v1/verify*` → enterprise_api
  - `/api/v1/public/verify*` → enterprise_api

## Configuration (.env.example)
Copy `.env.example` to `.env` and set values as needed.

## Development
```bash
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Security Notes
- Do not use wildcard CORS in production.
- Do not log secrets or full tokens.
- Enforce TLS at the edge (ingress/load balancer).
