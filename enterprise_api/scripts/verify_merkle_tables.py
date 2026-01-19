#!/usr/bin/env python3
"""
Verify Merkle tree tables were created successfully.

Usage:
    uv run python scripts/verify_merkle_tables.py
"""

import asyncio

from sqlalchemy import text

from app.config import settings
from app.database import engine


async def verify_tables():
    """Verify all Merkle tables exist."""
    print("=" * 60)
    print("Verifying Merkle Tree Tables")
    print("=" * 60)
    database_url = settings.database_url or ""
    database_label = database_url.split("@", 1)[1] if database_url and "@" in database_url else "Unknown"
    print(f"Database: {database_label}\n")

    async with engine.begin() as conn:
        # Check tables
        result = await conn.execute(
            text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname='public' AND tablename LIKE 'merkle%'
            ORDER BY tablename
        """)
        )
        tables = [row[0] for row in result.fetchall()]

        print("Tables created:")
        for table in tables:
            print(f"  ✓ {table}")

        if len(tables) != 3:
            print(f"\n✗ Expected 3 tables, found {len(tables)}")
            return False

        # Check organizations columns
        result = await conn.execute(
            text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'organizations' 
            AND column_name IN ('tier', 'merkle_enabled', 'monthly_merkle_quota', 'merkle_calls_this_month', 'quota_reset_at')
            ORDER BY column_name
        """)
        )
        columns = [row[0] for row in result.fetchall()]

        print("\nOrganizations columns added:")
        for column in columns:
            print(f"  ✓ {column}")

        if len(columns) != 5:
            print(f"\n✗ Expected 5 columns, found {len(columns)}")
            return False

        # Check indexes
        result = await conn.execute(
            text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE schemaname='public' AND indexname LIKE 'idx_merkle%'
            ORDER BY indexname
        """)
        )
        indexes = [row[0] for row in result.fetchall()]

        print(f"\nIndexes created: {len(indexes)}")
        for idx in indexes:
            print(f"  ✓ {idx}")

        # Check demo organization tier
        result = await conn.execute(
            text("""
            SELECT organization_id, tier, merkle_enabled, monthly_merkle_quota
            FROM organizations
            WHERE organization_id = 'org_demo'
        """)
        )
        row = result.fetchone()

        if row:
            print("\nDemo organization configuration:")
            print(f"  Organization ID: {row[0]}")
            print(f"  Tier: {row[1]}")
            print(f"  Merkle Enabled: {row[2]}")
            print(f"  Monthly Quota: {row[3]}")
        else:
            print("\n✗ Demo organization not found")
            return False

        # Count rows in each table
        print("\nTable row counts:")
        for table in tables:
            result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"  {table}: {count} rows")

        result = await conn.execute(text("SELECT COUNT(*) FROM attribution_reports"))
        count = result.scalar()
        print(f"  attribution_reports: {count} rows")

    print("\n" + "=" * 60)
    print("✓ All verifications passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = asyncio.run(verify_tables())
    exit(0 if success else 1)
