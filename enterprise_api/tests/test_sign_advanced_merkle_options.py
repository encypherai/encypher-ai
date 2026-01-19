from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, call, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_sign_advanced_multi_level_merkle_enforces_quota_and_returns_merkle_trees(
    async_client: AsyncClient,
    business_auth_headers: dict,
) -> None:
    mock_sentence_root = SimpleNamespace(id="mrk_sentence", root_hash="root_sentence", leaf_count=2, tree_depth=1)
    mock_paragraph_root = SimpleNamespace(id="mrk_paragraph", root_hash="root_paragraph", leaf_count=1, tree_depth=1)

    class _FakeSegmenter:
        def __init__(self, text: str, include_words: bool = False):
            self._text = text

        def get_segments(self, level: str):
            if level == "sentence":
                return ["Hello world.", "Second sentence."]
            if level == "paragraph":
                return ["Hello world. Second sentence."]
            return [self._text]

    check_quota = AsyncMock(return_value=True)

    with (
        patch("app.utils.quota.QuotaManager.check_quota", new=check_quota),
        patch(
            "app.services.embedding_executor.MerkleService.encode_document",
            new=AsyncMock(return_value={"sentence": mock_sentence_root, "paragraph": mock_paragraph_root}),
        ),
        patch("app.utils.segmentation.HierarchicalSegmenter", new=_FakeSegmenter),
        patch(
            "app.services.embedding_service.EmbeddingService.create_embeddings",
            new=AsyncMock(return_value=([], "signed")),
        ),
    ):
        response = await async_client.post(
            "/api/v1/sign/advanced",
            json={
                "document_id": "doc_adv_merkle_001",
                "text": "Hello world. Second sentence.",
                "segmentation_level": "sentence",
                "segmentation_levels": ["sentence", "paragraph"],
                "index_for_attribution": True,
            },
            headers=business_auth_headers,
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["success"] is True
    assert payload["document_id"] == "doc_adv_merkle_001"
    assert "merkle_trees" in payload
    assert set(payload["merkle_trees"].keys()) == {"sentence", "paragraph"}

    check_quota.assert_awaited()


@pytest.mark.asyncio
async def test_sign_advanced_merkle_index_opt_out_skips_merkle_quota(
    async_client: AsyncClient,
    business_auth_headers: dict,
) -> None:
    mock_sentence_root = SimpleNamespace(id="mrk_sentence", root_hash="root_sentence", leaf_count=2, tree_depth=1)

    class _FakeSegmenter:
        def __init__(self, text: str, include_words: bool = False):
            self._text = text

        def get_segments(self, level: str):
            return ["Hello world.", "Second sentence."]

    check_quota = AsyncMock(return_value=True)

    with (
        patch("app.utils.quota.QuotaManager.check_quota", new=check_quota),
        patch(
            "app.services.embedding_executor.MerkleService.encode_document",
            new=AsyncMock(return_value={"sentence": mock_sentence_root}),
        ) as encode_mock,
        patch("app.utils.segmentation.HierarchicalSegmenter", new=_FakeSegmenter),
        patch(
            "app.services.embedding_service.EmbeddingService.create_embeddings",
            new=AsyncMock(return_value=([], "signed")),
        ),
    ):
        response = await async_client.post(
            "/api/v1/sign/advanced",
            json={
                "document_id": "doc_adv_merkle_002",
                "text": "Hello world. Second sentence.",
                "segmentation_level": "sentence",
                "segmentation_levels": ["sentence"],
                "index_for_attribution": False,
            },
            headers=business_auth_headers,
        )

    assert response.status_code == 201

    # Should not enforce Merkle indexing quota when opting out.
    called_quota_types = [call.kwargs.get("quota_type") for call in check_quota.await_args_list if call.kwargs.get("quota_type") is not None]
    assert all(str(qt) != "QuotaType.MERKLE_ENCODING" for qt in called_quota_types)

    assert encode_mock.await_count == 1
