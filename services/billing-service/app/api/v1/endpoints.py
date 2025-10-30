"""API endpoints for Billing Service v1"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List
import httpx

from ...db.session import get_db
from ...models.schemas import (
    SubscriptionCreate,
    SubscriptionResponse,
    InvoiceResponse,
    BillingStats,
    MessageResponse,
)
from ...services.billing_service import BillingService
from ...core.config import settings

router = APIRouter()


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
