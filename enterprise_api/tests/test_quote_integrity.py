"""Tests for POST /api/v1/verify/quote-integrity endpoint."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

# ---------------------------------------------------------------------------
# 1. Request model structure
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_quote_integrity_request_structure(async_client: AsyncClient) -> None:
    """Valid request body is accepted and returns 200."""
    response = await async_client.post(
        "/api/v1/verify/quote-integrity",
        json={
            "quote": "The economy grew by 3.2% last quarter.",
            "attribution": "According to Reuters",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "data" in body
    assert "correlation_id" in body


# ---------------------------------------------------------------------------
# 2. Response model structure
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_quote_integrity_response_structure(async_client: AsyncClient) -> None:
    """Response contains all required QuoteIntegrityResponse fields."""
    response = await async_client.post(
        "/api/v1/verify/quote-integrity",
        json={
            "quote": "Some quote text",
            "attribution": "According to AP News",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "verdict" in data
    assert "similarity_score" in data
    assert "confidence" in data
    assert "explanation" in data
    assert "matched_document" in data
    assert "matched_excerpt" in data
    assert "merkle_proof" in data


# ---------------------------------------------------------------------------
# 3. Verdict: accurate (high similarity)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_verdict_accurate_high_similarity(async_client: AsyncClient) -> None:
    """When similarity >= 0.95, verdict is 'accurate' with 'high' confidence."""
    from app.database import get_content_db

    mock_session = AsyncMock()

    # Simulate a ContentReference row with text_content nearly identical to the quote
    mock_ref = MagicMock()
    mock_ref.text_content = "The economy grew by 3.2% last quarter."
    mock_ref.document_id = "doc_123"
    mock_ref.organization_id = "org_reuters"
    mock_ref.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

    # First execute call: ContentReference query returns our mock ref
    mock_result_refs = MagicMock()
    mock_result_refs.scalars.return_value.all.return_value = [mock_ref]

    # Second execute call: MerkleRoot doc_metadata query
    mock_result_title = MagicMock()
    mock_result_title.scalar_one_or_none.return_value = {"title": "Reuters Q3 Report"}

    mock_session.execute = AsyncMock(side_effect=[mock_result_refs, mock_result_title])

    async def override_content_db():
        yield mock_session

    from app.main import app

    app.dependency_overrides[get_content_db] = override_content_db
    try:
        response = await async_client.post(
            "/api/v1/verify/quote-integrity",
            json={
                "quote": "The economy grew by 3.2% last quarter.",
                "attribution": "According to Reuters",
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["verdict"] == "accurate"
        assert data["confidence"] == "high"
        assert data["similarity_score"] >= 0.95
    finally:
        app.dependency_overrides.pop(get_content_db, None)


# ---------------------------------------------------------------------------
# 4. Verdict: approximate (medium similarity)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_verdict_approximate_medium_similarity(
    async_client: AsyncClient,
) -> None:
    """When similarity is between threshold and 0.95, verdict is 'approximate'."""
    from app.database import get_content_db

    mock_session = AsyncMock()

    mock_ref = MagicMock()
    # Slightly different text to get ~0.85-0.95 similarity
    mock_ref.text_content = "The economy expanded by about 3.2 percent in the last quarter of the year."
    mock_ref.document_id = "doc_456"
    mock_ref.organization_id = "org_ap"
    mock_ref.created_at = datetime(2025, 2, 1, tzinfo=timezone.utc)

    mock_result_refs = MagicMock()
    mock_result_refs.scalars.return_value.all.return_value = [mock_ref]

    mock_result_title = MagicMock()
    mock_result_title.scalar_one_or_none.return_value = None

    mock_session.execute = AsyncMock(side_effect=[mock_result_refs, mock_result_title])

    async def override_content_db():
        yield mock_session

    from app.main import app

    app.dependency_overrides[get_content_db] = override_content_db
    try:
        response = await async_client.post(
            "/api/v1/verify/quote-integrity",
            json={
                "quote": "The economy grew by 3.2% last quarter.",
                "attribution": "According to AP News",
                "fuzzy_threshold": 0.50,
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["verdict"] == "approximate"
        assert data["confidence"] == "medium"
        assert 0.50 <= data["similarity_score"] < 0.95
    finally:
        app.dependency_overrides.pop(get_content_db, None)


# ---------------------------------------------------------------------------
# 5. Verdict: hallucinated (low similarity)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_verdict_hallucinated_low_similarity(
    async_client: AsyncClient,
) -> None:
    """When similarity < threshold, verdict is 'hallucinated'."""
    from app.database import get_content_db

    mock_session = AsyncMock()

    mock_ref = MagicMock()
    mock_ref.text_content = "Completely unrelated content about sports and weather forecasts for tomorrow."
    mock_ref.document_id = "doc_789"
    mock_ref.organization_id = "org_bbc"
    mock_ref.created_at = datetime(2025, 3, 1, tzinfo=timezone.utc)

    mock_result_refs = MagicMock()
    mock_result_refs.scalars.return_value.all.return_value = [mock_ref]

    mock_session.execute = AsyncMock(return_value=mock_result_refs)

    async def override_content_db():
        yield mock_session

    from app.main import app

    app.dependency_overrides[get_content_db] = override_content_db
    try:
        response = await async_client.post(
            "/api/v1/verify/quote-integrity",
            json={
                "quote": "The economy grew by 3.2% last quarter.",
                "attribution": "According to BBC",
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["verdict"] == "hallucinated"
        assert data["confidence"] == "high"
        assert data["similarity_score"] < 0.85
    finally:
        app.dependency_overrides.pop(get_content_db, None)


# ---------------------------------------------------------------------------
# 6. Verdict: unverifiable (no signed content)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_verdict_unverifiable_no_content(async_client: AsyncClient) -> None:
    """When no signed content is found, verdict is 'unverifiable'."""
    from app.database import get_content_db

    mock_session = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    mock_session.execute = AsyncMock(return_value=mock_result)

    async def override_content_db():
        yield mock_session

    from app.main import app

    app.dependency_overrides[get_content_db] = override_content_db
    try:
        response = await async_client.post(
            "/api/v1/verify/quote-integrity",
            json={
                "quote": "Something nobody ever published.",
                "attribution": "According to an unknown source",
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["verdict"] == "unverifiable"
        assert data["confidence"] == "low"
        assert data["similarity_score"] == 0.0
        assert data["matched_document"] is None
        assert data["matched_excerpt"] is None
    finally:
        app.dependency_overrides.pop(get_content_db, None)


# ---------------------------------------------------------------------------
# 7. Request with org_id scope
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_quote_integrity_with_org_id(async_client: AsyncClient) -> None:
    """When org_id is provided, search is scoped to that organization."""
    from app.database import get_content_db

    mock_session = AsyncMock()

    mock_ref = MagicMock()
    mock_ref.text_content = "Inflation fell to 2.1% in December."
    mock_ref.document_id = "doc_org_scoped"
    mock_ref.organization_id = "org_reuters"
    mock_ref.created_at = datetime(2025, 4, 1, tzinfo=timezone.utc)

    mock_result_refs = MagicMock()
    mock_result_refs.scalars.return_value.all.return_value = [mock_ref]

    mock_result_title = MagicMock()
    mock_result_title.scalar_one_or_none.return_value = None

    mock_session.execute = AsyncMock(side_effect=[mock_result_refs, mock_result_title])

    async def override_content_db():
        yield mock_session

    from app.main import app

    app.dependency_overrides[get_content_db] = override_content_db
    try:
        response = await async_client.post(
            "/api/v1/verify/quote-integrity",
            json={
                "quote": "Inflation fell to 2.1% in December.",
                "attribution": "Reuters reported",
                "org_id": "org_reuters",
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["verdict"] == "accurate"
        assert data["matched_document"] is not None
        assert data["matched_document"]["org_id"] == "org_reuters"
    finally:
        app.dependency_overrides.pop(get_content_db, None)


# ---------------------------------------------------------------------------
# 8. Request with doc_id scope
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_quote_integrity_with_doc_id(async_client: AsyncClient) -> None:
    """When doc_id is provided, search is scoped to MerkleLeaf nodes of that document."""
    from app.database import get_content_db

    mock_session = AsyncMock()

    mock_subhash = MagicMock()
    mock_subhash.text_content = "GDP growth reached 4.5% in Q2 2025."
    mock_subhash.node_type = "leaf"

    mock_root = MagicMock()
    mock_root.document_id = "doc_specific"
    mock_root.organization_id = "org_wsj"
    mock_root.created_at = datetime(2025, 5, 1, tzinfo=timezone.utc)

    # First execute: join query returns (subhash, root) tuples
    mock_result_leaves = MagicMock()
    mock_result_leaves.all.return_value = [(mock_subhash, mock_root)]

    # Second execute: doc_metadata query
    mock_result_title = MagicMock()
    mock_result_title.scalar_one_or_none.return_value = {"title": "WSJ Q2 Analysis"}

    mock_session.execute = AsyncMock(side_effect=[mock_result_leaves, mock_result_title])

    async def override_content_db():
        yield mock_session

    from app.main import app

    app.dependency_overrides[get_content_db] = override_content_db
    try:
        response = await async_client.post(
            "/api/v1/verify/quote-integrity",
            json={
                "quote": "GDP growth reached 4.5% in Q2 2025.",
                "attribution": "Wall Street Journal",
                "doc_id": "doc_specific",
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["verdict"] == "accurate"
        assert data["matched_document"]["id"] == "doc_specific"
        assert data["matched_document"]["title"] == "WSJ Q2 Analysis"
    finally:
        app.dependency_overrides.pop(get_content_db, None)


# ---------------------------------------------------------------------------
# 9. Explanation text is human-readable
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_quote_integrity_explanation_text(async_client: AsyncClient) -> None:
    """Explanation field contains a human-readable string."""
    response = await async_client.post(
        "/api/v1/verify/quote-integrity",
        json={
            "quote": "Any quote text here.",
            "attribution": "Some source",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    explanation = data["explanation"]
    assert isinstance(explanation, str)
    assert len(explanation) > 10


# ---------------------------------------------------------------------------
# 10. Custom fuzzy_threshold is respected
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_quote_integrity_custom_threshold(async_client: AsyncClient) -> None:
    """Custom fuzzy_threshold changes verdict boundaries."""
    from app.database import get_content_db

    mock_session = AsyncMock()

    # Text that gives ~0.65 similarity with the quote
    mock_ref = MagicMock()
    mock_ref.text_content = "The economy grew modestly and steadily through last quarter according to initial estimates."
    mock_ref.document_id = "doc_threshold"
    mock_ref.organization_id = "org_ft"
    mock_ref.created_at = datetime(2025, 6, 1, tzinfo=timezone.utc)

    mock_result_refs = MagicMock()
    mock_result_refs.scalars.return_value.all.return_value = [mock_ref]

    mock_result_title = MagicMock()
    mock_result_title.scalar_one_or_none.return_value = None

    mock_session.execute = AsyncMock(side_effect=[mock_result_refs, mock_result_title])

    async def override_content_db():
        yield mock_session

    from app.main import app

    app.dependency_overrides[get_content_db] = override_content_db
    try:
        # With a low threshold of 0.40, this should be "approximate" not "hallucinated"
        response = await async_client.post(
            "/api/v1/verify/quote-integrity",
            json={
                "quote": "The economy grew by 3.2% last quarter.",
                "attribution": "Financial Times",
                "fuzzy_threshold": 0.40,
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        # With threshold=0.40 and similarity likely ~0.5-0.7, should be "approximate"
        assert data["verdict"] in ("approximate", "accurate")
        assert data["similarity_score"] >= 0.40
    finally:
        app.dependency_overrides.pop(get_content_db, None)
