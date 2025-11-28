"""
Stripe webhook endpoints.

Handles incoming webhooks from Stripe for subscription events,
payment events, and Connect account events.
"""
import logging
from fastapi import APIRouter, Request, HTTPException, status, Header

from ...services.stripe_service import StripeService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhooks/stripe")
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature")
):
    """
    Handle incoming Stripe webhooks.
    
    This endpoint receives all Stripe webhook events and routes them
    to the appropriate handlers.
    """
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe-Signature header"
        )

    # Get raw body
    payload = await request.body()

    try:
        # Verify webhook signature
        event = StripeService.verify_webhook_signature(payload, stripe_signature)

        # Handle the event
        result = await StripeService.handle_webhook_event(event)

        logger.info(f"Processed webhook {event.type}: {result}")
        return {"status": "success", "result": result}

    except ValueError as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


@router.post("/webhooks/stripe/connect")
async def handle_stripe_connect_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature")
):
    """
    Handle Stripe Connect webhooks.
    
    Separate endpoint for Connect-specific events like account updates
    and payout events.
    """
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe-Signature header"
        )

    payload = await request.body()

    try:
        # Note: Connect webhooks may use a different webhook secret
        event = StripeService.verify_webhook_signature(payload, stripe_signature)

        # Handle Connect-specific events
        event_type = event.type
        data = event.data.object

        if event_type == "account.updated":
            # Publisher completed onboarding or updated their account
            account_id = data.get("id")
            charges_enabled = data.get("charges_enabled")
            payouts_enabled = data.get("payouts_enabled")

            logger.info(
                f"Connect account {account_id} updated: "
                f"charges={charges_enabled}, payouts={payouts_enabled}"
            )

            # TODO: Update organization's payout status in database

            return {
                "status": "success",
                "account_id": account_id,
                "payouts_enabled": payouts_enabled
            }

        elif event_type == "payout.paid":
            # Payout to publisher succeeded
            payout_id = data.get("id")
            amount = data.get("amount")

            logger.info(f"Payout {payout_id} completed: ${amount/100:.2f}")

            return {"status": "success", "payout_id": payout_id}

        elif event_type == "payout.failed":
            # Payout to publisher failed
            payout_id = data.get("id")
            failure_message = data.get("failure_message")

            logger.error(f"Payout {payout_id} failed: {failure_message}")

            # TODO: Notify publisher and retry

            return {"status": "failed", "payout_id": payout_id}

        return {"status": "ignored", "event_type": event_type}

    except ValueError as e:
        logger.error(f"Connect webhook signature verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )
