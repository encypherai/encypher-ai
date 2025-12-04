"""
Script to seed the database with sample data for dashboard testing.
This will create sample audit logs and policy validation results.
"""
import asyncio
import os
import random
import sys
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models.audit_log import AuditLog
from app.models.policy_validation import PolicySchema, PolicyValidationResult

# Sample data for generation
DEPARTMENTS = ["Engineering", "Marketing", "Sales", "Finance", "HR", "Legal"]
SOURCE_TYPES = ["CLI", "API", "Dashboard", "File Upload"]
STATUSES = ["VERIFIED", "UNVERIFIED", "ERROR"]
ERROR_MESSAGES = [
    "Invalid metadata format",
    "Missing required fields",
    "Schema validation failed",
    "Unauthorized access",
    "Resource not found"
]
ERROR_TYPES = [
    "missing_field",
    "invalid_format",
    "size_exceeded",
    "unauthorized_access",
    "schema_mismatch"
]

async def create_policy_schema(db: AsyncSession) -> PolicySchema:
    """Create a sample policy schema if none exists."""
    from sqlalchemy import select
    
    # Check if we already have a schema
    result = await db.execute(select(PolicySchema).limit(1))
    existing_schema = result.scalar_one_or_none()
    
    if existing_schema:
        print(f"Using existing policy schema: {existing_schema.name}")
        return existing_schema
    
    # Create a new schema
    schema = PolicySchema(
        name="Metadata Policy Schema",
        description="Default policy schema for metadata validation",
        schema={
            "type": "object",
            "required": ["title", "description", "author"],
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "author": {"type": "string"},
                "department": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}}
            }
        }
    )
    db.add(schema)
    await db.flush()
    print(f"Created new policy schema: {schema.name}")
    return schema

async def create_audit_logs(db: AsyncSession, count: int = 50):
    """Create sample audit logs."""
    now = datetime.now()
    logs = []
    
    for i in range(count):
        # Create a random date within the last 30 days
        days_ago = random.randint(0, 30)
        verification_time = now - timedelta(days=days_ago)
        
        # Randomize data
        department = random.choice(DEPARTMENTS)
        source_type = random.choice(SOURCE_TYPES)
        status = random.choice(STATUSES)
        is_verified = status == "VERIFIED"
        
        # Create event data
        event_data = {
            "file_name": f"document_{i}.pdf",
            "file_size": random.randint(1000, 10000000),
            "mime_type": "application/pdf",
            "user_id": random.randint(1, 10),
            "action": "upload" if random.random() > 0.5 else "download"
        }
        
        # Add error message for ERROR status
        error_message = None
        if status == "ERROR":
            error_message = random.choice(ERROR_MESSAGES)
        
        # Create the audit log
        log = AuditLog(
            source=f"/path/to/document_{i}.pdf",
            is_verified=is_verified,
            status=status,
            verification_time=verification_time,
            event_data=event_data,
            error_message=error_message,
            model_id=f"model_{random.randint(1, 5)}",
            source_type=source_type,
            department=department
        )
        logs.append(log)
    
    db.add_all(logs)
    await db.flush()
    print(f"Created {len(logs)} audit logs")

async def create_validation_results(db: AsyncSession, schema: PolicySchema, count: int = 50):
    """Create sample policy validation results."""
    now = datetime.now()
    results = []
    
    for i in range(count):
        # Create a random date within the last 30 days
        days_ago = random.randint(0, 30)
        validation_time = now - timedelta(days=days_ago)
        
        # Randomize data
        department = random.choice(DEPARTMENTS)
        source_type = random.choice(SOURCE_TYPES)
        is_valid = random.random() > 0.3  # 70% valid
        
        # Create validated data
        validated_data = {
            "title": f"Document {i}",
            "description": f"This is a sample document {i} for testing",
            "author": f"User {random.randint(1, 10)}",
            "department": department,
            "tags": ["test", "sample", department.lower()]
        }
        
        # Add errors for invalid results
        errors = None
        if not is_valid:
            error_count = random.randint(1, 3)
            errors = [random.choice(ERROR_TYPES) for _ in range(error_count)]
        
        # Create the validation result
        result = PolicyValidationResult(
            source=f"/path/to/document_{i}.pdf",
            policy_schema_id=schema.id,
            is_valid=is_valid,
            validation_time=validation_time,
            validated_data=validated_data,
            errors=errors,
            source_type=source_type,
            department=department
        )
        results.append(result)
    
    db.add_all(results)
    await db.flush()
    print(f"Created {len(results)} policy validation results")

async def main():
    """Main function to seed the database."""
    async with AsyncSessionLocal() as db:
        try:
            # Create policy schema
            schema = await create_policy_schema(db)
            
            # Create sample data
            await create_audit_logs(db, count=100)
            await create_validation_results(db, schema, count=100)
            
            # Commit the transaction
            await db.commit()
            print("Successfully seeded the database with sample data")
            
        except Exception as e:
            await db.rollback()
            print(f"Error seeding database: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(main())
