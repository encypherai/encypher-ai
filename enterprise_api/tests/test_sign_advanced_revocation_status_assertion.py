from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_sign_advanced_embeds_status_list_assertion(
    async_client: AsyncClient,
    business_auth_headers: dict,
) -> None:
    mock_merkle_root = SimpleNamespace(id="mrk_status", root_hash="root", leaf_count=1, tree_depth=1)

    class _FakeSegmenter:
        def __init__(self, text: str, include_words: bool = False):
            self._text = text

        def get_segments(self, level: str):
            return [self._text]

    allocate_mock = AsyncMock(
        return_value=(1, 7, "https://status.encypherai.com/v1/org_business/list/1")
    )

    with (
        patch("app.utils.quota.QuotaManager.check_quota", new=AsyncMock(return_value=True)),
        patch(
            "app.services.embedding_executor.status_service.allocate_status_index",
            new=allocate_mock,
        ),
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
            "/api/v1/sign/advanced",
            json={
                "document_id": "doc_adv_status_001",
                "text": "Hello world.",
                "segmentation_level": "sentence",
            },
            headers=business_auth_headers,
        )

    assert response.status_code == 201

    allocate_kwargs = allocate_mock.call_args.kwargs
    assert allocate_kwargs["organization_id"] == "org_business"
    assert allocate_kwargs["document_id"] == "doc_adv_status_001"

    called_assertions = mock_create.call_args.kwargs.get("custom_assertions")
    assert called_assertions is not None
    assert any(
        assertion.get("label") == "org.encypher.status"
        and assertion.get("data", {}).get("statusListCredential") == "https://status.encypherai.com/v1/org_business/list/1"
        and str(assertion.get("data", {}).get("statusListIndex")) == "7"
        for assertion in called_assertions
    )
