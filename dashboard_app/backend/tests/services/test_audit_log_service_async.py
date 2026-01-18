import csv
import os
import tempfile
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogCreate, AuditLogFilters
from app.services.audit_log import (
    create_audit_log,
    get_audit_log_by_id,
    get_audit_log_stats,
    get_audit_logs,
    import_audit_log_from_csv,
)

pytestmark = pytest.mark.asyncio


async def test_create_audit_log(db: AsyncSession) -> None:
    """Test creating an audit log entry."""
    log_create_data = AuditLogCreate(
        source="test_source_create",
        is_verified=True,
        status="SUCCESS",
        event_data={"action": "USER_LOGIN", "ip_address": "127.0.0.1", "user_id": "test_user_create"},
        model_id="model_abc_123",
        source_type="API",
        department="Security",
    )
    created_log = await create_audit_log(db, audit_log_in=log_create_data)

    assert created_log is not None
    assert created_log.id is not None
    assert created_log.source == log_create_data.source
    assert created_log.is_verified == log_create_data.is_verified
    assert created_log.status == log_create_data.status
    assert created_log.event_data == log_create_data.event_data
    assert created_log.model_id == log_create_data.model_id
    assert created_log.source_type == log_create_data.source_type
    assert created_log.department == log_create_data.department
    assert created_log.verification_time is not None  # Should be set by server_default
    assert created_log.created_at is not None  # Should be set by server_default
    # updated_at might be None on creation depending on DB and SQLAlchemy version behavior for onupdate


async def test_get_audit_log_by_id_existing(db: AsyncSession) -> None:
    """Test retrieving an existing audit log by ID."""
    log_create_data = AuditLogCreate(
        source="test_source_get_existing",
        is_verified=False,
        status="INFO",
        event_data={"action": "ITEM_VIEWED", "item_id": "xyz789"},
        model_id="model_def_456",
        source_type="BACKGROUND_TASK",
        department="Analytics",
    )
    created_log = await create_audit_log(db, audit_log_in=log_create_data)
    assert created_log.id is not None

    retrieved_log = await get_audit_log_by_id(db, audit_log_id=created_log.id)
    assert retrieved_log is not None
    assert retrieved_log.id == created_log.id
    assert retrieved_log.source == log_create_data.source
    assert retrieved_log.status == log_create_data.status
    assert retrieved_log.event_data == log_create_data.event_data


async def test_get_audit_log_by_id_non_existing(db: AsyncSession) -> None:
    """Test retrieving a non-existing audit log by ID."""
    retrieved_log = await get_audit_log_by_id(db, audit_log_id=999999)  # Assuming this ID won't exist
    assert retrieved_log is None


async def test_get_audit_logs_no_filters(db: AsyncSession) -> None:
    """Test retrieving audit logs without any filters."""
    log1_data = AuditLogCreate(
        source="test_source_get_logs_1",
        is_verified=True,
        status="SUCCESS",
        event_data={"action": "DATA_EXPORT"},
        model_id="model_log_1",
        department="Ops",
    )
    log2_data = AuditLogCreate(
        source="test_source_get_logs_2",
        is_verified=False,
        status="FAILURE",
        event_data={"action": "DATA_IMPORT", "error": "timeout"},
        model_id="model_log_2",
        department="Dev",
    )
    await create_audit_log(db, audit_log_in=log1_data)
    await create_audit_log(db, audit_log_in=log2_data)

    # Ensure some time passes for distinct created_at if filtering by time later
    # For this test, not strictly necessary but good practice if we extend it.

    logs, total_count = await get_audit_logs(db, filters=AuditLogFilters(), skip=0, limit=10)

    assert total_count == 2  # Expecting exactly 2 logs created in this test
    assert len(logs) == 2

    found_log1 = any(log.source == "test_source_get_logs_1" for log in logs)
    found_log2 = any(log.source == "test_source_get_logs_2" for log in logs)
    assert found_log1, "Log 1 not found in results without filters"
    assert found_log2, "Log 2 not found in results without filters"


