#!/usr/bin/env python3
"""
Database initialization and seeding script for Enterprise API.

This script:
1. Waits for PostgreSQL to be ready
2. Runs SQL migrations for core and content databases
3. Seeds test data (optional)

Supports two-database architecture:
- CORE_DATABASE_URL: Customer/billing data
- CONTENT_DATABASE_URL: Verification/content data

Usage:
    python scripts/init_and_seed.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


def _normalize_url(url: str) -> str:
    """Ensure URL uses asyncpg driver."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://")
    return url


# Two-database architecture
CORE_DATABASE_URL = os.getenv("CORE_DATABASE_URL") or os.getenv("DATABASE_URL")
CONTENT_DATABASE_URL = os.getenv("CONTENT_DATABASE_URL") or os.getenv("DATABASE_URL")

# Fallback for local development
if not CORE_DATABASE_URL:
    CORE_DATABASE_URL = "postgresql://encypher:encypher_dev_password@postgres:5432/encypher"
if not CONTENT_DATABASE_URL:
    CONTENT_DATABASE_URL = "postgresql://encypher:encypher_dev_password@postgres:5432/encypher"

# Normalize URLs for SQLAlchemy
CORE_DATABASE_URL = _normalize_url(CORE_DATABASE_URL)
CONTENT_DATABASE_URL = _normalize_url(CONTENT_DATABASE_URL)

# Migration file paths
MIGRATIONS_DIR = Path(__file__).parent.parent.parent / "services" / "migrations"
CORE_MIGRATIONS = MIGRATIONS_DIR / "core_db"
CONTENT_MIGRATIONS = MIGRATIONS_DIR / "content_db"


def parse_db_url(url: str) -> dict:
    """Parse database URL into components."""
    # Remove driver prefix
    clean_url = url.replace("postgresql+asyncpg://", "").replace("postgresql://", "")
    parts = clean_url.split("@")
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    host_port = host_db[0].split(":")

    return {
        "user": user_pass[0],
        "password": user_pass[1] if len(user_pass) > 1 else None,
        "host": host_port[0],
        "port": int(host_port[1]) if len(host_port) > 1 else 5432,
        "database": host_db[1].split("?")[0] if len(host_db) > 1 else "railway",
    }


async def wait_for_postgres(db_url: str, db_name: str, max_retries: int = 30, delay: float = 2.0) -> bool:
    """Wait for PostgreSQL to be ready."""
    print(f"Waiting for {db_name} database to be ready...")

    params = parse_db_url(db_url)

    for attempt in range(max_retries):
        try:
            conn = await asyncpg.connect(
                user=params["user"],
                password=params["password"],
                host=params["host"],
                port=params["port"],
                database=params["database"],
            )
            await conn.close()
            print(f"{db_name} database is ready! (attempt {attempt + 1})")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries}: {e}")
            await asyncio.sleep(delay)

    print(f"ERROR: {db_name} database did not become ready in time")
    return False


def split_sql_statements(sql_content: str) -> list[str]:
    """
    Split SQL content into statements, handling dollar-quoted strings properly.

    Dollar-quoting ($$...$$) is used in PostgreSQL for function bodies and
    should not be split on semicolons inside them.
    """
    statements = []
    current_stmt = []
    in_dollar_quote = False
    lines = sql_content.split("\n")

    for line in lines:
        stripped = line.strip()

        # Skip pure comment lines
        if stripped.startswith("--"):
            continue

        # Track dollar quoting
        dollar_count = line.count("$$")
        if dollar_count % 2 == 1:
            in_dollar_quote = not in_dollar_quote

        current_stmt.append(line)

        # If we're not in a dollar quote and line ends with semicolon, end statement
        if not in_dollar_quote and stripped.endswith(";"):
            stmt = "\n".join(current_stmt).strip()
            if stmt and not stmt.startswith("--"):
                statements.append(stmt)
            current_stmt = []

    # Handle any remaining content
    if current_stmt:
        stmt = "\n".join(current_stmt).strip()
        if stmt and not stmt.startswith("--"):
            statements.append(stmt)

    return statements


