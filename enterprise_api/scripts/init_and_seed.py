#!/usr/bin/env python3
"""
Database initialization and seeding script for Enterprise API.

This script:
1. Waits for PostgreSQL to be ready
2. Creates all tables from SQLAlchemy models
3. Seeds test data for all tiers

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


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@postgres:5432/encypher"
)

# Convert to asyncpg format for direct connection
ASYNCPG_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


async def wait_for_postgres(max_retries: int = 30, delay: float = 2.0):
    """Wait for PostgreSQL to be ready."""
    print("Waiting for PostgreSQL to be ready...")
    
    # Parse connection string
    parts = ASYNCPG_URL.replace("postgresql://", "").split("@")
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    host_port = host_db[0].split(":")
    
    user = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else None
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 5432
    database = host_db[1] if len(host_db) > 1 else "encypher"
    
    for attempt in range(max_retries):
        try:
            conn = await asyncpg.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=database,
            )
            await conn.close()
            print(f"PostgreSQL is ready! (attempt {attempt + 1})")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries}: {e}")
            await asyncio.sleep(delay)
    
    print("ERROR: PostgreSQL did not become ready in time")
    return False


async def create_tables():
    """Create all tables from SQLAlchemy models."""
    print("\nCreating database tables...")
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # Import models to register them with Base
    from app.database import Base
    from app.models import c2pa_schema, c2pa_template  # noqa: F401
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("Tables created successfully!")


async def run_init_sql():
    """Run the init_db.sql script to create additional tables."""
    print("\nRunning init_db.sql...")
    
    init_sql_path = Path(__file__).parent / "init_db.sql"
    if not init_sql_path.exists():
        print(f"Warning: {init_sql_path} not found, skipping")
        return
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # Read and execute SQL file
    sql_content = init_sql_path.read_text(encoding="utf-8")
    
    # Split by semicolons and execute each statement
    statements = [s.strip() for s in sql_content.split(";") if s.strip()]
    
    success_count = 0
    skip_count = 0
    
    for stmt in statements:
        if stmt and not stmt.startswith("--"):
            # Run each statement in its own transaction to avoid cascading failures
            async with engine.begin() as conn:
                try:
                    await conn.execute(text(stmt))
                    success_count += 1
                except Exception as e:
                    error_str = str(e).lower()
                    # Ignore "already exists" and "does not exist" errors
                    if "already exists" in error_str or "does not exist" in error_str:
                        skip_count += 1
                    else:
                        print(f"Warning: {e}")
    
    await engine.dispose()
    print(f"init_db.sql executed: {success_count} statements, {skip_count} skipped")


async def seed_test_data():
    """Seed test data for all tiers."""
    print("\nSeeding test data...")
    
    seed_sql_path = Path(__file__).parent / "seed_test_data.sql"
    if not seed_sql_path.exists():
        print(f"Warning: {seed_sql_path} not found, skipping")
        return
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # Read and execute SQL file
    sql_content = seed_sql_path.read_text(encoding="utf-8")
    
    # Split by semicolons and execute each statement
    statements = [s.strip() for s in sql_content.split(";") if s.strip()]
    
    success_count = 0
    skip_count = 0
    
    for stmt in statements:
        if stmt and not stmt.startswith("--"):
            # Run each statement in its own transaction
            async with engine.begin() as conn:
                try:
                    await conn.execute(text(stmt))
                    success_count += 1
                except Exception as e:
                    error_str = str(e).lower()
                    # Ignore conflicts and already exists
                    if "duplicate" in error_str or "conflict" in error_str or "already exists" in error_str:
                        skip_count += 1
                    else:
                        print(f"Warning: {e}")
    
    await engine.dispose()
    print(f"Test data seeded: {success_count} statements, {skip_count} skipped")


async def verify_setup():
    """Verify the database setup."""
    print("\nVerifying database setup...")
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        # Check organizations (unified schema uses 'id' not 'organization_id')
        result = await conn.execute(text("SELECT id, tier FROM organizations"))
        orgs = result.fetchall()
        print(f"  Organizations: {len(orgs)}")
        for org in orgs:
            print(f"    - {org[0]} ({org[1]})")
        
        # Check API keys
        result = await conn.execute(text("SELECT COUNT(*) FROM api_keys"))
        count = result.scalar()
        print(f"  API Keys: {count}")
        
        # Check tables exist
        result = await conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]
        print(f"  Tables: {len(tables)}")
    
    await engine.dispose()
    print("\nDatabase setup verified!")


async def main():
    """Main entry point."""
    print("=" * 50)
    print("Enterprise API Database Initialization")
    print("=" * 50)
    
    # Wait for PostgreSQL
    if not await wait_for_postgres():
        sys.exit(1)
    
    # Create tables
    await create_tables()
    
    # Run init SQL
    await run_init_sql()
    
    # Seed test data
    await seed_test_data()
    
    # Verify
    await verify_setup()
    
    print("\n" + "=" * 50)
    print("Database initialization complete!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
