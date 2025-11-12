#!/usr/bin/env python3
"""
Migration runner for Merkle tree tables.

This script runs all Merkle-related database migrations in order.
It can be run multiple times safely (uses IF NOT EXISTS).

Usage:
    uv run python scripts/run_merkle_migrations.py
"""
import asyncio
import sys
from pathlib import Path
from sqlalchemy import text
from app.database import engine
from app.config import settings

# Migration files in order
MIGRATIONS = [
    "006_create_merkle_roots.sql",
    "007_create_merkle_subhashes.sql",
    "008_create_merkle_proof_cache.sql",
    "009_create_attribution_reports.sql",
    "010_alter_organizations_for_tiers.sql",
    "011_create_content_references.sql",
]


async def run_migration(migration_file: Path) -> None:
    """Run a single migration file."""
    print(f"Running migration: {migration_file.name}")
    
    # Read migration SQL
    sql_content = migration_file.read_text()
    
    # Split into individual statements
    # Remove comments and split on semicolons
    lines = []
    for line in sql_content.split('\n'):
        # Skip comment-only lines
        if line.strip().startswith('--'):
            continue
        lines.append(line)
    
    clean_sql = '\n'.join(lines)
    statements = [s.strip() for s in clean_sql.split(';') if s.strip()]
    
    # Execute each statement in a transaction
    async with engine.begin() as conn:
        for i, statement in enumerate(statements, 1):
            try:
                await conn.execute(text(statement))
                print(f"  ✓ Statement {i}/{len(statements)}")
            except Exception as e:
                print(f"  ✗ Error in statement {i}: {e}")
                print(f"  Statement: {statement[:100]}...")
                raise
    
    print(f"  ✓ Migration {migration_file.name} completed")


async def main():
    """Run all migrations."""
    print("=" * 60)
    print("Merkle Tree Database Migrations")
    print("=" * 60)
    print(f"Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'Unknown'}")
    print(f"Environment: {settings.environment}")
    print("=" * 60)
    
    migrations_dir = Path(__file__).parent.parent / "migrations"
    
    if not migrations_dir.exists():
        print(f"Error: Migrations directory not found: {migrations_dir}")
        sys.exit(1)
    
    print(f"\nRunning {len(MIGRATIONS)} migrations...\n")
    
    for migration_name in MIGRATIONS:
        migration_file = migrations_dir / migration_name
        
        if not migration_file.exists():
            print(f"Error: Migration file not found: {migration_file}")
            sys.exit(1)
        
        try:
            await run_migration(migration_file)
        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            print("\nTo rollback, run:")
            print("  psql -U postgres -d encypher_enterprise -f migrations/rollback_merkle_tables.sql")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ All migrations completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Verify tables: SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename LIKE 'merkle%';")
    print("  2. Check indexes: \\di merkle*")
    print("  3. Verify organizations tier column: SELECT organization_id, tier, merkle_enabled FROM organizations;")


if __name__ == "__main__":
    asyncio.run(main())
