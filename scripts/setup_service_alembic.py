#!/usr/bin/env python3
"""
Setup Alembic for a microservice with database-per-service architecture.

Usage:
    uv run python scripts/setup_service_alembic.py <service_name>
    
Example:
    uv run python scripts/setup_service_alembic.py key-service
"""
import os
import sys
from pathlib import Path

# Alembic configuration template
ALEMBIC_INI_TEMPLATE = '''# Alembic configuration for {service_name}

[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

# Database URL is set via environment variable
sqlalchemy.url = 

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
'''

ENV_PY_TEMPLATE = '''"""
Alembic environment configuration for {service_name}
"""
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Import models for autogenerate support
from app.db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    """Get database URL from environment variable."""
    return os.environ.get("DATABASE_URL", "postgresql://localhost/{db_name}")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={{"paramstyle": "named"}},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

SCRIPT_PY_MAKO_TEMPLATE = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''


def setup_alembic(service_name: str):
    """Set up Alembic for a service."""
    # Determine paths
    services_dir = Path(__file__).parent.parent / "services"
    service_dir = services_dir / service_name
    
    if not service_dir.exists():
        print(f"Error: Service directory not found: {service_dir}")
        sys.exit(1)
    
    alembic_dir = service_dir / "alembic"
    versions_dir = alembic_dir / "versions"
    
    # Create directories
    alembic_dir.mkdir(exist_ok=True)
    versions_dir.mkdir(exist_ok=True)
    
    # Database name (e.g., key-service -> encypher_keys)
    db_name_map = {
        "auth-service": "encypher_auth",
        "key-service": "encypher_keys",
        "billing-service": "encypher_billing",
        "user-service": "encypher_users",
        "notification-service": "encypher_notifications",
        "encoding-service": "encypher_encoding",
        "verification-service": "encypher_verification",
        "analytics-service": "encypher_analytics",
        "coalition-service": "encypher_coalition",
    }
    db_name = db_name_map.get(service_name, f"encypher_{service_name.replace('-', '_')}")
    
    # Write alembic.ini
    alembic_ini_path = service_dir / "alembic.ini"
    if not alembic_ini_path.exists():
        with open(alembic_ini_path, "w") as f:
            f.write(ALEMBIC_INI_TEMPLATE.format(service_name=service_name))
        print(f"Created: {alembic_ini_path}")
    else:
        print(f"Exists: {alembic_ini_path}")
    
    # Write env.py
    env_py_path = alembic_dir / "env.py"
    if not env_py_path.exists():
        with open(env_py_path, "w") as f:
            f.write(ENV_PY_TEMPLATE.format(service_name=service_name, db_name=db_name))
        print(f"Created: {env_py_path}")
    else:
        print(f"Exists: {env_py_path}")
    
    # Write script.py.mako
    mako_path = alembic_dir / "script.py.mako"
    if not mako_path.exists():
        with open(mako_path, "w") as f:
            f.write(SCRIPT_PY_MAKO_TEMPLATE)
        print(f"Created: {mako_path}")
    else:
        print(f"Exists: {mako_path}")
    
    # Create __init__.py in versions
    init_path = versions_dir / "__init__.py"
    if not init_path.exists():
        init_path.touch()
        print(f"Created: {init_path}")
    
    print(f"\n✅ Alembic setup complete for {service_name}")
    print(f"   Database: {db_name}")
    print(f"\nNext steps:")
    print(f"  1. Create initial migration:")
    print(f"     cd services/{service_name}")
    print(f"     alembic revision --autogenerate -m 'initial_schema'")
    print(f"  2. Update Dockerfile to run migrations on startup")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python setup_service_alembic.py <service_name>")
        print("Example: python setup_service_alembic.py key-service")
        sys.exit(1)
    
    service_name = sys.argv[1]
    setup_alembic(service_name)
