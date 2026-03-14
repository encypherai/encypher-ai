"""
Stripe integration service for Encypher billing.

Handles:
- Customer management
- Subscription lifecycle
- Checkout sessions
- Billing portal
- Webhook processing
- Stripe Connect for publisher payouts
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

import stripe
from stripe import StripeError
import httpx

from ..db.session import SessionLocal
from ..db.models import Subscription
from ..services.billing_service import PRICING_TIERS

from ..core.config import settings
from .price_cache import get_stripe_price_id

logger = logging.getLogger(__name__)


def _resolve_tier_from_price_id(price_id: Optional[str]) -> Optional[str]:
    """Resolve tier from Stripe price ID.

    TEAM_145: professional/business tiers no longer exist.
    Legacy price IDs map to 'free' for backward compatibility.
    """
    if not price_id:
        return None
    # Legacy price IDs from old professional/business tiers -> free
    if price_id in {settings.STRIPE_PRICE_PROFESSIONAL_MONTHLY, settings.STRIPE_PRICE_PROFESSIONAL_ANNUAL}:
        return "free"
    if price_id in {settings.STRIPE_PRICE_BUSINESS_MONTHLY, settings.STRIPE_PRICE_BUSINESS_ANNUAL}:
        return "free"
    return None


async def _sync_org_tier(
    *,
    organization_id: str,
    tier: str,
    stripe_customer_id: Optional[str],
    stripe_subscription_id: Optional[str],
    subscription_status: Optional[str],
) -> None:
    if not organization_id:
        logger.warning("missing_organization_id_for_webhook_sync")
        return

    payload = {
        "tier": tier,
        "stripe_customer_id": stripe_customer_id,
        "stripe_subscription_id": stripe_subscription_id,
        "subscription_status": subscription_status,
    }
    headers = {}
    if settings.INTERNAL_SERVICE_TOKEN:
        headers["X-Internal-Token"] = settings.INTERNAL_SERVICE_TOKEN

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            f"{settings.AUTH_SERVICE_URL}/api/v1/organizations/internal/{organization_id}/tier",
            json=payload,
            headers=headers,
        )
        if response.status_code >= 400:
            logger.error(f"auth_service_tier_update_failed: status={response.status_code}, body={response.text}")
        else:
            logger.info(f"auth_service_tier_update_success: organization_id={organization_id}, tier={tier}")


def _get_tier_pricing(tier: str) -> Dict[str, Any]:
    return PRICING_TIERS.get(tier, {})


def _upsert_subscription_record(
    *,
    user_id: Optional[str],
    organization_id: Optional[str],
    tier: Optional[str],
    subscription: Optional[Dict[str, Any]],
    customer_id: Optional[str],
    price_id: Optional[str],
) -> None:
    if not subscription or not subscription.get("id"):
        return

    stripe_subscription_id = subscription.get("id")
    status = subscription.get("status")
    billing_cycle = subscription.get("items", {}).get("data", [{}])[0].get("price", {}).get("recurring", {}).get("interval")
    current_period_start = subscription.get("current_period_start")
    current_period_end = subscription.get("current_period_end")

    plan_config = _get_tier_pricing(tier or "")
    plan_name = plan_config.get("name", tier or "Unknown")
    amount = plan_config.get("price_monthly", 0) if billing_cycle == "month" else plan_config.get("price_annual", 0)

    db = SessionLocal()
    try:
        existing = db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_subscription_id).first()
        if existing:
            existing.status = status or existing.status
            existing.plan_id = tier or existing.plan_id
            existing.plan_name = plan_name
            existing.billing_cycle = "monthly" if billing_cycle == "month" else "annual"
            existing.amount = amount
            existing.stripe_customer_id = customer_id or existing.stripe_customer_id
            existing.extra_data = {
                "stripe_price_id": price_id,
                "stripe_subscription": subscription,
            }
        else:
            db.add(
                Subscription(
                    user_id=user_id or "unknown",
                    organization_id=organization_id,
                    plan_id=tier or "unknown",
                    plan_name=plan_name,
                    status=status or "active",
                    billing_cycle="monthly" if billing_cycle == "month" else "annual",
                    amount=amount,
                    currency="usd",
                    current_period_start=datetime.utcfromtimestamp(current_period_start) if current_period_start else datetime.utcnow(),
                    current_period_end=datetime.utcfromtimestamp(current_period_end) if current_period_end else datetime.utcnow(),
                    stripe_subscription_id=stripe_subscription_id,
                    stripe_customer_id=customer_id,
                    extra_data={
                        "stripe_price_id": price_id,
                        "stripe_subscription": subscription,
                    },
                )
            )
        db.commit()
    finally:
        db.close()


# Initialize Stripe
stripe.api_key = settings.STRIPE_API_KEY


# Stripe Product IDs (to be created in Stripe Dashboard)
# These will be populated after running setup_stripe_products()
# TEAM_145: Only free and enterprise tiers. No self-service Stripe checkout.
STRIPE_PRODUCTS = {
    "free": {
        "product_id": None,  # Free tier - no Stripe product needed
        "price_monthly": None,
        "price_annual": None,
    },
    "enterprise": {
        "product_id": None,  # Custom pricing - handled manually
        "price_monthly": None,
        "price_annual": None,
    },
}


class StripeService:
    """
    Service for Stripe payment operations.

    Handles all Stripe API interactions including customers,
    subscriptions, checkout, and webhooks.
    """

    # =========================================================================
    # Customer Management
    # =========================================================================

    @staticmethod
    async def create_customer(
        email: str, name: Optional[str] = None, organization_id: Optional[str] = None, metadata: Optional[Dict[str, str]] = None
    ) -> stripe.Customer:
        """
        Create a Stripe customer.

        Args:
            email: Customer email
            name: Customer/organization name
            organization_id: Encypher organization ID
            metadata: Additional metadata

        Returns:
            Stripe Customer object
        """
        try:
            customer_metadata = metadata or {}
            if organization_id:
                customer_metadata["organization_id"] = organization_id

            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=customer_metadata,
            )

            logger.info(f"Created Stripe customer {customer.id} for {email}")
            return customer

        except StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise

    @staticmethod
    async def get_customer(customer_id: str) -> Optional[stripe.Customer]:
        """Get a Stripe customer by ID."""
        try:
            return stripe.Customer.retrieve(customer_id)
        except StripeError as e:
            logger.error(f"Failed to retrieve customer {customer_id}: {e}")
            return None

    @staticmethod
    async def get_or_create_customer(email: str, name: Optional[str] = None, organization_id: Optional[str] = None) -> stripe.Customer:
        """
        Get existing customer by email or create new one.
        """
        try:
            # Search for existing customer
            customers = stripe.Customer.list(email=email, limit=1)

            if customers.data:
                customer = customers.data[0]
                logger.info(f"Found existing Stripe customer {customer.id}")
                return customer

            # Create new customer
            return await StripeService.create_customer(email=email, name=name, organization_id=organization_id)

        except StripeError as e:
            logger.error(f"Failed to get/create customer: {e}")
            raise

    @staticmethod
    async def list_active_subscriptions(customer_id: str, limit: int = 1) -> List[stripe.Subscription]:
        """List active subscriptions for a customer."""
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status="active",
                limit=limit,
            )
            return subscriptions.data
        except StripeError as e:
            logger.error(f"Failed to list subscriptions for {customer_id}: {e}")
            return []

    # =========================================================================
    # Checkout Sessions
    # =========================================================================

    @staticmethod
    async def create_checkout_session(
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        organization_id: Optional[str] = None,
        trial_days: int = 0,
        metadata: Optional[Dict[str, str]] = None,
    ) -> stripe.checkout.Session:
        """
        Create a Stripe Checkout session for subscription.

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel
            organization_id: Encypher organization ID
            trial_days: Number of trial days (0 for no trial)
            metadata: Additional metadata

        Returns:
            Stripe Checkout Session
        """
        try:
            session_metadata = metadata or {}
            if organization_id:
                session_metadata["organization_id"] = organization_id

            session_params = {
                "customer": customer_id,
                "payment_method_types": ["card"],
                "line_items": [{"price": price_id, "quantity": 1}],
                "mode": "subscription",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": session_metadata,
                "subscription_data": {
                    "metadata": session_metadata,
                },
                "customer_update": {"name": "auto", "address": "auto"},
                "allow_promotion_codes": True,
                "billing_address_collection": "required",
                "tax_id_collection": {"enabled": True},
            }

            if trial_days > 0:
                session_params["subscription_data"]["trial_period_days"] = trial_days

            session = stripe.checkout.Session.create(**session_params)

            logger.info(f"Created checkout session {session.id} for customer {customer_id}")
            return session

        except StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise

    @staticmethod
    async def create_one_time_checkout_session(
        customer_id: str,
        price_id: str,
        quantity: int,
        success_url: str,
        cancel_url: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> stripe.checkout.Session:
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": quantity}],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
                customer_update={"name": "auto", "address": "auto"},
                allow_promotion_codes=True,
                billing_address_collection="required",
                tax_id_collection={"enabled": True},
            )

            logger.info(f"Created one-time checkout session {session.id} for customer {customer_id}")
            return session
        except StripeError as e:
            logger.error(f"Failed to create one-time checkout session: {e}")
            raise

    # =========================================================================
    # Billing Portal
    # =========================================================================

    @staticmethod
    async def create_billing_portal_session(
        customer_id: str,
        return_url: str,
        flow_data: Optional[Dict[str, Any]] = None,
    ) -> stripe.billing_portal.Session:
        """
        Create a Stripe Billing Portal session.

        Allows customers to manage their subscription, payment methods,
        and view invoices.
        """
        try:
            session_params: Dict[str, Any] = {
                "customer": customer_id,
                "return_url": return_url,
            }
            if settings.STRIPE_BILLING_PORTAL_CONFIG_ID:
                session_params["configuration"] = settings.STRIPE_BILLING_PORTAL_CONFIG_ID
            if flow_data:
                session_params["flow_data"] = flow_data

            session = stripe.billing_portal.Session.create(**session_params)

            logger.info(f"Created billing portal session for customer {customer_id}")
            return session

        except StripeError as e:
            logger.error(f"Failed to create billing portal session: {e}")
            raise

    # =========================================================================
    # Subscription Management
    # =========================================================================

    @staticmethod
    async def get_subscription(subscription_id: str) -> Optional[stripe.Subscription]:
        """Get a subscription by ID."""
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except StripeError as e:
            logger.error(f"Failed to retrieve subscription {subscription_id}: {e}")
            return None

    @staticmethod
    async def cancel_subscription(subscription_id: str, cancel_at_period_end: bool = True) -> stripe.Subscription:
        """
        Cancel a subscription.

        Args:
            subscription_id: Stripe subscription ID
            cancel_at_period_end: If True, cancel at end of billing period
                                  If False, cancel immediately
        """
        try:
            if cancel_at_period_end:
                subscription = stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
            else:
                subscription = stripe.Subscription.delete(subscription_id)

            logger.info(f"Canceled subscription {subscription_id}")
            return subscription

        except StripeError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            raise

    @staticmethod
    async def update_subscription(
        subscription_id: str,
        new_price_id: str,
        proration_behavior: str = "create_prorations",
        metadata: Optional[Dict[str, str]] = None,
    ) -> stripe.Subscription:
        """
        Update subscription to a new price (upgrade/downgrade).

        Args:
            subscription_id: Stripe subscription ID
            new_price_id: New Stripe price ID
            proration_behavior: How to handle prorations
                - "create_prorations": Prorate charges
                - "none": No proration
                - "always_invoice": Invoice immediately
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)

            update_params: Dict[str, Any] = {
                "items": [
                    {
                        "id": subscription["items"]["data"][0].id,
                        "price": new_price_id,
                    }
                ],
                "proration_behavior": proration_behavior,
            }
            if metadata:
                update_params["metadata"] = metadata

            updated = stripe.Subscription.modify(
                subscription_id,
                **update_params,
            )

            logger.info(f"Updated subscription {subscription_id} to price {new_price_id}")
            return updated

        except StripeError as e:
            logger.error(f"Failed to update subscription: {e}")
            raise

    # =========================================================================
    # Invoices
    # =========================================================================

    @staticmethod
    async def get_invoices(customer_id: str, limit: int = 10) -> List[stripe.Invoice]:
        """Get invoices for a customer."""
        try:
            invoices = stripe.Invoice.list(
                customer=customer_id,
                limit=limit,
            )
            return invoices.data

        except StripeError as e:
            logger.error(f"Failed to get invoices: {e}")
            return []

    @staticmethod
    async def get_upcoming_invoice(customer_id: str) -> Optional[stripe.Invoice]:
        """Get upcoming invoice for a customer."""
        try:
            return stripe.Invoice.upcoming(customer=customer_id)
        except StripeError as e:
            logger.error(f"Failed to get upcoming invoice: {e}")
            return None

    # =========================================================================
    # Webhook Processing
    # =========================================================================

    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str) -> stripe.Event:
        """
        Verify and parse a Stripe webhook event.

        Args:
            payload: Raw request body
            signature: Stripe-Signature header value

        Returns:
            Verified Stripe Event

        Raises:
            ValueError: If signature verification fails
        """
        try:
            event = stripe.Webhook.construct_event(payload, signature, settings.STRIPE_WEBHOOK_SECRET)
            return event

        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            raise ValueError("Invalid webhook signature")

    @staticmethod
    async def handle_webhook_event(event: stripe.Event) -> Dict[str, Any]:
        """
        Handle a Stripe webhook event.

        Args:
            event: Verified Stripe Event

        Returns:
            Dict with handling result
        """
        event_type = event.type
        data = event.data.object

        logger.info(f"Processing webhook event: {event_type}")

        handlers = {
            "checkout.session.completed": StripeService._handle_checkout_completed,
            "customer.subscription.created": StripeService._handle_subscription_created,
            "customer.subscription.updated": StripeService._handle_subscription_updated,
            "customer.subscription.deleted": StripeService._handle_subscription_deleted,
            "invoice.paid": StripeService._handle_invoice_paid,
            "invoice.payment_failed": StripeService._handle_invoice_payment_failed,
            "customer.created": StripeService._handle_customer_created,
        }

        handler = handlers.get(event_type)
        if handler:
            return await handler(data)

        logger.info(f"Unhandled webhook event type: {event_type}")
        return {"status": "ignored", "event_type": event_type}

    @staticmethod
    async def _handle_checkout_completed(session: Dict) -> Dict[str, Any]:
        """Handle successful checkout completion."""
        logger.info(f"Checkout completed: {session.get('id')}")

        # Extract metadata
        organization_id = session.get("metadata", {}).get("organization_id")
        subscription_id = session.get("subscription")
        customer_id = session.get("customer")

        tier = None
        if subscription_id:
            try:
                subscription = stripe.Subscription.retrieve(subscription_id)
                subscription_metadata = subscription.get("metadata", {})
                subscription_org_id = subscription_metadata.get("organization_id") or organization_id
                user_id = subscription_metadata.get("user_id")
                price_id = subscription["items"]["data"][0]["price"]["id"] if subscription.get("items") else None
                tier = _resolve_tier_from_price_id(price_id)
                if tier:
                    await _sync_org_tier(
                        organization_id=subscription_org_id,
                        tier=tier,
                        stripe_customer_id=customer_id,
                        stripe_subscription_id=subscription_id,
                        subscription_status=subscription.get("status"),
                    )
                _upsert_subscription_record(
                    user_id=user_id,
                    organization_id=subscription_org_id,
                    tier=tier,
                    subscription=subscription,
                    customer_id=customer_id,
                    price_id=price_id,
                )
            except StripeError as e:
                logger.error(f"Failed to retrieve subscription for checkout: {e}")

        return {
            "status": "success",
            "action": "subscription_created",
            "organization_id": organization_id,
            "subscription_id": subscription_id,
            "customer_id": customer_id,
            "tier": tier,
        }

    @staticmethod
    async def _handle_subscription_created(subscription: Dict) -> Dict[str, Any]:
        """Handle new subscription creation."""
        logger.info(f"Subscription created: {subscription.get('id')}")
        metadata = subscription.get("metadata", {})
        organization_id = metadata.get("organization_id")
        user_id = metadata.get("user_id")
        customer_id = subscription.get("customer")
        price_id = subscription["items"]["data"][0]["price"]["id"] if subscription.get("items") else None
        tier = _resolve_tier_from_price_id(price_id)

        if tier:
            await _sync_org_tier(
                organization_id=organization_id,
                tier=tier,
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription.get("id"),
                subscription_status=subscription.get("status"),
            )

        _upsert_subscription_record(
            user_id=user_id,
            organization_id=organization_id,
            tier=tier,
            subscription=subscription,
            customer_id=customer_id,
            price_id=price_id,
        )

        return {"status": "success", "action": "subscription_created", "tier": tier}

    @staticmethod
    async def _handle_subscription_updated(subscription: Dict) -> Dict[str, Any]:
        """Handle subscription update (upgrade/downgrade)."""
        logger.info(f"Subscription updated: {subscription.get('id')}")
        metadata = subscription.get("metadata", {})
        organization_id = metadata.get("organization_id")
        user_id = metadata.get("user_id")
        customer_id = subscription.get("customer")
        price_id = subscription["items"]["data"][0]["price"]["id"] if subscription.get("items") else None
        tier = _resolve_tier_from_price_id(price_id)

        if tier:
            await _sync_org_tier(
                organization_id=organization_id,
                tier=tier,
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription.get("id"),
                subscription_status=subscription.get("status"),
            )

        _upsert_subscription_record(
            user_id=user_id,
            organization_id=organization_id,
            tier=tier,
            subscription=subscription,
            customer_id=customer_id,
            price_id=price_id,
        )

        return {"status": "success", "action": "subscription_updated", "tier": tier}

    @staticmethod
    async def _handle_subscription_deleted(subscription: Dict) -> Dict[str, Any]:
        """Handle subscription cancellation."""
        logger.info(f"Subscription deleted: {subscription.get('id')}")
        metadata = subscription.get("metadata", {})
        organization_id = metadata.get("organization_id")
        user_id = metadata.get("user_id")
        customer_id = subscription.get("customer")

        await _sync_org_tier(
            organization_id=organization_id,
            tier="free",
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription.get("id"),
            subscription_status=subscription.get("status"),
        )

        price_id = subscription.get("items", {}).get("data", [{}])[0].get("price", {}).get("id")
        _upsert_subscription_record(
            user_id=user_id,
            organization_id=organization_id,
            tier="free",
            subscription=subscription,
            customer_id=customer_id,
            price_id=price_id,
        )

        return {"status": "success", "action": "subscription_canceled", "tier": "free"}

    @staticmethod
    async def _handle_invoice_paid(invoice: Dict) -> Dict[str, Any]:
        """Handle successful invoice payment."""
        logger.info(f"Invoice paid: {invoice.get('id')}")

        # TODO: Record payment in database
        # TODO: Send receipt email

        return {"status": "success", "action": "invoice_paid"}

    @staticmethod
    async def _handle_invoice_payment_failed(invoice: Dict) -> Dict[str, Any]:
        """Handle failed invoice payment."""
        logger.warning(f"Invoice payment failed: {invoice.get('id')}")

        # TODO: Send payment failure notification
        # TODO: Update subscription status

        return {"status": "success", "action": "payment_failed_handled"}

    @staticmethod
    async def _handle_customer_created(customer: Dict) -> Dict[str, Any]:
        """Handle new customer creation."""
        logger.info(f"Customer created: {customer.get('id')}")
        return {"status": "success", "action": "customer_created"}

    # =========================================================================
    # Stripe Connect (Publisher Payouts)
    # =========================================================================

    @staticmethod
    async def create_connect_account(email: str, organization_id: str, country: str = "US") -> stripe.Account:
        """
        Create a Stripe Connect account for publisher payouts.

        Args:
            email: Publisher email
            organization_id: Encypher organization ID
            country: Two-letter country code

        Returns:
            Stripe Connect Account
        """
        try:
            account = stripe.Account.create(
                type="express",  # Express accounts are easiest to set up
                country=country,
                email=email,
                capabilities={
                    "transfers": {"requested": True},
                },
                metadata={
                    "organization_id": organization_id,
                },
            )

            logger.info(f"Created Connect account {account.id} for org {organization_id}")
            return account

        except StripeError as e:
            logger.error(f"Failed to create Connect account: {e}")
            raise

    @staticmethod
    async def create_connect_onboarding_link(account_id: str, refresh_url: str, return_url: str) -> stripe.AccountLink:
        """
        Create onboarding link for Connect account.

        Publishers use this to complete their payout account setup.
        """
        try:
            link = stripe.AccountLink.create(
                account=account_id,
                refresh_url=refresh_url,
                return_url=return_url,
                type="account_onboarding",
            )

            return link

        except StripeError as e:
            logger.error(f"Failed to create onboarding link: {e}")
            raise

    @staticmethod
    async def create_payout(connect_account_id: str, amount_cents: int, currency: str = "usd", description: Optional[str] = None) -> stripe.Transfer:
        """
        Create a payout to a publisher's Connect account.

        Args:
            connect_account_id: Publisher's Stripe Connect account ID
            amount_cents: Amount in cents
            currency: Currency code
            description: Payout description

        Returns:
            Stripe Transfer object
        """
        try:
            transfer = stripe.Transfer.create(
                amount=amount_cents,
                currency=currency,
                destination=connect_account_id,
                description=description or "Encypher Coalition Revenue Share",
            )

            logger.info(f"Created payout of ${amount_cents / 100:.2f} to {connect_account_id}")
            return transfer

        except StripeError as e:
            logger.error(f"Failed to create payout: {e}")
            raise

    # =========================================================================
    # Product/Price Setup (Run once to configure Stripe)
    # =========================================================================

    @staticmethod
    async def setup_stripe_products() -> Dict[str, Any]:
        """
        Create Stripe products and prices for freemium add-ons.

        TEAM_173: Replaced old professional/business SaaS tiers with
        freemium add-on products per Feb 2026 pricing model.
        Free tier has no Stripe product (no charge).
        Enterprise tier uses custom invoicing (no self-service Stripe product).

        Run this once to set up your Stripe catalog.
        Returns the product/price IDs to configure in your app.
        """
        products_created = {}

        add_ons = [
            {
                "id": "attribution_analytics",
                "name": "Encypher Attribution Analytics",
                "description": "Full dashboard showing where your signed content appears in AI outputs.",
                "price_monthly": 29900,  # $299 in cents
            },
            {
                "id": "custom_signing_identity",
                "name": "Encypher Custom Signing Identity",
                "description": "Sign content as your brand instead of Encypher Coalition Member.",
                "price_monthly": 49900,  # $499 in cents
            },
            {
                "id": "white_label_verification",
                "name": "Encypher White-Label Verification",
                "description": "Verification pages hosted on your domain with your branding.",
                "price_monthly": 29900,  # $299 in cents
            },
            {
                "id": "custom_verification_domain",
                "name": "Encypher Custom Verification Domain",
                "description": "Point a custom domain to your verification pages.",
                "price_monthly": 2900,  # $29 in cents
            },
            {
                "id": "byok",
                "name": "Encypher BYOK (Bring Your Own Keys)",
                "description": "Use your organization's existing PKI infrastructure and signing certificates.",
                "price_monthly": 49900,  # $499 in cents
            },
            {
                "id": "priority_support",
                "name": "Encypher Priority Support",
                "description": "Email support with 4-hour response SLA during business hours.",
                "price_monthly": 19900,  # $199 in cents
            },
            {
                "id": "enforcement_bundle",
                "name": "Encypher Enforcement Bundle",
                "description": "Attribution Analytics + 2 Formal Notices/mo + 1 Evidence Package/mo.",
                "price_monthly": 99900,  # $999 in cents
            },
            {
                "id": "publisher_identity_bundle",
                "name": "Encypher Publisher Identity Bundle",
                "description": "Custom Signing Identity + White-Label Verification + Custom Domain.",
                "price_monthly": 74900,  # $749 in cents
            },
            {
                "id": "full_stack_bundle",
                "name": "Encypher Full Stack Bundle",
                "description": "Enforcement Bundle + Publisher Identity Bundle.",
                "price_monthly": 169900,  # $1,699 in cents
            },
        ]

        try:
            for add_on in add_ons:
                product = stripe.Product.create(
                    name=add_on["name"],
                    description=add_on["description"],
                    metadata={"add_on_id": add_on["id"]},
                )

                price_monthly = stripe.Price.create(
                    product=product.id,
                    unit_amount=add_on["price_monthly"],
                    currency="usd",
                    recurring={"interval": "month"},
                    metadata={"add_on_id": add_on["id"], "billing_cycle": "monthly"},
                )

                products_created[add_on["id"]] = {
                    "product_id": product.id,
                    "price_monthly": price_monthly.id,
                }

                logger.info(f"Created Stripe product for {add_on['id']}: {product.id}")

            return products_created

        except StripeError as e:
            logger.error(f"Failed to setup Stripe products: {e}")
            raise


# Keep this for backward compatibility
__all__ = ["StripeService", "get_stripe_price_id"]
