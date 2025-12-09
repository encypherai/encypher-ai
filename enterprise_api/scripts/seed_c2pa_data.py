"""
Seed database with standard C2PA schemas and templates.

Run this script to populate the database with standard C2PA assertion
schemas and pre-built templates for common use cases.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.c2pa_schema import C2PASchema
from app.models.c2pa_template import C2PAAssertionTemplate
from app.services.c2pa_seed_data import get_standard_schemas, get_standard_templates


async def seed_schemas(session: AsyncSession):
    """Seed standard C2PA schemas."""
    schemas = get_standard_schemas()
    created_count = 0
    
    for schema_data in schemas:
        # Check if schema already exists
        stmt = select(C2PASchema).where(
            C2PASchema.namespace == schema_data["namespace"],
            C2PASchema.label == schema_data["label"],
            C2PASchema.version == schema_data["version"]
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"  ⏭️  Schema {schema_data['label']} v{schema_data['version']} already exists")
            continue
        
        # Create new schema
        schema = C2PASchema(
            namespace=schema_data["namespace"],
            label=schema_data["label"],
            version=schema_data["version"],
            schema=schema_data["schema"],
            description=schema_data["description"],
            is_public=schema_data["is_public"],
            organization_id=None  # System schemas have no organization
        )
        
        session.add(schema)
        created_count += 1
        print(f"  ✅ Created schema: {schema_data['label']} v{schema_data['version']}")
    
    await session.commit()
    return created_count


async def seed_templates(session: AsyncSession):
    """Seed standard C2PA templates."""
    templates = get_standard_templates()
    created_count = 0
    
    for template_data in templates:
        # Check if template already exists
        stmt = select(C2PAAssertionTemplate).where(
            C2PAAssertionTemplate.name == template_data["name"],
            C2PAAssertionTemplate.category == template_data["category"]
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"  ⏭️  Template '{template_data['name']}' already exists")
            continue
        
        # Create new template
        template = C2PAAssertionTemplate(
            name=template_data["name"],
            description=template_data["description"],
            assertions=template_data["assertions"],
            category=template_data["category"],
            is_public=template_data["is_public"],
            organization_id=None  # System templates have no organization
        )
        
        session.add(template)
        created_count += 1
        print(f"  ✅ Created template: {template_data['name']} ({template_data['category']})")
    
    await session.commit()
    return created_count


async def main():
    """Main seeding function."""
    print("🌱 Seeding C2PA standard data...\n")
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Seed schemas
        print("📋 Seeding C2PA schemas...")
        schema_count = await seed_schemas(session)
        print(f"   Created {schema_count} new schemas\n")
        
        # Seed templates
        print("📝 Seeding C2PA templates...")
        template_count = await seed_templates(session)
        print(f"   Created {template_count} new templates\n")
    
    await engine.dispose()
    
    print("✅ Seeding complete!")
    print(f"   Total schemas: {schema_count}")
    print(f"   Total templates: {template_count}")


if __name__ == "__main__":
    asyncio.run(main())
