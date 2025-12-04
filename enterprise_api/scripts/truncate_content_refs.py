#!/usr/bin/env python3
"""
Truncate content_references table for clean embeddings benchmarks.
Usage: uv run python scripts/truncate_content_refs.py
"""
import asyncio

from sqlalchemy import text

from app.database import engine


async def truncate():
    async with engine.begin() as conn:
        # Check if table exists first
        result = await conn.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = 'content_references')"
        ))
        exists = result.scalar()
        
        if exists:
            await conn.execute(text("TRUNCATE TABLE content_references CASCADE;"))
            print("✓ Truncated content_references table")
        else:
            print("⚠ content_references table does not exist yet - skipping truncate")


if __name__ == "__main__":
    asyncio.run(truncate())
