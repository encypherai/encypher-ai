"""
Tests for the Ghost CMS integration service and router.

Covers:
- HTML text extraction (skipping Ghost card types)
- HTML text embedding
- C2PA embedding detection/stripping
- Badge injection
- Loop prevention
- Webhook payload parsing
- Ghost Admin API client JWT generation
- Webhook token generation, hashing, and URL building
"""

import hashlib
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import app.routers.integrations as integrations_router

from app.services.ghost_integration import (
    GhostAdminClient,
    _TextExtractor,
    clear_in_flight,
    detect_c2pa_embeddings,
    embed_signed_text_in_html,
    extract_text_from_html,
    generate_badge_script,
    is_in_flight,
    merge_badge_injection,
    sign_ghost_post,
    set_in_flight,
    strip_c2pa_embeddings,
)
from app.schemas.integration_schemas import (
    GhostIntegrationCreate,
    GhostIntegrationResponse,
    GhostTokenRegenerateResponse,
    GhostWebhookPayload,
    GhostManualSignRequest,
)
from app.routers.integrations import (
    _generate_webhook_token,
    _hash_token,
    _build_webhook_url,
    _mask_key,
    WEBHOOK_TOKEN_PREFIX,
    WEBHOOK_BASE_PATH,
)


# =============================================================================
# HTML Text Extraction Tests
# =============================================================================


class TestExtractTextFromHtml:
    def test_basic_paragraphs(self):
        html = "<p>Hello world.</p><p>Second paragraph.</p>"
        result = extract_text_from_html(html)
        assert "Hello world." in result
        assert "Second paragraph." in result

    def test_headings_and_lists(self):
        html = "<h2>Title</h2><ul><li>Item one</li><li>Item two</li></ul>"
        result = extract_text_from_html(html)
        assert "Title" in result
        assert "Item one" in result
        assert "Item two" in result

    def test_skips_image_cards(self):
        html = '<div class="kg-image-card"><img src="photo.jpg"><figcaption>Caption</figcaption></div><p>After image.</p>'
        result = extract_text_from_html(html)
        assert "Caption" not in result
        assert "After image." in result

    def test_skips_code_cards(self):
        html = '<div class="kg-code-card"><pre><code>console.log("hi")</code></pre></div><p>After code.</p>'
        result = extract_text_from_html(html)
        assert "console.log" not in result
        assert "After code." in result

    def test_skips_embed_cards(self):
        html = '<div class="kg-embed-card"><iframe src="https://youtube.com"></iframe></div><p>After embed.</p>'
        result = extract_text_from_html(html)
        assert "youtube" not in result
        assert "After embed." in result

    def test_skips_script_and_style(self):
        html = "<p>Visible.</p><script>alert('x')</script><style>.foo{}</style><p>Also visible.</p>"
        result = extract_text_from_html(html)
        assert "Visible." in result
        assert "Also visible." in result
        assert "alert" not in result
        assert ".foo" not in result

    def test_empty_html(self):
        assert extract_text_from_html("") == ""
        assert extract_text_from_html("<p>   </p>") == ""

    def test_nested_elements(self):
        html = "<div><p>Outer <strong>bold</strong> text.</p></div>"
        result = extract_text_from_html(html)
        assert "Outer" in result
        assert "bold" in result
        assert "text." in result

    def test_skips_gallery_card(self):
        html = '<div class="kg-gallery-card"><div class="kg-gallery-container"></div></div><p>After gallery.</p>'
        result = extract_text_from_html(html)
        assert "After gallery." in result

    def test_skips_video_card(self):
        html = '<div class="kg-video-card"><video src="v.mp4"></video></div><p>After video.</p>'
        result = extract_text_from_html(html)
        assert "After video." in result

    def test_skips_audio_card(self):
        html = '<div class="kg-audio-card"><audio src="a.mp3"></audio></div><p>After audio.</p>'
        result = extract_text_from_html(html)
        assert "After audio." in result


# =============================================================================
# C2PA Embedding Detection / Stripping Tests
# =============================================================================


