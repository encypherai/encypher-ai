"""API endpoints for Billing Service v1"""

import asyncio
import httpx
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db.session import get_db
from ...models.schemas import (
    BillingStats,
    InvoiceResponse,
    MessageResponse,
    PlanInfo,
    TierName,
    SubscriptionCreate,
    SubscriptionResponse,
    UpgradeRequest,
    UpgradeResponse,
)
from ...services.billing_service import BillingService
from ...services.stripe_service import StripeService, get_stripe_price_id
from ...services.price_cache import get_add_on_stripe_price_id

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response models for Stripe endpoints
class CheckoutRequest(BaseModel):
    """Request to create a checkout session"""

    tier: TierName
    billing_cycle: str  # "monthly" or "annual"
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CheckoutResponse(BaseModel):
    """Response with checkout session URL"""

    checkout_url: str
    session_id: str


class PortalResponse(BaseModel):
    """Response with billing portal URL"""

    portal_url: str


class AddOnCheckoutRequest(BaseModel):
    add_on: str
    quantity: int = Field(ge=1, le=100000)
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class InternalTrialRequest(BaseModel):
    """Internal request to provision a trial subscription."""

    organization_id: str
    user_id: str
    tier: TierName
    trial_months: int = Field(ge=1, le=24)


class InternalTrialResponse(BaseModel):
    """Response for internal trial provisioning."""

    success: bool = True
    data: SubscriptionResponse


def _build_subscription_response(subscription: object) -> SubscriptionResponse:
    if isinstance(subscription, SubscriptionResponse):
        return subscription
    # `tier` is not a DB column; derive it from plan_id before validation.
    fields = {field: getattr(subscription, field, None) for field in SubscriptionResponse.model_fields}
    # Override tier only when absent or None — it mirrors plan_id.
    if not fields.get("tier"):
        fields["tier"] = getattr(subscription, "plan_id", None) or ""
    return SubscriptionResponse.model_validate(fields)


async def get_current_user(authorization: str = Header(...)) -> dict:
    """Verify user token with auth service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify", headers={"Authorization": authorization})
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=("Invalid authentication credentials. Provide a valid Bearer token in the Authorization header."),
                )
            payload = response.json()
            if isinstance(payload, dict) and "data" in payload:
                data = payload["data"]
                # Map default_organization_id to organization_id for convenience
                if "default_organization_id" in data and "organization_id" not in data:
                    data["organization_id"] = data["default_organization_id"]
                return data
            return payload
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=("Auth service unavailable. Please retry in a few moments. If the problem persists, contact support@encypherai.com."),
        )


@router.post("/subscription", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new subscription"""
    try:
        subscription = BillingService.create_subscription(
            db=db,
            user_id=current_user["id"],
            subscription_data=subscription_data,
        )
        return _build_subscription_response(subscription)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(f"Request validation failed: {e}. See available plans: GET /api/v1/billing/plans."),
        )


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get current subscription"""
    subscription = BillingService.get_user_subscription(db, current_user["id"])

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No active subscription found. To create one: POST /api/v1/billing/subscription. To view available plans: GET /api/v1/billing/plans."
            ),
        )

    return _build_subscription_response(subscription)


@router.delete("/subscription/{subscription_id}", response_model=MessageResponse)
async def cancel_subscription(
    subscription_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Cancel a subscription"""
    success = BillingService.cancel_subscription(db, subscription_id, current_user["id"])

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=("Subscription not found. To retrieve your current subscription ID: GET /api/v1/billing/subscription."),
        )

    return {"message": "Subscription will be canceled at period end"}


