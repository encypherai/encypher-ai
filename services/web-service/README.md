# EncypherAI Web Service

Backend service for the EncypherAI marketing website, handling contact forms, demo requests, and web analytics.

## Features

- **Demo Requests**: API endpoints to submit and manage demo requests.
- **Analytics**: Event tracking for page views and user interactions.
- **Email Notifications**: Automated email notifications for new leads.
- **Database**: PostgreSQL integration with Alembic migrations.

## Setup

1. **Install Dependencies**:
   This project uses `poetry` for dependency management.
   ```bash
   poetry install
   ```

2. **Environment Variables**:
   Copy `.env.example` to `.env` and update the values.
   ```bash
   cp .env.example .env
   ```

3. **Database Migration**:
   Run Alembic migrations to set up the database schema.
   ```bash
   alembic upgrade head
   ```

4. **Run Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

## Testing

Run the test suite using `pytest`:
```bash
pytest
```
