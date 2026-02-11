"""Usage metering router for billing integration."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_content_db, get_db
from app.dependencies import require_read_permission, require_super_admin_dep

router = APIRouter()


class UsageMetric(BaseModel):
    """Single usage metric with limit info."""

    name: str
    used: int
    limit: int  # -1 for unlimited
    remaining: int  # -1 for unlimited
    percentage_used: float
    available: bool


class UsageResponse(BaseModel):
    """Usage statistics response."""

    organization_id: str
    tier: str
    period_start: str
    period_end: str
    metrics: dict[str, UsageMetric]
    reset_date: str


class UsageResetResponse(BaseModel):
    """Response after resetting usage counters."""

    success: bool
    message: str
    organization_id: str
    reset_at: str


from app.core.tier_config import get_tier_limits as _get_tier_limits, coerce_tier_name as _coerce_tier


def _calculate_metric(used: int, limit: int, name: str) -> UsageMetric:
    """Calculate a usage metric with percentage and availability."""
    if limit == -1:
        return UsageMetric(
            name=name,
            used=used,
            limit=-1,
            remaining=-1,
            percentage_used=0.0,
            available=True,
        )
    elif limit == 0:
        return UsageMetric(
            name=name,
            used=used,
            limit=0,
            remaining=0,
            percentage_used=100.0 if used > 0 else 0.0,
            available=False,
        )
    else:
        remaining = max(0, limit - used)
        percentage = (used / limit) * 100 if limit > 0 else 0.0
        return UsageMetric(
            name=name,
            used=used,
            limit=limit,
            remaining=remaining,
            percentage_used=round(percentage, 2),
            available=used < limit,
        )


def _build_metric(metric_key: str, used: int, limit: int) -> UsageMetric:
    display_names = {
        "c2pa_signatures": "C2PA Signatures",
        "sentences_tracked": "Sentences Tracked",
        "batch_operations": "Batch Operations",
        "api_calls": "API Calls",
    }
    return _calculate_metric(used=used, limit=limit, name=display_names.get(metric_key, metric_key))


def _build_user_level_response(org_id: str, tier: str, limits: dict) -> UsageResponse:
    period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    period_end = period_start.replace(
        month=period_start.month + 1 if period_start.month < 12 else 1,
        year=period_start.year if period_start.month < 12 else period_start.year + 1,
    )

    # User-level keys are not tracked in DB; report zero usage with tier limits.
    return UsageResponse(
        organization_id=org_id,
        tier=tier,
        period_start=period_start.isoformat(),
        period_end=period_end.isoformat(),
        metrics={
            "c2pa_signatures": _build_metric("c2pa_signatures", 0, limits.get("c2pa_signatures", 0)),
            "sentences_tracked": _build_metric("sentences_tracked", 0, limits.get("sentences_tracked", 0)),
            "batch_operations": _build_metric("batch_operations", 0, limits.get("batch_operations", 0)),
            "api_calls": _build_metric("api_calls", 0, -1),
        },
        reset_date=period_end.date().isoformat(),
    )


async def _fetch_usage_counts(db: AsyncSession, content_db: AsyncSession, org_id: str) -> tuple[str, int, int, int, int, int]:
    result = await db.execute(
        text(
            """
            SELECT tier, monthly_api_usage, monthly_api_limit
            FROM organizations
            WHERE id = :org_id
            """
        ),
        {"org_id": org_id},
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    doc_result = await content_db.execute(text("SELECT COUNT(*) FROM documents WHERE organization_id = :org_id"), {"org_id": org_id})
    documents_signed = doc_result.scalar() or 0

    sent_result = await content_db.execute(text("SELECT COUNT(*) FROM sentence_records WHERE organization_id = :org_id"), {"org_id": org_id})
    sentences_tracked = sent_result.scalar() or 0

    batch_result = await db.execute(text("SELECT COUNT(*) FROM batch_requests WHERE organization_id = :org_id"), {"org_id": org_id})
    batch_operations = batch_result.scalar() or 0

    return (
        row.tier or "free",
        row.monthly_api_usage or 0,
        row.monthly_api_limit or 0,
        documents_signed,
        sentences_tracked,
        batch_operations,
    )


@router.get("/usage", response_model=UsageResponse)
async def get_usage_stats(
    organization: dict = Depends(require_read_permission),
    db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
) -> UsageResponse:
    """
    Get current period usage statistics for the organization.

    Returns usage metrics including:
    - C2PA signatures (documents signed)
    - Sentences tracked
    - Batch operations
    - API calls
    """
    org_id = organization["organization_id"]

    # Handle user-level keys (synthetic org IDs like "user_{user_id}")
    if org_id.startswith("user_"):
        tier = "free"
        limits = _get_tier_limits(tier)
        return _build_user_level_response(org_id, tier, limits)

    tier, api_calls, api_limit, documents_signed, sentences_tracked, batch_operations = await _fetch_usage_counts(db, content_db, org_id)
    tier = _coerce_tier(tier)
    limits = _get_tier_limits(tier)

    # Calculate period dates (monthly billing cycle)
    now = datetime.now(timezone.utc)
    period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        period_end = period_start.replace(year=now.year + 1, month=1)
    else:
        period_end = period_start.replace(month=now.month + 1)

    # Build metrics
    metrics = {
        "c2pa_signatures": _calculate_metric(
            used=documents_signed,
            limit=limits["c2pa_signatures"],
            name="C2PA Signatures",
        ),
        "sentences_tracked": _calculate_metric(
            used=sentences_tracked,
            limit=limits["sentences_tracked"],
            name="Sentences Tracked",
        ),
        "batch_operations": _calculate_metric(
            used=batch_operations,
            limit=limits["batch_operations"],
            name="Batch Operations",
        ),
        "api_calls": _calculate_metric(
            used=api_calls,
            limit=api_limit if api_limit != -1 else -1,
            name="API Calls",
        ),
    }

    return UsageResponse(
        organization_id=org_id,
        tier=tier,
        period_start=period_start.isoformat(),
        period_end=period_end.isoformat(),
        metrics=metrics,
        reset_date=period_end.isoformat(),
    )


@router.post(
    "/usage/reset",
    response_model=UsageResetResponse,
    tags=["Admin"],
)
async def reset_monthly_usage(
    organization: dict = Depends(require_super_admin_dep),
    db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
) -> UsageResetResponse:
    """
    Reset monthly usage counters.

    This is typically called by a scheduled job at the start of each billing period.
    Requires super admin permissions.
    """
    org_id = organization["organization_id"]
    now = datetime.now(timezone.utc)

    tier, api_calls, api_limit, documents_signed, sentences_tracked, batch_operations = await _fetch_usage_counts(db, content_db, org_id)
    period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        period_end = period_start.replace(year=now.year + 1, month=1)
    else:
        period_end = period_start.replace(month=now.month + 1)

    await db.execute(
        text(
            """
            INSERT INTO usage_history (
                organization_id, period_start, period_end,
                c2pa_signatures, sentences_tracked, batch_operations, api_calls
            ) VALUES (
                :org_id, :period_start, :period_end,
                :c2pa_signatures, :sentences_tracked, :batch_operations, :api_calls
            )
            """
        ),
        {
            "org_id": org_id,
            "period_start": period_start,
            "period_end": period_end,
            "c2pa_signatures": documents_signed,
            "sentences_tracked": sentences_tracked,
            "batch_operations": batch_operations,
            "api_calls": api_calls,
        },
    )

    # Reset monthly API usage counter
    await db.execute(
        text("""
            UPDATE organizations
            SET 
                monthly_api_usage = 0,
                updated_at = :updated_at
            WHERE id = :org_id
        """),
        {"org_id": org_id, "updated_at": now},
    )
    await db.commit()

    return UsageResetResponse(
        success=True,
        message="Monthly usage counters reset successfully",
        organization_id=org_id,
        reset_at=now.isoformat(),
    )


@router.get("/usage/history")
async def get_usage_history(
    months: int = Query(6, ge=1, le=24),
    organization: dict = Depends(require_read_permission),
    db: AsyncSession = Depends(get_db),
):
    """
    Get historical usage data for the organization.

    Returns monthly usage summaries for the specified number of months.
    """
    org_id = organization["organization_id"]

    if org_id.startswith("user_"):
        now = datetime.now(timezone.utc)
        history = []
        for i in range(months):
            month = now.month - i
            year = now.year
            if month <= 0:
                month += 12
                year -= 1
            history.append(
                {
                    "period": f"{year}-{month:02d}",
                    "c2pa_signatures": 0,
                    "sentences_tracked": 0,
                    "batch_operations": 0,
                    "api_calls": 0,
                }
            )
        return {"organization_id": org_id, "history": history}

    result = await db.execute(
        text(
            """
            SELECT period_start, c2pa_signatures, sentences_tracked, batch_operations, api_calls
            FROM usage_history
            WHERE organization_id = :org_id
            ORDER BY period_start DESC
            LIMIT :limit
            """
        ),
        {"org_id": org_id, "limit": months},
    )
    rows = result.fetchall()

    history = [
        {
            "period": f"{row.period_start.year}-{row.period_start.month:02d}",
            "c2pa_signatures": row.c2pa_signatures,
            "sentences_tracked": row.sentences_tracked,
            "batch_operations": row.batch_operations,
            "api_calls": row.api_calls,
        }
        for row in rows
    ]

    return {"organization_id": org_id, "history": history}