async def test_get_audit_logs_with_filters(db: AsyncSession) -> None:
    """Test retrieving audit logs with various filters."""
    # Create a diverse set of logs
    log_data_list = [
        AuditLogCreate(
            source="filter_src_1",
            is_verified=True,
            status="SUCCESS",
            event_data={"action": "login"},
            model_id="model_A",
            department="HR",
            source_type="API",
        ),
        AuditLogCreate(
            source="filter_src_2",
            is_verified=False,
            status="FAILURE",
            event_data={"action": "upload"},
            model_id="model_B",
            department="Finance",
            source_type="UI",
        ),
        AuditLogCreate(
            source="filter_src_3",
            is_verified=True,
            status="SUCCESS",
            event_data={"action": "report"},
            model_id="model_A",
            department="HR",
            source_type="Scheduled",
        ),
        AuditLogCreate(
            source="filter_src_4",
            is_verified=True,
            status="PENDING",
            event_data={"action": "verify"},
            model_id="model_C",
            department="Support",
            source_type="API",
        ),
    ]
    created_logs = []
    for data in log_data_list:
        created_logs.append(await create_audit_log(db, audit_log_in=data))

    # Wait a moment to ensure created_at timestamps are distinct if needed for time-based filtering
    # For these specific filters, not critical, but good for future-proofing.

    # Filter by status
    logs_success, count_success = await get_audit_logs(db, filters=AuditLogFilters(status="SUCCESS"), skip=0, limit=10)
    assert count_success == 2  # Expecting 2 'SUCCESS' logs from the initial set
    assert len(logs_success) == 2
    assert all(log.status == "SUCCESS" for log in logs_success)
    assert any(log.source == "filter_src_1" for log in logs_success)
    assert any(log.source == "filter_src_3" for log in logs_success)

    # Filter by model_id
    logs_model_A, count_model_A = await get_audit_logs(db, filters=AuditLogFilters(model_id="model_A"), skip=0, limit=10)
    assert count_model_A == 2  # Expecting 2 'model_A' logs from the initial set
    assert len(logs_model_A) == 2
    assert all(log.model_id == "model_A" for log in logs_model_A)

    # Filter by department
    logs_hr, count_hr = await get_audit_logs(db, filters=AuditLogFilters(department="HR"), skip=0, limit=10)
    assert count_hr == 2  # Expecting 2 'HR' logs from the initial set
    assert len(logs_hr) == 2
    assert all(log.department == "HR" for log in logs_hr)

    # Filter by source_type
    logs_api, count_api = await get_audit_logs(db, filters=AuditLogFilters(source_type="API"), skip=0, limit=10)
    assert count_api == 2  # Expecting 2 'API' logs from the initial set
    assert len(logs_api) == 2
    assert all(log.source_type == "API" for log in logs_api)

    # Filter by a combination
    logs_combo, count_combo = await get_audit_logs(db, filters=AuditLogFilters(status="SUCCESS", department="HR"), skip=0, limit=10)
    assert count_combo == 2  # Expecting 2 'SUCCESS' and 'HR' logs from the initial set
    assert len(logs_combo) == 2
    assert all(log.status == "SUCCESS" and log.department == "HR" for log in logs_combo)

    # Filter yielding no results
    logs_none, count_none = await get_audit_logs(db, filters=AuditLogFilters(status="NON_EXISTENT_STATUS"), skip=0, limit=10)
    assert count_none == 0
    assert len(logs_none) == 0

    # Test pagination (skip and limit)
    # Assuming we have at least 3 logs with model_A (we have 2 from above)
    # Let's add one more to make pagination more meaningful for this specific filter
    await create_audit_log(
        db,
        AuditLogCreate(
            source="filter_src_5_model_A", is_verified=True, status="SUCCESS", event_data={"action": "extra"}, model_id="model_A", department="HR"
        ),
    )

    all_model_a_logs, total_model_a = await get_audit_logs(db, filters=AuditLogFilters(model_id="model_A"), skip=0, limit=10)
    assert total_model_a == 3  # Now we have 3

    logs_page1, count_page1 = await get_audit_logs(db, filters=AuditLogFilters(model_id="model_A"), skip=0, limit=2)
    assert count_page1 == 3  # Total count remains the same
    assert len(logs_page1) == 2

    logs_page2, count_page2 = await get_audit_logs(db, filters=AuditLogFilters(model_id="model_A"), skip=2, limit=2)
    assert count_page2 == 3
    assert len(logs_page2) == 1  # Only one remaining


