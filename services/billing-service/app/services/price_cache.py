"""
Price cache service for Stripe products.

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
        
    def get_price_id(self, tier: str, billing_cycle: str) -> Optional[str]:
        """
        Get price ID from .env configuration.
        
        This is the primary method - uses .env for fast, reliable lookups.
        
        Args:
            tier: "professional" or "business"
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
            
        return tier_prices.get(billing_cycle)
    
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
            ("professional_monthly", settings.STRIPE_PRICE_PROFESSIONAL_MONTHLY),
            ("professional_annual", settings.STRIPE_PRICE_PROFESSIONAL_ANNUAL),
            ("business_monthly", settings.STRIPE_PRICE_BUSINESS_MONTHLY),
            ("business_annual", settings.STRIPE_PRICE_BUSINESS_ANNUAL),
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
                
                logger.info(f"✅ Validated price {name}: {price_id} (${price.unit_amount/100:.2f}/{price.recurring.get('interval')})")
                
            except StripeError as e:
                logger.error(f"❌ Failed to validate price {name} ({price_id}): {e}")
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


# Convenience function for backward compatibility
def get_stripe_price_id(tier: str, billing_cycle: str) -> Optional[str]:
    """
    Get Stripe price ID for a tier and billing cycle.
    
    This is the primary function to use throughout the codebase.
    Uses .env configuration for fast, reliable lookups.
    
    Args:
        tier: "professional" or "business"
        billing_cycle: "monthly" or "annual"
        
    Returns:
        Stripe price ID or None
    """
    return price_cache.get_price_id(tier, billing_cycle)
