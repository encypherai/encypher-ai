import json
import httpx
import pytest

from encypher_enterprise import EncypherClient
from encypher_enterprise.exceptions import AuthenticationError
from encypher_enterprise.models import SignResponse, VerifyResponse, LookupResponse, StatsResponse, UsageStats


def _setup_mock_client(monkeypatch, handler) -> EncypherClient:
    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    def client_factory(*args, **kwargs):
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr("encypher_enterprise.client.httpx.Client", client_factory)
    return EncypherClient(api_key="test-token", base_url="https://api.encypherai.com")


def test_sign_success_includes_metadata(monkeypatch):
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = json.loads(request.content.decode())
        response = SignResponse(
            success=True,
            document_id="doc_123",
            signed_text="signed:hello",
            total_sentences=1,
            verification_url="https://verify/123",
        )
        return httpx.Response(200, json=response.model_dump())

    client = _setup_mock_client(monkeypatch, handler)
    result = client.sign("hello world", metadata={"source": "unit-test"})
    client.close()

    assert result.document_id == "doc_123"
    assert captured["json"]["custom_metadata"] == {"source": "unit-test"}
    assert captured["json"]["text"] == "hello world"


def test_sign_raises_authentication_error(monkeypatch):
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": {"message": "invalid"}})

    client = _setup_mock_client(monkeypatch, handler)

    with pytest.raises(AuthenticationError):
        client.sign("should fail")

    client.close()


def test_verify_success(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/verify"
        payload = VerifyResponse(
            success=True,
            is_valid=True,
            signer_id="org_1",
            organization_name="Encypher",
            signature_timestamp=None,
            manifest={"data": "value"},
            tampered=False,
        )
        return httpx.Response(200, json=payload.model_dump())

    client = _setup_mock_client(monkeypatch, handler)
    result = client.verify("signed content")
    client.close()

    assert result.is_valid is True
    assert result.manifest == {"data": "value"}


def test_lookup_success(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/lookup"
        payload = LookupResponse(
            success=True,
            found=True,
            document_title="Title",
            organization_name="Org",
            publication_date=None,
            sentence_index=3,
            document_url="https://example.com",
        )
        return httpx.Response(200, json=payload.model_dump())

    client = _setup_mock_client(monkeypatch, handler)
    result = client.lookup("sentence")
    client.close()

    assert result.found is True
    assert result.document_title == "Title"


def test_stats_success(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/stats"
        payload = StatsResponse(
            success=True,
            organization_id="org_1",
            organization_name="Encypher",
            tier="enterprise",
            usage=UsageStats(
                documents_signed=10,
                sentences_signed=50,
                api_calls_this_month=5,
                monthly_quota=100,
                quota_remaining=95,
            ),
        )
        return httpx.Response(200, json=payload.model_dump())

    client = _setup_mock_client(monkeypatch, handler)
    stats = client.get_stats()
    client.close()

    assert stats.usage.documents_signed == 10
    assert stats.tier == "enterprise"
