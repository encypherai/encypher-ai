#!/usr/bin/env python3
"""
Setup Stripe products and prices for Encypher tiers.

This script creates the necessary Stripe products and prices for:
- Professional tier ($99/month, $950/year)
- Business tier ($499/month, $4,790/year)

Usage:
    cd services/billing-service
    uv run python ../../scripts/setup_stripe_products.py

The script will output the price IDs that you need to add to your .env file.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add billing service to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "billing-service"))

# Ensure required settings don't block the setup script
os.environ.setdefault("DATABASE_URL", "postgresql://user:password@localhost:5432/encypher_billing")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/5")

from app.services.stripe_service import StripeService


async def main():
    """Run Stripe product setup."""
    print("🚀 Setting up Stripe products for Encypher...")
    print("=" * 60)
    
    try:
        # Create products and prices
        products = await StripeService.setup_stripe_products()
        
        print("\n✅ Successfully created Stripe products!\n")
        print("=" * 60)
        print("📋 Add these to your .env file:")
        print("=" * 60)
        
        for tier_id, tier_data in products.items():
            print(f"\n# {tier_id.title()} Tier")
            if tier_id == "professional":
                print(f"STRIPE_PRICE_PROFESSIONAL_MONTHLY={tier_data['price_monthly']}")
                print(f"STRIPE_PRICE_PROFESSIONAL_ANNUAL={tier_data['price_annual']}")
            elif tier_id == "business":
                print(f"STRIPE_PRICE_BUSINESS_MONTHLY={tier_data['price_monthly']}")
                print(f"STRIPE_PRICE_BUSINESS_ANNUAL={tier_data['price_annual']}")
        
        print("\n" + "=" * 60)
        print("✨ Setup complete! Copy the above to services/billing-service/.env")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error setting up Stripe products: {e}")
        print("\nMake sure:")
        print("1. You have STRIPE_API_KEY set in services/billing-service/.env")
        print("2. The key starts with sk_test_ for test mode")
        print("3. You have internet connectivity")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
