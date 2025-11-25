# Coalition Service

Coalition infrastructure and auto-onboarding microservice for Encypher platform.

## Overview

The Coalition Service manages the coalition membership infrastructure that automatically onboards free tier users into a content licensing collective. This enables small publishers to pool their content for bulk licensing to AI companies.

## Features

- **Auto-Onboarding**: Automatically enroll free tier users upon signup
- **Content Aggregation**: Index and aggregate signed content from coalition members
- **Licensing Management**: Create and manage bulk licensing agreements with AI companies
- **Revenue Distribution**: Calculate and distribute revenue to coalition members
- **Access Tracking**: Track content access by AI companies

## Architecture

- **Port**: 8009
- **Database**: PostgreSQL
- **Cache**: Redis
- **Framework**: FastAPI

## API Endpoints

### Coalition Member Endpoints

- `POST /api/v1/coalition/join` - Join the coalition
- `POST /api/v1/coalition/leave` - Leave the coalition (opt-out)
- `GET /api/v1/coalition/status/{user_id}` - Get membership status
- `GET /api/v1/coalition/stats/{user_id}` - Get coalition statistics
- `GET /api/v1/coalition/revenue/{user_id}` - Get revenue breakdown

### Licensing Agreement Endpoints (Admin)

- `POST /api/v1/coalition/agreements` - Create licensing agreement
- `GET /api/v1/coalition/agreements` - List all agreements

### Content Management

- `POST /api/v1/coalition/content` - Index signed content
- `GET /api/v1/coalition/content-pool` - View content pool (Admin)
- `POST /api/v1/coalition/track-access` - Track content access

## Database Schema

### Tables

- `coalition_members` - Coalition membership records
- `coalition_content` - Aggregated signed content
- `licensing_agreements` - Licensing deals with AI companies
- `content_access_logs` - Access tracking
- `revenue_distributions` - Revenue calculation records
- `member_revenue` - Individual member payouts
- `coalition_settings` - Configuration settings

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+

### Installation

1. Install dependencies:
```bash
uv pip install -r pyproject.toml
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the service:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8009
```

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Configuration

Key environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SERVICE_PORT` - Service port (default: 8009)
- `REVENUE_SPLIT_ENCYPHER` - Encypher revenue share % (default: 30)
- `REVENUE_SPLIT_MEMBERS` - Members revenue share % (default: 70)
- `MIN_PAYOUT_THRESHOLD` - Minimum payout amount (default: 10 USD)
- `AUTO_ONBOARD_FREE_TIER` - Auto-enroll free tier users (default: true)

## Revenue Distribution

The coalition uses a 70/30 revenue split:
- **70%** to coalition members (distributed based on content usage)
- **30%** to Encypher platform

Revenue is calculated monthly and distributed based on:
- Number of documents contributed
- Number of times content was accessed
- Quality/engagement metrics (future)

## Integration

### Auth Service Integration

The auth-service should call the coalition join endpoint during free tier signup:

```python
# In auth-service signup flow
if user_tier == "free":
    await coalition_client.join_coalition(
        user_id=user.id,
        tier="free",
        accept_terms=True
    )
```

### Enterprise API Integration

The enterprise_api should index content after signing:

```python
# After document signing
await coalition_client.index_content(
    member_id=member.id,
    document_id=document.id,
    content_hash=document.hash,
    content_type="article",
    word_count=document.word_count,
    signed_at=document.signed_at
)
```

## Monitoring

- Health check: `GET /health`
- Metrics: `GET /metrics` (Prometheus format)

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black app/
ruff check app/
```

## License

Copyright © 2025 Encypher Corporation