async def test_get_audit_log_stats_no_filters(db: AsyncSession) -> None:
    """Test audit log statistics without any filters."""
    # Clear previous logs for accurate stats or ensure test DB is clean per test
    # For now, assuming a relatively clean state or that other tests don't interfere significantly
    # with these specific stats. A dedicated setup/teardown per test or class would be more robust.

    log_data_list = [
        AuditLogCreate(
            source="stats_src_1",
            is_verified=True,
            status="VERIFIED",
            event_data={"action": "login"},
            model_id="model_X",
            department="Sales",
            source_type="API",
        ),
        AuditLogCreate(
            source="stats_src_2",
            is_verified=False,
            status="UNVERIFIED",
            event_data={"action": "upload"},
            model_id="model_Y",
            department="Marketing",
            source_type="UI",
        ),
        AuditLogCreate(
            source="stats_src_3",
            is_verified=True,
            status="VERIFIED",
            event_data={"action": "report"},
            model_id="model_X",
            department="Sales",
            source_type="Scheduled",
        ),
        AuditLogCreate(
            source="stats_src_4",
            is_verified=False,
            status="ERROR",
            event_data={"action": "verify"},
            model_id="model_Z",
            department="Support",
            source_type="API",
        ),
        AuditLogCreate(
            source="stats_src_5",
            is_verified=True,
            status="VERIFIED",
            event_data={"action": "download"},
            model_id="model_X",
            department="Sales",
            source_type="UI",
        ),
    ]
    for data in log_data_list:
        await create_audit_log(db, audit_log_in=data)

    stats = await get_audit_log_stats(db, filters=AuditLogFilters())

    assert stats.total_documents == 5
    assert stats.verified_count == 3
    assert stats.unverified_count == 1  # Based on status="UNVERIFIED"
    assert stats.error_count == 1  # Based on status="ERROR"
    assert stats.verification_rate == (3 / 5) * 100
    assert stats.model_usage == {"model_X": 3, "model_Y": 1, "model_Z": 1}
    assert stats.department_stats == {"Sales": 3, "Marketing": 1, "Support": 1}


