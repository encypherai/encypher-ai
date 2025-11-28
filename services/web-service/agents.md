# Web Service Agents Guide

## Context
This service handles the backend functionality for the public marketing website (encypherai.com).
It is designed to be a lightweight service separate from the core `enterprise_api`.

**Migrated from**: `encypher_website/backend` (old monolithic backend)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/ai-demo/demo-requests` | POST | AI demo page requests |
| `/api/v1/ai-demo/analytics/events` | POST | AI demo analytics |
| `/api/v1/publisher-demo/demo-requests` | POST | Publisher demo requests |
| `/api/v1/publisher-demo/analytics/events` | POST | Publisher demo analytics |
| `/api/v1/sales/enterprise-requests` | POST | Enterprise sales inquiries |
| `/api/v1/sales/general-requests` | POST | General sales inquiries |
| `/api/v1/demo-requests` | POST/GET | Legacy generic demo requests |
| `/api/v1/analytics` | POST | Legacy generic analytics |
| `/health` | GET | Health check |

## Responsibilities
- **Demo Requests**: Handle submissions from AI demo and publisher demo pages
- **Sales Contact Forms**: Handle enterprise and general sales inquiries
- **Web Analytics**: Track page views and user events
- **Email Notifications**: Send notifications to sales team and confirmations to users

## Dependencies
- **Database**: PostgreSQL (`encypher_web` database)
- **Auth**: Public endpoints for submission. Admin endpoints require internal auth (TODO)
- **Email**: SMTP server configuration (see `.env.example`)

## Development

```bash
# Install dependencies (UV required)
uv sync

# Run migrations
uv run alembic upgrade head

# Start server
uv run uvicorn app.main:app --reload --port 8002
```

- **Port**: 8002 (to avoid conflicts with other services)
- **Framework**: FastAPI
- **ORM**: SQLAlchemy + Alembic
- **Package Manager**: UV (migrated from Poetry)

## Environment Variables

Required in production:
- `POSTGRES_SERVER`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `SECRET_KEY`
- `EMAILS_ENABLED=true` with SMTP configuration

See `.env.example` for full list.

## Known Issues / Todo
- [ ] **Authentication**: Admin endpoints need auth integration
- [ ] **Email Templates**: HTML templates are hardcoded; consider external templates
- [ ] **Analytics**: Basic implementation; consider PostHog/Plausible for scale
