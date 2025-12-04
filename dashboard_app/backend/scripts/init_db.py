"""
Script to initialize the database with sample data for testing.
"""
import asyncio
import os
import random
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.audit_log import AuditLog
from app.models.policy_validation import PolicySchema, PolicyValidationResult
from app.models.user import User


# Create all tables - we'll do this asynchronously
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def init_db() -> None:
    """Initialize the database with sample data."""
    async with AsyncSessionLocal() as db:
        try:
            # Create sample users
            result = await db.execute(select(func.count()).select_from(User))
            user_count = result.scalar()
            if user_count == 0:
                print("Creating sample users...")
                admin_user = User(
                    username="admin",
                    email="admin@encypherai.com",
                    full_name="Admin User",
                    is_superuser=True,
                    hashed_password=get_password_hash("admin123")
                )
                db.add(admin_user)
                
                regular_user = User(
                    username="user",
                    email="user@encypherai.com",
                    full_name="Regular User",
                    is_superuser=False,
                    hashed_password=get_password_hash("user123")
                )
                db.add(regular_user)
                await db.commit()
                print("Sample users created.")
            
            # Create sample policy schemas
            result = await db.execute(select(func.count()).select_from(PolicySchema))
            policy_count = result.scalar()
            if policy_count == 0:
                print("Creating sample policy schemas...")
                basic_policy = PolicySchema(
                    name="Basic Metadata Policy",
                    description="Basic policy requiring model_id and department",
                    schema={
                        "rules": [
                            {
                                "key": "model_id",
                                "required": True,
                                "type": "string"
                            },
                            {
                                "key": "department",
                                "required": True,
                                "type": "string",
                                "allowed_values": ["HR", "Finance", "Marketing", "Engineering", "Legal"]
                            }
                        ]
                    }
                )
                
                advanced_policy = PolicySchema(
                    name="Advanced Metadata Policy",
                    description="Advanced policy with additional requirements",
                    schema={
                        "rules": [
                            {
                                "key": "model_id",
                                "required": True,
                                "type": "string"
                            },
                            {
                                "key": "department",
                                "required": True,
                                "type": "string",
                                "allowed_values": ["HR", "Finance", "Marketing", "Engineering", "Legal"]
                            },
                            {
                                "key": "purpose",
                                "required": True,
                                "type": "string"
                            },
                            {
                                "key": "data_sensitivity",
                                "required": True,
                                "type": "string",
                                "allowed_values": ["low", "medium", "high"]
                            },
                            {
                                "key": "retention_period",
                                "required": False,
                                "type": "integer"
                            }
                        ]
                    }
                )
                
                db.add(basic_policy)
                db.add(advanced_policy)
                await db.commit()
                
                # Refresh to get IDs
                await db.refresh(basic_policy)
                await db.refresh(advanced_policy)
                print("Sample policy schemas created.")
            
            # Create sample audit logs
            result = await db.execute(select(func.count()).select_from(AuditLog))
            audit_count = result.scalar()
            if audit_count == 0:
                print("Creating sample audit logs...")
                # Get existing policy schemas
                result = await db.execute(select(PolicySchema).filter(PolicySchema.name == "Basic Metadata Policy").limit(1))
                basic_policy = result.scalars().first()
                
                # Sample model IDs and departments
                model_ids = ["gpt-4", "gpt-3.5-turbo", "claude-2", "llama-2", "falcon-7b"]
                departments = ["HR", "Finance", "Marketing", "Engineering", "Legal"]
                source_types = ["file", "api", "database"]
                
                # Create 50 sample audit logs over the past 30 days
                for i in range(50):
                    # Random date in the past 30 days
                    days_ago = random.randint(0, 30)
                    verification_time = datetime.now() - timedelta(days=days_ago)
                    
                    # Random model and department
                    model_id = random.choice(model_ids)
                    department = random.choice(departments)
                    source_type = random.choice(source_types)
                    
                    # 80% chance of being verified
                    is_verified = random.random() < 0.8
                    
                    # Status based on verification
                    if is_verified:
                        status = "VERIFIED"
                        error_message = None
                    else:
                        status = random.choice(["UNVERIFIED", "ERROR"])
                        error_message = "Metadata verification failed" if status == "ERROR" else None
                    
                    # Sample metadata
                    metadata = {
                        "model_id": model_id,
                        "department": department,
                        "purpose": f"Sample purpose for {model_id}",
                        "created_by": f"user{random.randint(1, 10)}@encypherai.com",
                        "data_sensitivity": random.choice(["low", "medium", "high"])
                    }
                    
                    # Create audit log
                    audit_log = AuditLog(
                        source=f"sample/path/to/document_{i}.pdf" if source_type == "file" else f"api/endpoint/{i}",
                        is_verified=is_verified,
                        status=status,
                        error_message=error_message,
                        metadata=metadata,
                        model_id=model_id,
                        department=department,
                        source_type=source_type,
                        verification_time=verification_time
                    )
                    
                    db.add(audit_log)
                
                await db.commit()
                print("Sample audit logs created.")
            
            # Create sample policy validation results
            result = await db.execute(select(func.count()).select_from(PolicyValidationResult))
            validation_count = result.scalar()
            if validation_count == 0:
                print("Creating sample policy validation results...")
                # Get existing policy schemas
                result = await db.execute(select(PolicySchema).filter(PolicySchema.name == "Basic Metadata Policy").limit(1))
                basic_policy = result.scalars().first()
                result = await db.execute(select(PolicySchema).filter(PolicySchema.name == "Advanced Metadata Policy").limit(1))
                advanced_policy = result.scalars().first()
                
                # Sample model IDs and departments
                model_ids = ["gpt-4", "gpt-3.5-turbo", "claude-2", "llama-2", "falcon-7b"]
                departments = ["HR", "Finance", "Marketing", "Engineering", "Legal"]
                source_types = ["file", "api", "database"]
                
                # Create 50 sample validation results over the past 30 days
                for i in range(50):
                    # Random date in the past 30 days
                    days_ago = random.randint(0, 30)
                    validation_time = datetime.now() - timedelta(days=days_ago)
                    
                    # Random model and department
                    model_id = random.choice(model_ids)
                    department = random.choice(departments)
                    source_type = random.choice(source_types)
                    
                    # Random policy schema
                    policy_schema = random.choice([basic_policy, advanced_policy])
                    
                    # 70% chance of being valid
                    is_valid = random.random() < 0.7
                    
                    # Sample metadata
                    metadata = {
                        "model_id": model_id,
                        "department": department,
                    }
                    
                    # For advanced policy, add more fields
                    if policy_schema.id == advanced_policy.id:
                        metadata["purpose"] = f"Sample purpose for {model_id}"
                        metadata["data_sensitivity"] = random.choice(["low", "medium", "high"])
                        if random.random() < 0.7:  # 70% chance of including optional field
                            metadata["retention_period"] = random.randint(30, 365)
                    
                    # Errors if not valid
                    errors = []
                    if not is_valid:
                        if policy_schema.id == basic_policy.id:
                            if random.random() < 0.5:
                                errors.append("Missing required field: model_id")
                                metadata.pop("model_id", None)
                            else:
                                errors.append("Missing required field: department")
                                metadata.pop("department", None)
                        else:  # advanced policy
                            error_type = random.choice(["missing", "invalid_type", "invalid_value"])
                            if error_type == "missing":
                                field = random.choice(["model_id", "department", "purpose", "data_sensitivity"])
                                errors.append(f"Missing required field: {field}")
                                metadata.pop(field, None)
                            elif error_type == "invalid_type":
                                errors.append("Invalid type for field: retention_period (expected integer)")
                                metadata["retention_period"] = "not_an_integer"
                            else:  # invalid_value
                                errors.append("Invalid value for field: data_sensitivity (must be one of ['low', 'medium', 'high'])")
                                metadata["data_sensitivity"] = "extreme"
                    
                    # Create validation result
                    validation_result = PolicyValidationResult(
                        source=f"sample/path/to/document_{i}.pdf" if source_type == "file" else f"api/endpoint/{i}",
                        policy_schema_id=policy_schema.id,
                        is_valid=is_valid,
                        metadata=metadata,
                        errors=errors,
                        department=department,
                        source_type=source_type,
                        validation_time=validation_time
                    )
                    
                    db.add(validation_result)
                
                await db.commit()
                print("Sample policy validation results created.")
            
            print("Database initialization completed successfully.")
        except Exception as e:
            print(f"Error during database initialization: {e}")
            raise

async def main():
    await create_tables()
    await init_db()

if __name__ == "__main__":
    asyncio.run(main())
