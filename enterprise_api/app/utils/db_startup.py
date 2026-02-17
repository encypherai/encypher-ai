"""Database startup utilities for Enterprise API.

SSOT: startup migration checks are Alembic-driven.
"""

import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class DatabaseStartupError(Exception):
    """Raised when database startup fails."""

    pass


def check_database_connection(database_url: str, max_retries: int = 5, retry_delay: float = 2.0, service_name: str = "enterprise-api") -> bool:
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
        raise DatabaseStartupError(f"[{service_name}] DATABASE_URL is not set or empty. Please configure the database URL environment variable.")

    # Validate URL format
    try:
        parsed = urlparse(database_url)
        if not parsed.scheme or not parsed.hostname:
            raise ValueError("Invalid URL format")
    except Exception as e:
        raise DatabaseStartupError(f"[{service_name}] Invalid DATABASE_URL format: {e}. URL should be: postgresql://user:pass@host:port/dbname")

    # Mask password in logs
    safe_url = database_url.replace(parsed.password or "", "***") if parsed.password else database_url

    try:
        from sqlalchemy import create_engine, text
    except ImportError:
        raise DatabaseStartupError(f"[{service_name}] SQLAlchemy is not installed.")

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[{service_name}] Attempting database connection (attempt {attempt}/{max_retries})...")

            # Normalize URL for sync connection
            sync_url = database_url.replace("+asyncpg", "").replace("+aiopg", "")

            engine = create_engine(sync_url, pool_pre_ping=True)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()

            logger.info(f"[{service_name}] ✓ Database connection successful")
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
                )

    return False


def run_alembic_migrations(
    service_name: str = "enterprise-api",
    alembic_ini_path: Optional[str] = None,
    database_url: Optional[str] = None,
) -> bool:
    """Run Alembic migrations to the reconciled head."""
    project_root = Path(__file__).resolve().parents[2]
    alembic_ini = Path(alembic_ini_path) if alembic_ini_path else project_root / "alembic.ini"

    if not alembic_ini.exists():
        raise DatabaseStartupError(f"[{service_name}] Alembic config not found: {alembic_ini}")

    cmd = ["alembic", "-c", str(alembic_ini), "upgrade", "head"]
    logger.info("[%s] Running Alembic migrations: %s", service_name, " ".join(cmd))

    env = os.environ.copy()
    if database_url:
        env["DATABASE_URL"] = database_url
        env["CORE_DATABASE_URL"] = database_url

    try:
        completed = subprocess.run(
            cmd,
            cwd=str(project_root),
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
    except Exception as e:  # pragma: no cover - defensive runtime guard
        raise DatabaseStartupError(f"[{service_name}] Failed to execute Alembic: {e}")

    if completed.returncode != 0:
        raise DatabaseStartupError(
            f"[{service_name}] Alembic migration failed (exit={completed.returncode}): "
            f"{(completed.stderr or completed.stdout).strip()}"
        )

    if completed.stdout.strip():
        logger.info("[%s] Alembic output: %s", service_name, completed.stdout.strip())
    logger.info("[%s] ✓ Alembic migrations completed", service_name)
    return True


def ensure_database_ready(
    database_url: Optional[str] = None,
    service_name: str = "enterprise-api",
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
        database_url: PostgreSQL connection URL (defaults to CORE_DATABASE_URL or DATABASE_URL env var)
        service_name: Name of the service (for logging)
        max_retries: Maximum number of connection attempts
        retry_delay: Seconds to wait between retries
        run_migrations: If True, run migrations
        exit_on_failure: If True, call sys.exit(1) on failure

    Returns:
        True if database is ready

    Raises:
        DatabaseStartupError: If database is not ready (only if exit_on_failure=False)
    """
    # Get database URL from parameter or environment
    db_url = database_url or os.environ.get("CORE_DATABASE_URL") or os.environ.get("DATABASE_URL")

    if not db_url:
        raise DatabaseStartupError(
            f"[{service_name}] DATABASE_URL is not set or empty. Please configure the database URL environment variable."
        )

    logger.info(f"[{service_name}] Starting database readiness check...")

    try:
        # Step 1: Check connection
        check_database_connection(database_url=db_url, max_retries=max_retries, retry_delay=retry_delay, service_name=service_name)

        # Step 2: Run migrations if requested
        if run_migrations:
            run_alembic_migrations(service_name=service_name, database_url=db_url)

        logger.info(f"[{service_name}] ✓ Database is ready")
        return True

    except DatabaseStartupError as e:
        logger.error(str(e))
        if exit_on_failure:
            sys.exit(1)
        raise