async def run_migrations(db_url: str, migrations_dir: Path, db_name: str):
    """Run SQL migration files from a directory."""
    print(f"\nRunning {db_name} migrations from {migrations_dir}...")

    if not migrations_dir.exists():
        print(f"Warning: {migrations_dir} not found, skipping")
        return

    # Get all SQL files sorted by name
    sql_files = sorted(migrations_dir.glob("*.sql"))
    if not sql_files:
        print(f"No migration files found in {migrations_dir}")
        return

    engine = create_async_engine(db_url, echo=False)

    for sql_file in sql_files:
        print(f"  Running {sql_file.name}...")
        sql_content = sql_file.read_text(encoding="utf-8")

        # Split SQL properly handling dollar-quoted strings
        statements = split_sql_statements(sql_content)

        success_count = 0
        skip_count = 0
        error_count = 0

        for stmt in statements:
            # Run each statement in its own transaction
            async with engine.begin() as conn:
                try:
                    await conn.execute(text(stmt))
                    success_count += 1
                except Exception as e:
                    error_str = str(e).lower()
                    # Ignore "already exists" errors (idempotent migrations)
                    if "already exists" in error_str:
                        skip_count += 1
                    else:
                        error_count += 1
                        # Only print first 200 chars of error to avoid log spam
                        print(f"    Warning: {str(e)[:200]}")

        print(f"    {sql_file.name}: {success_count} executed, {skip_count} skipped, {error_count} errors")

    await engine.dispose()
    print(f"{db_name} migrations complete!")


async def verify_setup():
    """Verify the database setup."""
    print("\nVerifying database setup...")

    # Verify Core DB
    print("\n  Core Database:")
    core_engine = create_async_engine(CORE_DATABASE_URL, echo=False)
    try:
        async with core_engine.begin() as conn:
            # Check organizations
            result = await conn.execute(text("SELECT id, tier FROM organizations LIMIT 5"))
            orgs = result.fetchall()
            print(f"    Organizations: {len(orgs)}")
            for org in orgs:
                print(f"      - {org[0]} ({org[1]})")

            # Check tables exist
            result = await conn.execute(
                text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            )
            tables = [row[0] for row in result.fetchall()]
            print(f"    Tables: {len(tables)}")
    except Exception as e:
        print(f"    Error: {e}")
    finally:
        await core_engine.dispose()

    # Verify Content DB
    print("\n  Content Database:")
    content_engine = create_async_engine(CONTENT_DATABASE_URL, echo=False)
    try:
        async with content_engine.begin() as conn:
            # Check tables exist
            result = await conn.execute(
                text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            )
            tables = [row[0] for row in result.fetchall()]
            print(f"    Tables: {len(tables)}")
    except Exception as e:
        print(f"    Error: {e}")
    finally:
        await content_engine.dispose()

    print("\nDatabase setup verified!")


async def main():
    """Main entry point."""
    print("=" * 50)
    print("Enterprise API Database Initialization")
    print("=" * 50)
    print(f"Core DB: {CORE_DATABASE_URL.split('@')[1] if '@' in CORE_DATABASE_URL else 'Not configured'}")
    print(f"Content DB: {CONTENT_DATABASE_URL.split('@')[1] if '@' in CONTENT_DATABASE_URL else 'Not configured'}")
    print(f"Migrations Dir: {MIGRATIONS_DIR}")

    # Wait for Core PostgreSQL
    if not await wait_for_postgres(CORE_DATABASE_URL, "Core"):
        print("Warning: Core database not ready, continuing anyway...")

    # Wait for Content PostgreSQL (might be same as core)
    if CONTENT_DATABASE_URL != CORE_DATABASE_URL:
        if not await wait_for_postgres(CONTENT_DATABASE_URL, "Content"):
            print("Warning: Content database not ready, continuing anyway...")

    # Run Core DB migrations
    await run_migrations(CORE_DATABASE_URL, CORE_MIGRATIONS, "Core")

    # Run Content DB migrations
    await run_migrations(CONTENT_DATABASE_URL, CONTENT_MIGRATIONS, "Content")

    # Verify
    await verify_setup()

    print("\n" + "=" * 50)
    print("Database initialization complete!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
