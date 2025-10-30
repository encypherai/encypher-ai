# Encypher Encoding Service

Document encoding and signing microservice for the Encypher platform.

## Features

- ✅ Document signing with Ed25519
- ✅ Metadata embedding
- ✅ C2PA-style manifests
- ✅ API key verification
- ✅ Operation tracking
- ✅ Multiple format support (text, json, markdown)

## Tech Stack

- FastAPI, Uvicorn
- PostgreSQL, Redis
- SQLAlchemy, Pydantic
- Cryptography (Ed25519)
- UV package manager

## Setup

```bash
cd services/encoding-service
uv sync
cp .env.example .env.local
# Edit .env.local
uv run python -m app.main
```

Service at: http://localhost:8004

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/encode/sign` | Sign document |
| POST | `/api/v1/encode/embed` | Embed metadata |
| GET | `/api/v1/encode/documents` | List documents |
| GET | `/api/v1/encode/documents/{id}` | Get document |
| GET | `/api/v1/encode/documents/{id}/manifest` | Get manifest |
| GET | `/api/v1/encode/stats` | Operation stats |
| GET | `/health` | Health check |

## Docker

```bash
docker build -t encypher-encoding-service .
docker run -p 8004:8004 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e AUTH_SERVICE_URL=http://auth-service:8001 \
  -e KEY_SERVICE_URL=http://key-service:8003 \
  encypher-encoding-service
```

## Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection
- `AUTH_SERVICE_URL` - Auth service URL
- `KEY_SERVICE_URL` - Key service URL

Optional:
- `SERVICE_PORT` - Port (default: 8004)
- `LOG_LEVEL` - Log level (default: INFO)
- `MAX_DOCUMENT_SIZE` - Max size in bytes (default: 10MB)

## License

Proprietary - Encypher AI
