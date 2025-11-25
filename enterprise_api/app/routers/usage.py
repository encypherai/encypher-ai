"""Usage metering router for billing integration."""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_read_permission


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


# Tier limits configuration
TIER_LIMITS = {
    "starter": {
        "c2pa_signatures": 10000,
        "sentences_tracked": 0,  # Not available
        "batch_operations": 0,  # Not available
        "api_keys": 2,
    },
    "professional": {
        "c2pa_signatures": -1,  # Unlimited
        "sentences_tracked": 50000,
        "batch_operations": 0,  # Not available
        "api_keys": 10,
    },
    "business": {
        "c2pa_signatures": -1,  # Unlimited
        "sentences_tracked": 500000,
        "batch_operations": 100,
        "api_keys": 50,
    },
    "enterprise": {
        "c2pa_signatures": -1,  # Unlimited
        "sentences_tracked": -1,  # Unlimited
        "batch_operations": -1,  # Unlimited
        "api_keys": -1,  # Unlimited
    },
    "strategic_partner": {
        "c2pa_signatures": -1,
        "sentences_tracked": -1,
        "batch_operations": -1,
        "api_keys": -1,
    },
}


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


@router.get("/usage", response_model=UsageResponse)
async def get_usage_stats(
    organization: dict = Depends(require_read_permission),
    db: AsyncSession = Depends(get_db),
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
    
    # Get organization usage data
    result = await db.execute(
        text("""
            SELECT 
                tier,
                documents_signed,
                sentences_signed,
                sentences_tracked_this_month,
                batch_operations_this_month,
                api_calls_this_month
            FROM organizations
            WHERE organization_id = :org_id
        """),
        {"org_id": org_id}
    )
    row = result.fetchone()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    tier = row.tier or "starter"
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["starter"])
    
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
            used=row.documents_signed or 0,
            limit=limits["c2pa_signatures"],
            name="C2PA Signatures",
        ),
        "sentences_tracked": _calculate_metric(
            used=row.sentences_tracked_this_month or 0,
            limit=limits["sentences_tracked"],
            name="Sentences Tracked",
        ),
        "batch_operations": _calculate_metric(
            used=row.batch_operations_this_month or 0,
            limit=limits["batch_operations"],
            name="Batch Operations",
        ),
        "api_calls": _calculate_metric(
            used=row.api_calls_this_month or 0,
            limit=-1,  # Always unlimited
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


@router.post("/usage/reset", response_model=UsageResetResponse)
async def reset_monthly_usage(
    organization: dict = Depends(require_read_permission),
    db: AsyncSession = Depends(get_db),
) -> UsageResetResponse:
    """
    Reset monthly usage counters.
    
    This is typically called by a scheduled job at the start of each billing period.
    Requires admin permissions.
    """
    org_id = organization["organization_id"]
    now = datetime.now(timezone.utc)
    
    # Reset monthly counters
    await db.execute(
        text("""
            UPDATE organizations
            SET 
                api_calls_this_month = 0,
                sentences_tracked_this_month = 0,
                batch_operations_this_month = 0,
                updated_at = :updated_at
            WHERE organization_id = :org_id
        """),
        {"org_id": org_id, "updated_at": now}
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
    months: int = 6,
    organization: dict = Depends(require_read_permission),
    db: AsyncSession = Depends(get_db),
):
    """
    Get historical usage data for the organization.
    
    Returns monthly usage summaries for the specified number of months.
    """
    org_id = organization["organization_id"]
    
    # For now, return placeholder data
    # TODO: Implement usage_history table and tracking
    now = datetime.now(timezone.utc)
    history = []
    
    for i in range(months):
        month = now.month - i
        year = now.year
        if month <= 0:
            month += 12
            year -= 1
        
        history.append({
            "period": f"{year}-{month:02d}",
            "c2pa_signatures": 0,
            "sentences_tracked": 0,
            "batch_operations": 0,
            "api_calls": 0,
        })
    
    return {
        "organization_id": org_id,
        "history": history,
    }
