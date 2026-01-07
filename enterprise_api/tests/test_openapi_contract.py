import json

import pytest

from app.main import public_openapi


@pytest.mark.asyncio
async def test_public_openapi_includes_sign_advanced() -> None:
    """Verify /sign/advanced is in public OpenAPI and legacy embeddings endpoints are removed."""
    resp = await public_openapi()
    assert resp.status_code == 200

    payload = json.loads(resp.body.decode("utf-8"))
    paths = payload.get("paths", {})

    # /sign/advanced should be present
    assert "/api/v1/sign/advanced" in paths

    # Legacy embeddings endpoints should NOT be present (removed in 1.0)
    legacy_encode = "/api/v1/enterprise/embeddings/encode-with-embeddings"
    legacy_sign_advanced = "/api/v1/enterprise/embeddings/sign/advanced"

    assert legacy_encode not in paths, "Legacy encode-with-embeddings endpoint should be removed"
    assert legacy_sign_advanced not in paths, "Legacy embeddings/sign/advanced endpoint should be removed"
