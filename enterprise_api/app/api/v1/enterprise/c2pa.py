"""
C2PA Custom Assertions API Endpoints

Endpoints for managing custom C2PA schemas and templates.
"""

import logging
from typing import Any, Dict, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization
from app.models.c2pa_schema import C2PASchema
from app.models.c2pa_template import C2PAAssertionTemplate
from app.schemas.c2pa_schemas import (
    C2PAAssertionValidateRequest,
    C2PAAssertionValidateResponse,
    C2PASchemaCreate,
    C2PASchemaListResponse,
    C2PASchemaResponse,
    C2PASchemaUpdate,
    C2PATemplateCreate,
    C2PATemplateListResponse,
    C2PATemplateResponse,
    C2PATemplateUpdate,
)
from app.services.c2pa_builtin_templates import BUILTIN_TEMPLATES, get_builtin_template
from app.services.c2pa_validator import validator

logger = logging.getLogger(__name__)
router = APIRouter()


def require_enterprise_custom_assertion_authoring(
    organization: dict = Depends(get_current_organization),
) -> dict:
    tier = (organization.get("tier") or "starter").lower().replace("-", "_")
    allowed_tiers = {"enterprise", "strategic_partner", "demo"}
    if tier not in allowed_tiers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Custom assertion authoring requires Enterprise tier",
                "upgrade_url": "/billing/upgrade",
            },
        )
    return organization


def require_custom_assertion_templates_access(
    organization: dict = Depends(get_current_organization),
) -> dict:
    features = organization.get("features", {})
    custom_assertions_enabled = False
    if isinstance(features, dict):
        custom_assertions_enabled = features.get("custom_assertions", False)
    custom_assertions_enabled = custom_assertions_enabled or organization.get("custom_assertions_enabled", False)

    if not custom_assertions_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Custom assertion templates require Business tier or higher",
                "upgrade_url": "/billing/upgrade",
            },
        )

    return organization


# Schema Management Endpoints


