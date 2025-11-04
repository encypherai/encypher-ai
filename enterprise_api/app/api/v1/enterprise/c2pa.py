"""
C2PA Custom Assertions API Endpoints

Endpoints for managing custom C2PA schemas and templates.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.database import get_db
from app.middleware.api_key_auth import get_current_organization
from app.models.c2pa_schema import C2PASchema
from app.models.c2pa_template import C2PAAssertionTemplate
from app.schemas.c2pa_schemas import (
    C2PASchemaCreate,
    C2PASchemaUpdate,
    C2PASchemaResponse,
    C2PASchemaListResponse,
    C2PAAssertionValidateRequest,
    C2PAAssertionValidateResponse,
    C2PATemplateCreate,
    C2PATemplateUpdate,
    C2PATemplateResponse,
    C2PATemplateListResponse
)
from app.services.c2pa_validator import validator

logger = logging.getLogger(__name__)
router = APIRouter()


# Schema Management Endpoints

@router.post("/schemas", response_model=C2PASchemaResponse, status_code=201)
async def create_schema(
    schema_data: C2PASchemaCreate,
    organization_id: str = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """
    Register a custom C2PA assertion schema.
    
    Allows organizations to define custom assertion types with
    JSON Schema validation rules.
    """
    try:
        # Validate the schema itself
        validator.register_schema(schema_data.label, schema_data.schema)
        
        # Check if schema already exists
        stmt = select(C2PASchema).where(
            C2PASchema.namespace == schema_data.namespace,
            C2PASchema.label == schema_data.label,
            C2PASchema.version == schema_data.version
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Schema {schema_data.label} version {schema_data.version} already exists"
            )
        
        # Create new schema
        new_schema = C2PASchema(
            namespace=schema_data.namespace,
            label=schema_data.label,
            version=schema_data.version,
            schema=schema_data.schema,
            description=schema_data.description,
            organization_id=organization_id,
            is_public=schema_data.is_public
        )
        
        db.add(new_schema)
        await db.commit()
        await db.refresh(new_schema)
        
        logger.info(f"Created C2PA schema {schema_data.label} for org {organization_id}")
        
        return C2PASchemaResponse(**new_schema.to_dict())
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating schema: {e}")
        raise HTTPException(status_code=500, detail="Failed to create schema")


@router.get("/schemas", response_model=C2PASchemaListResponse)
async def list_schemas(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    namespace: Optional[str] = None,
    is_public: Optional[bool] = None,
    organization_id: str = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """
    List available C2PA assertion schemas.
    
    Returns schemas owned by the organization or public schemas.
    """
    # Build query
    stmt = select(C2PASchema).where(
        (C2PASchema.organization_id == organization_id) | (C2PASchema.is_public == True)
    )
    
    if namespace:
        stmt = stmt.where(C2PASchema.namespace == namespace)
    if is_public is not None:
        stmt = stmt.where(C2PASchema.is_public == is_public)
    
    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Paginate
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    
    result = await db.execute(stmt)
    schemas = result.scalars().all()
    
    return C2PASchemaListResponse(
        schemas=[C2PASchemaResponse(**s.to_dict()) for s in schemas],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/schemas/{schema_id}", response_model=C2PASchemaResponse)
async def get_schema(
    schema_id: UUID,
    organization_id: str = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific C2PA assertion schema."""
    stmt = select(C2PASchema).where(
        C2PASchema.id == schema_id,
        (C2PASchema.organization_id == organization_id) | (C2PASchema.is_public == True)
    )
    result = await db.execute(stmt)
    schema = result.scalar_one_or_none()
    
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    
    return C2PASchemaResponse(**schema.to_dict())


