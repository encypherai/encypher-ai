import pytest
from fastapi.openapi.utils import get_openapi
from fastapi import HTTPException

from app.dependencies import require_super_admin
from app.main import app, docs_landing, public_openapi

@pytest.mark.asyncio
async def test_docs_landing_page_is_branded_with_swagger() -> None:
    resp = await docs_landing()
    assert resp.status_code == 200
    assert "text/html" in resp.media_type
    body = resp.body.decode("utf-8")
    # Branded header with logo (now served from encypherai.com)
    assert "https://encypherai.com/encypher_full_logo_white.svg" in body
    assert "Enterprise API" in body
    # Design system CSS
    assert "/docs/assets/design-system.css" in body
    # Swagger UI embedded
    assert "swagger-ui" in body
    assert "/docs/openapi.json" in body


@pytest.mark.asyncio
async def test_public_openapi_excludes_internal_tags() -> None:
    resp = await public_openapi()
    assert resp.status_code == 200
    data = resp.body
    assert isinstance(data, (bytes, bytearray))
    text = data.decode("utf-8")
    assert "/api/v1/licensing/agreements" not in text
    assert "/api/v1/provisioning/auto-provision" not in text


@pytest.mark.asyncio
async def test_internal_openapi_exists_and_full_spec_includes_licensing() -> None:
    # We can't exercise dependency injection here without spinning up the app.
    # Instead, assert the internal schema (full spec) contains licensing routes.
    base = get_openapi(
        title=f"{app.title} (Internal)",
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    assert "/api/v1/licensing/agreements" in base.get("paths", {})


@pytest.mark.asyncio
async def test_openapi_does_not_advertise_deprecated_tools_endpoints() -> None:
    public_resp = await public_openapi()
    assert public_resp.status_code == 200
    public_text = public_resp.body.decode("utf-8")
    assert "/api/v1/tools/encode" not in public_text
    assert "/api/v1/tools/decode" not in public_text

    internal = get_openapi(
        title=f"{app.title} (Internal)",
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    assert "/api/v1/tools/encode" not in internal.get("paths", {})
    assert "/api/v1/tools/decode" not in internal.get("paths", {})


@pytest.mark.asyncio
async def test_require_super_admin_enforces_feature_flag() -> None:
    with pytest.raises(HTTPException):
        await require_super_admin({"organization_id": "org_test", "features": {"is_super_admin": False}})

    org = await require_super_admin({"organization_id": "org_test", "features": {"is_super_admin": True}})
    assert org["organization_id"] == "org_test"
