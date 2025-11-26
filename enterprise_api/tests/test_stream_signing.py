"""
Tests for stream signing endpoint.

Tests the SSE-based streaming signing endpoint at /api/v1/stream/sign.
"""
import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.response_models import SignResponse
from app.dependencies import require_sign_permission


@pytest.mark.asyncio
async def fake_execute_signing(*, document_id, **_):
    """Mock signing executor for testing."""
    return SignResponse(
        success=True,
        document_id=document_id,
        signed_text="signed-content",
        total_sentences=1,
        verification_url="http://verify.local",
    )


def override_sign_permission():
    """Override authentication for testing."""
    return {
        "organization_id": "org_test",
        "organization_name": "Test Org",
        "api_key": "demo",
        "is_demo": True,
    }


def test_stream_signing_sends_events(monkeypatch):
    """Test that stream signing sends SSE events correctly."""
    from app.routers import streaming

    app.dependency_overrides[require_sign_permission] = override_sign_permission
    monkeypatch.setattr(streaming, "execute_signing", fake_execute_signing)

    client = TestClient(app)
    response = client.post(
        "/api/v1/stream/sign",  # Correct path with API prefix
        json={"document_id": "doc-stream", "text": "hello streaming"},
        headers={"Authorization": "Bearer demo"},
    )
    
    # Parse SSE events
    events = [block.strip() for block in response.text.strip().split("\n\n") if block.strip()]
    
    # Should have start event
    assert events[0].startswith("event: start")
    
    # Should have final event
    assert any(block.startswith("event: final") for block in events)

    # Parse final payload
    payload_line = next(line for line in events[-1].splitlines() if line.startswith("data:"))
    payload = json.loads(payload_line.removeprefix("data: ").strip())
    assert payload["document_id"] == "doc-stream"
    assert payload["status"] == "final"

    app.dependency_overrides.pop(require_sign_permission, None)


def test_stream_signing_requires_auth():
    """Test that stream signing requires authentication."""
    client = TestClient(app)
    response = client.post(
        "/api/v1/stream/sign",
        json={"document_id": "doc-test", "text": "test content"},
        # No auth header
    )
    
    # Should return 401 or 403
    assert response.status_code in [401, 403]
