import asyncio

from sqlalchemy import text

from app.database import engine


async def check():
    async with engine.begin() as conn:
        # Check if table exists
        result = await conn.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_name = 'content_references')"
        ))
        exists = result.scalar()
        print(f"content_references table exists: {exists}")
        
        if exists:
            # Get columns
            result = await conn.execute(text(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name = 'content_references' ORDER BY ordinal_position"
            ))
            cols = result.fetchall()
            print("\nColumns:")
            for col in cols:
                print(f"  {col[0]}: {col[1]}")

asyncio.run(check())
