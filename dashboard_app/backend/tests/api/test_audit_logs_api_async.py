"""
Async API tests for Audit Log endpoints.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# import tempfile # Not used yet
# import os # Not used yet
# import csv # Not used yet
# import json # Not used yet
from app.core.config import settings
from app.core.security import get_password_hash  # Corrected import for creating test user
from app.models.audit_log import AuditLog as AuditLogModel  # For creating test data
from app.models.user import User as UserModel

pytestmark = pytest.mark.asyncio

async def get_test_user_token(client: AsyncClient, db: AsyncSession) -> Dict[str, str]:
    print("Attempting to get test user token...")
    test_username = "testuser_api_token_helper@example.com" 
    test_password = "TestPassword123!"

    try:
        print(f"Checking/creating user: {test_username}")
        from sqlalchemy import select
        user = (await db.execute(select(UserModel).where(UserModel.email == test_username))).scalar_one_or_none()
        if not user:
            print(f"User {test_username} not found, creating...")
            hashed_password = get_password_hash(test_password)
            user = UserModel(email=test_username, hashed_password=hashed_password, is_active=True, is_superuser=False)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print(f"User {test_username} created.")
        else:
            print(f"User {test_username} found.")

        login_data = {
            "username": test_username,
            "password": test_password,
        }
        token_url = f"{settings.API_V1_STR}/auth/login"
        print(f"Attempting to login user {test_username} at {token_url}")
        response = await client.post(token_url, data=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Login failed! Status: {response.status_code}, Body: {response.text}")
            raise Exception(f"Could not log in test user. Status: {response.status_code}, Body: {response.text}")
        
        tokens = response.json()
        print(f"Login successful, token obtained for {test_username}: {tokens.get('access_token')[:20]}...")
        return {"Authorization": f"Bearer {tokens['access_token']}"}
    except Exception as e:
        print(f"Error in get_test_user_token: {e}")
        raise

async def create_test_audit_logs(db: AsyncSession, count: int = 5, department: str = "General", model_id_prefix: str = "model") -> List[AuditLogModel]:
    print(f"Creating {count} test audit logs for department {department}...")
    logs = []
    for i in range(count):
        log = AuditLogModel(
            source=f"test_source_api_{i}",
            is_verified=(i % 2 == 0),
            status="SUCCESS" if (i % 2 == 0) else "FAILURE",
            error_message="Test error" if (i % 2 != 0) else None,
            event_data={"detail": f"event_data_api_{i}", "value": i},
            verification_time=datetime.now(timezone.utc) - timedelta(days=i),
            model_id=f"{model_id_prefix}_{i}",
            department=department,
            source_type="API_TEST"
        )
        logs.append(log)
    db.add_all(logs)
    await db.commit()
    refreshed_logs = []
    for log_item in logs: 
        await db.refresh(log_item)
        refreshed_logs.append(log_item)
    print(f"Created {len(refreshed_logs)} test audit logs.")
    return refreshed_logs

# --- Test Cases Start Here ---

async def test_read_audit_logs_default_pagination(client: AsyncClient, db: AsyncSession) -> None:
    """Test GET /audit_logs/ with default pagination."""
    print("\n--- Starting test_read_audit_logs_default_pagination ---")
    headers = await get_test_user_token(client, db)
    initial_logs_count = 3 # Reduced for faster test
    print(f"Creating {initial_logs_count} initial logs for this test...")
    await create_test_audit_logs(db, count=initial_logs_count, department="API_Test_Dept_Paginate")
    print("Initial logs created for department API_Test_Dept_Paginate.")

    print(f"Making GET request to {settings.API_V1_STR}/audit-logs/")
    response = await client.get(f"{settings.API_V1_STR}/audit-logs/", headers=headers)
    print(f"GET /audit-logs/ response status: {response.status_code}")
    # print(f"GET /audit_logs/ response body: {response.text[:500]}...") # Log part of body if needed

    assert response.status_code == 200
    page_data = response.json()
    assert "items" in page_data
    assert "total" in page_data
    
    # To ensure test isolation, we should only count logs created by *this test instance*.
    # The best way is to filter by a unique characteristic, like the department.
    from sqlalchemy import func, select
    count_stmt = select(func.count(AuditLogModel.id)).where(AuditLogModel.department == "API_Test_Dept_Paginate")
    db_total_for_dept = (await db.execute(count_stmt)).scalar_one()
    print(f"DB count for department 'API_Test_Dept_Paginate': {db_total_for_dept}")
    print(f"API response total: {page_data['total']}, items count: {len(page_data['items'])}")

    assert page_data["total"] == db_total_for_dept, f"Expected total {db_total_for_dept} but got {page_data['total']}"
    # Default page size is 100, so if db_total_for_dept is less, items length will match db_total_for_dept
    assert len(page_data["items"]) == min(db_total_for_dept, 100), \
        f"Expected items length {min(db_total_for_dept, 100)} but got {len(page_data['items'])}"

    found_test_dept_logs_in_response = False
    for item in page_data["items"]:
        assert "source" in item
        if item["department"] == "API_Test_Dept_Paginate":
            found_test_dept_logs_in_response = True
    assert found_test_dept_logs_in_response, "Logs from 'API_Test_Dept_Paginate' were not found in the response items."
    print("--- Finished test_read_audit_logs_default_pagination ---")

# TODO: Test for GET / (read_audit_logs) - with filters and pagination
# TODO: Test for GET /stats (read_audit_log_stats)

async def test_read_single_audit_log(client: AsyncClient, db: AsyncSession) -> None:
    """Test GET /audit-logs/{audit_log_id} to retrieve a single audit log."""
    print("\n--- Starting test_read_single_audit_log ---")
    headers = await get_test_user_token(client, db)
    
    print("Creating a test audit log...")
    test_logs = await create_test_audit_logs(db, count=1, department="API_Test_Single_Log", model_id_prefix="single_test")
    assert len(test_logs) == 1
    test_log = test_logs[0]
    print(f"Test log created with ID: {test_log.id}, Source: {test_log.source}")

    print(f"Making GET request to {settings.API_V1_STR}/audit-logs/{test_log.id}")
    response = await client.get(f"{settings.API_V1_STR}/audit-logs/{test_log.id}", headers=headers)
    print(f"GET /audit-logs/{test_log.id} response status: {response.status_code}")

    assert response.status_code == 200
    retrieved_log_data = response.json()
    
    assert retrieved_log_data["id"] == test_log.id
    assert retrieved_log_data["source"] == test_log.source
    assert retrieved_log_data["department"] == "API_Test_Single_Log"
    assert retrieved_log_data["model_id"] == "single_test_0"
    assert retrieved_log_data["is_verified"] == test_log.is_verified # (0 % 2 == 0) -> True

    # Test retrieving a non-existent log ID
    non_existent_id = 999999
    print(f"Making GET request for non-existent ID: {settings.API_V1_STR}/audit-logs/{non_existent_id}")
    response_not_found = await client.get(f"{settings.API_V1_STR}/audit-logs/{non_existent_id}", headers=headers)
    print(f"GET /audit-logs/{non_existent_id} response status: {response_not_found.status_code}")
    assert response_not_found.status_code == 404
    print("--- Finished test_read_single_audit_log ---")

async def test_create_new_audit_log(client: AsyncClient, db: AsyncSession) -> None:
    """Test POST /audit-logs/ to create a new audit log."""
    print("\n--- Starting test_create_new_audit_log ---")
    headers = await get_test_user_token(client, db)

    log_create_data = {
        "source": "api_test_creation_source",
        "is_verified": True,
        "status": "SUCCESS",
        "event_data": {"action": "create", "details": "test log created via API"},
        "verification_time": datetime.now(timezone.utc).isoformat(), # Ensure ISO format
        "model_id": "model_created_via_api",
        "department": "API_Test_Create_Dept",
        "source_type": "API_DIRECT_CREATE"
    }

    print(f"Making POST request to {settings.API_V1_STR}/audit-logs/ with data: {log_create_data}")
    response = await client.post(f"{settings.API_V1_STR}/audit-logs/", headers=headers, json=log_create_data)
    print(f"POST /audit-logs/ response status: {response.status_code}")
    # print(f"POST /audit-logs/ response body: {response.text}")

    assert response.status_code == 201 # Check for 201 Created status
    created_log_data = response.json()

    assert "id" in created_log_data
    assert created_log_data["source"] == log_create_data["source"]
    assert created_log_data["is_verified"] == log_create_data["is_verified"]
    assert created_log_data["status"] == log_create_data["status"]
    assert created_log_data["event_data"] == log_create_data["event_data"]
    assert created_log_data["model_id"] == log_create_data["model_id"]
    assert created_log_data["department"] == log_create_data["department"]
    assert created_log_data["source_type"] == log_create_data["source_type"]
    
    # Verification time might have slight precision differences, check it's close or parse and compare date part
    # For now, let's check it's a valid datetime string
    print(f"Debug: created_log_data raw: {created_log_data}")
    print(f"Debug: verification_time type: {type(created_log_data.get('verification_time'))}, value: {created_log_data.get('verification_time')}")
    print(f"Debug: created_at type: {type(created_log_data.get('created_at'))}, value: {created_log_data.get('created_at')}")
    print(f"Debug: updated_at type: {type(created_log_data.get('updated_at'))}, value: {created_log_data.get('updated_at')}")

    # Verification time should be a string as it was part of the input or set by server
    assert isinstance(created_log_data["verification_time"], str)
    assert datetime.fromisoformat(created_log_data["verification_time"])
    
    assert "created_at" in created_log_data
    assert isinstance(created_log_data["created_at"], str)
    assert datetime.fromisoformat(created_log_data["created_at"])

    assert "updated_at" in created_log_data
    if created_log_data["updated_at"] is not None:
        assert isinstance(created_log_data["updated_at"], str)
        assert datetime.fromisoformat(created_log_data["updated_at"])
    # If updated_at is None, it's acceptable for a newly created record.

    # Optionally, verify by fetching the created log
    created_log_id = created_log_data["id"]
    print(f"Debug: created_log_id: {created_log_id}, type: {type(created_log_id)}")
    fetch_url = f"{settings.API_V1_STR}/audit-logs/{created_log_id}"
    print(f"Debug: Fetching created log by ID using URL: {fetch_url}")
    get_response = await client.get(fetch_url, headers=headers)
    print(f"Debug: GET response status for {fetch_url}: {get_response.status_code}")
    if get_response.status_code != 200:
        print(f"Debug: GET response body for {fetch_url}: {get_response.text}")
    assert get_response.status_code == 200
    fetched_log_data = get_response.json()
    assert fetched_log_data["source"] == log_create_data["source"]
    print("--- Finished test_create_new_audit_log ---")

# TODO: Test for POST /import-csv/ (import_audit_logs_from_csv_file)

async def test_dummy_api_test(client: AsyncClient) -> None:
    """A dummy test to check basic client functionality and app responsiveness."""
    print("Running dummy API test...")
    try:
        # Using /docs as it's a known, simple, unauthenticated endpoint.
        response = await client.get("/docs") 
        print(f"Dummy test response status for /docs: {response.status_code}")
        assert response.status_code == 200 # /docs should return 200 if app is serving correctly
        print("Dummy API test for /docs passed.")
    except Exception as e:
        print(f"Dummy test EXCEPTION: {e}")
        assert False, f"Dummy test failed with exception: {e}"


