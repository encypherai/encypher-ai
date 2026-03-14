# Encypher Key Service

API Key management microservice for the Encypher platform.

## Features

- ✅ Secure API key generation
- ✅ Key permissions management
- ✅ Key rotation
- ✅ Usage tracking
- ✅ Key verification for other services
- ✅ Key revocation
- ✅ Expiration support
- ✅ Health check endpoints

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Cache:** Redis
- **Package Manager:** UV
- **Key Generation:** Cryptographically secure random

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- UV package manager

### Installation

1. **Install dependencies:**
   ```bash
   cd services/key-service
   uv sync
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the service:**
   ```bash
   uv run python -m app.main
   ```

The service will be available at `http://localhost:8003`

## API Endpoints

### Key Management

**POST /api/v1/keys/generate**
- Generate a new API key
- Body: `{ "name": "My Key", "permissions": ["sign", "verify"], "description": "..." }`
- Returns: API key (only shown once!)

**GET /api/v1/keys**
- List all API keys for current user
- Query: `?include_revoked=false`
- Returns: Array of key info (without actual keys)

**GET /api/v1/keys/{key_id}**
- Get details of a specific key
- Returns: Key information

**PUT /api/v1/keys/{key_id}**
- Update key name, description, or permissions
- Body: `{ "name": "New Name", "permissions": [...] }`
- Returns: Updated key info

**DELETE /api/v1/keys/{key_id}**
- Revoke an API key
- Returns: Success message

**POST /api/v1/keys/{key_id}/rotate**
- Rotate a key (create new, revoke old)
- Body: `{ "reason": "Security rotation" }`
- Returns: New key (only shown once!)

**POST /api/v1/keys/verify**
- Verify an API key (public endpoint)
- Body: `{ "key": "ency_..." }`
- Returns: Validation result with permissions

**GET /api/v1/keys/{key_id}/usage**
- Get usage statistics for a key
- Returns: Usage stats

### Health

**GET /health**
- Health check endpoint
- Returns: `{ "status": "healthy", "service": "key-service" }`

## Docker

### Build

```bash
docker build -t encypher-key-service .
```

### Run

```bash
docker run -p 8003:8003 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e AUTH_SERVICE_URL=http://auth-service:8001 \
  encypher-key-service
```

## Development

### Run tests

```bash
uv run pytest
```

### Code formatting

```bash
uv run black app/
uv run ruff app/
```

## Environment Variables

See `.env.example` for all available configuration options.

### Required

- `DATABASE_URL` - PostgreSQL connection string
- `AUTH_SERVICE_URL` - URL of auth service

### Optional

- `SERVICE_PORT` - Port to run on (default: 8003)
- `LOG_LEVEL` - Logging level (default: INFO)
- `REDIS_URL` - Redis connection string
- `KEY_PREFIX` - Prefix for generated keys (default: ency_)
- `KEY_LENGTH` - Length of random part (default: 32)
- `SUPERADMIN_PUBLISHER_DISPLAY_NAME` - Publisher identity label used for user-level super-admin keys (default: `Encypher Publisher`)
- `SUPERADMIN_USER_IDS` - Comma-separated list of user UUIDs that receive superadmin privileges on user-level keys (no org). **Must be set in every environment.** Example: `SUPERADMIN_USER_IDS=a1621dd6-3298-473f-b2ad-232ca72c3df5`. If left empty, no user gets superadmin access via this mechanism. This variable replaces the previously hardcoded UUID. See also: the `is_super_admin` flag returned by the auth service, which takes effect independently of this list.

## Architecture

```
app/
├── api/
│   └── v1/
│       └── endpoints.py    # API routes
├── core/
│   ├── config.py          # Configuration
│   ├── response.py        # Shared error/success response helpers
│   └── security.py        # Key generation
├── db/
│   ├── models.py          # Database models
│   └── session.py         # Database session
├── middleware/
│   └── timing.py          # X-Processing-Time-Ms header middleware
├── models/
│   └── schemas.py         # Pydantic schemas
├── services/
│   └── key_service.py     # Business logic (includes permission allowlist)
└── main.py                # Application entry point
```

## Integration with Other Services

### Verifying Keys

Other services can verify API keys by calling:

```python
import httpx

async def verify_api_key(api_key: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://key-service:8003/api/v1/keys/verify",
            json={"key": api_key}
        )
        if response.status_code == 200:
            data = response.json()
            if data["valid"]:
                return {
                    "user_id": data["user_id"],
                    "permissions": data["permissions"]
                }
        return None
```

### Authentication

All endpoints (except `/verify`) require authentication via the Auth Service.
Include the JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Security

- Keys are generated using cryptographically secure random
- Keys are hashed (SHA-256) before storage
- Only key hashes are stored in database
- Actual keys are only shown once upon creation
- Keys can be revoked at any time
- Keys support expiration dates
- Usage is tracked for audit purposes

## Key Format

Generated keys follow this format:
```
ency_<random_32_chars>
```

Example: `ency_Xk9mP2vN8qR5tY7wZ3bC6fH1jL4nM0sA`

## Monitoring

- Health check: `/health`
- Prometheus metrics: Port 9003 (if enabled)
- Logs: Structured JSON logs to stdout

## License

Proprietary - Encypher Corporation
