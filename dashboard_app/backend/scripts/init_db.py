"""
Script to initialize the database with sample data for testing.
"""
import os
import sys
import json
from datetime import datetime, timedelta
import random

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.policy_validation import PolicySchema, PolicyValidationResult
from app.services.user import create_user

# Create all tables
Base.metadata.create_all(bind=engine)

def init_db() -> None:
    """Initialize the database with sample data."""
    db = SessionLocal()
    try:
        # Create sample users
        if db.query(User).count() == 0:
            print("Creating sample users...")
            create_user(
                db=db,
                username="admin",
                email="admin@encypherai.com",
                password="admin123",
                full_name="Admin User",
                is_superuser=True
            )
            
            create_user(
                db=db,
                username="user",
                email="user@encypherai.com",
                password="user123",
                full_name="Regular User",
                is_superuser=False
            )
            print("Sample users created.")
        
        # Create sample policy schemas
        if db.query(PolicySchema).count() == 0:
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
            db.commit()
            
            # Refresh to get IDs
            db.refresh(basic_policy)
            db.refresh(advanced_policy)
            print("Sample policy schemas created.")
        
        # Create sample audit logs
        if db.query(AuditLog).count() == 0:
            print("Creating sample audit logs...")
            # Get existing policy schemas
            basic_policy = db.query(PolicySchema).filter_by(name="Basic Metadata Policy").first()
            
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
            
            db.commit()
            print("Sample audit logs created.")
        
        # Create sample policy validation results
        if db.query(PolicyValidationResult).count() == 0:
            print("Creating sample policy validation results...")
            # Get existing policy schemas
            basic_policy = db.query(PolicySchema).filter_by(name="Basic Metadata Policy").first()
            advanced_policy = db.query(PolicySchema).filter_by(name="Advanced Metadata Policy").first()
            
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
            
            db.commit()
            print("Sample policy validation results created.")
        
        print("Database initialization completed successfully.")
    
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
