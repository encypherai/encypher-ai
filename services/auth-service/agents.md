# Auth Service - Agent Development Guide

## Overview
Microservice providing JWT-based authentication, OAuth integration, session management, and **team management** for the Encypher platform.

## Current Status
✅ **Production Ready** - Fully functional authentication service
✅ **Well Documented** - Complete README with API reference
✅ **Clean Architecture** - FastAPI best practices
✅ **Team Management** - Organizations, members, invitations, RBAC (Nov 2025)
✅ **Unit Tests** - 29 tests for OrganizationService

## Architecture

### Tech Stack
- **Framework**: FastAPI (async)
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Cache**: Redis (session management)
- **Package Manager**: UV
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt_sha256 (passlib)
- **OAuth**: Google, GitHub integration

### Service Information
- **Port**: 8001
- **Base URL**: `http://localhost:8001`
- **Health Check**: `GET /health`
- **API Version**: v1 (`/api/v1/auth/*`)

### Directory Structure
```
auth-service/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints.py     # Auth API routes
│   │       └── organizations.py # Team management routes
│   ├── core/
│   │   ├── config.py        # Pydantic settings
│   │   └── security.py      # JWT, password hashing
│   ├── db/
│   │   ├── models.py        # SQLAlchemy models (User, Organization, etc.)
│   │   └── session.py       # Database session
│   ├── models/
│   │   └── schemas.py       # Pydantic schemas
│   └── services/
│       ├── auth_service.py        # Auth business logic
│       └── organization_service.py # Team management logic
├── alembic/
│   └── versions/
│       ├── 001_initial_schema.py
│       └── 002_team_management.py
├── tests/
│   ├── conftest.py
│   └── test_organization_service.py
├── .env.example
├── Dockerfile
├── pytest.ini
├── pyproject.toml
└── README.md
```

## Development Constraints

### Package Management
**CRITICAL**: Always use UV for package management
```bash
# Add dependency
uv add fastapi sqlalchemy

# Add dev dependency
uv add --dev pytest pytest-asyncio

# Never edit pyproject.toml directly
# Never use pip commands
```

### Running Locally
```bash
# Navigate to service
cd services/auth-service

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run the service
uv run python -m app.main

# Or with uvicorn directly
uv run uvicorn app.main:app --reload --port 8001
```

### Testing
```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=app --cov-report=html

# Specific test file
uv run pytest tests/test_auth.py -v

# Integration tests
uv run pytest tests/integration/ -v
```

### Code Quality
```bash
# Linting
uv run ruff check app/

# Formatting
uv run black app/

# Type checking
uv run mypy app/
```

## API Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/signup
Create a new user account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "John Doe"
}
```

**Response**:
```json
{
  "id": "user_abc123",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-10-30T12:00:00Z"
}
```

#### POST /api/v1/auth/login
Authenticate user and receive tokens.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST /api/v1/auth/refresh
Refresh access token using refresh token.

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST /api/v1/auth/logout
Revoke refresh token (logout).

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response**:
```json
{
  "message": "Successfully logged out"
}
```

#### POST /api/v1/auth/verify
Verify access token (used by other services).

**Headers**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Response**:
```json
{
  "id": "user_abc123",
  "email": "user@example.com",
  "name": "John Doe",
  "roles": ["user"]
}
```

### OAuth Endpoints

#### GET /api/v1/auth/oauth/google
Initiate Google OAuth flow.

#### GET /api/v1/auth/oauth/google/callback
Google OAuth callback handler.

#### GET /api/v1/auth/oauth/github
Initiate GitHub OAuth flow.

#### GET /api/v1/auth/oauth/github/callback
GitHub OAuth callback handler.

### Health Check

#### GET /health
Service health check.

**Response**:
```json
{
  "status": "healthy",
  "service": "auth-service",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}
```

## Configuration

### Required Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/encypher_auth

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Service
SERVICE_NAME=auth-service
SERVICE_PORT=8001
LOG_LEVEL=INFO
```

