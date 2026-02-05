from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_sign_advanced_embeds_rights_assertion(
    async_client: AsyncClient,
    business_auth_headers: dict,
) -> None:
    mock_merkle_root = SimpleNamespace(id="mrk_rights", root_hash="root", leaf_count=1, tree_depth=1)

    class _FakeSegmenter:
        def __init__(self, text: str, include_words: bool = False):
            self._text = text

        def get_segments(self, level: str):
            return [self._text]

    with (
        patch(
            "app.services.embedding_executor.MerkleService.encode_document",
            new=AsyncMock(return_value={"sentence": mock_merkle_root}),
        ),
        patch("app.utils.segmentation.HierarchicalSegmenter", new=_FakeSegmenter),
        patch(
            "app.services.embedding_service.EmbeddingService.create_embeddings",
            new=AsyncMock(return_value=([], "signed")),
        ) as mock_create,
    ):
        response = await async_client.post(
            "/api/v1/sign",
            json={
                "text": "Hello world.",
                "options": {
                    "segmentation_level": "sentence",
                    "rights": {
                        "copyright_holder": "Example Publisher",
                        "license_url": "https://example.com/license",
                        "syndication_allowed": False,
                    },
                },
            },
            headers=business_auth_headers,
        )

    assert response.status_code == 201

    called_assertions = mock_create.call_args.kwargs.get("custom_assertions")
    assert called_assertions is not None
    assert any(
        assertion.get("label") == "com.encypher.rights.v1" and assertion.get("data", {}).get("copyright_holder") == "Example Publisher"
        for assertion in called_assertions
    )
