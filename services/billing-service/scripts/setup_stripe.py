#!/usr/bin/env python3
"""
Stripe Product & Price Setup CLI

Creates all Stripe products and prices for the current pricing model:
- 9 freemium add-on subscriptions
- 1 one-time add-on (bulk archive backfill)
- 1 usage overage product (for metered billing)
- Billing Portal configuration

Idempotent: searches for existing products by metadata before creating new ones.

Usage:
    # Test mode (default)
    cd services/billing-service
    uv run python scripts/setup_stripe.py

    # Production mode (prompts for confirmation)
    STRIPE_API_KEY=sk_live_... uv run python scripts/setup_stripe.py

    # Dry run (shows what would be created)
    uv run python scripts/setup_stripe.py --dry-run

Prerequisites:
    Set STRIPE_API_KEY in your environment or .env file.
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")

# ---------------------------------------------------------------
# Product catalog -- single source of truth
# ---------------------------------------------------------------

ADD_ON_SUBSCRIPTIONS = [
    {
        "id": "attribution_analytics",
        "name": "Encypher Attribution Analytics",
        "description": "Full dashboard showing where your signed content appears in AI outputs.",
        "price_monthly_cents": 29900,
    },
    {
        "id": "custom_signing_identity",
        "name": "Encypher Custom Signing Identity",
        "description": "Sign content as your brand instead of Encypher Coalition Member.",
        "price_monthly_cents": 2000,
    },
    {
        "id": "white_label_verification",
        "name": "Encypher White-Label Verification",
        "description": "Verification pages hosted on your domain with your branding.",
        "price_monthly_cents": 29900,
    },
    {
        "id": "custom_verification_domain",
        "name": "Encypher Custom Verification Domain",
        "description": "Point a custom domain to your verification pages.",
        "price_monthly_cents": 2900,
    },
    {
        "id": "byok",
        "name": "Encypher BYOK (Bring Your Own Keys)",
        "description": "Use your organization's existing PKI infrastructure and signing certificates.",
        "price_monthly_cents": 49900,
    },
    {
        "id": "priority_support",
        "name": "Encypher Priority Support",
        "description": "Email support with 4-hour response SLA during business hours.",
        "price_monthly_cents": 19900,
    },
    {
        "id": "enforcement_bundle",
        "name": "Encypher Enforcement Bundle",
        "description": "Attribution Analytics + 2 Formal Notices/mo + 1 Evidence Package/mo.",
        "price_monthly_cents": 99900,
    },
    {
        "id": "publisher_identity_bundle",
        "name": "Encypher Publisher Identity Bundle",
        "description": "Custom Signing Identity + White-Label Verification + Custom Domain.",
        "price_monthly_cents": 33900,
    },
    {
        "id": "full_stack_bundle",
        "name": "Encypher Full Stack Bundle",
        "description": "Enforcement Bundle + Publisher Identity Bundle.",
        "price_monthly_cents": 169900,
    },
]

ONE_TIME_PRODUCTS = [
    {
        "id": "bulk_archive_backfill",
        "name": "Encypher Archive Backfill",
        "description": "One-time bulk signing of existing content archive.",
        "price_cents": 1,  # $0.01 per document
        "unit_label": "document",
    },
]

OVERAGE_PRODUCT = {
    "id": "usage_overage",
    "name": "Encypher Usage Overage",
    "description": "Per-unit overage charges for usage beyond plan limits ($0.02/unit).",
    "price_cents": 2,  # $0.02 per unit
}


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------


def find_product_by_metadata(key: str, value: str):
    """Search for an existing Stripe product by metadata key/value."""
    try:
        results = stripe.Product.search(query=f"metadata['{key}']:'{value}'")
        if results.data:
            return results.data[0]
    except stripe.error.StripeError:
        pass
    return None


def find_active_price(product_id: str, recurring_interval: str = None):
    """Find an active price on a product, optionally matching a recurring interval."""
    prices = stripe.Price.list(product=product_id, active=True, limit=10)
    for price in prices.data:
        if recurring_interval:
            if price.recurring and price.recurring.interval == recurring_interval:
                return price
        else:
            # One-time price (no recurring)
            if not price.recurring:
                return price
    return None


def fmt_price(cents: int) -> str:
    return f"${cents / 100:,.2f}"


# ---------------------------------------------------------------
# Setup functions
# ---------------------------------------------------------------


def setup_add_on_subscriptions(dry_run: bool) -> dict:
    """Create or find monthly subscription add-on products."""
    results = {}

    for addon in ADD_ON_SUBSCRIPTIONS:
        existing = find_product_by_metadata("add_on_id", addon["id"])

        if existing:
            product = existing
            print(f"  [exists]  {addon['name']} -> {product.id}")
        elif dry_run:
            print(f"  [dry-run] Would create: {addon['name']} ({fmt_price(addon['price_monthly_cents'])}/mo)")
            results[addon["id"]] = {"product_id": "dry_run", "price_monthly": "dry_run"}
            continue
        else:
            product = stripe.Product.create(
                name=addon["name"],
                description=addon["description"],
                metadata={"add_on_id": addon["id"]},
            )
            print(f"  [created] {addon['name']} -> {product.id}")

        # Find or create monthly price
        price = find_active_price(product.id, "month")
        if price:
            print(f"            Monthly price exists: {price.id} ({fmt_price(price.unit_amount)})")
        elif dry_run:
            print(f"            Would create monthly price: {fmt_price(addon['price_monthly_cents'])}")
            results[addon["id"]] = {"product_id": product.id, "price_monthly": "dry_run"}
            continue
        else:
            price = stripe.Price.create(
                product=product.id,
                unit_amount=addon["price_monthly_cents"],
                currency="usd",
                recurring={"interval": "month"},
                metadata={"add_on_id": addon["id"], "billing_cycle": "monthly"},
            )
            print(f"            Created monthly price: {price.id} ({fmt_price(price.unit_amount)})")

        results[addon["id"]] = {
            "product_id": product.id,
            "price_monthly": price.id,
        }

    return results


def setup_one_time_products(dry_run: bool) -> dict:
    """Create or find one-time purchase products."""
    results = {}

    for product_def in ONE_TIME_PRODUCTS:
        existing = find_product_by_metadata("add_on_id", product_def["id"])

        if existing:
            product = existing
            print(f"  [exists]  {product_def['name']} -> {product.id}")
        elif dry_run:
            print(f"  [dry-run] Would create: {product_def['name']} ({fmt_price(product_def['price_cents'])}/unit)")
            results[product_def["id"]] = {"product_id": "dry_run", "price_unit": "dry_run"}
            continue
        else:
            product = stripe.Product.create(
                name=product_def["name"],
                description=product_def["description"],
                metadata={"add_on_id": product_def["id"]},
                unit_label=product_def.get("unit_label"),
            )
            print(f"  [created] {product_def['name']} -> {product.id}")

        # Find or create one-time price
        price = find_active_price(product.id, None)
        if price:
            print(f"            Unit price exists: {price.id} ({fmt_price(price.unit_amount)})")
        elif dry_run:
            print(f"            Would create unit price: {fmt_price(product_def['price_cents'])}")
            results[product_def["id"]] = {"product_id": product.id, "price_unit": "dry_run"}
            continue
        else:
            price = stripe.Price.create(
                product=product.id,
                unit_amount=product_def["price_cents"],
                currency="usd",
                metadata={"add_on_id": product_def["id"]},
            )
            print(f"            Created unit price: {price.id} ({fmt_price(price.unit_amount)})")

        results[product_def["id"]] = {
            "product_id": product.id,
            "price_unit": price.id,
        }

    return results


def setup_overage_product(dry_run: bool) -> dict:
    """Create or find the usage overage product."""
    existing = find_product_by_metadata("product_type", "overage")

    if existing:
        product = existing
        print(f"  [exists]  {OVERAGE_PRODUCT['name']} -> {product.id}")
    elif dry_run:
        print(f"  [dry-run] Would create: {OVERAGE_PRODUCT['name']} ({fmt_price(OVERAGE_PRODUCT['price_cents'])}/unit)")
        return {"product_id": "dry_run", "price_unit": "dry_run"}
    else:
        product = stripe.Product.create(
            name=OVERAGE_PRODUCT["name"],
            description=OVERAGE_PRODUCT["description"],
            metadata={"product_type": "overage"},
        )
        print(f"  [created] {OVERAGE_PRODUCT['name']} -> {product.id}")

    # Find or create unit price (one-time, not recurring)
    price = find_active_price(product.id, None)
    if price:
        print(f"            Unit price exists: {price.id} ({fmt_price(price.unit_amount)})")
    elif dry_run:
        print(f"            Would create unit price: {fmt_price(OVERAGE_PRODUCT['price_cents'])}")
        return {"product_id": product.id, "price_unit": "dry_run"}
    else:
        price = stripe.Price.create(
            product=product.id,
            unit_amount=OVERAGE_PRODUCT["price_cents"],
            currency="usd",
            metadata={"product_type": "overage"},
        )
        print(f"            Created unit price: {price.id} ({fmt_price(price.unit_amount)})")

    return {"product_id": product.id, "price_unit": price.id}


def setup_billing_portal(subscription_results: dict, dry_run: bool) -> str | None:
    """Create or update the Billing Portal configuration."""
    if dry_run:
        print("  [dry-run] Would configure billing portal")
        return None

    allowed_products = []
    for addon_id, data in subscription_results.items():
        if data.get("price_monthly") and data["price_monthly"] != "dry_run":
            allowed_products.append(
                {
                    "product": data["product_id"],
                    "prices": [data["price_monthly"]],
                }
            )

    if not allowed_products:
        print("  [skip]    No subscription products to configure in portal")
        return None

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
                "products": allowed_products,
            },
        },
    }

    configs = stripe.billing_portal.Configuration.list(limit=1)
    if configs.data:
        config = stripe.billing_portal.Configuration.modify(configs.data[0].id, **portal_config)
        print(f"  [updated] Portal configuration: {config.id}")
    else:
        config = stripe.billing_portal.Configuration.create(**portal_config)
        print(f"  [created] Portal configuration: {config.id}")

    return config.id


# ---------------------------------------------------------------
# Output
# ---------------------------------------------------------------


def print_env_output(subscription_results: dict, one_time_results: dict, overage_result: dict, portal_config_id: str | None):
    """Print .env variables for all created products."""
    print("\n" + "=" * 64)
    print("  Add these to your .env / Railway variables:")
    print("=" * 64 + "\n")

    env_lines = []

    # Add-on subscription prices
    for addon_id, data in subscription_results.items():
        price_id = data.get("price_monthly", "")
        env_name = f"STRIPE_PRICE_{addon_id.upper()}"
        env_lines.append(f"{env_name}={price_id}")

    # One-time product prices
    for product_id, data in one_time_results.items():
        price_id = data.get("price_unit", "")
        env_name = f"STRIPE_PRICE_{product_id.upper()}"
        env_lines.append(f"{env_name}={price_id}")

    # Overage price
    if overage_result.get("price_unit"):
        env_lines.append(f"STRIPE_PRICE_USAGE_OVERAGE={overage_result['price_unit']}")

    # Portal config
    if portal_config_id:
        env_lines.append(f"STRIPE_BILLING_PORTAL_CONFIG_ID={portal_config_id}")

    for line in sorted(env_lines):
        print(f"  {line}")

    print("\n" + "=" * 64)
    print("  Webhook events to subscribe to:")
    print("=" * 64)
    print("""
  checkout.session.completed
  customer.subscription.created
  customer.subscription.updated
  customer.subscription.deleted
  invoice.paid
  invoice.payment_failed
  payment_method.detached
  customer.created

  Endpoint URL:
    Production:  https://api.encypher.com/api/v1/webhooks/stripe
    Development: Use `stripe listen --forward-to localhost:8007/api/v1/webhooks/stripe`