@router.put("/schemas/{schema_id}", response_model=C2PASchemaResponse)
async def update_schema(
    schema_id: UUID,
    schema_update: C2PASchemaUpdate,
    organization_id: str = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Update a C2PA assertion schema."""
    stmt = select(C2PASchema).where(
        C2PASchema.id == schema_id,
        C2PASchema.organization_id == organization_id
    )
    result = await db.execute(stmt)
    schema = result.scalar_one_or_none()
    
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found or not owned by organization")
    
    # Update fields
    if schema_update.schema is not None:
        # Validate new schema
        try:
            validator.register_schema(schema.label, schema_update.schema)
            schema.schema = schema_update.schema
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    if schema_update.description is not None:
        schema.description = schema_update.description
    if schema_update.is_public is not None:
        schema.is_public = schema_update.is_public
    
    await db.commit()
    await db.refresh(schema)
    
    logger.info(f"Updated C2PA schema {schema_id} for org {organization_id}")
    
    return C2PASchemaResponse(**schema.to_dict())


@router.delete("/schemas/{schema_id}", status_code=204)
async def delete_schema(
    schema_id: UUID,
    organization_id: str = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Delete a C2PA assertion schema."""
    stmt = select(C2PASchema).where(
        C2PASchema.id == schema_id,
        C2PASchema.organization_id == organization_id
    )
    result = await db.execute(stmt)
    schema = result.scalar_one_or_none()
    
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found or not owned by organization")
    
    await db.delete(schema)
    await db.commit()
    
    logger.info(f"Deleted C2PA schema {schema_id} for org {organization_id}")


# Assertion Validation Endpoint

@router.post("/validate", response_model=C2PAAssertionValidateResponse)
async def validate_assertion(
    request: C2PAAssertionValidateRequest,
    organization_id: str = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """
    Validate a C2PA assertion before embedding.
    
    Checks the assertion data against its registered schema.
    """
    # Get schema if it exists
    stmt = select(C2PASchema).where(
        C2PASchema.label == request.label,
        (C2PASchema.organization_id == organization_id) | (C2PASchema.is_public == True)
    ).order_by(C2PASchema.created_at.desc())
    
    result = await db.execute(stmt)
    schema_model = result.scalar_one_or_none()
    
    schema = schema_model.schema if schema_model else None
    
    # Validate
    is_valid, errors, warnings = validator.validate_assertion(
        request.label,
        request.data,
        schema
    )
    
    return C2PAAssertionValidateResponse(
        valid=is_valid,
        assertions=[{
            'label': request.label,
            'valid': is_valid,
            'errors': errors,
            'warnings': warnings
        }]
    )


# Template Management Endpoints

@router.post("/templates", response_model=C2PATemplateResponse, status_code=201)
async def create_template(
    template_data: C2PATemplateCreate,
    organization_id: str = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Create a new assertion template."""
    new_template = C2PAAssertionTemplate(
        name=template_data.name,
        description=template_data.description,
        assertions=template_data.assertions,
        organization_id=organization_id,
        is_public=template_data.is_public,
        category=template_data.category
    )
    
    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)
    
    logger.info(f"Created C2PA template {template_data.name} for org {organization_id}")
    
    return C2PATemplateResponse(**new_template.to_dict())


@router.get("/templates", response_model=C2PATemplateListResponse)
async def list_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    organization_id: str = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """List available assertion templates."""
    stmt = select(C2PAAssertionTemplate).where(
        (C2PAAssertionTemplate.organization_id == organization_id) | (C2PAAssertionTemplate.is_public == True)
    )
    
    if category:
        stmt = stmt.where(C2PAAssertionTemplate.category == category)
    
    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Paginate
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    
    result = await db.execute(stmt)
    templates = result.scalars().all()
    
    return C2PATemplateListResponse(
        templates=[C2PATemplateResponse(**t.to_dict()) for t in templates],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/templates/{template_id}", response_model=C2PATemplateResponse)
async def get_template(
    template_id: UUID,
    organization_id: str = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific assertion template."""
    stmt = select(C2PAAssertionTemplate).where(
        C2PAAssertionTemplate.id == template_id,
        (C2PAAssertionTemplate.organization_id == organization_id) | (C2PAAssertionTemplate.is_public == True)
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return C2PATemplateResponse(**template.to_dict())


@router.put("/templates/{template_id}", response_model=C2PATemplateResponse)
async def update_template(
    template_id: UUID,
    template_update: C2PATemplateUpdate,
    organization_id: str = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Update an assertion template."""
    stmt = select(C2PAAssertionTemplate).where(
        C2PAAssertionTemplate.id == template_id,
        C2PAAssertionTemplate.organization_id == organization_id
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found or not owned by organization")
    
    # Update fields
    if template_update.name is not None:
        template.name = template_update.name
    if template_update.description is not None:
        template.description = template_update.description
    if template_update.assertions is not None:
        template.assertions = template_update.assertions
    if template_update.category is not None:
        template.category = template_update.category
    if template_update.is_public is not None:
        template.is_public = template_update.is_public
    
    await db.commit()
    await db.refresh(template)
    
    logger.info(f"Updated C2PA template {template_id} for org {organization_id}")
    
    return C2PATemplateResponse(**template.to_dict())


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: UUID,
    organization_id: str = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Delete an assertion template."""
    stmt = select(C2PAAssertionTemplate).where(
        C2PAAssertionTemplate.id == template_id,
        C2PAAssertionTemplate.organization_id == organization_id
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found or not owned by organization")
    
    await db.delete(template)
    await db.commit()
    
    logger.info(f"Deleted C2PA template {template_id} for org {organization_id}")
