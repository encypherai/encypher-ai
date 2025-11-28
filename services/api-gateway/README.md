# API Gateway (Traefik)

Traefik-based API Gateway for routing requests to microservices on Railway.

## Purpose

Routes all API requests to the appropriate microservice based on path prefix:

| Path | Service |
|------|---------|
| `/api/v1/auth/*` | auth-service |
| `/api/v1/keys/*` | key-service |
| `/api/v1/analytics/*` | analytics-service |
| `/api/v1/billing/*` | billing-service |
| `/api/v1/users/*`, `/api/v1/profile/*` | user-service |
| `/api/v1/verify/*` | verification-service |
| `/api/v1/encode/*`, `/api/v1/documents/*` | encoding-service |
| `/api/v1/coalition/*` | coalition-service |
| `/api/v1/notifications/*` | notification-service |
| `/api/v1/sign/*`, `/api/v1/batch/*`, etc. | enterprise-api |

## Features

- **Path-based routing** - Routes to correct microservice
- **CORS handling** - Centralized CORS configuration
- **Health checks** - `/ping` endpoint for Railway
- **Load balancing** - Built-in load balancer

## Configuration

- `traefik.yml` - Static configuration (entrypoints, providers)
- `dynamic.yml` - Dynamic configuration (routers, services, middlewares)

## Deployment

Deployed as a Docker container on Railway. Uses Railway's internal networking to communicate with other services.

### Environment Variables

None required - all routing is configured in the YAML files.

### Health Check

Railway should use `/ping` as the health check endpoint.

## Local Development

For local development, use the Traefik config in `/config/traefik/` with docker-compose.

## Architecture

```
Browser → API Gateway (Traefik) → Microservices
              ↓
         /api/v1/keys → key-service
         /api/v1/auth → auth-service
         /api/v1/analytics → analytics-service
         ...
```