class TestC2paEmbeddings:
    def test_detect_no_embeddings(self):
        assert detect_c2pa_embeddings("Hello world") == 0

    def test_detect_vs_chars(self):
        text = "Hello\uFE01 world\uFE0F"
        assert detect_c2pa_embeddings(text) == 2

    def test_detect_supplementary_vs(self):
        text = "Hello\U000E0100 world\U000E01EF"
        assert detect_c2pa_embeddings(text) == 2

    def test_detect_bom(self):
        text = "Hello\uFEFF world"
        assert detect_c2pa_embeddings(text) == 1

    def test_strip_removes_all(self):
        text = "He\uFE01llo\uFEFF wo\U000E0100rld"
        stripped = strip_c2pa_embeddings(text)
        assert stripped == "Hello world"
        assert detect_c2pa_embeddings(stripped) == 0

    def test_strip_preserves_normal_text(self):
        text = "Hello world, no markers here!"
        assert strip_c2pa_embeddings(text) == text


# =============================================================================
# HTML Embedding Tests
# =============================================================================


class TestEmbedSignedText:
    def test_basic_embedding(self):
        html = "<p>Hello world.</p><p>Second line.</p>"
        signed = "Hello\uFE01 world.\nSecond\uFE02 line."
        result = embed_signed_text_in_html(html, signed)
        assert "\uFE01" in result
        assert "\uFE02" in result

    def test_preserves_html_structure(self):
        html = "<h2>Title</h2><p>Content here.</p>"
        signed = "Title\nContent\uFE01 here."
        result = embed_signed_text_in_html(html, signed)
        assert "<h2>" in result
        assert "<p>" in result

    def test_empty_html_returns_original(self):
        html = "<p>   </p>"
        signed = "some signed text"
        result = embed_signed_text_in_html(html, signed)
        assert result == html


# =============================================================================
# Badge Injection Tests
# =============================================================================


class TestBadgeInjection:
    def test_generate_badge_script(self):
        script = generate_badge_script("doc_123", "inst_456")
        assert "doc_123" in script
        assert "Encypher Provenance Badge" in script
        assert "verify.encypherai.com" in script

    def test_generate_badge_custom_url(self):
        script = generate_badge_script("doc_123", "inst_456", "https://custom.verify.com")
        assert "custom.verify.com" in script

    def test_merge_badge_no_existing(self):
        badge = "<!-- Encypher Provenance Badge --><script>badge</script>"
        result = merge_badge_injection(None, badge)
        assert result == badge

    def test_merge_badge_with_existing_code(self):
        existing = "<script>analytics()</script>"
        badge = "<!-- Encypher Provenance Badge --><script>badge</script>"
        result = merge_badge_injection(existing, badge)
        assert "analytics()" in result
        assert "badge" in result

    def test_merge_badge_replaces_previous(self):
        existing = "<!-- Encypher Provenance Badge --><script>old_badge</script>"
        badge = "<!-- Encypher Provenance Badge --><script>new_badge</script>"
        result = merge_badge_injection(existing, badge)
        assert "old_badge" not in result
        assert "new_badge" in result


# =============================================================================
# Loop Prevention Tests
# =============================================================================


class TestLoopPrevention:
    def setup_method(self):
        from app.services.ghost_integration import _in_flight
        _in_flight.clear()

    def test_not_in_flight_initially(self):
        assert not is_in_flight("post_123")

    def test_set_and_check_in_flight(self):
        set_in_flight("post_123")
        assert is_in_flight("post_123")
        assert not is_in_flight("post_456")

    def test_clear_in_flight(self):
        set_in_flight("post_123")
        assert is_in_flight("post_123")
        clear_in_flight("post_123")
        assert not is_in_flight("post_123")

    def test_ttl_expiry(self):
        from app.services.ghost_integration import _in_flight, _IN_FLIGHT_TTL_SECONDS
        set_in_flight("post_123")
        # Manually backdate the timestamp
        _in_flight["post_123"] = time.time() - _IN_FLIGHT_TTL_SECONDS - 1
        assert not is_in_flight("post_123")


# =============================================================================
# Webhook Payload Parsing Tests
# =============================================================================


class TestWebhookPayload:
    def test_post_published(self):
        payload = GhostWebhookPayload(
            post={"current": {"id": "abc123", "title": "Test", "status": "published"}}
        )
        assert payload.get_resource_type() == "post"
        current = payload.get_current()
        assert current["id"] == "abc123"

    def test_page_published(self):
        payload = GhostWebhookPayload(
            page={"current": {"id": "page456", "title": "About", "status": "published"}}
        )
        assert payload.get_resource_type() == "page"
        current = payload.get_current()
        assert current["id"] == "page456"

    def test_empty_payload(self):
        payload = GhostWebhookPayload()
        assert payload.get_resource_type() is None
        assert payload.get_current() is None

    def test_post_without_current(self):
        payload = GhostWebhookPayload(post={"previous": {"id": "old"}})
        assert payload.get_resource_type() == "post"
        assert payload.get_current() is None


