"""
Service for recording and querying usage/overage data.

Operates on the UsageRecord ORM model for metering and billing reconciliation.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usage_record import UsageRecord

logger = logging.getLogger(__name__)


def _current_period_bounds() -> tuple[datetime, datetime]:
    """Return (period_start, period_end) for the current calendar month in UTC."""
    now = datetime.now(timezone.utc)
    period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        period_end = period_start.replace(year=now.year + 1, month=1)
    else:
        period_end = period_start.replace(month=now.month + 1)
    return period_start, period_end


class UsageRecordService:
    """Async static methods for usage record CRUD."""

    @staticmethod
    async def record_overage(
        db: AsyncSession,
        org_id: str,
        metric: str,
        count: int,
        rate_cents: int,
        included_in_plan: int,
    ) -> None:
        """Upsert the current month's usage record for org+metric with overage info."""
        period_start, period_end = _current_period_bounds()
        period_key = period_start.strftime("%Y%m")
        record_id = f"ur_{org_id}_{metric}_{period_key}"

        result = await db.execute(select(UsageRecord).where(UsageRecord.id == record_id))
        record = result.scalar_one_or_none()

        if record is None:
            overage_count = max(0, count - included_in_plan)
            record = UsageRecord(
                id=record_id,
                organization_id=org_id,
                metric=metric,
                count=count,
                period_start=period_start,
                period_end=period_end,
                period_type="monthly",
                billable=True,
                billed=False,
                rate_cents=rate_cents,
                included_in_plan=included_in_plan,
                overage_count=overage_count,
                overage_amount_cents=overage_count * rate_cents,
                recorded_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
            )
            db.add(record)
        else:
            record.count = count
            overage_count = max(0, count - included_in_plan)
            record.overage_count = overage_count
            record.overage_amount_cents = overage_count * rate_cents
            record.rate_cents = rate_cents
            record.included_in_plan = included_in_plan
            record.recorded_at = datetime.now(timezone.utc)

        await db.flush()

    @staticmethod
    async def get_current_period_overage(db: AsyncSession, org_id: str) -> int:
        """Return total overage_amount_cents for the current billing period across all metrics."""
        period_start, period_end = _current_period_bounds()

        result = await db.execute(
            select(UsageRecord).where(
                UsageRecord.organization_id == org_id,
                UsageRecord.period_start == period_start,
                UsageRecord.period_end == period_end,
            )
        )
        records = result.scalars().all()
        return sum(r.overage_amount_cents or 0 for r in records)

    @staticmethod
    async def get_unbilled_records(db: AsyncSession) -> list[UsageRecord]:
        """Return all UsageRecord where billed=False and overage_amount_cents > 0."""
        result = await db.execute(
            select(UsageRecord).where(
                UsageRecord.billed == False,  # noqa: E712
                UsageRecord.overage_amount_cents > 0,
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def mark_billed(db: AsyncSession, record_ids: list[str], invoice_id: str) -> None:
        """Set billed=True and invoice_id on matching records."""
        if not record_ids:
            return
        await db.execute(update(UsageRecord).where(UsageRecord.id.in_(record_ids)).values(billed=True, invoice_id=invoice_id))
        await db.flush()
