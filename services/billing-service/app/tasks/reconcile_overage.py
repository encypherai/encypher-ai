"""
Monthly overage reconciliation job.

Fetches unbilled overage records from enterprise_api, creates Stripe invoices
per organization, and marks records as billed.
"""

import logging
from collections import defaultdict

import httpx
import stripe

from ..core.config import settings

logger = logging.getLogger(__name__)


async def reconcile_monthly_overage() -> dict:
    """
    Reconcile monthly overage charges for all organizations.

    1. Fetch unbilled overage records from enterprise_api.
    2. Group by organization_id.
    3. For each org, look up stripe_customer_id via auth-service.
    4. Create Stripe InvoiceItems + Invoice per org.
    5. Mark records as billed via enterprise_api.
    6. Trigger quota reset via enterprise_api.

    Returns a summary dict.
    """
    headers = {}
    if settings.INTERNAL_SERVICE_TOKEN:
        headers["X-Internal-Token"] = settings.INTERNAL_SERVICE_TOKEN

    async with httpx.AsyncClient(timeout=30) as client:
        # 1. Fetch unbilled records
        resp = await client.post(
            f"{settings.ENTERPRISE_API_URL}/api/v1/internal/usage/unbilled",
            headers=headers,
        )
        resp.raise_for_status()
        records = resp.json().get("records", [])

        if not records:
            logger.info("reconcile_overage: no unbilled records found")
            return {"invoices_created": 0, "organizations": 0}

        # 2. Group by organization_id
        by_org = defaultdict(list)
        for record in records:
            by_org[record["organization_id"]].append(record)

        invoices_created = 0

        for org_id, org_records in by_org.items():
            try:
                # 3. Look up stripe_customer_id from auth-service
                org_resp = await client.get(
                    f"{settings.AUTH_SERVICE_URL}/api/v1/organizations/internal/{org_id}",
                    headers=headers,
                )
                if org_resp.status_code != 200:
                    logger.warning(
                        "reconcile_overage: could not fetch org %s from auth-service: %s",
                        org_id,
                        org_resp.status_code,
                    )
                    continue

                org_data = org_resp.json()
                stripe_customer_id = org_data.get("data", {}).get("stripe_customer_id") or org_data.get("stripe_customer_id")
                if not stripe_customer_id:
                    logger.warning("reconcile_overage: org %s has no stripe_customer_id", org_id)
                    continue

                # 4. Create InvoiceItems for each metric with overage
                record_ids = []
                for record in org_records:
                    overage_cents = record.get("overage_amount_cents", 0)
                    if overage_cents <= 0:
                        continue
                    metric = record.get("metric", "unknown")
                    stripe.InvoiceItem.create(
                        customer=stripe_customer_id,
                        amount=overage_cents,
                        currency="usd",
                        description=f"Encypher usage overage: {metric} ({record.get('overage_count', 0)} units @ ${record.get('rate_cents', 0) / 100:.2f}/unit)",
                        metadata={
                            "organization_id": org_id,
                            "metric": metric,
                            "record_id": record["id"],
                        },
                    )
                    record_ids.append(record["id"])

                if not record_ids:
                    continue

                # Create and finalize the invoice
                invoice = stripe.Invoice.create(
                    customer=stripe_customer_id,
                    auto_advance=True,
                    metadata={"organization_id": org_id, "type": "overage"},
                    description="Encypher monthly usage overage charges",
                )

                # 5. Mark records as billed
                mark_resp = await client.post(
                    f"{settings.ENTERPRISE_API_URL}/api/v1/internal/usage/mark-billed",
                    headers=headers,
                    json={"record_ids": record_ids, "invoice_id": invoice.id},
                )
                mark_resp.raise_for_status()

                invoices_created += 1
                logger.info(
                    "reconcile_overage: created invoice %s for org %s (%d records)",
                    invoice.id,
                    org_id,
                    len(record_ids),
                )

            except Exception:
                logger.exception("reconcile_overage: failed for org %s", org_id)
                continue

        # 6. Trigger quota reset
        try:
            reset_resp = await client.post(
                f"{settings.ENTERPRISE_API_URL}/api/v1/internal/quotas/reset",
                headers=headers,
            )
            reset_resp.raise_for_status()
            logger.info("reconcile_overage: monthly quotas reset")
        except Exception:
            logger.exception("reconcile_overage: failed to reset quotas")

    summary = {
        "invoices_created": invoices_created,
        "organizations": len(by_org),
        "total_records": len(records),
    }
    logger.info("reconcile_overage: completed %s", summary)
    return summary
