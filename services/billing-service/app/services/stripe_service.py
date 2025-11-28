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
from typing import Optional, Dict, Any, List

import stripe
from stripe import StripeError

from ..core.config import settings

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_API_KEY


# Stripe Product IDs (to be created in Stripe Dashboard)
# These will be populated after running setup_stripe_products()
STRIPE_PRODUCTS = {
    "starter": {
        "product_id": None,  # Free tier - no Stripe product needed
        "price_monthly": None,
        "price_annual": None,
    },
    "professional": {
        "product_id": None,  # Set after creating in Stripe
        "price_monthly": None,  # $99/month
        "price_annual": None,  # $950/year
    },
    "business": {
        "product_id": None,  # Set after creating in Stripe
        "price_monthly": None,  # $499/month
        "price_annual": None,  # $4790/year
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
        email: str,
        name: Optional[str] = None,
        organization_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
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
    async def get_or_create_customer(
        email: str,
        name: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> stripe.Customer:
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
            return await StripeService.create_customer(
                email=email,
                name=name,
                organization_id=organization_id
            )

        except StripeError as e:
            logger.error(f"Failed to get/create customer: {e}")
            raise

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
        metadata: Optional[Dict[str, str]] = None
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
    async def create_upgrade_checkout(
        customer_id: str,
        current_subscription_id: str,
        new_price_id: str,
        success_url: str,
        cancel_url: str
    ) -> stripe.checkout.Session:
        """
        Create checkout session for upgrading subscription.
        
        Uses Stripe's proration to handle upgrade billing.
        """
        try:
            # For upgrades, we use the billing portal or modify subscription directly
            # Checkout is mainly for new subscriptions
            session = stripe.checkout.Session.create(
                customer=customer_id,
                mode="subscription",
                line_items=[{"price": new_price_id, "quantity": 1}],
                success_url=success_url,
                cancel_url=cancel_url,
                subscription_data={
                    "metadata": {"upgrade_from": current_subscription_id}
                },
            )

            return session

        except StripeError as e:
            logger.error(f"Failed to create upgrade checkout: {e}")
            raise

    # =========================================================================
    # Billing Portal
    # =========================================================================

    @staticmethod
    async def create_billing_portal_session(
        customer_id: str,
        return_url: str
    ) -> stripe.billing_portal.Session:
        """
        Create a Stripe Billing Portal session.
        
        Allows customers to manage their subscription, payment methods,
        and view invoices.
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )

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
    async def cancel_subscription(
        subscription_id: str,
        cancel_at_period_end: bool = True
    ) -> stripe.Subscription:
        """
        Cancel a subscription.
        
        Args:
            subscription_id: Stripe subscription ID
            cancel_at_period_end: If True, cancel at end of billing period
                                  If False, cancel immediately
        """
        try:
            if cancel_at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
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
        proration_behavior: str = "create_prorations"
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

            updated = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0].id,
                    "price": new_price_id,
                }],
                proration_behavior=proration_behavior,
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
    async def get_invoices(
        customer_id: str,
        limit: int = 10
    ) -> List[stripe.Invoice]:
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
    def verify_webhook_signature(
        payload: bytes,
        signature: str
    ) -> stripe.Event:
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
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET
            )
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

        # TODO: Update organization subscription in database
        # This should:
        # 1. Update organization tier based on subscription
        # 2. Sync feature flags
        # 3. Update coalition rev share

        return {
            "status": "success",
            "action": "subscription_created",
            "organization_id": organization_id,
            "subscription_id": subscription_id,
            "customer_id": customer_id,
        }

    @staticmethod
    async def _handle_subscription_created(subscription: Dict) -> Dict[str, Any]:
        """Handle new subscription creation."""
        logger.info(f"Subscription created: {subscription.get('id')}")
        return {"status": "success", "action": "subscription_created"}

    @staticmethod
    async def _handle_subscription_updated(subscription: Dict) -> Dict[str, Any]:
        """Handle subscription update (upgrade/downgrade)."""
        logger.info(f"Subscription updated: {subscription.get('id')}")

        # Check if this is a tier change
        # TODO: Update organization tier if needed

        return {"status": "success", "action": "subscription_updated"}

    @staticmethod
    async def _handle_subscription_deleted(subscription: Dict) -> Dict[str, Any]:
        """Handle subscription cancellation."""
        logger.info(f"Subscription deleted: {subscription.get('id')}")

        # TODO: Downgrade organization to Starter tier

        return {"status": "success", "action": "subscription_canceled"}

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
    async def create_connect_account(
        email: str,
        organization_id: str,
        country: str = "US"
    ) -> stripe.Account:
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
    async def create_connect_onboarding_link(
        account_id: str,
        refresh_url: str,
        return_url: str
    ) -> stripe.AccountLink:
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
    async def create_payout(
        connect_account_id: str,
        amount_cents: int,
        currency: str = "usd",
        description: Optional[str] = None
    ) -> stripe.Transfer:
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

            logger.info(
                f"Created payout of ${amount_cents/100:.2f} to {connect_account_id}"
            )
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
        Create Stripe products and prices for all tiers.
        
        Run this once to set up your Stripe catalog.
        Returns the product/price IDs to configure in your app.
        """
        products_created = {}

        tiers = [
            {
                "id": "professional",
                "name": "Encypher Professional",
                "description": "Sentence-level tracking, streaming, BYOK, and better coalition revenue share.",
                "price_monthly": 9900,  # $99 in cents
                "price_annual": 95000,  # $950 in cents
            },
            {
                "id": "business",
                "name": "Encypher Business",
                "description": "Merkle infrastructure, plagiarism detection, team management, and audit logs.",
                "price_monthly": 49900,  # $499 in cents
                "price_annual": 479000,  # $4790 in cents
            },
        ]

        try:
            for tier in tiers:
                # Create product
                product = stripe.Product.create(
                    name=tier["name"],
                    description=tier["description"],
                    metadata={"tier_id": tier["id"]},
                )

                # Create monthly price
                price_monthly = stripe.Price.create(
                    product=product.id,
                    unit_amount=tier["price_monthly"],
                    currency="usd",
                    recurring={"interval": "month"},
                    metadata={"tier_id": tier["id"], "billing_cycle": "monthly"},
                )

                # Create annual price
                price_annual = stripe.Price.create(
                    product=product.id,
                    unit_amount=tier["price_annual"],
                    currency="usd",
                    recurring={"interval": "year"},
                    metadata={"tier_id": tier["id"], "billing_cycle": "annual"},
                )

                products_created[tier["id"]] = {
                    "product_id": product.id,
                    "price_monthly": price_monthly.id,
                    "price_annual": price_annual.id,
                }

                logger.info(f"Created Stripe product for {tier['id']}: {product.id}")

            return products_created

        except StripeError as e:
            logger.error(f"Failed to setup Stripe products: {e}")
            raise


def get_stripe_price_id(tier: str, billing_cycle: str) -> Optional[str]:
    """
    Get Stripe price ID for a tier and billing cycle.
    
    Args:
        tier: Tier name (professional, business)
        billing_cycle: "monthly" or "annual"
        
    Returns:
        Stripe price ID or None
    """
    price_map = {
        "professional": {
            "monthly": settings.STRIPE_PRICE_PROFESSIONAL_MONTHLY,
            "annual": settings.STRIPE_PRICE_PROFESSIONAL_ANNUAL,
        },
        "business": {
            "monthly": settings.STRIPE_PRICE_BUSINESS_MONTHLY,
            "annual": settings.STRIPE_PRICE_BUSINESS_ANNUAL,
        },
    }

    tier_prices = price_map.get(tier)
    if not tier_prices:
        return None

    price_id = tier_prices.get(billing_cycle)
    return price_id if price_id else None
