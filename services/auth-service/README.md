# Encypher Auth Service

Authentication and authorization microservice for the Encypher platform.

## Features

- ✅ User registration and login
- ✅ **Email verification flow** (verification required before login)
- ✅ JWT-based authentication
- ✅ Refresh token management
- ✅ OAuth integration (Google, GitHub)
- ✅ Password hashing with bcrypt (SHA-256 prehash)
- ✅ Prometheus metrics exposed at `/metrics`
- ✅ Token verification for other services
- ✅ Session management
- ✅ Health check endpoints
- ✅ **Branded email templates** (via shared library)
- ✅ **Team Management** (Organizations, Members, Invitations)
- ✅ **Role-based Access Control** (Owner, Admin, Manager, Member, Viewer)
- ✅ **Audit Logging** for organization actions
- 🚧 **SAML SSO (Enterprise)** — metadata/login scaffolding; ACS currently fails closed until full validation is implemented
- ✅ **SCIM 2.0 (Enterprise)** — Users provisioning endpoints under `/scim/v2` with org-scoped bearer tokens (tenant isolated)

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Cache:** Redis
- **Package Manager:** UV
- **Authentication:** JWT (PyJWT)
- **Password Hashing:** bcrypt (with SHA-256 prehash)

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
- Sends verification email automatically
- Body: `{ "email": "user@example.com", "password": "password123", "name": "John Doe" }`
- Returns: User object with `verification_email_sent: true`

**POST /api/v1/auth/verify-email**
- Verify user's email address
- Body: `{ "token": "verification-token-from-email" }`
- Returns: User object (sends welcome email on success)

**POST /api/v1/auth/resend-verification**
- Resend verification email
- Body: `{ "email": "user@example.com" }`
- Returns: Success message (rate limited: 3 per 5 minutes)

**POST /api/v1/auth/login**
- Authenticate user (requires verified email)
- Body: `{ "email": "user@example.com", "password": "password123" }`
- Returns: `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer" }`
- Error 403 if email not verified

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

### SAML SSO (Enterprise)

**GET /api/v1/auth/saml/metadata**
- Query params: `org_id`
- Returns: SP metadata XML

**GET /api/v1/auth/saml/login**
- Query params: `org_id`, `return_to` (optional)
- Returns: Redirect to dashboard SSO entrypoint with `SAMLRequest` + `RelayState`
- `return_to` is allowlisted (must be a relative path or match configured frontend origins); untrusted values return 400

**POST /api/v1/auth/saml/acs**
- Form fields: `SAMLResponse`, `RelayState` (optional)
- Currently: returns `501 Not Implemented` for base64-valid `SAMLResponse` (fail-closed until signature/conditions validation is implemented)

### Team Management (Organizations)

**POST /api/v1/organizations**
- Create a new organization (current user becomes owner)
- Body: `{ "name": "Acme Corp", "email": "team@acme.com" }`
- Returns: Organization object

**GET /api/v1/organizations**
- List organizations the current user belongs to
- Returns: Array of organization objects

**GET /api/v1/organizations/:id**
- Get organization details
- Returns: Organization object

**PATCH /api/v1/organizations/:id**
- Update organization settings (Admin+ only)
- Body: `{ "name": "New Name" }`
- Returns: Updated organization object

### Team Members

**GET /api/v1/organizations/:id/members**
- List all members of an organization
- Returns: Array of member objects with user details

**PATCH /api/v1/organizations/:id/members/:userId**
- Update a member's role (Admin+ only)
- Body: `{ "role": "admin" }` (admin, manager, member, viewer)
- Returns: Updated member object

**DELETE /api/v1/organizations/:id/members/:userId**
- Remove a member from the organization (Admin+ only)
- Returns: Success message

**GET /api/v1/organizations/:id/seats**
- Get seat usage information
- Returns: `{ "used": 3, "max": 5, "available": 2, "unlimited": false }`

### Invitations

**POST /api/v1/organizations/:id/invitations**
- Send an invitation to join the organization (Manager+ only)
- Body: `{ "email": "new@example.com", "role": "member", "message": "Welcome!" }`
- Returns: Invitation object

**GET /api/v1/organizations/:id/invitations**
- List pending invitations (Manager+ only)
- Returns: Array of invitation objects

**DELETE /api/v1/organizations/:id/invitations/:invitationId**
- Cancel a pending invitation (Manager+ only)
- Returns: Success message

**POST /api/v1/organizations/:id/invitations/:invitationId/resend**
- Resend an invitation (generates new token, extends expiry)
- Returns: Updated invitation object

**GET /api/v1/organizations/invitations/:token**
- Get invitation details (public endpoint for invitation page)
- Returns: Invitation details including org name, inviter, role

**POST /api/v1/organizations/invitations/:token/accept**
- Accept invitation (for logged-in users)
- Returns: Membership details

**POST /api/v1/organizations/invitations/:token/accept-new**
- Accept invitation and create new account
- Body: `{ "name": "John Doe", "password": "securepass123" }`
- Returns: User object, membership, and auth tokens