async def test_get_audit_log_stats_with_filters(db: AsyncSession) -> None:
    """Test audit log statistics with various filters."""
    # Logs created in test_get_audit_log_stats_no_filters will be present if tests run sequentially in the same session
    # and DB is not cleared. For robust independent tests, create specific data here.
    # To simplify, we'll assume the data from the previous test is available or re-create similar, specific data.
    # For this example, let's create specific data to ensure independence.

    # First, ensure a clean slate or known state if possible. Here, we add new, distinct logs.
    log_data_list_filtered_test = [
        AuditLogCreate(
            source="stats_filter_1",
            is_verified=True,
            status="VERIFIED",
            event_data={"key": "val"},
            model_id="model_F1",
            department="Finance",
            source_type="API",
        ),
        AuditLogCreate(
            source="stats_filter_2",
            is_verified=False,
            status="UNVERIFIED",
            event_data={"key": "val"},
            model_id="model_F2",
            department="Finance",
            source_type="UI",
        ),
        AuditLogCreate(
            source="stats_filter_3",
            is_verified=True,
            status="VERIFIED",
            event_data={"key": "val"},
            model_id="model_F1",
            department="Finance",
            source_type="API",
        ),
    ]
    for data in log_data_list_filtered_test:
        await create_audit_log(db, audit_log_in=data)

    # Filter by department "Finance"
    stats_finance = await get_audit_log_stats(db, filters=AuditLogFilters(department="Finance"))
    assert stats_finance.total_documents == 3
    assert stats_finance.verified_count == 2
    assert stats_finance.unverified_count == 1
    assert stats_finance.error_count == 0
    assert stats_finance.verification_rate == (2 / 3) * 100
    assert stats_finance.model_usage == {"model_F1": 2, "model_F2": 1}
    assert stats_finance.department_stats == {"Finance": 3}

    # Filter by model_id "model_F1"
    stats_model_f1 = await get_audit_log_stats(db, filters=AuditLogFilters(model_id="model_F1"))
    assert stats_model_f1.total_documents == 2
    assert stats_model_f1.verified_count == 2
    assert stats_model_f1.unverified_count == 0
    assert stats_model_f1.error_count == 0
    assert stats_model_f1.verification_rate == 100.0
    assert stats_model_f1.model_usage == {"model_F1": 2}
    # Department stats will reflect only logs matching model_F1
    assert stats_model_f1.department_stats == {"Finance": 2}

    # Filter by status "VERIFIED" and department "Finance"
    stats_verified_finance = await get_audit_log_stats(db, filters=AuditLogFilters(status="VERIFIED", department="Finance"))
    assert stats_verified_finance.total_documents == 2
    assert stats_verified_finance.verified_count == 2
    assert stats_verified_finance.unverified_count == 0
    assert stats_verified_finance.error_count == 0
    assert stats_verified_finance.verification_rate == 100.0
    assert stats_verified_finance.model_usage == {"model_F1": 2}
    assert stats_verified_finance.department_stats == {"Finance": 2}

    # Filter yielding no results
    stats_none = await get_audit_log_stats(db, filters=AuditLogFilters(department="NonExistentDept"))
    assert stats_none.total_documents == 0
    assert stats_none.verified_count == 0
    assert stats_none.unverified_count == 0
    assert stats_none.error_count == 0
    assert stats_none.verification_rate == 0.0
    assert stats_none.model_usage == {}
    assert stats_none.department_stats == {}


