"""
Account router for organization information and quota details.

Provides endpoints for customers to view their account info, tier, features, and quota.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_content_db, get_db
from app.dependencies import get_current_organization

router = APIRouter(prefix="/account", tags=["Account"])


# =============================================================================
# Response Models
# =============================================================================


class FeatureFlags(BaseModel):
    """Organization feature flags."""

    merkle_enabled: bool = Field(False, description="Merkle tree features enabled")
    byok_enabled: bool = Field(False, description="Bring Your Own Key enabled")
    sentence_tracking: bool = Field(False, description="Sentence-level tracking enabled")
    bulk_operations: bool = Field(False, description="Bulk/batch operations enabled")
    custom_assertions: bool = Field(False, description="Custom C2PA assertions enabled")
    streaming: bool = Field(True, description="Streaming API enabled")
    team_management: bool = Field(False, description="Team management enabled")
    audit_logs: bool = Field(False, description="Audit logs enabled")
    sso: bool = Field(False, description="SSO/SAML enabled")
    max_team_members: int = Field(1, description="Maximum team members allowed")


class QuotaMetric(BaseModel):
    """Single quota metric."""

    name: str = Field(..., description="Human-readable metric name")
    used: int = Field(..., description="Amount used this period")
    limit: int = Field(..., description="Period limit (-1 for unlimited)")
    remaining: int = Field(..., description="Amount remaining (-1 for unlimited)")
    percentage_used: float = Field(..., description="Percentage of limit used")


class AccountInfo(BaseModel):
    """Organization account information."""

    organization_id: str = Field(..., description="Organization ID")
    name: str = Field(..., description="Organization name")
    email: Optional[str] = Field(None, description="Primary contact email")
    tier: str = Field(..., description="Subscription tier")
    features: FeatureFlags = Field(..., description="Enabled features")
    created_at: Optional[str] = Field(None, description="Account creation date")
    subscription_status: str = Field("active", description="Subscription status")


class AccountResponse(BaseModel):
    """Response for account info endpoint."""

    success: bool = True
    data: AccountInfo


class QuotaInfo(BaseModel):
    """Detailed quota information."""

    organization_id: str
    tier: str
    period_start: str
    period_end: str
    metrics: Dict[str, QuotaMetric]
    reset_date: str


class QuotaResponse(BaseModel):
    """Response for quota endpoint."""

    success: bool = True
    data: QuotaInfo


# =============================================================================
# Tier Feature Mapping
# =============================================================================

TIER_FEATURES: Dict[str, Dict[str, Any]] = {
    "starter": {
        "merkle_enabled": False,
        "byok_enabled": False,
        "sentence_tracking": False,
        "bulk_operations": False,
        "custom_assertions": False,
        "streaming": True,
        "team_management": False,
        "audit_logs": False,
        "sso": False,
        "max_team_members": 1,
    },
    "professional": {
        "merkle_enabled": False,
        "byok_enabled": False,
        "sentence_tracking": True,
        "bulk_operations": False,
        "custom_assertions": False,
        "streaming": True,
        "team_management": True,
        "audit_logs": True,
        "sso": False,
        "max_team_members": 5,
    },
    "business": {
        "merkle_enabled": True,
        "byok_enabled": False,
        "sentence_tracking": True,
        "bulk_operations": True,
        "custom_assertions": False,
        "streaming": True,
        "team_management": True,
        "audit_logs": True,
        "sso": False,
        "max_team_members": 25,
    },
    "enterprise": {
        "merkle_enabled": True,
        "byok_enabled": True,
        "sentence_tracking": True,
        "bulk_operations": True,
        "custom_assertions": True,
        "streaming": True,
        "team_management": True,
        "audit_logs": True,
        "sso": True,
        "max_team_members": -1,  # Unlimited
    },
    "strategic_partner": {
        "merkle_enabled": True,
        "byok_enabled": True,
        "sentence_tracking": True,
        "bulk_operations": True,
        "custom_assertions": True,
        "streaming": True,
        "team_management": True,
        "audit_logs": True,
        "sso": True,
        "max_team_members": -1,
    },
}

TIER_LIMITS: Dict[str, Dict[str, int]] = {
    "starter": {
        "c2pa_signatures": 10000,
        "sentences_tracked": 0,
        "batch_operations": 0,
        "api_keys": 2,
    },
    "professional": {
        "c2pa_signatures": -1,
        "sentences_tracked": 50000,
        "batch_operations": 0,
        "api_keys": 10,
    },
    "business": {
        "c2pa_signatures": -1,
        "sentences_tracked": 500000,
        "batch_operations": 100,
        "api_keys": 50,
    },
    "enterprise": {
        "c2pa_signatures": -1,
        "sentences_tracked": -1,
        "batch_operations": -1,
        "api_keys": -1,
    },
    "strategic_partner": {
        "c2pa_signatures": -1,
        "sentences_tracked": -1,
        "batch_operations": -1,
        "api_keys": -1,
    },
}


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=AccountResponse)
async def get_account_info(
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> AccountResponse:
    """
    Get current organization account information.

    Returns organization details including:
    - Organization ID and name
    - Current subscription tier
    - Enabled feature flags
    - Account creation date
    """
    org_id = organization.get("organization_id")

    # Handle user-level keys (synthetic org IDs)
    if org_id and org_id.startswith("user_"):
        tier = "starter"
        features_dict = TIER_FEATURES.get(tier, TIER_FEATURES["starter"])
        return AccountResponse(
            data=AccountInfo(
                organization_id=org_id,
                name="Personal Account",
                email=None,
                tier=tier,
                features=FeatureFlags(**features_dict),
                created_at=None,
                subscription_status="active",
            )
        )

    # Query organization details
    result = await db.execute(
        text("""
            SELECT 
                id, name, email, tier, 
                subscription_status, created_at,
                features
            FROM organizations
            WHERE id = :org_id
        """),
        {"org_id": org_id},
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    tier = row.tier or "starter"

    # Merge database features with tier defaults
    db_features = row.features if isinstance(row.features, dict) else {}
    tier_features = TIER_FEATURES.get(tier, TIER_FEATURES["starter"])
    merged_features = {**tier_features, **db_features}

    return AccountResponse(
        data=AccountInfo(
            organization_id=row.id,
            name=row.name,
            email=row.email,
            tier=tier,
            features=FeatureFlags(**merged_features),
            created_at=row.created_at.isoformat() if row.created_at else None,
            subscription_status=row.subscription_status or "active",
        )
    )


@router.get("/quota", response_model=QuotaResponse)
async def get_account_quota(
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
) -> QuotaResponse:
    """
    Get detailed quota information for the organization.

    Returns current usage and limits for:
    - C2PA signatures
    - Sentences tracked
    - Batch operations
    - API calls
    """
    org_id = organization.get("organization_id")
    now = datetime.now(timezone.utc)

    # Calculate period dates
    period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        period_end = period_start.replace(year=now.year + 1, month=1)
    else:
        period_end = period_start.replace(month=now.month + 1)

    # Handle user-level keys
    if org_id and org_id.startswith("user_"):
        tier = "starter"
        limits = TIER_LIMITS.get(tier, TIER_LIMITS["starter"])
        return QuotaResponse(
            data=QuotaInfo(
                organization_id=org_id,
                tier=tier,
                period_start=period_start.isoformat(),
                period_end=period_end.isoformat(),
                metrics={
                    "c2pa_signatures": QuotaMetric(
                        name="C2PA Signatures",
                        used=0,
                        limit=limits["c2pa_signatures"],
                        remaining=limits["c2pa_signatures"],
                        percentage_used=0.0,
                    ),
                    "api_keys": QuotaMetric(
                        name="API Keys",
                        used=1,
                        limit=limits["api_keys"],
                        remaining=limits["api_keys"] - 1,
                        percentage_used=50.0,
                    ),
                },
                reset_date=period_end.isoformat(),
            )
        )

    # Get organization tier
    result = await db.execute(
        text("SELECT tier, monthly_api_usage, monthly_api_limit FROM organizations WHERE id = :org_id"),
        {"org_id": org_id},
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    tier = row.tier or "starter"
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["starter"])

    # Get document count
    doc_result = await content_db.execute(
        text("SELECT COUNT(*) FROM documents WHERE organization_id = :org_id"),
        {"org_id": org_id},
    )
    documents_signed = doc_result.scalar() or 0

    # Get sentence count
    sent_result = await content_db.execute(
        text("SELECT COUNT(*) FROM sentence_records WHERE organization_id = :org_id"),
        {"org_id": org_id},
    )
    sentences_tracked = sent_result.scalar() or 0

    # Get batch count
    batch_result = await db.execute(
        text("SELECT COUNT(*) FROM batch_requests WHERE organization_id = :org_id"),
        {"org_id": org_id},
    )
    batch_operations = batch_result.scalar() or 0

    # Get API key count
    key_result = await db.execute(
        text("SELECT COUNT(*) FROM api_keys WHERE organization_id = :org_id AND is_active = true"),
        {"org_id": org_id},
    )
    api_keys_count = key_result.scalar() or 0

    def build_metric(name: str, used: int, limit: int) -> QuotaMetric:
        if limit == -1:
            return QuotaMetric(name=name, used=used, limit=-1, remaining=-1, percentage_used=0.0)
        elif limit == 0:
            return QuotaMetric(name=name, used=used, limit=0, remaining=0, percentage_used=100.0 if used > 0 else 0.0)
        else:
            remaining = max(0, limit - used)
            percentage = (used / limit) * 100 if limit > 0 else 0.0
            return QuotaMetric(name=name, used=used, limit=limit, remaining=remaining, percentage_used=round(percentage, 2))

    return QuotaResponse(
        data=QuotaInfo(
            organization_id=org_id,
            tier=tier,
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            metrics={
                "c2pa_signatures": build_metric("C2PA Signatures", documents_signed, limits["c2pa_signatures"]),
                "sentences_tracked": build_metric("Sentences Tracked", sentences_tracked, limits["sentences_tracked"]),
                "batch_operations": build_metric("Batch Operations", batch_operations, limits["batch_operations"]),
                "api_keys": build_metric("API Keys", api_keys_count, limits["api_keys"]),
                "api_calls": build_metric(
                    "API Calls",
                    row.monthly_api_usage or 0,
                    row.monthly_api_limit if row.monthly_api_limit != -1 else -1,
                ),
            },
            reset_date=period_end.isoformat(),
        )
    )