""")


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Set up Stripe products and prices for Encypher")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without making changes")
    args = parser.parse_args()

    if not stripe.api_key:
        print("Error: STRIPE_API_KEY not set")
        print("Set it in your .env file or environment")
        sys.exit(1)

    is_live = stripe.api_key.startswith("sk_live_")

    print("\n" + "=" * 64)
    print("  Encypher Stripe Setup")
    if args.dry_run:
        print("  (DRY RUN -- no changes will be made)")
    print("=" * 64)

    if is_live:
        print("\n  ** LIVE MODE ** -- This will create real products.\n")
        response = input("  Continue? (yes/no): ").strip()
        if response.lower() != "yes":
            print("  Aborted.")
            sys.exit(0)
    else:
        print("\n  Running in TEST mode\n")

    # 1. Subscription add-ons
    print("\n-- Subscription Add-ons --")
    subscription_results = setup_add_on_subscriptions(args.dry_run)

    # 2. One-time products
    print("\n-- One-time Products --")
    one_time_results = setup_one_time_products(args.dry_run)

    # 3. Overage product
    print("\n-- Usage Overage --")
    overage_result = setup_overage_product(args.dry_run)

    # 4. Billing portal
    print("\n-- Billing Portal --")
    portal_config_id = setup_billing_portal(subscription_results, args.dry_run)

    # 5. Output
    print_env_output(subscription_results, one_time_results, overage_result, portal_config_id)

    print("Done.\n")


if __name__ == "__main__":
    main()
