# Encypher Notification Service

Notification microservice for the Encypher platform.

## Features

- ✅ Email notifications
- ✅ SMS notifications (planned)
- ✅ Webhook delivery (planned)
- ✅ Notification history

## Tech Stack

- FastAPI, Uvicorn
- PostgreSQL, Redis
- SMTP integration

## Setup

```bash
cd services/notification-service
uv sync
cp .env.example .env.local
uv run python -m app.main
```

Service at: http://localhost:8008

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/notifications/send` | Send notification |
| GET | `/api/v1/notifications/notifications` | List notifications |
| GET | `/health` | Health check |

## License

Proprietary - Encypher AI