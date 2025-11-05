# Encypher Auth Service

Authentication and authorization microservice for the Encypher platform.

## Features

- ✅ User registration and login
- ✅ JWT-based authentication
- ✅ Refresh token management
- ✅ OAuth integration (Google, GitHub)
- ✅ Password hashing with bcrypt_sha256 (passlib)
- ✅ Prometheus metrics exposed at `/metrics`
- ✅ Token verification for other services
- ✅ Session management
- ✅ Health check endpoints

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Cache:** Redis
- **Package Manager:** UV
- **Authentication:** JWT (PyJWT)
- **Password Hashing:** bcrypt_sha256 (passlib)

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- UV package manager

### Installation

1. **Install dependencies:**
   ```bash
   cd services/auth-service
   uv sync
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Set up database:**
   ```bash
   # Create database
   createdb encypher_auth
   
   # Run migrations (tables will be created automatically on startup)
   ```

4. **Run the service:**
   ```bash
   uv run python -m app.main
   ```

The service will be available at `http://localhost:8001`

## API Endpoints

### Authentication

**POST /api/v1/auth/signup**
- Create a new user account
- Body: `{ "email": "user@example.com", "password": "password123", "name": "John Doe" }`
- Returns: User object

**POST /api/v1/auth/login**
- Authenticate user
- Body: `{ "email": "user@example.com", "password": "password123" }`
- Returns: `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer" }`

**POST /api/v1/auth/refresh**
- Refresh access token
- Body: `{ "refresh_token": "..." }`
- Returns: New access token

**POST /api/v1/auth/logout**
- Revoke tokens
- Provide either:
  - Body: `{ "refresh_token": "..." }` (revokes that token), or
  - Header: `Authorization: Bearer <access_token>` (revokes all refresh tokens for the user)
- Returns: Success message

**POST /api/v1/auth/verify**
- Verify access token (used by other services)
- Header: `Authorization: Bearer <token>`
- Returns: User object

### Health

**GET /health**
- Health check endpoint
- Returns: `{ "status": "healthy", "service": "auth-service" }`

## Docker

### Build

```bash
docker build -t encypher-auth-service .
```

### Run

```bash
docker run -p 8001:8001 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e JWT_SECRET_KEY=your-secret-key \
  encypher-auth-service
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

### Type checking

```bash
uv run mypy app/
```

## Environment Variables

See `.env.example` for all available configuration options.

### Required

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT signing

### Optional

- `SERVICE_PORT` - Port to run on (default: 8001)
- `LOG_LEVEL` - Logging level (default: INFO)
- `REDIS_URL` - Redis connection string
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `GITHUB_CLIENT_ID` - GitHub OAuth client ID
- `GITHUB_CLIENT_SECRET` - GitHub OAuth client secret

## Architecture

```
app/
├── api/
│   └── v1/
│       └── endpoints.py    # API routes
├── core/
│   ├── config.py          # Configuration
│   └── security.py        # Security utilities
├── db/
│   ├── models.py          # Database models
│   └── session.py         # Database session
├── models/
│   └── schemas.py         # Pydantic schemas
├── services/
│   └── auth_service.py    # Business logic
└── main.py                # Application entry point
```

## Integration with Other Services

Other services can verify tokens by calling:

```python
import httpx

async def verify_token(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://auth-service:8001/api/v1/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None
```

## Security

- Passwords are hashed using bcrypt
- JWT tokens are signed with HS256
- Refresh tokens are stored in database
- Tokens can be revoked
- Rate limiting recommended at API Gateway level

## Monitoring

- Health check: `/health`
- Prometheus metrics: `/metrics` (same service port)
- Logs: Structured JSON logs to stdout

## License

Proprietary - Encypher AI