# =============================================================================
# Schema Validation Tests
# =============================================================================


class TestGhostIntegrationCreate:
    def test_valid_create(self):
        body = GhostIntegrationCreate(
            ghost_url="https://myblog.ghost.io",
            ghost_admin_api_key="1234567890abcdef:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        )
        assert body.ghost_url == "https://myblog.ghost.io"
        assert body.manifest_mode == "micro"
        assert body.segmentation_level == "sentence"
        assert body.ecc is True
        assert body.embed_c2pa is True

    def test_strips_trailing_slash(self):
        body = GhostIntegrationCreate(
            ghost_url="https://myblog.ghost.io/",
            ghost_admin_api_key="1234567890abcdef:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        )
        assert body.ghost_url == "https://myblog.ghost.io"

    def test_rejects_invalid_url(self):
        with pytest.raises(Exception):
            GhostIntegrationCreate(
                ghost_url="not-a-url",
                ghost_admin_api_key="1234567890abcdef:abcdef1234567890",
            )

    def test_rejects_invalid_key_format(self):
        with pytest.raises(Exception):
            GhostIntegrationCreate(
                ghost_url="https://myblog.ghost.io",
                ghost_admin_api_key="no-colon-here",
            )

    def test_rejects_invalid_manifest_mode(self):
        with pytest.raises(Exception):
            GhostIntegrationCreate(
                ghost_url="https://myblog.ghost.io",
                ghost_admin_api_key="1234567890abcdef:abcdef1234567890",
                manifest_mode="invalid_mode",
            )

    def test_rejects_invalid_segmentation_level(self):
        with pytest.raises(Exception):
            GhostIntegrationCreate(
                ghost_url="https://myblog.ghost.io",
                ghost_admin_api_key="1234567890abcdef:abcdef1234567890",
                segmentation_level="chapter",
            )


class TestGhostManualSignRequest:
    def test_default_post(self):
        req = GhostManualSignRequest()
        assert req.post_type == "post"

    def test_page(self):
        req = GhostManualSignRequest(post_type="page")
        assert req.post_type == "page"

    def test_rejects_invalid(self):
        with pytest.raises(Exception):
            GhostManualSignRequest(post_type="comment")


# =============================================================================
# Ghost Admin Client JWT Tests
# =============================================================================


class TestGhostAdminClient:
    def test_jwt_generation(self):
        client = GhostAdminClient(
            ghost_url="https://myblog.ghost.io",
            admin_api_key="1234567890abcdef:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        )
        token = client._make_token()
        assert isinstance(token, str)
        assert len(token) > 20

    def test_invalid_key_format(self):
        with pytest.raises(ValueError, match="format"):
            GhostAdminClient(
                ghost_url="https://myblog.ghost.io",
                admin_api_key="no-colon-here",
            )

    def test_api_url(self):
        client = GhostAdminClient(
            ghost_url="https://myblog.ghost.io",
            admin_api_key="1234567890abcdef:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        )
        assert client._api_url("posts/123/") == "https://myblog.ghost.io/ghost/api/admin/posts/123/"


class TestGhostSignOrchestration:
    @pytest.mark.asyncio
    async def test_sign_ghost_post_accepts_legacy_micro_ecc_c2pa_manifest_mode(self):
        ghost_client = MagicMock()
        ghost_client.read_post = AsyncMock(
            return_value={
                "id": "post_123",
                "title": "Hello",
                "url": "https://myblog.ghost.io/hello",
                "html": "<p>Hello world.</p>",
                "authors": [{"name": "Author"}],
                "tags": [],
                "updated_at": "2026-02-17T18:00:00.000Z",
                "codeinjection_foot": None,
            }
        )
        ghost_client.update_post = AsyncMock(return_value={"id": "post_123"})

        async def _fake_execute_unified_signing(*, request, **kwargs):
            assert request.options.manifest_mode == "micro"
            assert request.options.ecc is True
            assert request.options.embed_c2pa is True
            return {
                "success": True,
                "data": {
                    "document": {
                        "embedded_text": "Hello\uFE01 world.",
                        "document_id": "doc_123",
                        "instance_id": "inst_123",
                        "total_segments": 1,
                    }
                },
            }

        with patch("app.services.unified_signing_service.execute_unified_signing", new=AsyncMock(side_effect=_fake_execute_unified_signing)):
            result = await sign_ghost_post(
                ghost_client=ghost_client,
                post_id="post_123",
                post_type="post",
                organization={"organization_id": "org_123", "tier": "business"},
                core_db=MagicMock(),
                content_db=MagicMock(),
                manifest_mode="micro_ecc_c2pa",
                segmentation_level="sentence",
                badge_enabled=False,
            )

        assert result["success"] is True
        ghost_client.update_post.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_sign_ghost_post_uses_signed_text_field_from_unified_response(self):
        ghost_client = MagicMock()
        ghost_client.read_post = AsyncMock(
            return_value={
                "id": "post_789",
                "title": "Hello",
                "url": "https://myblog.ghost.io/hello",
                "html": "<p>Hello world.</p>",
                "authors": [{"name": "Author"}],
                "tags": [],
                "updated_at": "2026-02-17T18:00:00.000Z",
                "codeinjection_foot": None,
            }
        )
        ghost_client.update_post = AsyncMock(return_value={"id": "post_789"})

        async def _fake_execute_unified_signing(*, request, **kwargs):
            return {
                "success": True,
                "data": {
                    "document": {
                        "signed_text": "Hello\uFE01 world.",
                        "document_id": "doc_789",
                        "instance_id": "inst_789",
                        "total_segments": 1,
                    }
                },
            }

        with patch("app.services.unified_signing_service.execute_unified_signing", new=AsyncMock(side_effect=_fake_execute_unified_signing)):
            result = await sign_ghost_post(
                ghost_client=ghost_client,
                post_id="post_789",
                post_type="post",
                organization={"organization_id": "org_123", "tier": "business"},
                core_db=MagicMock(),
                content_db=MagicMock(),
                manifest_mode="micro",
                segmentation_level="sentence",
                badge_enabled=False,
            )

        assert result["success"] is True
        ghost_client.update_post.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_sign_ghost_post_passes_explicit_micro_flags(self):
        ghost_client = MagicMock()
        ghost_client.read_post = AsyncMock(
            return_value={
                "id": "post_456",
                "title": "Hello",
                "url": "https://myblog.ghost.io/hello",
                "html": "<p>Hello world.</p>",
                "authors": [{"name": "Author"}],
                "tags": [],
                "updated_at": "2026-02-17T18:00:00.000Z",
                "codeinjection_foot": None,
            }
        )
        ghost_client.update_post = AsyncMock(return_value={"id": "post_456"})

        async def _fake_execute_unified_signing(*, request, **kwargs):
            assert request.options.manifest_mode == "micro"
            assert request.options.ecc is False
            assert request.options.embed_c2pa is False
            return {
                "success": True,
                "data": {
                    "document": {
                        "embedded_text": "Hello\uFE01 world.",
                        "document_id": "doc_456",
                        "instance_id": "inst_456",
                        "total_segments": 1,
                    }
                },
            }

        with patch("app.services.unified_signing_service.execute_unified_signing", new=AsyncMock(side_effect=_fake_execute_unified_signing)):
            result = await sign_ghost_post(
                ghost_client=ghost_client,
                post_id="post_456",
                post_type="post",
                organization={"organization_id": "org_123", "tier": "business"},
                core_db=MagicMock(),
                content_db=MagicMock(),
                manifest_mode="micro",
                segmentation_level="sentence",
                badge_enabled=False,
                ecc=False,
                embed_c2pa=False,
            )

        assert result["success"] is True
        ghost_client.update_post.assert_awaited_once()


# =============================================================================
# Webhook Token Tests
# =============================================================================


class TestWebhookToken:
    def test_generate_token_has_prefix(self):
        token = _generate_webhook_token()
        assert token.startswith(WEBHOOK_TOKEN_PREFIX)

    def test_generate_token_is_unique(self):
        tokens = {_generate_webhook_token() for _ in range(100)}
        assert len(tokens) == 100

    def test_generate_token_sufficient_length(self):
        token = _generate_webhook_token()
        # ghwh_ prefix (5) + 43 chars of base64url = 48 chars minimum
        assert len(token) >= 40

    def test_hash_token_is_sha256(self):
        token = "ghwh_test_token_123"
        expected = hashlib.sha256(token.encode()).hexdigest()
        assert _hash_token(token) == expected

    def test_hash_token_is_deterministic(self):
        token = _generate_webhook_token()
        assert _hash_token(token) == _hash_token(token)

    def test_hash_token_different_tokens_different_hashes(self):
        t1 = _generate_webhook_token()
        t2 = _generate_webhook_token()
        assert _hash_token(t1) != _hash_token(t2)

    def test_build_webhook_url(self, monkeypatch: pytest.MonkeyPatch):
        token = "ghwh_abc123"
        monkeypatch.setattr(integrations_router.settings, "api_base_url", "https://api.encypherai.com")
        url = _build_webhook_url(token)
        assert url == f"https://api.encypherai.com{WEBHOOK_BASE_PATH}?token=ghwh_abc123"

    def test_build_webhook_url_contains_token(self, monkeypatch: pytest.MonkeyPatch):
        token = _generate_webhook_token()
        monkeypatch.setattr(integrations_router.settings, "api_base_url", "https://api.encypherai.com/")
        url = _build_webhook_url(token)
        assert token in url
        assert url.startswith(f"https://api.encypherai.com{WEBHOOK_BASE_PATH}")

    def test_build_webhook_url_uses_configured_base_url(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(integrations_router.settings, "api_base_url", "https://staging-api.encypherai.com")
        token = "ghwh_custom"
        url = _build_webhook_url(token)
        assert url == f"https://staging-api.encypherai.com{WEBHOOK_BASE_PATH}?token=ghwh_custom"

    def test_build_webhook_url_ignores_request_host(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(integrations_router.settings, "api_base_url", "https://api.encypherai.com")

        class _Req:
            base_url = "https://encypherai.com/"

        url = _build_webhook_url("ghwh_proxy", request=_Req())
        assert url == f"https://api.encypherai.com{WEBHOOK_BASE_PATH}?token=ghwh_proxy"


class TestMaskKey:
    def test_mask_long_key(self):
        result = _mask_key("1234567890abcdef:secret")
        assert result.endswith("cret")
        assert result.startswith("*")

    def test_mask_short_key(self):
        assert _mask_key("short") == "****"

    def test_mask_exactly_8(self):
        assert _mask_key("12345678") == "****"

    def test_mask_9_chars(self):
        result = _mask_key("123456789")
        assert result == "*****6789"


class TestGhostIntegrationResponseSchema:
    def test_response_with_token(self):
        resp = GhostIntegrationResponse(
            id="gi_test",
            organization_id="org_test",
            ghost_url="https://blog.example.com",
            ghost_admin_api_key_masked="****cret",
            auto_sign_on_publish=True,
            auto_sign_on_update=True,
            manifest_mode="micro",
            segmentation_level="sentence",
            ecc=True,
            embed_c2pa=True,
            badge_enabled=True,
            is_active=True,
            webhook_url="https://api.encypherai.com/api/v1/integrations/ghost/webhook?token=ghwh_abc",
            webhook_token="ghwh_abc",
        )
        assert resp.webhook_token == "ghwh_abc"
        assert "ghwh_abc" in resp.webhook_url
        assert resp.ecc is True
        assert resp.embed_c2pa is True

    def test_response_without_token(self):
        resp = GhostIntegrationResponse(
            id="gi_test",
            organization_id="org_test",
            ghost_url="https://blog.example.com",
            ghost_admin_api_key_masked="****cret",
            auto_sign_on_publish=True,
            auto_sign_on_update=True,
            manifest_mode="micro",
            segmentation_level="sentence",
            ecc=True,
            embed_c2pa=True,
            badge_enabled=True,
            is_active=True,
            webhook_url="https://api.encypherai.com/api/v1/integrations/ghost/webhook?token=ghwh_••••••••",
        )
        assert resp.webhook_token is None
        assert "••••••••" in resp.webhook_url
        assert resp.ecc is True
        assert resp.embed_c2pa is True

    def test_token_regenerate_response(self):
        resp = GhostTokenRegenerateResponse(
            webhook_url="https://api.encypherai.com/api/v1/integrations/ghost/webhook?token=ghwh_new",
            webhook_token="ghwh_new",
        )
        assert resp.webhook_token == "ghwh_new"


class TestGhostIntegrationCreateNoWebhookSecret:
    """Verify webhook_secret field was removed from the create schema."""

    def test_no_webhook_secret_field(self):
        fields = GhostIntegrationCreate.model_fields
        assert "webhook_secret" not in fields

    def test_create_without_webhook_secret(self):
        body = GhostIntegrationCreate(
            ghost_url="https://myblog.ghost.io",
            ghost_admin_api_key="1234567890abcdef:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        )
        assert not hasattr(body, "webhook_secret")
        assert body.ecc is True
        assert body.embed_c2pa is True
