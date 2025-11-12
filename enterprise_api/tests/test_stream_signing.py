import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.response_models import SignResponse
from app.routers.streaming import require_sign_permission


@pytest.mark.asyncio
async def fake_execute_signing(*, document_id, **_):
    return SignResponse(
        success=True,
        document_id=document_id,
        signed_text="signed-content",
        total_sentences=1,
        verification_url="http://verify.local",
    )


def override_sign_permission():
    return {
        "organization_id": "org_test",
        "organization_name": "Test Org",
        "api_key": "demo",
        "is_demo": True,
    }


def test_stream_signing_sends_events(monkeypatch):
    from app.routers import streaming

    app.dependency_overrides[require_sign_permission] = override_sign_permission
    monkeypatch.setattr(streaming, "execute_signing", fake_execute_signing)

    client = TestClient(app)
    response = client.post(
        "/stream/sign",
        json={"document_id": "doc-stream", "text": "hello streaming"},
        headers={"Authorization": "Bearer demo"},
    )
    events = [block.strip() for block in response.text.strip().split("\n\n") if block.strip()]
    assert events[0].startswith("event: start")
    assert any(block.startswith("event: final") for block in events)

    payload_line = next(line for line in events[-1].splitlines() if line.startswith("data:"))
    payload = json.loads(payload_line.removeprefix("data: ").strip())
    assert payload["document_id"] == "doc-stream"
    assert payload["status"] == "final"

    app.dependency_overrides.pop(require_sign_permission, None)
