# EncypherAI Dashboard Backend

This is the FastAPI backend for the EncypherAI Compliance Readiness Dashboard. It provides API endpoints for authentication, audit logs, policy validation, and CLI tool integration.

## Features

- **Authentication**: JWT-based authentication for secure API access
- **Audit Logs**: Endpoints for retrieving and analyzing audit log data
- **Policy Validation**: Endpoints for policy schemas and validation results
- **CLI Integration**: Endpoints for running the audit_log_cli and policy_validator_cli tools
- **Database**: Async SQLAlchemy ORM with PostgreSQL or SQLite database

## Setup

1. Ensure Python and UV are installed.
2. Navigate to this directory (`dashboard_app/backend`).
3. Create and activate a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows PowerShell
   ```
4. Install dependencies:
   ```bash
   uv pip sync
   ```
   *Note: For database drivers, ensure you have the appropriate async driver installed:*
   - *For SQLite (development): `uv pip install aiosqlite`*
   - *For PostgreSQL (production): `uv pip install asyncpg`*
5. **Set up Database**:
   
   **For Development (SQLite)**:
   No additional setup is required as SQLite creates a file-based database.
   
   **For Production (PostgreSQL)**:
   Ensure you have a PostgreSQL server running and accessible. You can install it directly or use Docker:
   ```bash
   # Example using Docker:
   docker run --name encypherai-postgres -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=appdb_dev -p 5432:5432 -d postgres
   ```
   This command starts a PostgreSQL container named `encypherai-postgres` with a user `user`, password `password`, and a database `appdb_dev`. Adjust these values as needed to match your `.env` configuration.

6. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file to configure your database connection:
   
   **For Development (SQLite)**:
   ```
   DATABASE_URL=sqlite+aiosqlite:///./encypherai_dashboard.db
   ```
   
   **For Production (PostgreSQL)**:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/appdb_dev
   ```
   
   Also ensure other settings (like `SECRET_KEY`) are correctly configured.

## Database Initialization

The application uses async SQLAlchemy with either SQLite (for development) or PostgreSQL (for production). The database tables are created automatically when running the initialization script.

To initialize the database with sample data, run:


```bash
uv run python scripts/init_db.py
```

## Running the Development Server

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - Get access token
- `GET /api/v1/auth/me` - Get current user information

### Audit Logs

- `GET /api/v1/audit-logs/` - List audit logs with filtering
- `GET /api/v1/audit-logs/stats` - Get audit log statistics
- `GET /api/v1/audit-logs/{audit_log_id}` - Get specific audit log
- `POST /api/v1/audit-logs/` - Create new audit log

### Policy Validation

- `GET /api/v1/policy-validation/schemas/` - List policy schemas
- `POST /api/v1/policy-validation/schemas/` - Create new policy schema
- `GET /api/v1/policy-validation/schemas/{schema_id}` - Get specific policy schema
- `GET /api/v1/policy-validation/results/` - List validation results with filtering
- `GET /api/v1/policy-validation/stats` - Get validation statistics
- `GET /api/v1/policy-validation/results/{result_id}` - Get specific validation result
- `POST /api/v1/policy-validation/results/` - Create new validation result
- `POST /api/v1/policy-validation/import-csv/` - Import validation results from CSV

### CLI Integration

- `POST /api/v1/cli/scan` - Run a scan using the CLI tools

## Integration with CLI Tools

The backend can integrate with the audit_log_cli and policy_validator_cli tools to run scans and import the results into the database. This is done through the `services/cli_integration.py` module.

## Project Structure

```
backend/
├── app/                    # Main application package
│   ├── api/                # API endpoints
│   │   ├── endpoints/      # Endpoint modules by feature
│   │   └── api.py          # API router
│   ├── core/               # Core modules
│   │   ├── config.py       # Configuration settings
│   │   ├── database.py     # Database connection
│   │   └── security.py     # Security utilities
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   └── main.py             # Application entry point
├── scripts/                # Utility scripts
│   └── init_db.py          # Database initialization
├── .env.example           # Environment variables template
├── pyproject.toml         # Project dependencies
└── README.md              # This file
```