@router.post("/schemas", response_model=C2PASchemaResponse, status_code=201)
async def create_schema(
    schema_data: C2PASchemaCreate, organization: dict = Depends(require_enterprise_custom_assertion_authoring), db: AsyncSession = Depends(get_db)
):
    """
    Register a custom C2PA assertion schema.

    Allows organizations to define custom assertion types with
    JSON Schema validation rules.
    """
    organization_id = organization["organization_id"]
    try:
        # Validate the schema itself
        validator.register_schema(schema_data.label, schema_data.json_schema)

        # Check if schema already exists for this org
        stmt = select(C2PASchema).where(
            C2PASchema.organization_id == organization_id, C2PASchema.label == schema_data.label, C2PASchema.version == schema_data.version
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(status_code=409, detail=f"Schema {schema_data.label} version {schema_data.version} already exists")

        # Create new schema
        new_schema = C2PASchema(
            name=schema_data.name,
            label=schema_data.label,
            version=schema_data.version,
            json_schema=schema_data.json_schema,
            description=schema_data.description,
            organization_id=organization_id,
            is_public=schema_data.is_public,
        )

        db.add(new_schema)
        await db.commit()
        await db.refresh(new_schema)

        logger.info(f"Created C2PA schema {schema_data.label} for org {organization_id}")

        return C2PASchemaResponse(**new_schema.to_dict())

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating schema: {e}")
        raise HTTPException(status_code=500, detail="Failed to create schema")


@router.get("/schemas", response_model=C2PASchemaListResponse)
async def list_schemas(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    is_public: Optional[bool] = None,
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """
    List available C2PA assertion schemas.

    Returns schemas owned by the organization or public schemas.
    """
    organization_id = organization["organization_id"]
    # Build query - show org's schemas and public schemas
    stmt = select(C2PASchema).where((C2PASchema.organization_id == organization_id) | (C2PASchema.is_public))

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

    return C2PASchemaListResponse(schemas=[C2PASchemaResponse(**s.to_dict()) for s in schemas], total=total, page=page, page_size=page_size)


@router.get("/schemas/{schema_id}", response_model=C2PASchemaResponse)
async def get_schema(schema_id: str, organization: dict = Depends(get_current_organization), db: AsyncSession = Depends(get_db)):
    """Get a specific C2PA assertion schema."""
    organization_id = organization["organization_id"]
    stmt = select(C2PASchema).where(C2PASchema.id == schema_id, (C2PASchema.organization_id == organization_id) | (C2PASchema.is_public))
    result = await db.execute(stmt)
    schema = result.scalar_one_or_none()

    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")

    return C2PASchemaResponse(**schema.to_dict())


@router.put("/schemas/{schema_id}", response_model=C2PASchemaResponse)
async def update_schema(
    schema_id: str,
    schema_update: C2PASchemaUpdate,
    organization: dict = Depends(require_enterprise_custom_assertion_authoring),
    db: AsyncSession = Depends(get_db),
):
    """Update a C2PA assertion schema."""
    organization_id = organization["organization_id"]
    stmt = select(C2PASchema).where(C2PASchema.id == schema_id, C2PASchema.organization_id == organization_id)
    result = await db.execute(stmt)
    schema = result.scalar_one_or_none()

    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found or not owned by organization")

    # Update fields
    schema_any = cast(Any, schema)
    if schema_update.json_schema is not None:
        # Validate new schema
        try:
            validator.register_schema(cast(str, schema.label), schema_update.json_schema)
            schema_any.json_schema = schema_update.json_schema
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    if schema_update.description is not None:
        schema_any.description = schema_update.description
    if schema_update.is_public is not None:
        schema_any.is_public = schema_update.is_public

    await db.commit()
    await db.refresh(schema)

    logger.info(f"Updated C2PA schema {schema_id} for org {organization_id}")

    return C2PASchemaResponse(**schema.to_dict())


@router.delete("/schemas/{schema_id}", status_code=204)
async def delete_schema(
    schema_id: str, organization: dict = Depends(require_enterprise_custom_assertion_authoring), db: AsyncSession = Depends(get_db)
):
    """Delete a C2PA assertion schema."""
    organization_id = organization["organization_id"]
    stmt = select(C2PASchema).where(C2PASchema.id == schema_id, C2PASchema.organization_id == organization_id)
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
    request: C2PAAssertionValidateRequest, organization: dict = Depends(get_current_organization), db: AsyncSession = Depends(get_db)
):
    """
    Validate a C2PA assertion before embedding.

    Checks the assertion data against its registered schema.
    """
    organization_id = organization["organization_id"]
    # Get schema if it exists
    stmt = (
        select(C2PASchema)
        .where(C2PASchema.label == request.label, (C2PASchema.organization_id == organization_id) | (C2PASchema.is_public))
        .order_by(C2PASchema.created_at.desc())
    )

    result = await db.execute(stmt)
    schema_model = result.scalar_one_or_none()

    json_schema = cast(Optional[Dict[str, Any]], schema_model.json_schema) if schema_model else None

    # Validate
    is_valid, errors, warnings = validator.validate_assertion(request.label, request.data, json_schema)

    return C2PAAssertionValidateResponse(
        valid=is_valid, assertions=[{"label": request.label, "valid": is_valid, "errors": errors, "warnings": warnings}]
    )


# Template Management Endpoints


@router.post("/templates", response_model=C2PATemplateResponse, status_code=201)
async def create_template(
    template_data: C2PATemplateCreate, organization: dict = Depends(require_enterprise_custom_assertion_authoring), db: AsyncSession = Depends(get_db)
):
    """Create a new assertion template."""
    organization_id = organization["organization_id"]
    new_template = C2PAAssertionTemplate(
        name=template_data.name,
        schema_id=template_data.schema_id,
        template_data=template_data.template_data,
        description=template_data.description,
        organization_id=organization_id,
        is_public=template_data.is_public,
        category=template_data.category,
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
    organization: dict = Depends(require_custom_assertion_templates_access),
    db: AsyncSession = Depends(get_db),
):
    """List available assertion templates."""
    organization_id = organization["organization_id"]

    stmt = select(C2PAAssertionTemplate).where((C2PAAssertionTemplate.organization_id == organization_id) | (C2PAAssertionTemplate.is_public))

    if category:
        stmt = stmt.where(C2PAAssertionTemplate.category == category)

    result = await db.execute(stmt)
    db_templates = [C2PATemplateResponse(**t.to_dict()) for t in result.scalars().all()]

    builtin_templates = []
    for template in BUILTIN_TEMPLATES.values():
        if category and template.get("category") != category:
            continue
        builtin_templates.append(C2PATemplateResponse(**template))

    all_templates = builtin_templates + db_templates

    total = len(all_templates)
    offset = (page - 1) * page_size
    paged = all_templates[offset : offset + page_size]

    return C2PATemplateListResponse(
        templates=paged,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/templates/{template_id}", response_model=C2PATemplateResponse)
async def get_template(template_id: str, organization: dict = Depends(require_custom_assertion_templates_access), db: AsyncSession = Depends(get_db)):
    """Get a specific assertion template."""
    organization_id = organization["organization_id"]

    builtin = get_builtin_template(template_id=template_id)
    if builtin is not None:
        return C2PATemplateResponse(**builtin)

    stmt = select(C2PAAssertionTemplate).where(
        C2PAAssertionTemplate.id == template_id, (C2PAAssertionTemplate.organization_id == organization_id) | (C2PAAssertionTemplate.is_public)
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return C2PATemplateResponse(**template.to_dict())


@router.put("/templates/{template_id}", response_model=C2PATemplateResponse)
async def update_template(
    template_id: str,
    template_update: C2PATemplateUpdate,
    organization: dict = Depends(require_enterprise_custom_assertion_authoring),
    db: AsyncSession = Depends(get_db),
):
    """Update an assertion template."""
    organization_id = organization["organization_id"]
    stmt = select(C2PAAssertionTemplate).where(C2PAAssertionTemplate.id == template_id, C2PAAssertionTemplate.organization_id == organization_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found or not owned by organization")

    # Update fields
    template_any = cast(Any, template)
    if template_update.name is not None:
        template_any.name = template_update.name
    if template_update.description is not None:
        template_any.description = template_update.description
    if template_update.template_data is not None:
        template_any.template_data = template_update.template_data
    if template_update.category is not None:
        template_any.category = template_update.category
    if template_update.is_public is not None:
        template_any.is_public = template_update.is_public

    await db.commit()
    await db.refresh(template)

    logger.info(f"Updated C2PA template {template_id} for org {organization_id}")

    return C2PATemplateResponse(**template.to_dict())


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: str, organization: dict = Depends(require_enterprise_custom_assertion_authoring), db: AsyncSession = Depends(get_db)
):
    """Delete an assertion template."""
    organization_id = organization["organization_id"]
    stmt = select(C2PAAssertionTemplate).where(C2PAAssertionTemplate.id == template_id, C2PAAssertionTemplate.organization_id == organization_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found or not owned by organization")

    await db.delete(template)
    await db.commit()

    logger.info(f"Deleted C2PA template {template_id} for org {organization_id}")