### Audit Logs

**GET /api/v1/organizations/:id/audit-logs**
- Get organization audit logs (any member)
- Query params: `limit`, `offset`, `action` (filter)
- Returns: Array of audit log entries

### SCIM 2.0 (Enterprise Provisioning)

All SCIM endpoints use media type `application/scim+json`.

Auth:
- Header: `Authorization: Bearer <token>`
- Token format: `scim.<org_id>.<secret>`
- Only a SHA-256 hash of the token is stored (in `organizations.features["scim_bearer_token_hash"]`)

**GET /scim/v2/Users**
- Returns only users who are members of the authenticated organization (tenant isolated)

**POST /scim/v2/Users**
- Creates or updates a user by `userName` (email)
- Ensures the user is a member of the authenticated organization (default role = `member`); membership insert is idempotent

**GET /scim/v2/Users/{id}**
- Returns 404 if the user is not found or not a member of the authenticated organization

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

### Email Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_HOST` | smtp.zoho.com | SMTP server hostname |
| `SMTP_PORT` | 587 | SMTP server port |
| `SMTP_USER` | | SMTP username (email address) |
| `SMTP_PASS` | | SMTP password or app password |
| `SMTP_TLS` | true | Enable TLS encryption |
| `EMAIL_FROM` | support@encypherai.com | From email address |
| `EMAIL_FROM_NAME` | Support - Encypher | From display name |
| `FRONTEND_URL` | http://localhost:3000 | Frontend URL for email links |
| `DASHBOARD_URL` | | Dashboard URL (optional) |
| `VERIFICATION_TOKEN_EXPIRE_HOURS` | 24 | Token expiry time |

## Architecture

```
app/
├── api/
│   ├── scim.py                # SCIM 2.0 provisioning endpoints
│   └── v1/
│       ├── endpoints.py       # Auth API routes
│       ├── organizations.py   # Team management API routes
│       └── saml.py            # SAML SSO endpoints
├── core/
│   ├── config.py              # Configuration
│   └── security.py            # Security utilities
├── db/
│   ├── models.py              # Database models (User, Organization, etc.)
│   └── session.py             # Database session
├── models/
│   └── schemas.py             # Pydantic schemas
├── services/
│   ├── auth_service.py        # Authentication business logic
│   └── organization_service.py # Team management business logic
├── deps/
│   └── rate_limit.py          # Rate limiting
└── main.py                    # Application entry point

alembic/
└── versions/
    ├── 001_initial_schema.py  # Users, tokens tables
    └── 002_team_management.py # Organizations, members, invitations

tests/
├── conftest.py                # Pytest configuration
├── test_api_access_gating.py   # Unit tests
├── test_organization_service.py # Unit tests
├── test_saml_contract.py       # Contract tests (SAML)
├── test_scim_users_contract.py # Contract tests (SCIM Users)
└── integration/
    ├── test_auth_flow.py      # E2E tests (requires running service)
    └── test_organization_api.py # E2E tests (requires running service)
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

## Role-Based Access Control

The team management system uses a 5-level role hierarchy:

| Role | Level | Permissions |
|------|-------|-------------|
| **Owner** | 5 | Full control, cannot be removed |
| **Admin** | 4 | Manage members, billing, settings, API keys |
| **Manager** | 3 | Invite members, create API keys |
| **Member** | 2 | Use API keys, view own analytics |
| **Viewer** | 1 | Read-only access |

### Permission Matrix

| Action | Owner | Admin | Manager | Member | Viewer |
|--------|-------|-------|---------|--------|--------|
| Invite members | ✅ | ✅ | ✅ | ❌ | ❌ |
| Manage members | ✅ | ✅ | ❌ | ❌ | ❌ |
| Manage billing | ✅ | ✅ | ❌ | ❌ | ❌ |
| Create API keys | ✅ | ✅ | ✅ | ❌ | ❌ |
| View audit logs | ✅ | ✅ | ✅ | ✅ | ✅ |

### Seat Limits by Plan

| Plan | Max Seats |
|------|-----------|
| Starter | 1 (no team features) |
| Professional | 1 (no team features) |
| Business | 5 |
| Enterprise | Unlimited |

## Security

- Passwords are hashed using bcrypt
- JWT tokens are signed with HS256
- Refresh tokens are stored in database
- Tokens can be revoked
- SCIM bearer tokens are stored hashed only (SHA-256) and scoped to a single organization
- SCIM Users endpoints are tenant isolated (OrganizationMember-scoped)
- SAML ACS fails closed (returns 501) until signature/conditions validation is implemented
- SAML login `return_to` is allowlisted (open redirect prevention)
- Request logs redact SAML/SCIM query params and common auth token keys
- Rate limiting recommended at API Gateway level
- Invitation tokens are cryptographically secure, expire after 7 days
- All team actions are logged to audit log
- Owner role is protected (cannot be removed or demoted)

## Monitoring

- Health check: `/health`
- Prometheus metrics: `/metrics` (same service port)
- Logs: Structured JSON logs to stdout

## License

Proprietary - Encypher Corporation
