"""
Integration tests for C2PA custom assertions API endpoints.
"""
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
        schema_data = {
            "namespace": "com.test",
            "label": "com.test.custom.v1",
            "version": "1.0",
            "description": "Test custom schema",
            "is_public": False,
            "schema": {
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
        assert data["namespace"] == "com.test"
        assert data["label"] == "com.test.custom.v1"
        assert data["version"] == "1.0"
        assert "id" in data
    
    async def test_create_schema_duplicate(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        """Test creating duplicate schema returns 409."""
        # Create first schema
        schema = C2PASchema(
            namespace="com.test",
            label="com.test.duplicate.v1",
            version="1.0",
            schema={"type": "object"},
            organization_id="org_test"
        )
        db.add(schema)
        await db.commit()
        
        # Try to create duplicate
        schema_data = {
            "namespace": "com.test",
            "label": "com.test.duplicate.v1",
            "version": "1.0",
            "schema": {"type": "object"}
        }
        
        response = await client.post(
            "/api/v1/enterprise/c2pa/schemas",
            json=schema_data,
            headers=auth_headers
        )
        
        assert response.status_code == 409
    
    async def test_create_schema_invalid_json_schema(self, client: AsyncClient, auth_headers: dict):
        """Test creating schema with invalid JSON Schema returns 400."""
        schema_data = {
            "namespace": "com.test",
            "label": "com.test.invalid.v1",
            "version": "1.0",
            "schema": {
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
        for i in range(3):
            schema = C2PASchema(
                namespace="com.test",
                label=f"com.test.schema{i}.v1",
                version="1.0",
                schema={"type": "object"},
                organization_id="org_test"
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
    
    async def test_list_schemas_with_namespace_filter(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        """Test listing schemas with namespace filter."""
        # Create schemas with different namespaces
        schema1 = C2PASchema(
            namespace="com.test",
            label="com.test.schema1.v1",
            version="1.0",
            schema={"type": "object"},
            organization_id="org_test"
        )
        schema2 = C2PASchema(
            namespace="com.other",
            label="com.other.schema1.v1",
            version="1.0",
            schema={"type": "object"},
            organization_id="org_test"
        )
        db.add_all([schema1, schema2])
        await db.commit()
        
        response = await client.get(
            "/api/v1/enterprise/c2pa/schemas?namespace=com.test",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(s["namespace"] == "com.test" for s in data["schemas"])
    
    async def test_get_schema(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        """Test getting a specific schema."""
        schema = C2PASchema(
            namespace="com.test",
            label="com.test.get.v1",
            version="1.0",
            schema={"type": "object"},
            organization_id="org_test"
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
        assert data["label"] == "com.test.get.v1"
    
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
        schema = C2PASchema(
            namespace="com.test",
            label="com.test.update.v1",
            version="1.0",
            schema={"type": "object"},
            description="Original description",
            organization_id="org_test"
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
        schema = C2PASchema(
            namespace="com.test",
            label="com.test.delete.v1",
            version="1.0",
            schema={"type": "object"},
            organization_id="org_test"
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
    
    async def test_create_template(self, client: AsyncClient, auth_headers: dict):
        """Test creating a new template."""
        template_data = {
            "name": "Test Template",
            "description": "Test template description",
            "category": "news",
            "is_public": False,
            "assertions": [
                {
                    "label": "c2pa.location.v1",
                    "description": "Story location",
                    "optional": True
                }
            ]
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
        # Create test templates
        for i in range(3):
            template = C2PAAssertionTemplate(
                name=f"Template {i}",
                assertions=[],
                category="news",
                organization_id="org_test"
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
        template1 = C2PAAssertionTemplate(
            name="News Template",
            assertions=[],
            category="news",
            organization_id="org_test"
        )
        template2 = C2PAAssertionTemplate(
            name="Legal Template",
            assertions=[],
            category="legal",
            organization_id="org_test"
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
        template = C2PAAssertionTemplate(
            name="Get Template",
            assertions=[],
            category="news",
            organization_id="org_test"
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
        template = C2PAAssertionTemplate(
            name="Update Template",
            description="Original description",
            assertions=[],
            category="news",
            organization_id="org_test"
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
        template = C2PAAssertionTemplate(
            name="Delete Template",
            assertions=[],
            category="news",
            organization_id="org_test"
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
