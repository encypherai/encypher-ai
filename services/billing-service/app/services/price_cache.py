"""
Price cache service for Stripe products.

TEAM_173: Updated from old professional/business SaaS tiers to
freemium add-on products per Feb 2026 pricing model.

Provides a hybrid approach:
- Uses .env price IDs as primary source (fast, reliable)
- Optionally validates against Stripe API on startup
- Caches product metadata for display purposes
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

import stripe
from stripe import StripeError

from ..core.config import settings

logger = logging.getLogger(__name__)


class PriceCache:
    """
    Cache for Stripe price information.

    Uses .env price IDs as primary source, with optional API validation.
    """

    def __init__(self):
        self._prices: Dict[str, Dict] = {}
        self._last_refresh: Optional[datetime] = None
        self._refresh_interval = timedelta(hours=24)

    def get_add_on_price_id(self, add_on: str) -> Optional[str]:
        """
        Get Stripe price ID for a freemium add-on from .env configuration.

        Args:
            add_on: Add-on identifier, e.g. "attribution_analytics",
                    "enforcement_bundle", "custom_signing_identity", etc.

        Returns:
            Stripe price ID or None
        """
        normalized_add_on = add_on.replace("-", "_")
        add_on_price_map: Dict[str, Optional[str]] = {
            "attribution_analytics": getattr(settings, "STRIPE_PRICE_ATTRIBUTION_ANALYTICS", None),
            "custom_signing_identity": getattr(settings, "STRIPE_PRICE_CUSTOM_SIGNING_IDENTITY", None),
            "white_label_verification": getattr(settings, "STRIPE_PRICE_WHITE_LABEL_VERIFICATION", None),
            "custom_verification_domain": getattr(settings, "STRIPE_PRICE_CUSTOM_VERIFICATION_DOMAIN", None),
            "byok": getattr(settings, "STRIPE_PRICE_BYOK", None),
            "priority_support": getattr(settings, "STRIPE_PRICE_PRIORITY_SUPPORT", None),
            "bulk_archive_backfill": getattr(settings, "STRIPE_PRICE_BULK_ARCHIVE_BACKFILL", None),
            "enforcement_bundle": getattr(settings, "STRIPE_PRICE_ENFORCEMENT_BUNDLE", None),
            "publisher_identity_bundle": getattr(settings, "STRIPE_PRICE_PUBLISHER_IDENTITY_BUNDLE", None),
            "full_stack_bundle": getattr(settings, "STRIPE_PRICE_FULL_STACK_BUNDLE", None),
        }
        return add_on_price_map.get(normalized_add_on)

    def get_price_id(self, tier: str, billing_cycle: str) -> Optional[str]:
        """
        Get price ID from .env configuration.

        TEAM_173: Legacy method kept for backward compatibility.
        The new pricing model uses add-ons (see get_add_on_price_id).
        Free tier has no Stripe price. Enterprise uses custom invoicing.

        Args:
            tier: tier name (legacy: "professional" or "business")
            billing_cycle: "monthly" or "annual"

        Returns:
            Stripe price ID or None
        """
        # Old SaaS tiers no longer exist — return None gracefully
        return None

    async def validate_prices_on_startup(self) -> Dict[str, bool]:
        """
        Validate that .env price IDs exist in Stripe.

        Call this on service startup to ensure configuration is correct.
        Logs warnings but doesn't block startup.

        Returns:
            Dict mapping price_id to validation status
        """
        validation_results = {}

        price_ids = [
            ("attribution_analytics", getattr(settings, "STRIPE_PRICE_ATTRIBUTION_ANALYTICS", None)),
            ("bulk_archive_backfill", getattr(settings, "STRIPE_PRICE_BULK_ARCHIVE_BACKFILL", None)),
            ("enforcement_bundle", getattr(settings, "STRIPE_PRICE_ENFORCEMENT_BUNDLE", None)),
            ("custom_signing_identity", getattr(settings, "STRIPE_PRICE_CUSTOM_SIGNING_IDENTITY", None)),
            ("white_label_verification", getattr(settings, "STRIPE_PRICE_WHITE_LABEL_VERIFICATION", None)),
            ("custom_verification_domain", getattr(settings, "STRIPE_PRICE_CUSTOM_VERIFICATION_DOMAIN", None)),
            ("byok", getattr(settings, "STRIPE_PRICE_BYOK", None)),
            ("priority_support", getattr(settings, "STRIPE_PRICE_PRIORITY_SUPPORT", None)),
            ("publisher_identity_bundle", getattr(settings, "STRIPE_PRICE_PUBLISHER_IDENTITY_BUNDLE", None)),
            ("full_stack_bundle", getattr(settings, "STRIPE_PRICE_FULL_STACK_BUNDLE", None)),
        ]

        for name, price_id in price_ids:
            if not price_id:
                logger.warning(f"Price ID not configured: {name}")
                validation_results[name] = False
                continue

            try:
                price = stripe.Price.retrieve(price_id)
                validation_results[name] = True

                # Cache metadata for display
                self._prices[price_id] = {
                    "id": price.id,
                    "amount": price.unit_amount,
                    "currency": price.currency,
                    "interval": price.recurring.get("interval") if price.recurring else None,
                    "product_id": price.product,
                    "active": price.active,
                }

                logger.info(f"Validated price {name}: {price_id} (${price.unit_amount/100:.2f}/{price.recurring.get('interval')})")

            except StripeError as e:
                logger.error(f"Failed to validate price {name} ({price_id}): {e}")
                validation_results[name] = False

        self._last_refresh = datetime.utcnow()
        return validation_results

    async def refresh_price_metadata(self) -> None:
        """
        Refresh cached price metadata from Stripe.

        Call periodically to keep display information up-to-date.
        Does not affect price ID lookups (those always use .env).
        """
        if self._last_refresh and datetime.utcnow() - self._last_refresh < self._refresh_interval:
            logger.debug("Price cache is still fresh, skipping refresh")
            return

        await self.validate_prices_on_startup()

    def get_price_metadata(self, price_id: str) -> Optional[Dict]:
        """
        Get cached metadata for a price.

        Useful for displaying price information without API calls.

        Returns:
            Dict with amount, currency, interval, etc. or None
        """
        return self._prices.get(price_id)

    def get_all_prices(self) -> Dict[str, Dict]:
        """Get all cached price metadata."""
        return self._prices.copy()


# Global instance
price_cache = PriceCache()


def get_add_on_stripe_price_id(add_on: str) -> Optional[str]:
    """
    Get Stripe price ID for a freemium add-on.

    This is the primary function to use throughout the codebase.
    Uses .env configuration for fast, reliable lookups.

    Args:
        add_on: Add-on identifier, e.g. "attribution_analytics"

    Returns:
        Stripe price ID or None
    """
    return price_cache.get_add_on_price_id(add_on)


# Legacy function kept for backward compatibility
def get_stripe_price_id(tier: str, billing_cycle: str) -> Optional[str]:
    """
    TEAM_173: Legacy — old SaaS tiers removed. Returns None.
    Use get_add_on_stripe_price_id() for add-on pricing.
    """
    return price_cache.get_price_id(tier, billing_cycle)
