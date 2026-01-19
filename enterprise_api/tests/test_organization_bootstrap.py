from __future__ import annotations

import pytest
from sqlalchemy import text

from app.services.organization_bootstrap import ensure_organization_exists


@pytest.mark.asyncio
async def test_ensure_organization_exists_creates_demo_org(db) -> None:
    org_id = "org_demo_bootstrap"
    organization = {
        "organization_id": org_id,
        "organization_name": "Bootstrap Demo Org",
        "tier": "starter",
        "is_demo": True,
        "features": {},
        "monthly_api_limit": 50000,
        "monthly_api_usage": 0,
        "coalition_member": False,
        "coalition_rev_share": 0,
    }

    await ensure_organization_exists(db, organization)

    result = await db.execute(
        text("SELECT id, name, email, tier FROM organizations WHERE id = :org_id"),
        {"org_id": org_id},
    )
    row = result.first()

    assert row is not None
    assert row.id == org_id
    assert row.name == "Bootstrap Demo Org"
    assert row.tier == "starter"


@pytest.mark.asyncio
async def test_ensure_organization_exists_creates_user_org(db) -> None:
    org_id = "user_bootstrap_123"
    organization = {
        "organization_id": org_id,
        "organization_name": "Personal Account",
        "tier": "enterprise",
        "is_demo": True,
        "features": {"is_super_admin": True},
        "monthly_api_limit": -1,
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": 65,
    }

    await ensure_organization_exists(db, organization)

    result = await db.execute(
        text("SELECT id, name, email, tier FROM organizations WHERE id = :org_id"),
        {"org_id": org_id},
    )
    row = result.first()

    assert row is not None
    assert row.id == org_id
    assert row.name == "Personal Account"
    assert row.tier == "enterprise"
