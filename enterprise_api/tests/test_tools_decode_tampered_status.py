from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_tools_decode_maps_tampered_status_to_failure(async_client: AsyncClient) -> None:
    multi_result = SimpleNamespace(
        total_found=2,
        embeddings=[
            SimpleNamespace(signer_id="org_demo"),
            SimpleNamespace(signer_id="org_demo"),
        ],
    )

    verified_result = SimpleNamespace(
        total_found=2,
        embeddings=[
            SimpleNamespace(
                index=0,
                signature_valid=True,
                content_hash_valid=False,
                verification_status="Tampered",
                metadata={"custom_metadata": {"leaf_index": 0}},
                signer_id="org_demo",
                signer_name="Demo Org",
                span=(0, 10),
                segment_text="segment-one",
                error="Content has been modified.",
            ),
            SimpleNamespace(
                index=1,
                signature_valid=True,
                content_hash_valid=True,
                verification_status="Success",
                metadata={"custom_metadata": {"leaf_index": 1}},
                signer_id="org_demo",
                signer_name="Demo Org",
                span=(11, 20),
                segment_text="segment-two",
                error=None,
            ),
        ],
        all_valid=False,
        any_valid=True,
    )

    with (
        patch("app.routers.tools._get_demo_keys", return_value=(object(), object())),
        patch("app.routers.tools.extract_all_embeddings", return_value=multi_result),
        patch("app.routers.tools.load_organization_public_key", new=AsyncMock(return_value=object())),
        patch(
            "app.routers.tools.extract_and_verify_all_embeddings",
            new=AsyncMock(return_value=verified_result),
        ),
    ):
        response = await async_client.post(
            "/api/v1/tools/decode",
            json={"encoded_text": "payload"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["verification_status"] == "Failure"
    assert payload["embeddings_found"] == 2
    assert payload["all_embeddings"][0]["verification_status"] == "Failure"
    assert payload["all_embeddings"][0]["verdict"]["tampered"] is True
    assert payload["all_embeddings"][0]["verdict"]["valid"] is False
