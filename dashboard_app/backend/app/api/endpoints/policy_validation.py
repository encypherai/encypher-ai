"""
API endpoints for policy validation.
"""
from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.policy_validation import (
    PolicySchema,
    PolicySchemaCreate,
    PolicyValidationResult,
    PolicyValidationResultCreate,
    PolicyValidationStats,
    PolicyValidationFilters
)
from app.services.user import get_current_user
from app.services.policy_validation import (
    get_policy_schemas,
    get_policy_schema_by_id,
    create_policy_schema,
    get_validation_results,
    get_validation_result_by_id,
    create_validation_result,
    get_validation_stats,
    import_validation_results_from_csv
)

router = APIRouter()

# Policy Schema endpoints
@router.get("/schemas/", response_model=List[PolicySchema])
async def read_policy_schemas(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve policy schemas.
    """
    return await get_policy_schemas(db, skip=skip, limit=limit) # Anticipating async service

@router.post("/schemas/", response_model=PolicySchema, status_code=status.HTTP_201_CREATED)
async def create_new_policy_schema(
    schema_in: PolicySchemaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new policy schema.
    """
    return await create_policy_schema(db, schema_in) # Anticipating async service

@router.get("/schemas/{schema_id}", response_model=PolicySchema)
async def read_policy_schema(
    schema_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a specific policy schema by ID.
    """
    schema = await get_policy_schema_by_id(db, schema_id) # Anticipating async service
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy schema not found"
        )
    return schema

# Validation Results endpoints
@router.get("/results/", response_model=List[PolicyValidationResult])
async def read_validation_results(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    policy_schema_id: Optional[int] = None,
    is_valid: Optional[bool] = None,
    department: Optional[str] = None,
    source_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve validation results with optional filtering.
    """
    filters = PolicyValidationFilters(
        start_date=start_date,
        end_date=end_date,
        policy_schema_id=policy_schema_id,
        is_valid=is_valid,
        department=department,
        source_type=source_type
    )
    return await get_validation_results(db, filters=filters, skip=skip, limit=limit) # Anticipating async service

@router.get("/stats")
async def read_policy_validation_stats(
    db: AsyncSession = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    policy_schema_id: Optional[int] = None,
    department: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get policy validation statistics for dashboard.
    """
    filters = PolicyValidationFilters(
        start_date=start_date,
        end_date=end_date,
        policy_schema_id=policy_schema_id,
        department=department
    )
    # Get the base stats
    stats = await get_validation_stats(db, filters=filters)
    
    # Transform to match frontend expectations
    from app.utils.stats_transformers import transform_validation_stats
    return transform_validation_stats(stats, start_date, end_date) # Anticipating async service

@router.get("/results/{result_id}", response_model=PolicyValidationResult)
async def read_validation_result(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a specific validation result by ID.
    """
    result = await get_validation_result_by_id(db, result_id) # Anticipating async service
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation result not found"
        )
    return result

@router.post("/results/", response_model=PolicyValidationResult, status_code=status.HTTP_201_CREATED)
async def create_new_validation_result(
    result_in: PolicyValidationResultCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new validation result.
    """
    return await create_validation_result(db, result_in) # Anticipating async service

@router.post("/import-csv/", status_code=status.HTTP_201_CREATED)
async def import_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Import validation results from a CSV file generated by the policy_validator_cli tool.
    """
    # Save the uploaded file temporarily
    import tempfile
    import os
    
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        contents = await file.read()
        with open(temp_file.name, 'wb') as f:
            f.write(contents)
        
        # Import the CSV file
        count = await import_validation_results_from_csv(db, temp_file.name) # Anticipating async service
        
        return {"message": f"Successfully imported {count} validation results"}
    finally:
        os.unlink(temp_file.name)
