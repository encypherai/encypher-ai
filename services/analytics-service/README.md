# Encypher Analytics Service

Analytics and metrics microservice for the Encypher platform.

## Features

- ✅ Usage metrics tracking
- ✅ Service-level statistics
- ✅ Time series data
- ✅ Comprehensive analytics reports
- ✅ Real-time metric recording
- ✅ Aggregated metrics

## Tech Stack

- FastAPI, Uvicorn
- PostgreSQL, Redis
- SQLAlchemy, Pydantic

## Setup

```bash
cd services/analytics-service
uv sync
cp .env.example .env.local
uv run python -m app.main
```

Service at: http://localhost:8006

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analytics/metrics` | Record metric |
| GET | `/api/v1/analytics/usage` | Usage statistics |
| GET | `/api/v1/analytics/services` | Service metrics |
| GET | `/api/v1/analytics/timeseries` | Time series data |
| GET | `/api/v1/analytics/report` | Full report |
| GET | `/health` | Health check |

## Docker

```bash
docker build -t encypher-analytics-service .
docker run -p 8006:8006 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e AUTH_SERVICE_URL=http://auth-service:8001 \
  encypher-analytics-service
```

## Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection
- `AUTH_SERVICE_URL` - Auth service URL

Optional:
- `SERVICE_PORT` - Port (default: 8006)
- `REDIS_URL` - Redis connection

## License

Proprietary - Encypher AI
