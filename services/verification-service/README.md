# Encypher Verification Service

Document verification microservice for the Encypher platform.

## Features

- ✅ Signature verification (Ed25519)
- ✅ Complete document verification
- ✅ Tampering detection
- ✅ Verification history
- ✅ Public endpoints (no auth required)
- ✅ Operation statistics

## Tech Stack

- FastAPI, Uvicorn
- PostgreSQL, Redis
- SQLAlchemy, Pydantic
- Cryptography (Ed25519)

## Setup

```bash
cd services/verification-service
uv sync
cp .env.example .env.local
uv run python -m app.main
```

Service at: http://localhost:8005

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/verify/signature` | Verify signature |
| POST | `/api/v1/verify/document` | Verify document |
| GET | `/api/v1/verify/history/{id}` | Verification history |
| GET | `/api/v1/verify/stats` | Statistics |
| GET | `/health` | Health check |

## Docker

```bash
docker build -t encypher-verification-service .
docker run -p 8005:8005 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e ENCODING_SERVICE_URL=http://encoding-service:8004 \
  encypher-verification-service
```

## Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection
- `ENCODING_SERVICE_URL` - Encoding service URL

Optional:
- `SERVICE_PORT` - Port (default: 8005)
- `AUTH_SERVICE_URL` - Auth service URL (optional)

## License

Proprietary - Encypher AI
