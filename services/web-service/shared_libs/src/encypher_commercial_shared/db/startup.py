"""
Database startup utilities for Encypher microservices.

Provides functions to validate database connections and run migrations
on service startup. Designed to be called from FastAPI lifespan events
or directly in main.py before starting the server.

Usage:
    from encypher_commercial_shared.db import ensure_database_ready

    # In FastAPI lifespan
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        ensure_database_ready(
            database_url=settings.DATABASE_URL,
            service_name="auth-service",
            alembic_config_path="alembic.ini"
        )
        yield

    # Or in main.py before uvicorn
    if __name__ == "__main__":
        ensure_database_ready(...)
        uvicorn.run(app, ...)
"""

import logging
import os
import sys
import time
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class DatabaseStartupError(Exception):
    """Raised when database startup fails."""

    pass


def check_database_connection(database_url: str, max_retries: int = 5, retry_delay: float = 2.0, service_name: str = "service") -> bool:
    """
    Check if the database is reachable and accepting connections.

    Args:
        database_url: PostgreSQL connection URL
        max_retries: Maximum number of connection attempts
        retry_delay: Seconds to wait between retries
        service_name: Name of the service (for logging)

    Returns:
        True if connection successful

    Raises:
        DatabaseStartupError: If connection fails after all retries
    """
    if not database_url:
        raise DatabaseStartupError(f"[{service_name}] DATABASE_URL is not set or empty. Please configure the DATABASE_URL environment variable.")

    # Validate URL format
    try:
        parsed = urlparse(database_url)
        if not parsed.scheme or not parsed.hostname:
            raise ValueError("Invalid URL format")
        if parsed.scheme not in ("postgresql", "postgres", "postgresql+psycopg2", "postgresql+asyncpg"):
            raise ValueError(f"Unsupported database scheme: {parsed.scheme}")
    except Exception as e:
        raise DatabaseStartupError(
            f"[{service_name}] Invalid DATABASE_URL format: {e}. URL should be: postgresql://user:pass@host:port/dbname"
        ) from e

    # Try to connect
    try:
        from sqlalchemy import create_engine, text
    except ImportError as e:
        raise DatabaseStartupError(f"[{service_name}] SQLAlchemy is not installed. Please add sqlalchemy to your dependencies.") from e

    # Mask password in logs
    safe_url = database_url.replace(parsed.password or "", "***") if parsed.password else database_url

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[{service_name}] Attempting database connection (attempt {attempt}/{max_retries})...")

            # Create a simple sync engine for connection test
            engine = create_engine(database_url, pool_pre_ping=True)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()

            logger.info(f"[{service_name}] ✓ Database connection successful: {safe_url}")
            engine.dispose()
            return True

        except Exception as e:
            logger.warning(f"[{service_name}] Connection attempt {attempt} failed: {e}")
            if attempt < max_retries:
                logger.info(f"[{service_name}] Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                raise DatabaseStartupError(
                    f"[{service_name}] Failed to connect to database after {max_retries} attempts. URL: {safe_url}, Error: {e}"
                ) from e

    return False


def run_migrations_if_needed(
    alembic_config_path: str = "alembic.ini",
    service_name: str = "service",
    auto_upgrade: bool = True,
    database_url: Optional[str] = None,
) -> bool:
    """
    Run Alembic migrations if the database is not up to date.

    Args:
        alembic_config_path: Path to alembic.ini file
        service_name: Name of the service (for logging)
        auto_upgrade: If True, automatically run 'upgrade head'

    Returns:
        True if migrations were run or already up to date

    Raises:
        DatabaseStartupError: If migration fails
    """
    if not os.path.exists(alembic_config_path):
        logger.warning(f"[{service_name}] No alembic.ini found at {alembic_config_path}, skipping migrations")
        return True

    try:
        from alembic import command
        from alembic.config import Config
        from alembic.runtime.migration import MigrationContext
        from alembic.script import ScriptDirectory
        from sqlalchemy import create_engine
    except ImportError:
        logger.warning(f"[{service_name}] Alembic not installed, skipping migrations")
        return True

    try:
        alembic_cfg = Config(alembic_config_path)
        script = ScriptDirectory.from_config(alembic_cfg)

        # Get current head revision
        head_revision = script.get_current_head()

        # Get database URL from alembic config or environment
        database_url = database_url or os.environ.get("DATABASE_URL")
        if database_url:
            alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        if not database_url:
            # Try to get from alembic config
            database_url = alembic_cfg.get_main_option("sqlalchemy.url")

        if not database_url:
            raise DatabaseStartupError(f"[{service_name}] Cannot determine DATABASE_URL for migrations")

        # Check current database revision
        engine = create_engine(database_url)
        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            current_revision = context.get_current_revision()
        engine.dispose()

        logger.info(f"[{service_name}] Current DB revision: {current_revision}, Head revision: {head_revision}")

        if current_revision == head_revision:
            logger.info(f"[{service_name}] ✓ Database is up to date")
            return True

        if auto_upgrade:
            logger.info(f"[{service_name}] Running migrations: {current_revision} -> {head_revision}")
            command.upgrade(alembic_cfg, "head")
            logger.info(f"[{service_name}] ✓ Migrations completed successfully")
            return True
        else:
            logger.warning(
                f"[{service_name}] Database needs migration: {current_revision} -> {head_revision}. "
                "Set auto_upgrade=True or run 'alembic upgrade head' manually."
            )
            return False

    except Exception as e:
        raise DatabaseStartupError(f"[{service_name}] Migration failed: {e}") from e


def ensure_database_ready(
    database_url: Optional[str] = None,
    service_name: str = "service",
    alembic_config_path: str = "alembic.ini",
    max_retries: int = 5,
    retry_delay: float = 2.0,
    run_migrations: bool = True,
    exit_on_failure: bool = True,
) -> bool:
    """
    Ensure the database is ready for the service to start.

    This is the main entry point that should be called on service startup.
    It validates the connection and optionally runs migrations.

    Args:
        database_url: PostgreSQL connection URL (defaults to DATABASE_URL env var)
        service_name: Name of the service (for logging)
        alembic_config_path: Path to alembic.ini file
        max_retries: Maximum number of connection attempts
        retry_delay: Seconds to wait between retries
        run_migrations: If True, run Alembic migrations
        exit_on_failure: If True, call sys.exit(1) on failure

    Returns:
        True if database is ready

    Raises:
        DatabaseStartupError: If database is not ready (only if exit_on_failure=False)
    """
    # Get database URL from parameter or environment
    db_url = database_url or os.environ.get("DATABASE_URL")

    logger.info(f"[{service_name}] Starting database readiness check...")

    try:
        # Step 1: Check connection
        check_database_connection(database_url=db_url, max_retries=max_retries, retry_delay=retry_delay, service_name=service_name)

        # Step 2: Run migrations if requested
        if run_migrations:
            run_migrations_if_needed(alembic_config_path=alembic_config_path, database_url=db_url, service_name=service_name, auto_upgrade=True)

        logger.info(f"[{service_name}] ✓ Database is ready")
        return True

    except DatabaseStartupError as e:
        logger.error(str(e))
        if exit_on_failure:
            sys.exit(1)
        raise
