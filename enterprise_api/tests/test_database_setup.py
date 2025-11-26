"""
Test database setup with PostgreSQL.

Verifies that the test database configuration works correctly.
Uses PostgreSQL via Docker for full compatibility.
"""
import pytest
import uuid
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
        unique_suffix = uuid.uuid4().hex[:8]
        unique_label = f"com.test.example.{unique_suffix}"
        
        schema = C2PASchema(
            name="Test Schema",
            label=unique_label,
            version="1.0",
            json_schema={
                "type": "object",
                "properties": {
                    "field1": {"type": "string"}
                }
            },
            description="Test schema",
            organization_id="org_business"
        )
        
        db.add(schema)
        await db.commit()
        await db.refresh(schema)
        
        assert schema.id is not None
        assert schema.label == unique_label
    
    async def test_create_c2pa_template(self, db: AsyncSession):
        """Test creating a C2PA assertion template."""
        # First create a schema to reference with unique label
        unique_suffix = uuid.uuid4().hex[:8]
        unique_label = f"com.test.template.{unique_suffix}"
        
        schema = C2PASchema(
            name="Template Schema",
            label=unique_label,
            version="1.0",
            json_schema={"type": "object"},
            organization_id="org_business"
        )
        db.add(schema)
        await db.commit()
        await db.refresh(schema)
        
        # Now create template referencing the schema
        template = C2PAAssertionTemplate(
            name="Test Template",
            description="A test template",
            schema_id=schema.id,
            template_data={
                "label": "c2pa.location.v1",
                "data": {
                    "latitude": 37.7749,
                    "longitude": -122.4194
                }
            },
            organization_id="org_business",
            is_default=False,
            is_active=True
        )
        
        db.add(template)
        await db.commit()
        await db.refresh(template)
        
        assert template.id is not None
        assert template.name == "Test Template"
        assert template.template_data is not None
    
    async def test_database_isolation(self, db: AsyncSession):
        """Test that database operations work correctly within a session."""
        # Create a unique schema for this test
        unique_label = f"com.test.isolation.{uuid.uuid4().hex[:8]}"
        schema = C2PASchema(
            name="Isolation Schema",
            label=unique_label,
            version="1.0",
            json_schema={"type": "object"},
            organization_id="org_business"
        )
        db.add(schema)
        await db.commit()
        
        # Verify it was created
        result = await db.execute(
            select(C2PASchema).where(C2PASchema.label == unique_label)
        )
        found = result.scalar_one_or_none()
        assert found is not None
        assert found.label == unique_label


@pytest.mark.asyncio
class TestDatabaseTransactions:
    """Test database transaction handling."""
    
    async def test_commit_persists_data(self, db: AsyncSession):
        """Test that committed data persists."""
        unique_suffix = uuid.uuid4().hex[:8]
        unique_label = f"com.test.commit.{unique_suffix}"
        
        schema = C2PASchema(
            name="Commit Schema",
            label=unique_label,
            version="1.0",
            json_schema={"type": "object"},
            organization_id="org_business"
        )
        
        db.add(schema)
        await db.commit()
        
        # Query again to verify persistence
        result = await db.execute(
            select(C2PASchema).where(C2PASchema.label == unique_label)
        )
        found = result.scalar_one_or_none()
        
        assert found is not None
        assert found.label == unique_label
    
    async def test_rollback_discards_data(self, db: AsyncSession):
        """Test that rollback discards uncommitted data."""
        unique_label = f"com.test.rollback.{uuid.uuid4().hex[:8]}"
        schema = C2PASchema(
            name="Rollback Schema",
            label=unique_label,
            version="1.0",
            json_schema={"type": "object"},
            organization_id="org_business"
        )
        
        db.add(schema)
        await db.rollback()
        
        # Query to verify data was discarded
        result = await db.execute(
            select(C2PASchema).where(C2PASchema.label == unique_label)
        )
        found = result.scalar_one_or_none()
        
        assert found is None
