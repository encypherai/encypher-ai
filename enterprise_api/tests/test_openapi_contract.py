import json

import pytest

from app.main import public_openapi


@pytest.mark.asyncio
async def test_public_openapi_includes_sign_advanced_and_deprecates_legacy_embeddings() -> None:
    resp = await public_openapi()
    assert resp.status_code == 200

    payload = json.loads(resp.body.decode("utf-8"))
    paths = payload.get("paths", {})

    assert "/api/v1/sign/advanced" in paths

    legacy_encode = "/api/v1/enterprise/embeddings/encode-with-embeddings"
    legacy_sign_advanced = "/api/v1/enterprise/embeddings/sign/advanced"

    assert legacy_encode in paths
    assert legacy_sign_advanced in paths

    assert paths[legacy_encode]["post"].get("deprecated") is True
    assert paths[legacy_sign_advanced]["post"].get("deprecated") is True
