# Encypher User Service

User management microservice for the Encypher platform.

## Features

- ✅ User profiles
- ✅ Team management
- ✅ User preferences

## Tech Stack

- FastAPI, Uvicorn
- PostgreSQL, Redis
- SQLAlchemy, Pydantic

## Setup

```bash
cd services/user-service
uv sync
cp .env.example .env.local
uv run python -m app.main
```

Service at: http://localhost:8002

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/profile` | Get profile |
| PUT | `/api/v1/users/profile` | Update profile |
| POST | `/api/v1/users/teams` | Create team |
| GET | `/api/v1/users/teams` | List teams |
| GET | `/health` | Health check |

## License

Proprietary - Encypher Corporation