@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    limit: int = Query(default=20, ge=1, le=100, description="Number of invoices to return (max 100)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get invoices (max 100 per request). Use limit param to control page size."""
    invoices = BillingService.get_invoices(db, current_user["id"], limit)
    return invoices


@router.get("/stats", response_model=BillingStats)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get billing statistics"""
    stats = BillingService.get_billing_stats(db, current_user["id"])
    return BillingStats(**stats)


@router.post("/internal/trials", response_model=InternalTrialResponse, include_in_schema=False)
async def create_trial_subscription_internal(
    payload: InternalTrialRequest,
    internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
    db: Session = Depends(get_db),
):
    if not settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Internal endpoint not configured")
    if not internal_token or internal_token != settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal token")
    try:
        subscription = BillingService.create_trial_subscription(
            db=db,
            user_id=payload.user_id,
            organization_id=payload.organization_id,
            tier=payload.tier.value,
            trial_months=payload.trial_months,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request validation failed: {e}. Valid tiers: free, pro, enterprise.",
        )

    return InternalTrialResponse(success=True, data=_build_subscription_response(subscription))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "billing-service"}


# =========================================================================
# Stripe Integration Endpoints
# =========================================================================


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    request: CheckoutRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a Stripe Checkout session for subscription upgrade.

    Returns a URL to redirect the user to Stripe's hosted checkout page.
    """
    # TEAM_145: No self-service checkout. Free tier is free, Enterprise is contact-sales.
    if request.tier in [TierName.FREE, TierName.ENTERPRISE, TierName.STRATEGIC_PARTNER]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot checkout for {request.tier.value} tier. "
                "Free tier requires no payment. "
                "Enterprise requires contacting sales at sales@encypherai.com. "
                "For self-service checkout, use tier=pro with billing_cycle=monthly or annual. "
                "See available plans: GET /api/v1/billing/plans."
            ),
        )

    # Get Stripe price ID
    price_id = get_stripe_price_id(request.tier.value, request.billing_cycle)
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Price not configured for {request.tier.value}/{request.billing_cycle}. "
                "Valid billing_cycle values: monthly, annual. "
                "See available plans: GET /api/v1/billing/plans."
            ),
        )

    try:
        # Get or create Stripe customer
        customer = await StripeService.get_or_create_customer(
            email=current_user.get("email"),
            name=current_user.get("name"),
            organization_id=current_user.get("organization_id"),
        )

        # Default URLs
        base_url = settings.DASHBOARD_URL
        success_url = request.success_url or f"{base_url}/billing?success=true"
        cancel_url = request.cancel_url or f"{base_url}/billing?canceled=true"

        # Create checkout session
        session = await StripeService.create_checkout_session(
            customer_id=customer.id,
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            organization_id=current_user.get("organization_id"),
            metadata={
                "user_id": current_user.get("id") or "",
                "organization_id": current_user.get("organization_id") or "",
            },
        )

        return CheckoutResponse(
            checkout_url=session.url,
            session_id=session.id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_checkout_session_failed error=%s type=%s", e, type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {type(e).__name__}. Contact support if this persists.",
        )


@router.post("/checkout/add-on", response_model=CheckoutResponse)
async def create_add_on_checkout_session(
    request: AddOnCheckoutRequest,
    current_user: dict = Depends(get_current_user),
):
    add_on = request.add_on.replace("-", "_")
    if add_on != "bulk_archive_backfill":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(f"Unsupported add-on: {request.add_on!r}. Valid add-ons: bulk_archive_backfill (also accepted as bulk-archive-backfill)."),
        )

    price_id = get_add_on_stripe_price_id(add_on)
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("Price not configured for add-on. The add-on price may not be set up in Stripe. Contact support@encypherai.com."),
        )

    try:
        customer = await StripeService.get_or_create_customer(
            email=current_user.get("email"),
            name=current_user.get("name"),
            organization_id=current_user.get("organization_id"),
        )

        base_url = settings.DASHBOARD_URL
        success_url = request.success_url or f"{base_url}/billing?success=true&addon=bulk-archive-backfill"
        cancel_url = request.cancel_url or f"{base_url}/billing?canceled=true&addon=bulk-archive-backfill"

        session = await StripeService.create_one_time_checkout_session(
            customer_id=customer.id,
            price_id=price_id,
            quantity=request.quantity,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": current_user.get("id") or "",
                "organization_id": current_user.get("organization_id") or "",
                "add_on": add_on,
                "quantity": str(request.quantity),
            },
        )

        return CheckoutResponse(checkout_url=session.url, session_id=session.id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_add_on_checkout_failed error=%s type=%s", e, type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create add-on checkout session: {type(e).__name__}. Contact support if this persists.",
        )