def _create_temp_csv_file(headers: list[str], rows: list[dict], directory: str = None) -> str:
    """Helper to create a temporary CSV file and return its path."""
    # Ensure the directory exists if specified, otherwise use default temp dir
    if directory:
        os.makedirs(directory, exist_ok=True)
        delete_on_close = False  # We'll manually delete if a directory is specified
    else:
        delete_on_close = False  # We will manually delete in tests to ensure service can read it

    temp_file = tempfile.NamedTemporaryFile(mode="w+", delete=delete_on_close, newline="", encoding="utf-8", suffix=".csv", dir=directory)
    writer = csv.DictWriter(temp_file, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    temp_file_path = temp_file.name
    temp_file.close()  # Close the file so the service function can open it (especially on Windows)
    return temp_file_path


async def test_import_audit_log_from_csv_success(db: AsyncSession) -> None:
    """Test successful import of audit logs from a valid CSV file."""
    headers = ["Source", "Is Verified", "Status", "Model ID", "Department", "Verification Time", "Custom Info", "Numeric Detail"]
    row_data = [
        {
            "Source": "csv_import_1",
            "Is Verified": "true",
            "Status": "SUCCESS",
            "Model ID": "model_csv_A",
            "Department": "Dept_CSV_1",
            "Verification Time": datetime.now().isoformat(),
            "Custom Info": "Some textual data",
            "Numeric Detail": '{"value": 123}',
        },
        {
            "Source": "csv_import_2",
            "Is Verified": "false",
            "Status": "FAILURE",
            "Model ID": "model_csv_B",
            "Department": "Dept_CSV_2",
            "Verification Time": (datetime.now() - timedelta(days=1)).isoformat(),
            "Custom Info": "More data",
            "Numeric Detail": '{"value": 456}',
        },
    ]
    temp_csv_path = _create_temp_csv_file(headers, row_data)

    try:
        imported_count = await import_audit_log_from_csv(db, temp_csv_path)
        assert imported_count == 2

        # Verify logs in DB
        result = await db.execute(select(AuditLog).where(AuditLog.source.like("csv_import_%")))
        logs_in_db = result.scalars().all()
        assert len(logs_in_db) == 2

        log1 = next(l for l in logs_in_db if l.source == "csv_import_1")
        assert log1.is_verified is True
        assert log1.status == "SUCCESS"
        assert log1.model_id == "model_csv_A"
        assert log1.department == "Dept_CSV_1"
        assert log1.event_data.get("custom_info") == "Some textual data"
        assert log1.event_data.get("numeric_detail") == {"value": 123}  # Parsed as JSON

        log2 = next(l for l in logs_in_db if l.source == "csv_import_2")
        assert log2.is_verified is False
        assert log2.status == "FAILURE"
        assert log2.event_data.get("numeric_detail") == {"value": 456}

    finally:
        os.unlink(temp_csv_path)


async def test_import_audit_log_from_csv_event_data_handling(db: AsyncSession) -> None:
    """Test how event_data is handled (JSON vs. plain string)."""
    headers = ["Source", "Json Data", "Plain Data"]
    row_data = [{"Source": "event_test_1", "Json Data": '{"key": "value", "num": 1}', "Plain Data": "Just a string"}]
    temp_csv_path = _create_temp_csv_file(headers, row_data)
    try:
        imported_count = await import_audit_log_from_csv(db, temp_csv_path)
        assert imported_count == 1
        log = (await db.execute(select(AuditLog).where(AuditLog.source == "event_test_1"))).scalar_one()
        assert log.event_data["json_data"] == {"key": "value", "num": 1}
        assert log.event_data["plain_data"] == "Just a string"
    finally:
        os.unlink(temp_csv_path)


async def test_import_audit_log_from_csv_verification_time_handling(db: AsyncSession) -> None:
    """Test handling of verification_time: valid, empty, invalid."""
    now = datetime.now()
    valid_time_str = (now - timedelta(hours=1)).isoformat()
    headers = ["Source", "Verification Time"]
    row_data = [
        {"Source": "vt_valid", "Verification Time": valid_time_str},
        {"Source": "vt_empty", "Verification Time": ""},
        {"Source": "vt_invalid", "Verification Time": "not-a-date"},
    ]
    temp_csv_path = _create_temp_csv_file(headers, row_data)
    try:
        imported_count = await import_audit_log_from_csv(db, temp_csv_path)
        assert imported_count == 3

        log_valid = (await db.execute(select(AuditLog).where(AuditLog.source == "vt_valid"))).scalar_one()
        assert log_valid.verification_time.isoformat().startswith(valid_time_str.split(".")[0])  # Compare without microseconds for safety

        log_empty = (await db.execute(select(AuditLog).where(AuditLog.source == "vt_empty"))).scalar_one()
        assert (datetime.now() - log_empty.verification_time).total_seconds() < 5  # Should be recent

        log_invalid = (await db.execute(select(AuditLog).where(AuditLog.source == "vt_invalid"))).scalar_one()
        assert (datetime.now() - log_invalid.verification_time).total_seconds() < 5  # Should be recent (fallback)
    finally:
        os.unlink(temp_csv_path)


async def test_import_audit_log_from_csv_empty_and_header_only(db: AsyncSession) -> None:
    """Test importing an empty CSV and a CSV with only headers."""
    # Empty CSV
    temp_empty_csv_path = _create_temp_csv_file([], [])
    try:
        imported_count_empty = await import_audit_log_from_csv(db, temp_empty_csv_path)
        assert imported_count_empty == 0
    finally:
        os.unlink(temp_empty_csv_path)

    # CSV with only headers
    headers = ["Source", "Status"]
    temp_header_only_csv_path = _create_temp_csv_file(headers, [])
    try:
        imported_count_header = await import_audit_log_from_csv(db, temp_header_only_csv_path)
        assert imported_count_header == 0
    finally:
        os.unlink(temp_header_only_csv_path)
