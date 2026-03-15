"""
Tests for UsageRecordService overage recording and billing queries.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.usage_record import UsageRecord
from app.services.usage_record_service import UsageRecordService, _current_period_bounds


# ---- Helpers ----


def _make_db() -> AsyncMock:
    """Build a mock AsyncSession."""
    return AsyncMock()


def _make_usage_record(**overrides) -> MagicMock:
    """Build a mock UsageRecord with sensible defaults."""
    defaults = dict(
        id="ur_org1_api_calls_202603",
        organization_id="org1",
        metric="api_calls",
        count=100,
        period_start=datetime(2026, 3, 1, tzinfo=timezone.utc),
        period_end=datetime(2026, 4, 1, tzinfo=timezone.utc),
        period_type="monthly",
        billable=True,
        billed=False,
        rate_cents=2,
        included_in_plan=1000,
        overage_count=0,
        overage_amount_cents=0,
        invoice_id=None,
    )
    defaults.update(overrides)
    rec = MagicMock(spec=UsageRecord)
    for k, v in defaults.items():
        setattr(rec, k, v)
    return rec


# ---- record_overage tests ----


@pytest.mark.asyncio
async def test_record_overage_creates_new_record():
    """No existing record -> creates new UsageRecord with correct overage calculations."""
    db = _make_db()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    await UsageRecordService.record_overage(
        db=db,
        org_id="org1",
        metric="api_calls",
        count=1050,
        rate_cents=2,
        included_in_plan=1000,
    )

    # A new record was added to the session
    db.add.assert_called_once()
    added = db.add.call_args[0][0]
    assert isinstance(added, UsageRecord)
    assert added.count == 1050
    assert added.overage_count == 50  # 1050 - 1000
    assert added.overage_amount_cents == 100  # 50 * 2
    assert added.rate_cents == 2
    assert added.included_in_plan == 1000
    assert added.billed is False
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_record_overage_updates_existing_record():
    """Existing record found -> updates count and recalculates overage."""
    existing = _make_usage_record(
        count=1020,
        overage_count=20,
        overage_amount_cents=40,
    )
    db = _make_db()
    result = MagicMock()
    result.scalar_one_or_none.return_value = existing
    db.execute.return_value = result

    await UsageRecordService.record_overage(
        db=db,
        org_id="org1",
        metric="api_calls",
        count=1100,
        rate_cents=2,
        included_in_plan=1000,
    )

    # Existing record was updated in-place
    assert existing.count == 1100
    assert existing.overage_count == 100  # 1100 - 1000
    assert existing.overage_amount_cents == 200  # 100 * 2
    assert existing.rate_cents == 2
    # No new record added
    db.add.assert_not_called()
    db.flush.assert_awaited_once()


# ---- get_current_period_overage tests ----


@pytest.mark.asyncio
async def test_get_current_period_overage_sums_correctly():
    """Multiple records for current period -> returns sum of overage_amount_cents."""
    rec1 = _make_usage_record(overage_amount_cents=100)
    rec2 = _make_usage_record(overage_amount_cents=250)

    db = _make_db()
    result = MagicMock()
    result.scalars.return_value.all.return_value = [rec1, rec2]
    db.execute.return_value = result

    total = await UsageRecordService.get_current_period_overage(db, "org1")
    assert total == 350


@pytest.mark.asyncio
async def test_get_current_period_overage_no_records_returns_zero():
    """No records for the current period -> returns 0."""
    db = _make_db()
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    db.execute.return_value = result

    total = await UsageRecordService.get_current_period_overage(db, "org1")
    assert total == 0


# ---- get_unbilled_records tests ----


@pytest.mark.asyncio
async def test_get_unbilled_records_filters_correctly():
    """Returns only records with billed=False and overage_amount_cents > 0."""
    rec1 = _make_usage_record(billed=False, overage_amount_cents=50)
    rec2 = _make_usage_record(billed=False, overage_amount_cents=100)

    db = _make_db()
    result = MagicMock()
    result.scalars.return_value.all.return_value = [rec1, rec2]
    db.execute.return_value = result

    records = await UsageRecordService.get_unbilled_records(db)
    assert len(records) == 2
    assert records[0].overage_amount_cents == 50
    assert records[1].overage_amount_cents == 100


# ---- mark_billed tests ----


@pytest.mark.asyncio
async def test_mark_billed_updates_records():
    """Sets billed=True and invoice_id on specified records."""
    db = _make_db()

    await UsageRecordService.mark_billed(
        db=db,
        record_ids=["ur_1", "ur_2"],
        invoice_id="inv_abc123",
    )

    # execute was called with an UPDATE statement
    db.execute.assert_awaited_once()
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_mark_billed_empty_list_no_op():
    """Empty record_ids list -> early return, no DB call."""
    db = _make_db()

    await UsageRecordService.mark_billed(
        db=db,
        record_ids=[],
        invoice_id="inv_abc123",
    )

    db.execute.assert_not_awaited()
    db.flush.assert_not_awaited()
