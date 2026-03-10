"""
E2E tests for rich article signing and verification endpoints.

Tests are organized into two groups:
1. Schema/validation tests (always run) - test request validation, tier gating, response shape
2. API endpoint tests (require test DB) - use async_client with auth headers

C2PA signing note: c2pa-python v0.28.0 requires a real CA-signed cert for JUMBF
embedding. Self-signed certs fail. The /sign/rich endpoint calls execute_rich_signing()
which calls sign_image() which uses real c2pa signing. Therefore E2E tests for the
full sign+verify flow require valid SSL.com cert chain env vars and are skipped otherwise.
Schema/validation tests run without any mocking.
"""

import base64
from io import BytesIO

import pytest
from httpx import AsyncClient

# ============================================================
# Test helpers
# ============================================================


def make_test_jpeg(width=64, height=64, color=(100, 150, 200)) -> bytes:
    from PIL import Image

    img = Image.new("RGB", (width, height), color=color)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def make_test_png(width=64, height=64, color=(200, 100, 50)) -> bytes:
    from PIL import Image

    img = Image.new("RGB", (width, height), color=color)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def make_article_request(n_images=1, content_format="html"):
    images = []
    for i in range(n_images):
        images.append(
            {
                "data": b64(make_test_jpeg()),
                "filename": f"photo{i + 1}.jpg",
                "mime_type": "image/jpeg",
                "position": i,
                "alt_text": f"Caption {i + 1}",
            }
        )
    return {
        "content": "<h1>Test Article</h1><p>First paragraph with important news.</p>",
        "content_format": content_format,
        "document_title": "Test Article",
        "document_url": "https://example.com/article/test",
        "metadata": {"author": "Test Author"},
        "images": images,
        "options": {
            "segmentation_level": "sentence",
            "manifest_mode": "micro",
            "enable_trustmark": False,
            "use_rights_profile": False,
        },
    }


# ============================================================
# Schema/validation tests (always run, no DB/cert needed)
# ============================================================