### Optional Environment Variables
```bash
# Redis (for session management)
REDIS_URL=redis://localhost:6379/0

# OAuth - Google
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8001/api/v1/auth/oauth/google/callback

# OAuth - GitHub
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:8001/api/v1/auth/oauth/github/callback

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

## Integration Points

### Used By (Consumers)
- **API Gateway** - Routes requests, validates tokens
- **User Service** - User profile management
- **Billing Service** - Subscription management
- **Dashboard App** - User authentication
- **Enterprise API** - API key validation
- **All other services** - Token verification

### Dependencies (Upstream)
- **PostgreSQL** - User data persistence
- **Redis** - Session management, token blacklist
- None on other microservices (independent)

### Integration Pattern
Other services verify tokens by calling:
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

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    password_hash VARCHAR(255),
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Refresh Tokens Table
```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
```

## Security Considerations

### Password Security
- **Hashing**: bcrypt_sha256 with cost factor ≥ 12
- **Minimum Length**: 8 characters
- **Complexity**: Enforced (uppercase, lowercase, number, special char)
- **Storage**: Never store plaintext passwords

### Token Security
- **JWT Algorithm**: HS256 (HMAC with SHA-256)
- **Secret Key**: Minimum 32 characters, random
- **Access Token**: Short-lived (1 hour default)
- **Refresh Token**: Long-lived (30 days default)
- **Token Revocation**: Refresh tokens stored in database, can be revoked

### OAuth Security
- **State Parameter**: CSRF protection
- **PKCE**: Code challenge for mobile apps
- **Redirect URI**: Whitelist validation
- **Token Exchange**: Secure server-to-server

### Rate Limiting
- **Login Attempts**: 5 per 15 minutes per IP
- **Signup**: 3 per hour per IP
- **Token Refresh**: 10 per minute per user
- **Password Reset**: 3 per hour per email

## Common Development Tasks

### Adding a New OAuth Provider
1. Add provider config in `app/core/config.py`
2. Create OAuth handler in `app/services/auth_service.py`
3. Add routes in `app/api/v1/endpoints.py`
4. Add provider-specific logic
5. Update tests
6. Update documentation

### Modifying Token Expiration
1. Update settings in `app/core/config.py`
2. Update token generation in `app/core/security.py`
3. Update tests
4. Document changes

### Adding User Roles/Permissions
1. Add role column to users table (migration)
2. Update user model in `app/db/models.py`
3. Add role validation in `app/core/security.py`
4. Update token payload to include roles
5. Add role-based decorators
6. Update tests

### Implementing 2FA
1. Add 2FA fields to users table
2. Install TOTP library: `uv add pyotp`
3. Add 2FA setup endpoint
4. Add 2FA verification in login flow
5. Add backup codes
6. Update tests

## Testing Strategy

### Unit Tests
- Password hashing/verification
- Token generation/validation
- User model methods
- Service layer logic

### Integration Tests
- Signup flow
- Login flow
- Token refresh flow
- OAuth flows
- Token verification

### End-to-End Tests
- Complete authentication workflow
- Multi-service token validation
- Session management

### Test Coverage Goals
- Routes: 90%+
- Services: 90%+
- Security utils: 95%+
- Overall: 85%+

## Performance Considerations

### Benchmarks (Target)
| Operation | Avg Latency | P95 | P99 |
|-----------|-------------|-----|-----|
| Signup | 150ms | 250ms | 400ms |
| Login | 120ms | 200ms | 350ms |
| Token Refresh | 50ms | 80ms | 120ms |
| Token Verify | 30ms | 50ms | 80ms |

### Optimization Strategies
- **Password Hashing**: Use async bcrypt
- **Database**: Connection pooling (10-20 connections)
- **Redis**: Cache user data for token verification
- **Token Verification**: Cache public keys
- **Rate Limiting**: Use Redis for distributed rate limiting

## Monitoring & Observability

### Metrics to Track
- **Authentication Success Rate**: % successful logins
- **Token Refresh Rate**: Refreshes per hour
- **Failed Login Attempts**: By IP, by user
- **OAuth Success Rate**: By provider
- **Response Times**: P50, P95, P99
- **Active Sessions**: Current active users

### Logging
```python
# Structured logging format
{
  "timestamp": "2025-10-30T12:00:00Z",
  "level": "INFO",
  "service": "auth-service",
  "event": "user_login",
  "user_id": "user_abc123",
  "ip": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "duration_ms": 120
}
```

### Alerts
- **High Failed Login Rate**: > 10% in 5 minutes
- **Token Verification Failures**: > 5% in 5 minutes
- **Database Connection Issues**: Any connection failures
- **Redis Connection Issues**: Any connection failures
- **High Response Times**: P95 > 500ms

## Troubleshooting

### Service Won't Start
```bash
# Check database connection
psql $DATABASE_URL

