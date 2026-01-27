"""
Helpers for ensuring organization records exist for demo/user contexts.
"""

from __future__ import annotations

import logging
from typing import Dict

from app.config import settings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def _should_bootstrap(org_id: str, organization: Dict) -> bool:
    if settings.compose_org_context_via_auth_service:
        return True
    if org_id.startswith("user_"):
        return True
    if organization.get("is_demo", False):
        return True
    if org_id.startswith("org_encypher"):
        return True
    return False


def _derive_email(org_id: str) -> str:
    if org_id.startswith("user_"):
        return f"{org_id}@personal.local"
    return f"{org_id}@demo.local"


async def ensure_organization_exists(db: AsyncSession, organization: Dict) -> bool:
    org_id = organization.get("organization_id")
    if not org_id:
        return False

    if not _should_bootstrap(org_id, organization):
        return False

    result = await db.execute(text("SELECT id FROM organizations WHERE id = :org_id"), {"org_id": org_id})
    if result.scalar_one_or_none():
        return False

    name = organization.get("organization_name") or "Demo Organization"
    tier = organization.get("tier") or "starter"
    monthly_api_limit = organization.get("monthly_api_limit", 10000)
    monthly_api_usage = organization.get("monthly_api_usage", 0)
    coalition_member = organization.get("coalition_member", True)
    coalition_rev_share = organization.get("coalition_rev_share", 65)
    email = organization.get("email") or _derive_email(org_id)

    await db.execute(
        text(
            """
            INSERT INTO organizations (
                id, name, email, tier, monthly_api_limit, monthly_api_usage,
                coalition_member, coalition_rev_share, created_at, updated_at
            )
            VALUES (
                :id, :name, :email, :tier, :monthly_api_limit, :monthly_api_usage,
                :coalition_member, :coalition_rev_share, NOW(), NOW()
            )
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {
            "id": org_id,
            "name": name,
            "email": email,
            "tier": tier,
            "monthly_api_limit": monthly_api_limit,
            "monthly_api_usage": monthly_api_usage,
            "coalition_member": coalition_member,
            "coalition_rev_share": coalition_rev_share,
        },
    )
    await db.flush()
    logger.info("Bootstrapped missing organization record for %s", org_id)
    return True
