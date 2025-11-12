"""
Add C2PA provenance columns to content_references table.
"""
import asyncio
from app.database import engine
from sqlalchemy import text

async def migrate():
    async with engine.begin() as conn:
        print("Adding C2PA provenance columns to content_references...")
        
        # Add instance_id column
        try:
            await conn.execute(text(
                "ALTER TABLE content_references ADD COLUMN IF NOT EXISTS "
                "instance_id VARCHAR(255)"
            ))
            print("✓ Added instance_id column")
        except Exception as e:
            print(f"✗ instance_id: {e}")
        
        # Add previous_instance_id column
        try:
            await conn.execute(text(
                "ALTER TABLE content_references ADD COLUMN IF NOT EXISTS "
                "previous_instance_id VARCHAR(255)"
            ))
            print("✓ Added previous_instance_id column")
        except Exception as e:
            print(f"✗ previous_instance_id: {e}")
        
        # Add manifest_data column
        try:
            await conn.execute(text(
                "ALTER TABLE content_references ADD COLUMN IF NOT EXISTS "
                "manifest_data JSONB"
            ))
            print("✓ Added manifest_data column")
        except Exception as e:
            print(f"✗ manifest_data: {e}")
        
        # Add indexes
        try:
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_content_references_instance_id "
                "ON content_references(instance_id)"
            ))
            print("✓ Added index on instance_id")
        except Exception as e:
            print(f"✗ index instance_id: {e}")
        
        try:
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_content_references_previous_instance_id "
                "ON content_references(previous_instance_id)"
            ))
            print("✓ Added index on previous_instance_id")
        except Exception as e:
            print(f"✗ index previous_instance_id: {e}")
        
        print("\nMigration complete!")

asyncio.run(migrate())