@router.get("/portal", response_model=PortalResponse)
async def get_billing_portal(
    return_url: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Get a URL to the Stripe Billing Portal.

    The portal allows customers to:
    - Update payment methods
    - View invoices
    - Cancel subscription
    - Update billing info
    """
    try:
        # Get customer
        customer = await StripeService.get_or_create_customer(
            email=current_user.get("email"),
            name=current_user.get("name"),
            organization_id=current_user.get("organization_id"),
        )

        # Default return URL
        base_url = settings.DASHBOARD_URL
        portal_return_url = return_url or f"{base_url}/billing"

        # Create portal session
        session = await StripeService.create_billing_portal_session(
            customer_id=customer.id,
            return_url=portal_return_url,
        )

        return PortalResponse(portal_url=session.url)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_billing_portal_failed error=%s type=%s", e, type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create billing portal session: {type(e).__name__}. Contact support if this persists.",
        )


@router.post("/upgrade", response_model=UpgradeResponse)
async def upgrade_subscription(
    request: UpgradeRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Change tier.

    Enterprise requires contacting sales. Free tier downgrades
    route through the Stripe Billing Portal for cancellation.
    """
    target_tier = request.target_tier

    # Enterprise requires custom pricing — no self-service path.
    if target_tier == TierName.ENTERPRISE:
        return UpgradeResponse(
            success=False,
            message="Enterprise plans require custom pricing. Please contact sales@encypherai.com",
        )

    # Free tier: redirect to Stripe Billing Portal to cancel existing subscription.
    if target_tier == TierName.FREE:
        try:
            existing_subscription = BillingService.get_user_subscription(db, current_user["id"])
            customer = await StripeService.get_or_create_customer(
                email=current_user.get("email"),
                organization_id=current_user.get("organization_id"),
            )
            base_url = settings.DASHBOARD_URL
            subscription_id = existing_subscription.stripe_subscription_id if existing_subscription else None
            portal_session = await StripeService.create_billing_portal_session(
                customer_id=customer.id,
                return_url=f"{base_url}/billing",
                flow_data={
                    "type": "subscription_cancel",
                    "subscription_cancel": {"subscription": subscription_id},
                }
                if subscription_id
                else None,
            )
            return UpgradeResponse(
                success=True,
                checkout_url=portal_session.url,
                message="Redirecting to Stripe to confirm your downgrade.",
                new_tier=TierName.FREE.value,
            )
        except Exception as e:
            logger.error("upgrade_to_free_failed error=%s", e)
            return UpgradeResponse(
                success=False,
                message="Failed to open billing portal. Please try again or contact support.",
            )

    return UpgradeResponse(
        success=False,
        message=f"Unrecognised target tier: {target_tier.value}",
    )


# =========================================================================
# Usage Statistics
# =========================================================================


@router.get("/usage")
async def get_usage_stats(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get current period usage statistics.

    Returns usage metrics for the current billing period including:
    - API calls
    - Documents signed
    - Sentences tracked
    - Verifications
    """
    from datetime import datetime
    from ...services.billing_service import PRICING_TIERS

    # Get user's organization/tier info
    # For now, default to starter tier if no subscription
    user_id = current_user.get("id")
    org_id = current_user.get("organization_id", user_id)

    # Get subscription to determine tier
    subscription = BillingService.get_user_subscription(db, user_id)
    tier = subscription.plan_id if subscription else "free"
    tier_info = PRICING_TIERS.get(tier, PRICING_TIERS["free"])
    limits = tier_info["limits"]

    # Calculate period dates (monthly billing cycle)
    now = datetime.utcnow()
    period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        period_end = period_start.replace(year=now.year + 1, month=1)
    else:
        period_end = period_start.replace(month=now.month + 1)

    # Fetch real usage from analytics service
    usage_data_raw = None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{settings.ANALYTICS_SERVICE_URL}/api/v1/usage",
                headers={"Authorization": authorization},
                params={"org_id": org_id},
            )
            if resp.status_code == 200:
                usage_data_raw = resp.json()
    except Exception as exc:
        logger.warning("analytics_service_unavailable error=%s", exc)

    # Build usage_data from real response or fall back to zeros
    if usage_data_raw and isinstance(usage_data_raw, dict):
        metrics_raw = usage_data_raw.get("metrics", {})
        usage_data = {
            "c2pa_signatures": {
                "used": metrics_raw.get("c2pa_signatures", {}).get("used", 0),
                "limit": limits.get("c2pa_signatures", 1000),
            },
            "sentences_tracked": {
                "used": metrics_raw.get("sentences_tracked", {}).get("used", 0),
                "limit": limits.get("sentences_tracked", 0),
            },
            "api_calls": {
                "used": metrics_raw.get("api_calls", {}).get("used", 0),
                "limit": -1,
            },
            "verifications": {
                "used": metrics_raw.get("verifications", {}).get("used", 0),
                "limit": -1,
            },
        }
    else:
        usage_data = {
            "c2pa_signatures": {"used": 0, "limit": limits.get("c2pa_signatures", 1000)},
            "sentences_tracked": {"used": 0, "limit": limits.get("sentences_tracked", 0)},
            "api_calls": {"used": 0, "limit": -1},
            "verifications": {"used": 0, "limit": -1},
        }

    metrics = {}
    for metric_name, data in usage_data.items():
        limit = data["limit"]
        used = data["used"]

        if limit == -1:
            remaining = "unlimited"
            percentage = 0.0
        elif limit == 0:
            remaining = 0
            percentage = 100.0 if used > 0 else 0.0
        else:
            remaining = max(0, limit - used)
            percentage = (used / limit) * 100 if limit > 0 else 0.0

        metrics[metric_name] = {
            "name": metric_name.replace("_", " ").title(),
            "limit": limit if limit >= 0 else "unlimited",
            "used": used,
            "remaining": remaining,
            "percentage_used": round(percentage, 2),
            "available": limit == -1 or used < limit,
        }

    return {
        "organization_id": org_id,
        "tier": tier,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "metrics": metrics,
        "reset_date": period_end.isoformat(),
    }


# =========================================================================
# Coalition Revenue
# =========================================================================


def _query_content_coalition_earnings(org_id: str) -> Optional[dict]:
    """
    Direct fallback query of encypher_content.coalition_earnings when the
    coalition-service is unreachable or auth fails.
    Returns a coalition summary dict or None on error.
    """
    try:
        from sqlalchemy import create_engine, text as sa_text

        # Derive encypher_content URL from the billing DB URL by swapping the DB name
        content_url = settings.DATABASE_URL.replace("/encypher_billing", "/encypher_content")
        if "/encypher_billing" not in settings.DATABASE_URL:
            # URL doesn't follow expected pattern; try to find the right content DB
            import re

            content_url = re.sub(r"/[^/]+$", "/encypher_content", settings.DATABASE_URL)
        engine = create_engine(content_url, pool_size=1, max_overflow=0)
        with engine.connect() as conn:
            rows = conn.execute(
                sa_text("""
                SELECT
                    ai_company,
                    period_start,
                    period_end,
                    publisher_earnings_cents,
                    status
                FROM coalition_earnings
                WHERE organization_id = :org_id
                ORDER BY period_start DESC
                LIMIT 50
            """),
                {"org_id": org_id},
            ).fetchall()

            if not rows:
                return None

            total_cents = sum(r.publisher_earnings_cents for r in rows)
            pending_cents = sum(r.publisher_earnings_cents for r in rows if r.status in ("pending", "confirmed"))
            paid_rows = [r for r in rows if r.status == "paid"]
            last_payout = paid_rows[0].period_end.isoformat() if paid_rows else None

            history = [
                {
                    "period": r.period_start.isoformat(),
                    "ai_company": r.ai_company,
                    "amount": r.publisher_earnings_cents / 100.0,
                    "status": r.status,
                }
                for r in rows[:12]
            ]

            return {
                "member": True,
                "opted_out": False,
                "total_content": 0,
                "total_earnings": total_cents / 100.0,
                "pending_earnings": pending_cents / 100.0,
                "last_payout_date": last_payout,
                "earnings_history": history,
                "payout_account_connected": False,
                "payout_account_url": None,
            }
    except Exception as exc:
        logger.warning("content_coalition_fallback_failed error=%s", exc)
        return None


@router.get("/coalition")
async def get_coalition_earnings(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get coalition earnings summary for the current user/organization.

    Returns:
    - Coalition membership status
    - Revenue share percentages
    - Earnings history
    - Pending payouts
    """
    from ...services.billing_service import PRICING_TIERS

    user_id = current_user.get("id")

    # Get subscription to determine tier and rev share
    subscription = BillingService.get_user_subscription(db, user_id)
    tier = subscription.plan_id if subscription else "free"
    tier_info = PRICING_TIERS.get(tier, PRICING_TIERS["free"])
    rev_share = tier_info["coalition_rev_share"]

    # Fetch real coalition data from coalition-service — both requests run concurrently.
    coalition_raw = None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            auth_headers = {"Authorization": authorization}
            status_resp, revenue_resp = await asyncio.gather(
                client.get(
                    f"{settings.COALITION_SERVICE_URL}/api/v1/coalition/status/{user_id}",
                    headers=auth_headers,
                ),
                client.get(
                    f"{settings.COALITION_SERVICE_URL}/api/v1/coalition/revenue/{user_id}",
                    headers=auth_headers,
                ),
            )
            if status_resp.status_code == 200 and revenue_resp.status_code == 200:
                coalition_raw = {
                    "status": status_resp.json().get("data", {}),
                    "revenue": revenue_resp.json().get("data", {}),
                }
    except Exception as exc:
        logger.warning("coalition_service_unavailable error=%s", exc)

    if coalition_raw:
        status_data = coalition_raw["status"]
        revenue_data = coalition_raw["revenue"]
        earnings_history = revenue_data.get("earnings_history", [])
        return {
            "member": status_data.get("is_member", True),
            "opted_out": status_data.get("opted_out", False),
            "publisher_share_percent": rev_share["publisher"],
            "encypher_share_percent": rev_share["encypher"],
            "total_content": revenue_data.get("total_content", 0),
            "total_earnings": revenue_data.get("total_earnings", 0.0),
            "pending_earnings": revenue_data.get("pending_earnings", 0.0),
            "last_payout_date": revenue_data.get("last_payout_date"),
            "earnings_history": earnings_history,
            "payout_account_connected": revenue_data.get("payout_account_connected", False),
            "payout_account_url": revenue_data.get("payout_account_url"),
            "pagination": {
                "returned": len(earnings_history),
                "note": "earnings_history shows most recent records only",
            },
        }
    else:
        # Coalition-service unreachable or auth failed.
        # Fall back to direct query of encypher_content.coalition_earnings.
        org_id = current_user.get("organization_id") or current_user.get("default_organization_id")
        content_earnings = _query_content_coalition_earnings(org_id) if org_id else None
        if content_earnings:
            history = content_earnings.get("earnings_history", [])
            result = content_earnings | {
                "publisher_share_percent": rev_share["publisher"],
                "encypher_share_percent": rev_share["encypher"],
                "pagination": {
                    "returned": len(history),
                    "note": "earnings_history capped at 12 most recent records (fallback query)",
                },
            }
            return result
        return {
            "member": True,
            "opted_out": False,
            "publisher_share_percent": rev_share["publisher"],
            "encypher_share_percent": rev_share["encypher"],
            "total_content": 0,
            "total_earnings": 0.0,
            "pending_earnings": 0.0,
            "last_payout_date": None,
            "earnings_history": [],
            "payout_account_connected": False,
            "payout_account_url": None,
            "pagination": {
                "returned": 0,
                "note": "no earnings data available",
            },
        }


# =========================================================================
# Plans & Pricing Info
# =========================================================================


@router.get("/plans", response_model=List[PlanInfo])
async def get_available_plans():
    """
    Get all available subscription plans.

    Returns pricing, features, and limits for each tier.
    """
    # Import pricing info
    from ...services.billing_service import PRICING_TIERS

    plans = []
    for tier_id, tier in PRICING_TIERS.items():
        if tier_id == "strategic_partner":
            continue  # Don't show invite-only tier

        plans.append(
            PlanInfo(
                id=tier_id,
                name=tier["name"],
                tier=TierName(tier_id) if tier_id in TierName.__members__.values() else TierName.FREE,
                price_monthly=tier["price_monthly"],
                price_annual=tier["price_annual"],
                features=tier["features"],
                limits=tier["limits"],
                coalition_rev_share=tier["coalition_rev_share"],
                enterprise=tier_id == "enterprise",  # Mark enterprise for custom pricing
                popular=tier_id == "free",  # Free tier is the recommended starting point
            )
        )

    return plans
