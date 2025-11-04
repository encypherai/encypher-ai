"""
Test database setup with SQLite.

Verifies that the test database configuration works correctly.
"""
import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.c2pa_schema import C2PASchema
from app.models.c2pa_template import C2PAAssertionTemplate


@pytest.mark.asyncio
class TestDatabaseSetup:
    """Test database setup and fixtures."""
    
    async def test_database_connection(self, db: AsyncSession):
        """Test that database connection works."""
        result = await db.execute(text("SELECT 1"))
        assert result.scalar() == 1
    
    async def test_c2pa_schema_table_exists(self, db: AsyncSession):
        """Test that c2pa_schemas table was created."""
        # Try to query the table
        result = await db.execute(select(C2PASchema))
        schemas = result.scalars().all()
        assert isinstance(schemas, list)
    
    async def test_c2pa_template_table_exists(self, db: AsyncSession):
        """Test that c2pa_assertion_templates table was created."""
        # Try to query the table
        result = await db.execute(select(C2PAAssertionTemplate))
        templates = result.scalars().all()
        assert isinstance(templates, list)
    
    async def test_create_c2pa_schema(self, db: AsyncSession):
        """Test creating a C2PA schema."""
        schema = C2PASchema(
            namespace="com.test",
            label="com.test.example.v1",
            version="1.0",
            schema={
                "type": "object",
                "properties": {
                    "field1": {"type": "string"}
                }
            },
            description="Test schema",
            organization_id="org_test",
            is_public=False
        )
        
        db.add(schema)
        await db.commit()
        await db.refresh(schema)
        
        assert schema.id is not None
        assert schema.label == "com.test.example.v1"
    
    async def test_create_c2pa_template(self, db: AsyncSession):
        """Test creating a C2PA assertion template."""
        template = C2PAAssertionTemplate(
            name="Test Template",
            description="A test template",
            assertions=[
                {
                    "label": "c2pa.location.v1",
                    "data": {
                        "latitude": 37.7749,
                        "longitude": -122.4194
                    }
                }
            ],
            organization_id="org_test",
            is_public=False,
            category="test"
        )
        
        db.add(template)
        await db.commit()
        await db.refresh(template)
        
        assert template.id is not None
        assert template.name == "Test Template"
        assert len(template.assertions) == 1
    
    async def test_database_isolation(self, db: AsyncSession):
        """Test that each test gets a clean database."""
        # This test should start with empty tables
        result = await db.execute(select(C2PASchema))
        schemas = result.scalars().all()
        
        # Should be empty since previous test's data was rolled back
        assert len(schemas) == 0


@pytest.mark.asyncio
class TestDatabaseTransactions:
    """Test database transaction handling."""
    
    async def test_commit_persists_data(self, db: AsyncSession):
        """Test that committed data persists."""
        schema = C2PASchema(
            namespace="com.test",
            label="com.test.commit.v1",
            version="1.0",
            schema={"type": "object"},
            organization_id="org_test"
        )
        
        db.add(schema)
        await db.commit()
        
        # Query again to verify persistence
        result = await db.execute(
            select(C2PASchema).where(C2PASchema.label == "com.test.commit.v1")
        )
        found = result.scalar_one_or_none()
        
        assert found is not None
        assert found.label == "com.test.commit.v1"
    
    async def test_rollback_discards_data(self, db: AsyncSession):
        """Test that rollback discards uncommitted data."""
        schema = C2PASchema(
            namespace="com.test",
            label="com.test.rollback.v1",
            version="1.0",
            schema={"type": "object"},
            organization_id="org_test"
        )
        
        db.add(schema)
        await db.rollback()
        
        # Query to verify data was discarded
        result = await db.execute(
            select(C2PASchema).where(C2PASchema.label == "com.test.rollback.v1")
        )
        found = result.scalar_one_or_none()
        
        assert found is None