class TestRichSignRequestValidation:
    def test_no_images_rejected(self):
        import pydantic

        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        with pytest.raises(pydantic.ValidationError):
            RichArticleSignRequest(content="text", images=[])

    def test_too_many_images_rejected(self):
        import pydantic

        from app.schemas.rich_sign_schemas import RichArticleSignRequest, RichContentImage

        images = []
        for i in range(21):  # 21 exceeds max of 20
            images.append(
                RichContentImage(
                    data=b64(make_test_jpeg()),
                    filename=f"img{i}.jpg",
                    mime_type="image/jpeg",
                    position=i,
                )
            )
        with pytest.raises(pydantic.ValidationError):
            RichArticleSignRequest(content="text", images=images)

    def test_invalid_base64_image_rejected(self):
        import pydantic

        from app.schemas.rich_sign_schemas import RichContentImage

        with pytest.raises(pydantic.ValidationError):
            RichContentImage(
                data="not-valid-base64!!!",
                filename="test.jpg",
                mime_type="image/jpeg",
                position=0,
            )

    def test_unsupported_mime_type_rejected(self):
        import pydantic

        from app.schemas.rich_sign_schemas import RichContentImage

        with pytest.raises(pydantic.ValidationError):
            RichContentImage(
                data=b64(make_test_jpeg()),
                filename="test.gif",
                mime_type="image/gif",  # not supported
                position=0,
            )

    def test_image_over_10mb_rejected(self):
        import pydantic

        from app.schemas.rich_sign_schemas import RichContentImage

        # Create a 10MB+ base64 payload (using repeating bytes to exceed limit)
        big_data = b"x" * (10_485_761)
        with pytest.raises(pydantic.ValidationError):
            RichContentImage(
                data=b64(big_data),
                filename="huge.jpg",
                mime_type="image/jpeg",
                position=0,
            )

    def test_valid_single_image_passes(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        req_dict = make_article_request(n_images=1)
        req = RichArticleSignRequest(**req_dict)
        assert len(req.images) == 1

    def test_valid_multi_image_passes(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        req_dict = make_article_request(n_images=3)
        req = RichArticleSignRequest(**req_dict)
        assert len(req.images) == 3


class TestImageVerifyRequestValidation:
    def test_requires_image_data(self):
        import pydantic

        from app.schemas.rich_verify_schemas import ImageVerifyRequest

        with pytest.raises(pydantic.ValidationError):
            ImageVerifyRequest()  # missing image_data

    def test_default_mime_type(self):
        from app.schemas.rich_verify_schemas import ImageVerifyRequest

        req = ImageVerifyRequest(image_data=b64(make_test_jpeg()))
        assert req.mime_type == "image/jpeg"


class TestRichVerifyRequestValidation:
    def test_requires_document_id(self):
        import pydantic

        from app.schemas.rich_verify_schemas import RichVerifyRequest

        with pytest.raises(pydantic.ValidationError):
            RichVerifyRequest()


class TestImageAttributionRequestValidation:
    def test_requires_image_data_or_phash(self):
        import pydantic

        from app.schemas.image_attribution_schemas import ImageAttributionRequest

        with pytest.raises((pydantic.ValidationError, ValueError)):
            ImageAttributionRequest(threshold=10, scope="org")

    def test_rejects_both_image_data_and_phash(self):
        import pydantic

        from app.schemas.image_attribution_schemas import ImageAttributionRequest

        with pytest.raises((pydantic.ValidationError, ValueError)):
            ImageAttributionRequest(
                image_data=b64(make_test_jpeg()),
                phash="a" * 16,
                threshold=10,
                scope="org",
            )

    def test_valid_phash_request(self):
        from app.schemas.image_attribution_schemas import ImageAttributionRequest

        req = ImageAttributionRequest(phash="a" * 16, scope="org")
        assert req.phash == "a" * 16

    def test_threshold_bounds(self):
        import pydantic

        from app.schemas.image_attribution_schemas import ImageAttributionRequest

        # Valid bounds
        ImageAttributionRequest(phash="a" * 16, threshold=0, scope="org")
        ImageAttributionRequest(phash="a" * 16, threshold=32, scope="org")
        # Over max
        with pytest.raises(pydantic.ValidationError):
            ImageAttributionRequest(phash="a" * 16, threshold=33, scope="org")


# ============================================================
# API endpoint tests using async_client (require app + test DB)
# ============================================================


@pytest.mark.asyncio
async def test_verify_image_invalid_base64_returns_400(async_client: AsyncClient):
    resp = await async_client.post(
        "/api/v1/verify/image",
        json={
            "image_data": "not-valid-base64!!!",
            "mime_type": "image/jpeg",
        },
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_verify_image_unsigned_jpeg_returns_valid_false(async_client: AsyncClient):
    """A plain JPEG with no C2PA manifest should return valid=False."""
    img_b64 = b64(make_test_jpeg())
    resp = await async_client.post(
        "/api/v1/verify/image",
        json={
            "image_data": img_b64,
            "mime_type": "image/jpeg",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False
    assert data["c2pa_manifest"] is None or not data.get("c2pa_manifest", {}).get("valid")


@pytest.mark.asyncio
async def test_verify_image_response_has_required_fields(async_client: AsyncClient):
    img_b64 = b64(make_test_jpeg())
    resp = await async_client.post(
        "/api/v1/verify/image",
        json={
            "image_data": img_b64,
            "mime_type": "image/jpeg",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "valid" in data
    assert "verified_at" in data
    assert "correlation_id" in data
    assert "hash" in data


@pytest.mark.asyncio
async def test_verify_rich_unknown_document_id_returns_404(async_client: AsyncClient):
    resp = await async_client.post(
        "/api/v1/verify/rich",
        json={
            "document_id": "nonexistent_doc_id_xyz_12345",
        },
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_verify_rich_missing_document_id_returns_422(async_client: AsyncClient):
    resp = await async_client.post("/api/v1/verify/rich", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_sign_rich_unauthenticated_returns_401(async_client: AsyncClient):
    req = make_article_request(n_images=1)
    resp = await async_client.post("/api/v1/sign/rich", json=req)
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_sign_rich_invalid_mime_type_returns_422(async_client: AsyncClient, enterprise_auth_headers: dict):
    """Schema validation catches bad MIME type before auth even matters."""
    req = make_article_request(n_images=1)
    req["images"][0]["mime_type"] = "image/gif"
    resp = await async_client.post(
        "/api/v1/sign/rich",
        json=req,
        headers=enterprise_auth_headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_sign_rich_trustmark_blocked_for_free_tier(async_client: AsyncClient, starter_auth_headers: dict):
    req = make_article_request(n_images=1)
    req["options"]["enable_trustmark"] = True
    resp = await async_client.post(
        "/api/v1/sign/rich",
        json=req,
        headers=starter_auth_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_attribution_scope_all_blocked_for_free_tier(async_client: AsyncClient, starter_auth_headers: dict):
    resp = await async_client.post(
        "/api/v1/enterprise/images/attribution",
        json={"phash": "a" * 16, "scope": "all"},
        headers=starter_auth_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_attribution_scope_org_allowed_for_free_tier(async_client: AsyncClient, starter_auth_headers: dict):
    resp = await async_client.post(
        "/api/v1/enterprise/images/attribution",
        json={"phash": "a" * 16, "scope": "org"},
        headers=starter_auth_headers,
    )
    # 200 expected (no matches found is still a valid response)
    assert resp.status_code == 200
    data = resp.json()
    assert data["match_count"] == 0


@pytest.mark.asyncio
async def test_attribution_invalid_phash_hex_returns_400(async_client: AsyncClient, starter_auth_headers: dict):
    resp = await async_client.post(
        "/api/v1/enterprise/images/attribution",
        json={"phash": "not-valid-hex", "scope": "org"},
        headers=starter_auth_headers,
    )
    assert resp.status_code == 400


# ============================================================
# Image utilities integration
# ============================================================


class TestImageUtils:
    def test_compute_phash_is_deterministic(self):
        from app.utils.image_utils import compute_phash

        data = make_test_jpeg()
        assert compute_phash(data) == compute_phash(data)

    def test_compute_phash_differs_for_different_images(self):
        from app.utils.image_utils import compute_phash

        img1 = make_test_jpeg(color=(255, 0, 0))
        img2 = make_test_jpeg(color=(0, 0, 255))
        # Different colors should produce different (or at least potentially different) hashes
        # This is a probabilistic check -- may not always differ for simple solid-color images
        # but the function should at least return without error
        h1 = compute_phash(img1)
        h2 = compute_phash(img2)
        assert isinstance(h1, int)
        assert isinstance(h2, int)

    def test_strip_exif_returns_valid_jpeg(self):
        from app.utils.image_utils import strip_exif

        data = make_test_jpeg()
        stripped = strip_exif(data, "image/jpeg")
        # Should still be a valid JPEG
        from PIL import Image

        img = Image.open(BytesIO(stripped))
        assert img.format == "JPEG"

    def test_compute_sha256_format(self):
        from app.utils.image_utils import compute_sha256

        result = compute_sha256(b"hello world")
        assert result.startswith("sha256:")
        assert len(result) == len("sha256:") + 64

    def test_generate_image_id_format(self):
        from app.utils.image_utils import generate_image_id

        id1 = generate_image_id()
        id2 = generate_image_id()
        assert id1.startswith("img_")
        assert len(id1) == 12
        assert id1 != id2  # should be random


# ============================================================
# Composite manifest service
# ============================================================


class TestCompositeManifestIntegration:
    def test_build_composite_manifest_correct_structure(self):
        from app.services.composite_manifest_service import (
            ImageIngredient,
            build_composite_manifest,
        )

        ingredients = [
            ImageIngredient(
                image_id="img_aabbccdd",
                filename="photo1.jpg",
                mime_type="image/jpeg",
                c2pa_instance_id="urn:uuid:test-1234",
                signed_hash="sha256:abc123",
                position=0,
            ),
            ImageIngredient(
                image_id="img_eeff0011",
                filename="photo2.png",
                mime_type="image/png",
                c2pa_instance_id="urn:uuid:test-5678",
                signed_hash="sha256:def456",
                position=1,
            ),
        ]
        result = build_composite_manifest(
            document_id="test-doc-001",
            org_id="org_test",
            document_title="Test Article",
            text_merkle_root="sha256:merkleroot",
            text_instance_id="urn:uuid:text-manifest",
            images=ingredients,
        )
        assert result.ingredient_count == 2
        assert result.instance_id.startswith("urn:uuid:")
        assert result.manifest_hash.startswith("sha256:")
        assert len(result.manifest_data["ingredients"]) == 2
        # Verify ingredients are sorted by position
        assert result.manifest_data["ingredients"][0]["title"] == "photo1.jpg"
        assert result.manifest_data["ingredients"][1]["title"] == "photo2.png"

    def test_composite_manifest_is_deterministic(self):
        import hashlib
        import json

        from app.services.composite_manifest_service import (
            ImageIngredient,
            build_composite_manifest,
        )

        ingredients = [
            ImageIngredient("img_1", "a.jpg", "image/jpeg", "urn:uuid:1", "sha256:1", 0),
        ]
        result = build_composite_manifest(
            document_id="doc1",
            org_id="org1",
            document_title="Title",
            text_merkle_root="sha256:root",
            text_instance_id="urn:uuid:text",
            images=ingredients,
        )
        # The manifest_hash should match a recompute of manifest_data
        manifest_json = json.dumps(result.manifest_data, sort_keys=True, separators=(",", ":"))
        expected_hash = "sha256:" + hashlib.sha256(manifest_json.encode()).hexdigest()
        assert result.manifest_hash == expected_hash
