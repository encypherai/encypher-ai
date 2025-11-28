"""API endpoints for Billing Service v1"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import httpx

from ...db.session import get_db
from ...models.schemas import (
    SubscriptionCreate,
    SubscriptionResponse,
    InvoiceResponse,
    BillingStats,
    MessageResponse,
    TierName,
    UpgradeRequest,
    UpgradeResponse,
    PlanInfo,
)
from ...services.billing_service import BillingService
from ...services.stripe_service import StripeService, get_stripe_price_id
from ...core.config import settings

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


async def get_current_user(authorization: str = Header(...)) -> dict:
    """Verify user token with auth service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
                headers={"Authorization": authorization}
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )
            return response.json()
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable",
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
        return subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
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
            detail="No active subscription found",
        )

    return subscription


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
            detail="Subscription not found",
        )

    return {"message": "Subscription will be canceled at period end"}


@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get invoices"""
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
    # Validate tier
    if request.tier in [TierName.STARTER, TierName.ENTERPRISE, TierName.STRATEGIC_PARTNER]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot checkout for {request.tier.value} tier. Use contact sales for Enterprise."
        )

    # Get Stripe price ID
    price_id = get_stripe_price_id(request.tier.value, request.billing_cycle)
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Price not configured for {request.tier.value} {request.billing_cycle}"
        )

    try:
        # Get or create Stripe customer
        customer = await StripeService.get_or_create_customer(
            email=current_user.get("email"),
            name=current_user.get("name"),
            organization_id=current_user.get("organization_id"),
        )

        # Default URLs
        base_url = settings.API_GATEWAY_URL.replace("/api", "")
        success_url = request.success_url or f"{base_url}/billing?success=true"
        cancel_url = request.cancel_url or f"{base_url}/billing?canceled=true"

        # Create checkout session
        session = await StripeService.create_checkout_session(
            customer_id=customer.id,
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            organization_id=current_user.get("organization_id"),
        )

        return CheckoutResponse(
            checkout_url=session.url,
            session_id=session.id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
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
        base_url = settings.API_GATEWAY_URL.replace("/api", "")
        portal_return_url = return_url or f"{base_url}/billing"

        # Create portal session
        session = await StripeService.create_billing_portal_session(
            customer_id=customer.id,
            return_url=portal_return_url,
        )

        return PortalResponse(portal_url=session.url)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create billing portal session: {str(e)}"
        )


@router.post("/upgrade", response_model=UpgradeResponse)
async def upgrade_subscription(
    request: UpgradeRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Upgrade to a higher tier.
    
    For paid tiers, returns a Stripe checkout URL.
    For downgrades or free tier, processes immediately.
    """
    target_tier = request.target_tier

    # If upgrading to a paid tier, redirect to checkout
    if target_tier in [TierName.PROFESSIONAL, TierName.BUSINESS]:
        price_id = get_stripe_price_id(target_tier.value, request.billing_cycle)

        if not price_id:
            return UpgradeResponse(
                success=False,
                message=f"Price not configured for {target_tier.value}. Please contact support.",
            )

        try:
            customer = await StripeService.get_or_create_customer(
                email=current_user.get("email"),
                organization_id=current_user.get("organization_id"),
            )

            base_url = settings.API_GATEWAY_URL.replace("/api", "")
            session = await StripeService.create_checkout_session(
                customer_id=customer.id,
                price_id=price_id,
                success_url=f"{base_url}/billing?upgrade=success",
                cancel_url=f"{base_url}/billing?upgrade=canceled",
                organization_id=current_user.get("organization_id"),
            )

            return UpgradeResponse(
                success=True,
                checkout_url=session.url,
                message=f"Redirecting to checkout for {target_tier.value} plan",
                new_tier=target_tier.value,
            )

        except Exception as e:
            return UpgradeResponse(
                success=False,
                message=f"Failed to create checkout: {str(e)}",
            )

    # For Enterprise, return contact sales message
    elif target_tier == TierName.ENTERPRISE:
        return UpgradeResponse(
            success=False,
            message="Enterprise plans require custom pricing. Please contact sales@encypherai.com",
        )

    # For Starter (downgrade), process immediately
    elif target_tier == TierName.STARTER:
        # TODO: Cancel Stripe subscription and downgrade
        return UpgradeResponse(
            success=True,
            message="Your subscription will be downgraded to Starter at the end of your billing period.",
            new_tier="starter",
        )

    return UpgradeResponse(
        success=False,
        message="Invalid tier specified",
    )


# =========================================================================
# Usage Statistics
# =========================================================================

@router.get("/usage")
async def get_usage_stats(
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
    tier = subscription.plan_id if subscription else "starter"
    tier_info = PRICING_TIERS.get(tier, PRICING_TIERS["starter"])
    limits = tier_info["limits"]

    # Calculate period dates (monthly billing cycle)
    now = datetime.utcnow()
    period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        period_end = period_start.replace(year=now.year + 1, month=1)
    else:
        period_end = period_start.replace(month=now.month + 1)

    # TODO: Get actual usage from analytics service
    # For now, return placeholder data
    usage_data = {
        "c2pa_signatures": {"used": 0, "limit": limits.get("c2pa_signatures", 10000)},
        "sentences_tracked": {"used": 0, "limit": limits.get("sentences_tracked", 0)},
        "api_calls": {"used": 0, "limit": -1},  # Unlimited
        "verifications": {"used": 0, "limit": -1},  # Unlimited
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

@router.get("/coalition")
async def get_coalition_earnings(
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
    current_user.get("organization_id", user_id)

    # Get subscription to determine tier and rev share
    subscription = BillingService.get_user_subscription(db, user_id)
    tier = subscription.plan_id if subscription else "starter"
    tier_info = PRICING_TIERS.get(tier, PRICING_TIERS["starter"])
    rev_share = tier_info["coalition_rev_share"]

    # TODO: Get actual coalition data from coalition-service
    # For now, return placeholder data
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
        "payout_account_url": None,  # Will be Stripe Connect onboarding URL
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

        plans.append(PlanInfo(
            id=tier_id,
            name=tier["name"],
            tier=TierName(tier_id) if tier_id in TierName.__members__.values() else TierName.STARTER,
            price_monthly=tier["price_monthly"],
            price_annual=tier["price_annual"],
            features=tier["features"],
            limits=tier["limits"],
            coalition_rev_share=tier["coalition_rev_share"],
        ))

    return plans
