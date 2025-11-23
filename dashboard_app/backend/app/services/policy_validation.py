"""
Service for policy validation operations.
"""
import csv
import json
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy import func, select 
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.caching import cached_async, invalidate_cache

from app.models.policy_validation import PolicySchema, PolicyValidationResult
from app.schemas.policy_validation import (
    PolicySchemaCreate,
    PolicyValidationResultCreate,
    PolicyValidationFilters,
    PolicyValidationStats
)

async def get_policy_schemas(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[PolicySchema]:
    """
    Get policy schemas.
    """
    stmt = select(PolicySchema).order_by(PolicySchema.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_policy_schema_by_id(db: AsyncSession, schema_id: int) -> Optional[PolicySchema]:
    """
    Get a policy schema by ID.
    """
    return await db.get(PolicySchema, schema_id)

async def create_policy_schema(db: AsyncSession, schema_in: PolicySchemaCreate) -> PolicySchema:
    """
    Create a new policy schema.
    """
    schema = PolicySchema(**schema_in.model_dump()) 
    db.add(schema)
    await db.commit()
    await db.refresh(schema)
    return schema

async def get_validation_results(
    db: AsyncSession,
    filters: Optional[PolicyValidationFilters] = None,
    skip: int = 0,
    limit: int = 100
) -> List[PolicyValidationResult]:
    """
    Get validation results with optional filtering.
    """
    stmt = select(PolicyValidationResult)
    
    if filters:
        if filters.start_date:
            stmt = stmt.where(PolicyValidationResult.validation_time >= filters.start_date)
        if filters.end_date:
            stmt = stmt.where(PolicyValidationResult.validation_time <= filters.end_date)
        if filters.policy_schema_id is not None:
            stmt = stmt.where(PolicyValidationResult.policy_schema_id == filters.policy_schema_id)
        if filters.is_valid is not None:
            stmt = stmt.where(PolicyValidationResult.is_valid == filters.is_valid)
        if filters.department:
            stmt = stmt.where(PolicyValidationResult.department == filters.department)
        if filters.source_type:
            stmt = stmt.where(PolicyValidationResult.source_type == filters.source_type)
    
    result = await db.execute(
        stmt.order_by(PolicyValidationResult.validation_time.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def get_validation_result_by_id(db: AsyncSession, result_id: int) -> Optional[PolicyValidationResult]:
    """
    Get a validation result by ID.
    """
    return await db.get(PolicyValidationResult, result_id)

async def create_validation_result(db: AsyncSession, result_in: PolicyValidationResultCreate) -> PolicyValidationResult:
    """
    Create a new validation result.
    """
    result = PolicyValidationResult(**result_in.model_dump()) 
    db.add(result)
    await db.commit()
    await db.refresh(result)
    
    # Invalidate stats cache when new data is added
    invalidate_cache("policy_validation_stats")
    
    return result

@cached_async(key_prefix="policy_validation_stats", ttl_seconds=300)
async def get_validation_stats(db: AsyncSession, filters: Optional[PolicyValidationFilters] = None) -> PolicyValidationStats:
    """
    Get validation statistics for dashboard.
    """
    def _get_base_filtered_stmt_for_stats():
        stmt = select(func.count(PolicyValidationResult.id))
        if filters:
            if filters.start_date:
                stmt = stmt.where(PolicyValidationResult.validation_time >= filters.start_date)
            if filters.end_date:
                stmt = stmt.where(PolicyValidationResult.validation_time <= filters.end_date)
            if filters.policy_schema_id is not None:
                stmt = stmt.where(PolicyValidationResult.policy_schema_id == filters.policy_schema_id)
            if filters.department:
                stmt = stmt.where(PolicyValidationResult.department == filters.department)
        return stmt

    total_documents_stmt = _get_base_filtered_stmt_for_stats()
    total_documents_result = await db.execute(total_documents_stmt)
    total_documents = total_documents_result.scalar_one()

    valid_count_stmt = _get_base_filtered_stmt_for_stats().where(PolicyValidationResult.is_valid == True)
    valid_count_result = await db.execute(valid_count_stmt)
    valid_count = valid_count_result.scalar_one()

    invalid_count_stmt = _get_base_filtered_stmt_for_stats().where(PolicyValidationResult.is_valid == False)
    invalid_count_result = await db.execute(invalid_count_stmt)
    invalid_count = invalid_count_result.scalar_one()
    
    validation_rate = (valid_count / total_documents) * 100 if total_documents > 0 else 0
    
    error_types: Dict[str, int] = {}
    error_results_stmt = select(PolicyValidationResult.errors).where(PolicyValidationResult.is_valid == False)
    if filters:
        if filters.start_date:
            error_results_stmt = error_results_stmt.where(PolicyValidationResult.validation_time >= filters.start_date)
        if filters.end_date:
            error_results_stmt = error_results_stmt.where(PolicyValidationResult.validation_time <= filters.end_date)
        if filters.policy_schema_id is not None:
            error_results_stmt = error_results_stmt.where(PolicyValidationResult.policy_schema_id == filters.policy_schema_id)
        if filters.department:
            error_results_stmt = error_results_stmt.where(PolicyValidationResult.department == filters.department)

    error_results_list_result = await db.execute(error_results_stmt)
    error_results_list = error_results_list_result.scalars().all()
    for errors_list_item in error_results_list: 
        if errors_list_item:
            for error_str in errors_list_item:
                error_type = error_str.split(':')[0].strip() if ':' in error_str else error_str
                error_types[error_type] = error_types.get(error_type, 0) + 1
                
    department_stats_stmt = select(
        PolicyValidationResult.department, func.count(PolicyValidationResult.id)
    ).where(PolicyValidationResult.department.isnot(None))
    
    if filters:
        if filters.start_date:
            department_stats_stmt = department_stats_stmt.where(PolicyValidationResult.validation_time >= filters.start_date)
        if filters.end_date:
            department_stats_stmt = department_stats_stmt.where(PolicyValidationResult.validation_time <= filters.end_date)
        if filters.policy_schema_id is not None:
            department_stats_stmt = department_stats_stmt.where(PolicyValidationResult.policy_schema_id == filters.policy_schema_id)
            
    department_stats_result = await db.execute(department_stats_stmt.group_by(PolicyValidationResult.department))
    department_stats = dict(department_stats_result.all())
    
    return PolicyValidationStats(
        total_documents=total_documents,
        valid_count=valid_count,
        invalid_count=invalid_count,
        validation_rate=validation_rate,
        error_types=error_types,
        department_stats=department_stats
    )

async def import_validation_results_from_csv(db: AsyncSession, csv_file_path: str) -> int:
    """
    Import validation results from a CSV file generated by the policy_validator_cli tool.
    """
    default_schema_stmt = select(PolicySchema).limit(1)
    default_schema_result = await db.execute(default_schema_stmt)
    default_schema = default_schema_result.scalar_one_or_none()

    if not default_schema:
        default_schema = PolicySchema(
            name="Default Policy",
            description="Default policy schema created during CSV import",
            schema_definition={"rules": []} 
        )
        db.add(default_schema)
        await db.commit()
        await db.refresh(default_schema)
    
    count = 0
    results_to_add = []
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            metadata = {}
            errors_list_from_csv = []
            
            standardized_row = {k.lower().replace(' ', '_'): v for k, v in row.items() if k}

            policy_valid = standardized_row.get('policy_valid', 'false').lower() == 'true'
            error_str = standardized_row.get('errors', '')
            if error_str:
                try:
                    parsed_errors = json.loads(error_str.replace("'", "\"")) 
                    if isinstance(parsed_errors, list):
                        errors_list_from_csv = [str(e) for e in parsed_errors]
                    elif isinstance(parsed_errors, str):
                         errors_list_from_csv = [parsed_errors]
                    else:
                        errors_list_from_csv = [str(parsed_errors)] 
                except (json.JSONDecodeError, TypeError):
                    errors_list_from_csv = [error_str]
            
            for key, value in standardized_row.items():
                if key not in ['source', 'policy_valid', 'errors', 'department', 'validation_time']:
                    try:
                        metadata[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        metadata[key] = value
            
            department = standardized_row.get('department')
            validation_time_str = standardized_row.get('validation_time')
            try:
                validation_time = datetime.fromisoformat(validation_time_str) if validation_time_str else datetime.now()
            except ValueError:
                validation_time = datetime.now()

            result = PolicyValidationResult(
                source=standardized_row.get('source', ''),
                policy_schema_id=default_schema.id, 
                is_valid=policy_valid,
                validated_data=metadata, # Changed from metadata
                errors=errors_list_from_csv,
                department=department,
                validation_time=validation_time
            )
            results_to_add.append(result)
            count += 1
        
    if results_to_add:
        db.add_all(results_to_add)
        await db.commit()
    
    return count
