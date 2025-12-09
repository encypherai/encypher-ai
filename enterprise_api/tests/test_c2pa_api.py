"""
Integration tests for C2PA custom assertions API endpoints.
"""
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.c2pa_schema import C2PASchema
from app.models.c2pa_template import C2PAAssertionTemplate


@pytest.mark.asyncio
class TestC2PASchemaAPI:
    """Test C2PA schema management API endpoints."""
    
    async def test_create_schema(self, client: AsyncClient, auth_headers: dict):
        """Test creating a new C2PA schema."""
        unique_label = f"com.test.custom.{uuid.uuid4().hex[:8]}"
        schema_data = {
            "name": "Test Custom Schema",
            "label": unique_label,
            "version": "1.0",
            "description": "Test custom schema",
            "is_public": False,
            "json_schema": {
                "type": "object",
                "properties": {
                    "field1": {"type": "string"},
                    "field2": {"type": "number"}
                },
                "required": ["field1"]
            }
        }
        
        response = await client.post(
            "/api/v1/enterprise/c2pa/schemas",
            json=schema_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Custom Schema"
        assert data["label"] == unique_label
        assert data["version"] == "1.0"
        assert "id" in data
    
    async def test_create_schema_duplicate(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        """Test creating duplicate schema returns 409."""
        unique_label = f"com.test.duplicate.{uuid.uuid4().hex[:8]}"
        # Create first schema
        schema = C2PASchema(
            name="Duplicate Test Schema",
            label=unique_label,
            version="1.0",
            json_schema={"type": "object"},
            organization_id="org_demo"  # Use seeded org
        )
        db.add(schema)
        await db.commit()
        
        # Try to create duplicate
        schema_data = {
            "name": "Duplicate Test Schema",
            "label": unique_label,
            "version": "1.0",
            "json_schema": {"type": "object"}
        }
        
        response = await client.post(
            "/api/v1/enterprise/c2pa/schemas",
            json=schema_data,
            headers=auth_headers
        )
        
        assert response.status_code == 409
    
    async def test_create_schema_invalid_json_schema(self, client: AsyncClient, auth_headers: dict):
        """Test creating schema with invalid JSON Schema returns 400."""
        unique_label = f"com.test.invalid.{uuid.uuid4().hex[:8]}"
        schema_data = {
            "name": "Invalid Schema",
            "label": unique_label,
            "version": "1.0",
            "json_schema": {
                "type": "invalid_type"  # Invalid
            }
        }
        
        response = await client.post(
            "/api/v1/enterprise/c2pa/schemas",
            json=schema_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    async def test_list_schemas(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        """Test listing schemas."""
        # Create test schemas
        unique_prefix = uuid.uuid4().hex[:8]
        for i in range(3):
            schema = C2PASchema(
                name=f"List Test Schema {i}",
                label=f"com.test.schema{unique_prefix}{i}.v1",
                version="1.0",
                json_schema={"type": "object"},
                organization_id="org_demo"  # Use seeded org
            )
            db.add(schema)
        await db.commit()
        
        response = await client.get(
            "/api/v1/enterprise/c2pa/schemas",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "schemas" in data
        assert "total" in data
        assert data["total"] >= 3
    
    async def test_list_schemas_with_is_public_filter(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        """Test listing schemas with is_public filter."""
        # Create schemas with different is_public values
        unique_prefix = uuid.uuid4().hex[:8]
        schema1 = C2PASchema(
            name="Public Schema",
            label=f"com.test.public.{unique_prefix}",
            version="1.0",
            json_schema={"type": "object"},
            organization_id="org_demo",
            is_public=True
        )
        schema2 = C2PASchema(
            name="Private Schema",
            label=f"com.test.private.{unique_prefix}",
            version="1.0",
            json_schema={"type": "object"},
            organization_id="org_demo",
            is_public=False
        )
        db.add_all([schema1, schema2])
        await db.commit()
        
        response = await client.get(
            "/api/v1/enterprise/c2pa/schemas?is_public=true",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(s["is_public"] is True for s in data["schemas"])
    
    async def test_get_schema(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        """Test getting a specific schema."""
        unique_label = f"com.test.get.{uuid.uuid4().hex[:8]}"
        schema = C2PASchema(
            name="Get Test Schema",
            label=unique_label,
            version="1.0",
            json_schema={"type": "object"},
            organization_id="org_demo"  # Use seeded org
        )
        db.add(schema)
        await db.commit()
        await db.refresh(schema)
        
        response = await client.get(
            f"/api/v1/enterprise/c2pa/schemas/{schema.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(schema.id)
        assert data["label"] == unique_label
    
    async def test_get_schema_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent schema returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(
            f"/api/v1/enterprise/c2pa/schemas/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_update_schema(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        """Test updating a schema."""
        unique_label = f"com.test.update.{uuid.uuid4().hex[:8]}"
        schema = C2PASchema(
            name="Update Test Schema",
            label=unique_label,
            version="1.0",
            json_schema={"type": "object"},
            description="Original description",
            organization_id="org_demo"  # Use seeded org
        )
        db.add(schema)
        await db.commit()
        await db.refresh(schema)
        
        update_data = {
            "description": "Updated description",
            "is_public": True
        }
        
        response = await client.put(
            f"/api/v1/enterprise/c2pa/schemas/{schema.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["is_public"] is True
    
    async def test_delete_schema(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        """Test deleting a schema."""
        unique_label = f"com.test.delete.{uuid.uuid4().hex[:8]}"
        schema = C2PASchema(
            name="Delete Test Schema",
            label=unique_label,
            version="1.0",
            json_schema={"type": "object"},
            organization_id="org_demo"  # Use seeded org
        )
        db.add(schema)
        await db.commit()
        await db.refresh(schema)
        
        response = await client.delete(
            f"/api/v1/enterprise/c2pa/schemas/{schema.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify deleted
        response = await client.get(
            f"/api/v1/enterprise/c2pa/schemas/{schema.id}",
            headers=auth_headers
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestC2PAValidationAPI:
    """Test C2PA assertion validation API endpoint."""
    
    async def test_validate_assertion_valid(self, client: AsyncClient, auth_headers: dict):
        """Test validating a valid assertion."""
        assertion_data = {
            "label": "c2pa.location.v1",
            "data": {
                "latitude": 37.7749,
                "longitude": -122.4194
            }
        }
        
        response = await client.post(
            "/api/v1/enterprise/c2pa/validate",
            json=assertion_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert len(data["assertions"]) == 1
        assert data["assertions"][0]["valid"] is True
    
    async def test_validate_assertion_invalid(self, client: AsyncClient, auth_headers: dict):
        """Test validating an invalid assertion."""
        assertion_data = {
            "label": "c2pa.location.v1",
            "data": {
                "latitude": 95.0,  # Invalid: > 90
                "longitude": -122.4194
            }
        }
        
        response = await client.post(
            "/api/v1/enterprise/c2pa/validate",
            json=assertion_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["assertions"]) == 1
        assert data["assertions"][0]["valid"] is False
        assert len(data["assertions"][0]["errors"]) > 0


@pytest.mark.asyncio
class TestC2PATemplateAPI:
    """Test C2PA template management API endpoints."""
    
    async def test_create_template(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        """Test creating a new template."""
        # First create a schema to reference
        unique_label = f"com.test.template.{uuid.uuid4().hex[:8]}"
        schema = C2PASchema(
            name="Template Test Schema",
            label=unique_label,
            version="1.0",
            json_schema={"type": "object"},
            organization_id="org_demo"
        )
        db.add(schema)
        await db.commit()
        await db.refresh(schema)
        
        template_data = {
            "name": "Test Template",
            "schema_id": schema.id,
            "description": "Test template description",
            "category": "news",
            "is_public": False,
            "template_data": {
                "label": "c2pa.location.v1",
                "description": "Story location",
                "optional": True
            }
        }
        
        response = await client.post(
            "/api/v1/enterprise/c2pa/templates",
            json=template_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Template"
        assert data["category"] == "news"
        assert "id" in data
    
    async def test_list_templates(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        """Test listing templates."""
        # First create a schema to reference
        unique_label = f"com.test.list.{uuid.uuid4().hex[:8]}"
        schema = C2PASchema(
            name="List Template Test Schema",
            label=unique_label,
            version="1.0",
            json_schema={"type": "object"},
            organization_id="org_demo"
        )
        db.add(schema)
        await db.commit()
        await db.refresh(schema)
        
        # Create test templates
        for i in range(3):
            template = C2PAAssertionTemplate(
                name=f"Template {uuid.uuid4().hex[:8]}",
                schema_id=schema.id,
                template_data={},
                category="news",
                organization_id="org_demo"
            )
            db.add(template)
        await db.commit()
        
        response = await client.get(
            "/api/v1/enterprise/c2pa/templates",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert "total" in data
        assert data["total"] >= 3
    
    async def test_list_templates_with_category_filter(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        """Test listing templates with category filter."""
        # First create a schema to reference
        unique_label = f"com.test.catfilter.{uuid.uuid4().hex[:8]}"
        schema = C2PASchema(
            name="Category Filter Test Schema",
            label=unique_label,
            version="1.0",
            json_schema={"type": "object"},
            organization_id="org_demo"
        )
        db.add(schema)
        await db.commit()
        await db.refresh(schema)
        
        template1 = C2PAAssertionTemplate(
            name=f"News Template {uuid.uuid4().hex[:8]}",
            schema_id=schema.id,
            template_data={},
            category="news",
            organization_id="org_demo"
        )
        template2 = C2PAAssertionTemplate(
            name=f"Legal Template {uuid.uuid4().hex[:8]}",
            schema_id=schema.id,
            template_data={},
            category="legal",
            organization_id="org_demo"
        )
        db.add_all([template1, template2])
        await db.commit()
        
        response = await client.get(
            "/api/v1/enterprise/c2pa/templates?category=news",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(t["category"] == "news" for t in data["templates"])
    
    async def test_get_template(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        """Test getting a specific template."""
        # First create a schema to reference
        unique_label = f"com.test.gettempl.{uuid.uuid4().hex[:8]}"
        schema = C2PASchema(
            name="Get Template Test Schema",
            label=unique_label,
            version="1.0",
            json_schema={"type": "object"},
            organization_id="org_demo"
        )
        db.add(schema)
        await db.commit()
        await db.refresh(schema)
        
        template = C2PAAssertionTemplate(
            name="Get Template",
            schema_id=schema.id,
            template_data={},
            category="news",
            organization_id="org_demo"
        )
        db.add(template)
        await db.commit()
        await db.refresh(template)
        
        response = await client.get(
            f"/api/v1/enterprise/c2pa/templates/{template.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(template.id)
        assert data["name"] == "Get Template"
    
    async def test_update_template(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        """Test updating a template."""
        # First create a schema to reference
        unique_label = f"com.test.updatetempl.{uuid.uuid4().hex[:8]}"
        schema = C2PASchema(
            name="Update Template Test Schema",
            label=unique_label,
            version="1.0",
            json_schema={"type": "object"},
            organization_id="org_demo"
        )
        db.add(schema)
        await db.commit()
        await db.refresh(schema)
        
        template = C2PAAssertionTemplate(
            name="Update Template",
            description="Original description",
            schema_id=schema.id,
            template_data={},
            category="news",
            organization_id="org_demo"
        )
        db.add(template)
        await db.commit()
        await db.refresh(template)
        
        update_data = {
            "description": "Updated description",
            "category": "legal"
        }
        
        response = await client.put(
            f"/api/v1/enterprise/c2pa/templates/{template.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["category"] == "legal"
    
    async def test_delete_template(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        """Test deleting a template."""
        # First create a schema to reference
        unique_label = f"com.test.deletetempl.{uuid.uuid4().hex[:8]}"
        schema = C2PASchema(
            name="Delete Template Test Schema",
            label=unique_label,
            version="1.0",
            json_schema={"type": "object"},
            organization_id="org_demo"
        )
        db.add(schema)
        await db.commit()
        await db.refresh(schema)
        
        template = C2PAAssertionTemplate(
            name="Delete Template",
            schema_id=schema.id,
            template_data={},
            category="news",
            organization_id="org_demo"
        )
        db.add(template)
        await db.commit()
        await db.refresh(template)
        
        response = await client.delete(
            f"/api/v1/enterprise/c2pa/templates/{template.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify deleted
        response = await client.get(
            f"/api/v1/enterprise/c2pa/templates/{template.id}",
            headers=auth_headers
        )
        assert response.status_code == 404