# Check Redis connection
redis-cli -u $REDIS_URL ping

# Check environment variables
cat .env

# Check logs
uv run python -m app.main
```

### Token Verification Fails
```bash
# Check JWT secret key
echo $JWT_SECRET_KEY

# Verify token manually
uv run python -c "
from app.core.security import verify_token
token = 'your-token-here'
print(verify_token(token))
"

# Check token expiration
# Decode JWT at jwt.io
```

### Database Migration Issues
```bash
# Check current migration
uv run alembic current

# View migration history
uv run alembic history

# Rollback and retry
uv run alembic downgrade -1
uv run alembic upgrade head
```

### OAuth Not Working
```bash
# Check OAuth credentials
echo $GOOGLE_CLIENT_ID
echo $GITHUB_CLIENT_ID

# Check redirect URIs
# Must match exactly in OAuth provider settings

# Test OAuth flow manually
curl "http://localhost:8001/api/v1/auth/oauth/google"
```

## Docker Deployment

### Build Image
```bash
docker build -t encypher-auth-service .
```

### Run Container
```bash
docker run -p 8001:8001 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e JWT_SECRET_KEY=your-secret-key \
  -e REDIS_URL=redis://redis:6379/0 \
  encypher-auth-service
```

### Docker Compose
```yaml
version: '3.8'
services:
  auth-service:
    build: .
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/encypher_auth
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
```

## Known Issues

### None Critical
The service is production-ready with no major known issues.

### Minor Enhancements
1. **Add 2FA Support** - TOTP-based two-factor authentication
2. **Add Social Login** - More OAuth providers (Microsoft, Apple)
3. **Add Magic Links** - Passwordless authentication
4. **Add Session Management UI** - View/revoke active sessions

## Future Enhancements

### High Priority
1. **Two-Factor Authentication** - TOTP, SMS, email
2. **Magic Link Authentication** - Passwordless login
3. **Session Management** - View and revoke sessions
4. **Account Recovery** - Password reset, account unlock

### Medium Priority
5. **More OAuth Providers** - Microsoft, Apple, LinkedIn
6. **API Key Management** - Generate/revoke API keys
7. **Audit Logging** - Track all authentication events
8. **Brute Force Protection** - Advanced rate limiting

### Low Priority
9. **Biometric Authentication** - WebAuthn support
10. **SSO Integration** - SAML, OpenID Connect
11. **Multi-Tenancy** - Organization-based isolation

## Best Practices

### Token Management
- Keep access tokens short-lived (1 hour)
- Store refresh tokens securely
- Implement token rotation
- Revoke tokens on logout
- Blacklist compromised tokens

### Password Management
- Enforce strong password policies
- Use bcrypt with high cost factor
- Never log passwords
- Implement password reset flow
- Rate limit password attempts

### OAuth Integration
- Validate redirect URIs
- Use state parameter for CSRF
- Implement PKCE for mobile
- Handle OAuth errors gracefully
- Log OAuth events

### Error Handling
- Don't leak sensitive information
- Use generic error messages
- Log detailed errors server-side
- Return appropriate HTTP status codes
- Implement retry logic for transient errors

## License
Proprietary - Encypher Commercial Suite
