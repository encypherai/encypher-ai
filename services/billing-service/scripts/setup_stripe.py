#!/usr/bin/env python3
"""
Stripe Setup Script

Run this script once to create Stripe products and prices for all tiers.
The script will output the price IDs that need to be added to your .env file.

Usage:
    uv run python scripts/setup_stripe.py

Prerequisites:
    - Set STRIPE_API_KEY in your environment or .env file
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")

if not stripe.api_key:
    print("❌ Error: STRIPE_API_KEY not set")
    print("   Set it in your .env file or environment")
    sys.exit(1)


def create_products_and_prices():
    """Create Stripe products and prices for all tiers."""

    print("🚀 Setting up Stripe products and prices...\n")

    tiers = [
        {
            "id": "professional",
            "name": "Encypher Professional",
            "description": (
                "For growing publishers who need sentence-level tracking, streaming signing, BYOK, and better coalition revenue share (70/30)."
            ),
            "price_monthly_cents": 9900,  # $99
            "price_annual_cents": 95000,  # $950
            "features": [
                "Sentence-level tracking (50K/month)",
                "Invisible embeddings",
                "Streaming signing (WebSocket/SSE)",
                "10 API keys",
                "Email support (48hr SLA)",
                "90-day analytics",
                "BYOK encryption",
                "WordPress Pro (no branding)",
                "70/30 coalition revenue share",
            ],
        },
        {
            "id": "business",
            "name": "Encypher Business",
            "description": (
                "For major publishers who need Merkle infrastructure, plagiarism detection, team features, and best coalition revenue share (75/25)."
            ),
            "price_monthly_cents": 49900,  # $499
            "price_annual_cents": 479000,  # $4790
            "features": [
                "Everything in Professional",
                "Merkle tree encoding",
                "Source attribution API",
                "Plagiarism detection",
                "Batch operations (100 docs)",
                "50 API keys",
                "Priority support (24hr SLA)",
                "1-year analytics",
                "Team management (10 users)",
                "Audit logs",
                "75/25 coalition revenue share",
            ],
        },
    ]

    results = {}

    for tier in tiers:
        print(f"📦 Creating {tier['name']}...")

        try:
            # Check if product already exists
            existing_products = stripe.Product.search(query=f"metadata['tier_id']:'{tier['id']}'")

            if existing_products.data:
                product = existing_products.data[0]
                print(f"   ℹ️  Product already exists: {product.id}")
            else:
                # Create product
                product = stripe.Product.create(
                    name=tier["name"],
                    description=tier["description"],
                    metadata={"tier_id": tier["id"]},
                    features=[{"name": f} for f in tier["features"][:8]],  # Stripe limits to 8
                )
                print(f"   ✅ Created product: {product.id}")

            # Check for existing prices
            existing_prices = stripe.Price.list(product=product.id, active=True)
            existing_monthly = None
            existing_annual = None

            for price in existing_prices.data:
                if price.recurring and price.recurring.interval == "month":
                    existing_monthly = price
                elif price.recurring and price.recurring.interval == "year":
                    existing_annual = price

            # Create monthly price if not exists
            if existing_monthly:
                price_monthly = existing_monthly
                print(f"   ℹ️  Monthly price exists: {price_monthly.id}")
            else:
                price_monthly = stripe.Price.create(
                    product=product.id,
                    unit_amount=tier["price_monthly_cents"],
                    currency="usd",
                    recurring={"interval": "month"},
                    metadata={"tier_id": tier["id"], "billing_cycle": "monthly"},
                )
                print(f"   ✅ Created monthly price: {price_monthly.id}")

            # Create annual price if not exists
            if existing_annual:
                price_annual = existing_annual
                print(f"   ℹ️  Annual price exists: {price_annual.id}")
            else:
                price_annual = stripe.Price.create(
                    product=product.id,
                    unit_amount=tier["price_annual_cents"],
                    currency="usd",
                    recurring={"interval": "year"},
                    metadata={"tier_id": tier["id"], "billing_cycle": "annual"},
                )
                print(f"   ✅ Created annual price: {price_annual.id}")

            results[tier["id"]] = {
                "product_id": product.id,
                "price_monthly": price_monthly.id,
                "price_annual": price_annual.id,
            }

            print()

        except stripe.error.StripeError as e:
            print(f"   ❌ Error: {e}")
            continue

    return results


def create_billing_portal_config():
    """Create or update the Stripe Billing Portal configuration."""

    print("🔧 Configuring Billing Portal...")

    try:
        # Check for existing configuration
        configs = stripe.billing_portal.Configuration.list(limit=1)

        portal_config = {
            "business_profile": {
                "headline": "Manage your Encypher subscription",
            },
            "features": {
                "customer_update": {
                    "enabled": True,
                    "allowed_updates": ["email", "address", "phone", "tax_id"],
                },
                "invoice_history": {"enabled": True},
                "payment_method_update": {"enabled": True},
                "subscription_cancel": {
                    "enabled": True,
                    "mode": "at_period_end",
                    "proration_behavior": "none",
                },
                "subscription_update": {
                    "enabled": True,
                    "default_allowed_updates": ["price"],
                    "proration_behavior": "create_prorations",
                },
            },
        }

        if configs.data:
            config = stripe.billing_portal.Configuration.modify(configs.data[0].id, **portal_config)
            print(f"   ✅ Updated portal configuration: {config.id}")
        else:
            config = stripe.billing_portal.Configuration.create(**portal_config)
            print(f"   ✅ Created portal configuration: {config.id}")

        return config.id

    except stripe.error.StripeError as e:
        print(f"   ❌ Error configuring portal: {e}")
        return None


def print_env_config(results):
    """Print the environment configuration to add to .env file."""

    print("\n" + "=" * 60)
    print("📋 Add these to your .env file:")
    print("=" * 60 + "\n")

    if "professional" in results:
        print(f"STRIPE_PRICE_PROFESSIONAL_MONTHLY={results['professional']['price_monthly']}")
        print(f"STRIPE_PRICE_PROFESSIONAL_ANNUAL={results['professional']['price_annual']}")

    if "business" in results:
        print(f"STRIPE_PRICE_BUSINESS_MONTHLY={results['business']['price_monthly']}")
        print(f"STRIPE_PRICE_BUSINESS_ANNUAL={results['business']['price_annual']}")

    print("\n" + "=" * 60)
    print("🔗 Webhook Configuration:")
    print("=" * 60)
    print("""
1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter your webhook URL:
   - Production: https://api.encypherai.com/api/v1/webhooks/stripe
   - Development: Use Stripe CLI or ngrok
4. Select events to listen for:
   - checkout.session.completed
   - customer.subscription.created
   - customer.subscription.updated
   - customer.subscription.deleted
   - invoice.paid
   - invoice.payment_failed
5. Copy the webhook signing secret to STRIPE_WEBHOOK_SECRET
""")

    print("=" * 60)
    print("🎉 Stripe setup complete!")
    print("=" * 60)


def main():
    print("\n" + "=" * 60)
    print("🔧 Encypher Stripe Setup")
    print("=" * 60 + "\n")

    # Check if we're in test mode
    if stripe.api_key.startswith("sk_test_"):
        print("⚠️  Running in TEST mode\n")
    elif stripe.api_key.startswith("sk_live_"):
        print("🔴 Running in LIVE mode - be careful!\n")
        response = input("Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            sys.exit(0)

    # Create products and prices
    results = create_products_and_prices()

    # Configure billing portal
    create_billing_portal_config()

    # Print configuration
    print_env_config(results)


if __name__ == "__main__":
    main()
