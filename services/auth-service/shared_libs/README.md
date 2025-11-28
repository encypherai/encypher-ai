# EncypherAI Commercial Shared Library

Shared Python library for EncypherAI commercial tools and services.

> **⚠️ Auto-Sync Enabled:** Changes to this directory are automatically synced to `services/*/shared_libs/` via GitHub Actions. See `.github/workflows/sync-shared-libs.yml`.

## Structure

```
shared_commercial_libs/
├── src/
│   └── encypher_commercial_shared/
│       ├── __init__.py
│       ├── core/           # EncypherAI wrapper (CLI tools)
│       │   ├── api.py      # EncypherAI class, VerificationResult
│       │   └── utils.py    # scan_directory, generate_report
│       ├── db/             # Database utilities (microservices)
│       │   ├── __init__.py
│       │   └── startup.py  # ensure_database_ready, check_database_connection
│       └── email/          # Email functionality (services)
│           ├── sender.py   # EmailConfig, send_email
│           ├── emails.py   # Pre-built email functions
│           └── templates/  # Jinja2 email templates
├── tests/
├── pyproject.toml
└── README.md
```

## Modules

### `core` - EncypherAI Wrapper
High-level API for CLI tools (audit_log_cli, policy_validator_cli).

```python
from encypher_commercial_shared import EncypherAI, VerificationResult
from encypher_commercial_shared.core import scan_directory, generate_report

encypher = EncypherAI(trusted_signers={"signer1": "key.pem"})
result = encypher.verify_from_text("Text with metadata")
```

### `db` - Database Startup Utilities
Database connection validation and migration utilities for microservices.

```python
from encypher_commercial_shared.db import (
    ensure_database_ready,
    check_database_connection,
    run_migrations_if_needed,
    DatabaseStartupError,
)

# Simple usage - validates connection and runs migrations
ensure_database_ready(
    service_name="auth-service",
    alembic_config_path="alembic.ini"
)

# Or with more control
check_database_connection(
    database_url=os.environ["DATABASE_URL"],
    max_retries=5,
    retry_delay=2.0,
    service_name="auth-service"
)

# Run migrations separately
run_migrations_if_needed(
    alembic_config_path="alembic.ini",
    service_name="auth-service",
    auto_upgrade=True
)
```

**Features:**
- Connection validation with configurable retries
- Automatic Alembic migration detection and execution
- Clear error messages for common issues (empty URL, invalid format)
- Graceful handling of missing alembic.ini
- Logging with service name prefix

### `email` - Email Service
Shared email functionality for microservices.

```python
from encypher_commercial_shared.email import (
    EmailConfig,
    send_email,
    send_verification_email,
    send_welcome_email,
)

# From environment variables
config = EmailConfig.from_env()

# Or explicit
config = EmailConfig(
    smtp_host="smtp.zoho.com",
    smtp_user="support@encypherai.com",
    smtp_pass="...",
)

# Send pre-built email
send_verification_email(config, "user@example.com", "John", token)

# Or custom email
send_email(config, "user@example.com", "Subject", "<h1>HTML</h1>")
```

## Installation

```bash
# From another project in the monorepo
uv pip install -e ../shared_commercial_libs

# Or add to pyproject.toml dependencies
# "encypher-commercial-shared"
```

## Environment Variables (for email)

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_HOST` | smtp.zoho.com | SMTP server |
| `SMTP_PORT` | 587 | SMTP port |
| `SMTP_USER` | | SMTP username |
| `SMTP_PASS` | | SMTP password |
| `SMTP_TLS` | true | Use TLS |
| `EMAIL_FROM` | support@encypherai.com | From address |
| `EMAIL_FROM_NAME` | Support - Encypher | From name |
| `FRONTEND_URL` | http://localhost:3000 | For email links |
| `DASHBOARD_URL` | | Dashboard URL |

## Development

```bash
cd shared_commercial_libs
uv sync
uv run pytest tests/
```
