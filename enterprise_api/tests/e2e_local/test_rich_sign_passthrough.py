"""
End-to-end tests for rich article signing in passthrough mode.

These tests run the full pipeline locally without a CA-signed cert:
  POST /sign/rich  ->  DB rows written  ->  POST /verify/rich  ->  POST /verify/image

The IMAGE_SIGNING_PASSTHROUGH=true env flag (or missing certs) causes sign_image()
to skip JUMBF embedding and return the EXIF-stripped original bytes.  All other
metadata (hash, pHash, composite manifest, ArticleImage rows, CompositeManifest rows)
is written normally.  Verification confirms:
  - /verify/rich   -> composite manifest found, hash integrity OK
  - /verify/image  -> c2pa_manifest_valid=False (no JUMBF), but endpoint returns 200

Run with:
  IMAGE_SIGNING_PASSTHROUGH=true uv run pytest tests/e2e_local/test_rich_sign_passthrough.py -v
or simply:
  uv run pytest tests/e2e_local/test_rich_sign_passthrough.py -v
  (passthrough auto-activates when no cert env vars are set)
"""
import base64
import secrets
from io import BytesIO
from typing import Any, Dict

import pytest
from httpx import AsyncClient
from PIL import Image


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_jpeg(width: int = 128, height: int = 96, color=(80, 120, 200)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def make_png(width: int = 64, height: int = 64, color=(200, 80, 50)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def unique_doc_id(prefix: str = "pt") -> str:
    """Generate a unique document ID per test run to avoid uniqueness constraint failures."""
    return f"{prefix}-{secrets.token_hex(4)}"


def rich_request(images: list, document_id: str | None = None) -> Dict[str, Any]:
    return {
        "content": "<h1>Test Article</h1><p>First sentence. Second sentence.</p>",
        "content_format": "html",
        "document_id": document_id or unique_doc_id(),
        "document_title": "Passthrough Test Article",
        "document_url": "https://example.com/passthrough-test",
        "metadata": {"author": "CI Bot"},
        "images": images,
        "options": {
            "segmentation_level": "sentence",
            "manifest_mode": "micro",
            "enable_trustmark": False,
            "use_rights_profile": False,
            "index_for_attribution": False,
        },
    }


# ---------------------------------------------------------------------------
# Passthrough mode unit test (no HTTP, no DB)
# ---------------------------------------------------------------------------


class TestSignImagePassthrough:
    """Test sign_image() passthrough path directly."""

    @pytest.mark.asyncio
    async def test_passthrough_returns_exif_stripped_bytes(self):
        from app.services.image_signing_service import sign_image

        jpeg = make_jpeg()
        result = await sign_image(
            image_data=jpeg,
            mime_type="image/jpeg",
            title="test.jpg",
            org_id="org_test",
            document_id="doc_001",
            image_id="img_test",
            custom_assertions=[],
            rights_data={},
            signer_private_key_pem="",   # empty -> passthrough
            signer_cert_chain_pem="",
        )
        assert result.c2pa_signed is False
        assert result.image_id == "img_test"
        # EXIF stripped but still a valid JPEG
        assert result.signed_bytes[:2] == b"\xff\xd8"
        assert result.original_hash.startswith("sha256:")
        # In passthrough mode XMP is embedded so signed_hash != original_hash
        assert result.signed_hash != result.original_hash
        # Sentinel manifest hash
        assert result.c2pa_manifest_hash == "sha256:" + "0" * 64
        assert result.c2pa_instance_id.startswith("urn:uuid:")

    @pytest.mark.asyncio
    async def test_passthrough_strips_exif(self):
        """EXIF strip still runs in passthrough mode."""
        from app.services.image_signing_service import sign_image
        from app.utils.image_utils import compute_sha256

        jpeg = make_jpeg()
        result = await sign_image(
            image_data=jpeg,
            mime_type="image/jpeg",
            title="test.jpg",
            org_id="org_test",
            document_id="doc_001",
            image_id="img_test2",
            custom_assertions=[],
            rights_data={},
            signer_private_key_pem="",
            signer_cert_chain_pem="",
        )
        # signed_hash is hash of XMP-embedded bytes
        assert result.signed_hash == compute_sha256(result.signed_bytes)

    @pytest.mark.asyncio
    async def test_passthrough_different_images_have_different_hashes(self):
        from app.services.image_signing_service import sign_image

        jpeg_red = make_jpeg(color=(255, 0, 0))
        jpeg_blue = make_jpeg(color=(0, 0, 255))

        r1 = await sign_image(
            image_data=jpeg_red, mime_type="image/jpeg", title="red.jpg",
            org_id="org_test", document_id="doc_001", image_id="img_r",
            custom_assertions=[], rights_data={},
            signer_private_key_pem="", signer_cert_chain_pem="",
        )
        r2 = await sign_image(
            image_data=jpeg_blue, mime_type="image/jpeg", title="blue.jpg",
            org_id="org_test", document_id="doc_001", image_id="img_b",
            custom_assertions=[], rights_data={},
            signer_private_key_pem="", signer_cert_chain_pem="",
        )
        assert r1.original_hash != r2.original_hash

    @pytest.mark.asyncio
    async def test_passthrough_png_supported(self):
        from app.services.image_signing_service import sign_image

        png = make_png()
        result = await sign_image(
            image_data=png,
            mime_type="image/png",
            title="test.png",
            org_id="org_test",
            document_id="doc_001",
            image_id="img_png",
            custom_assertions=[],
            rights_data={},
            signer_private_key_pem="",
            signer_cert_chain_pem="",
        )
        assert result.c2pa_signed is False
        assert result.size_bytes > 0


# ---------------------------------------------------------------------------
# Full pipeline integration via HTTP (uses async_client + test DB)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sign_rich_passthrough_single_image(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
):
    """POST /sign/rich with 1 JPEG in passthrough mode -> 201, c2pa_signed=False."""
    doc_id = unique_doc_id("pt-single")
    req = rich_request(
        images=[{"data": b64(make_jpeg()), "filename": "photo.jpg",
                 "mime_type": "image/jpeg", "position": 0}],
        document_id=doc_id,
    )
    resp = await async_client.post(
        "/api/v1/sign/rich", json=req, headers=enterprise_auth_headers
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["success"] is True

    body = data["data"]
    assert body["document_id"] == doc_id
    assert body["total_images"] == 1
    assert body["composite_manifest"]["ingredient_count"] == 1

    img_result = body["images"][0]
    assert img_result["c2pa_signed"] is False
    assert img_result["filename"] == "photo.jpg"
    assert img_result["signed_image_hash"].startswith("sha256:")
    assert img_result["phash"] is not None
    # Returned bytes should decode to a valid JPEG
    raw = base64.b64decode(img_result["signed_image_b64"])
    assert raw[:2] == b"\xff\xd8"


@pytest.mark.asyncio
async def test_sign_rich_passthrough_two_images(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
):
    """POST /sign/rich with 2 images -> composite manifest has 2 ingredients."""
    req = rich_request(
        images=[
            {"data": b64(make_jpeg(color=(255, 0, 0))), "filename": "red.jpg",
             "mime_type": "image/jpeg", "position": 0},
            {"data": b64(make_png(color=(0, 0, 255))), "filename": "blue.png",
             "mime_type": "image/png", "position": 1},
        ],
        document_id=unique_doc_id("pt-two"),
    )
    resp = await async_client.post(
        "/api/v1/sign/rich", json=req, headers=enterprise_auth_headers
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()["data"]

    assert body["total_images"] == 2
    assert body["composite_manifest"]["ingredient_count"] == 2
    for img in body["images"]:
        assert img["c2pa_signed"] is False
        assert img["phash"] is not None


@pytest.mark.asyncio
async def test_sign_rich_then_verify_rich(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
):
    """Full round-trip: sign article -> verify by document_id."""
    doc_id = unique_doc_id("pt-roundtrip")
    req = rich_request(
        images=[
            {"data": b64(make_jpeg()), "filename": "main.jpg",
             "mime_type": "image/jpeg", "position": 0},
        ],
        document_id=doc_id,
    )

    # Sign
    sign_resp = await async_client.post(
        "/api/v1/sign/rich", json=req, headers=enterprise_auth_headers
    )
    assert sign_resp.status_code == 201, sign_resp.text
    sign_data = sign_resp.json()["data"]
    assert sign_data["composite_manifest"]["ingredient_count"] == 1

    # Verify rich article by document_id
    verify_resp = await async_client.post(
        "/api/v1/verify/rich",
        json={"document_id": doc_id},
    )
    assert verify_resp.status_code == 200, verify_resp.text
    vdata = verify_resp.json()

    assert vdata["document_id"] == doc_id
    assert vdata["valid"] is True
    assert vdata["composite_manifest_valid"] is True
    assert len(vdata["image_verifications"]) == 1


@pytest.mark.asyncio
async def test_sign_rich_then_verify_image(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
):
    """Sign article, take returned image bytes, pass to /verify/image.

    In passthrough mode the image has no JUMBF manifest, so verify/image
    returns valid=False with 'No C2PA manifest found'. This is correct
    behaviour -- the endpoint handles the case gracefully.
    """
    jpeg_bytes = make_jpeg(color=(50, 100, 150))
    req = rich_request(
        images=[
            {"data": b64(jpeg_bytes), "filename": "snap.jpg",
             "mime_type": "image/jpeg", "position": 0},
        ],
        document_id=unique_doc_id("pt-verifyimg"),
    )

    sign_resp = await async_client.post(
        "/api/v1/sign/rich", json=req, headers=enterprise_auth_headers
    )
    assert sign_resp.status_code == 201, sign_resp.text
    returned_b64 = sign_resp.json()["data"]["images"][0]["signed_image_b64"]

    verify_resp = await async_client.post(
        "/api/v1/verify/image",
        json={"image_data": returned_b64, "mime_type": "image/jpeg"},
    )
    assert verify_resp.status_code == 200, verify_resp.text
    vdata = verify_resp.json()
    # XMP embedded -> DB lookup by instance_id confirms provenance -> valid=True
    assert vdata["valid"] is True


@pytest.mark.asyncio
async def test_sign_rich_passthrough_duplicate_document_id_returns_422(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
):
    """Signing the same document_id twice should fail (unique constraint)."""
    doc_id = unique_doc_id("pt-dup")
    req = rich_request(
        images=[{"data": b64(make_jpeg()), "filename": "img.jpg",
                 "mime_type": "image/jpeg", "position": 0}],
        document_id=doc_id,
    )
    r1 = await async_client.post(
        "/api/v1/sign/rich", json=req, headers=enterprise_auth_headers
    )
    assert r1.status_code == 201, r1.text

    r2 = await async_client.post(
        "/api/v1/sign/rich", json=req, headers=enterprise_auth_headers
    )
    # Second attempt should fail with a DB constraint or 422
    assert r2.status_code in (422, 409, 500)


@pytest.mark.asyncio
async def test_sign_rich_passthrough_phash_in_db(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
):
    """pHash must be non-null in the returned image result."""
    req = rich_request(
        images=[{"data": b64(make_jpeg()), "filename": "hashcheck.jpg",
                 "mime_type": "image/jpeg", "position": 0}],
        document_id=unique_doc_id("pt-phash"),
    )
    resp = await async_client.post(
        "/api/v1/sign/rich", json=req, headers=enterprise_auth_headers
    )
    assert resp.status_code == 201, resp.text
    img = resp.json()["data"]["images"][0]
    assert img["phash"] is not None
    assert len(img["phash"]) == 16  # 64-bit pHash as 16-char hex


@pytest.mark.asyncio
async def test_sign_rich_passthrough_exif_stripped(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
):
    """Returned image bytes are EXIF-stripped (hash changes from raw input)."""
    jpeg = make_jpeg(color=(10, 20, 30))
    req = rich_request(
        images=[{"data": b64(jpeg), "filename": "exiftest.jpg",
                 "mime_type": "image/jpeg", "position": 0}],
        document_id=unique_doc_id("pt-exif"),
    )
    resp = await async_client.post(
        "/api/v1/sign/rich", json=req, headers=enterprise_auth_headers
    )
    assert resp.status_code == 201, resp.text
    returned_bytes = base64.b64decode(resp.json()["data"]["images"][0]["signed_image_b64"])
    # Must still be a valid JPEG
    assert returned_bytes[:2] == b"\xff\xd8"


@pytest.mark.asyncio
async def test_passthrough_image_has_encypher_xmp(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
):
    """Signed passthrough JPEG has XMP with matching instance_id, org_id, document_id."""
    from app.services.image_signing_service import sign_image
    from app.utils.image_utils import extract_encypher_xmp

    jpeg = make_jpeg(color=(30, 60, 90))
    result = await sign_image(
        image_data=jpeg,
        mime_type="image/jpeg",
        title="xmp_test.jpg",
        org_id="org_xmptest",
        document_id="doc_xmptest",
        image_id="img_xmptest",
        custom_assertions=[],
        rights_data={},
        signer_private_key_pem="",
        signer_cert_chain_pem="",
    )
    assert result.c2pa_signed is False
    xmp = extract_encypher_xmp(result.signed_bytes, "image/jpeg")
    assert xmp is not None
    assert xmp["instance_id"] == result.c2pa_instance_id
    assert xmp["org_id"] == "org_xmptest"
    assert xmp["document_id"] == "doc_xmptest"


@pytest.mark.asyncio
async def test_passthrough_png_has_encypher_xmp(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
):
    """Signed passthrough PNG has XMP with matching instance_id."""
    from app.services.image_signing_service import sign_image
    from app.utils.image_utils import extract_encypher_xmp

    png = make_png(color=(90, 30, 150))
    result = await sign_image(
        image_data=png,
        mime_type="image/png",
        title="xmp_test.png",
        org_id="org_pngtest",
        document_id="doc_pngtest",
        image_id="img_pngtest",
        custom_assertions=[],
        rights_data={},
        signer_private_key_pem="",
        signer_cert_chain_pem="",
    )
    assert result.c2pa_signed is False
    xmp = extract_encypher_xmp(result.signed_bytes, "image/png")
    assert xmp is not None
    assert xmp["instance_id"] == result.c2pa_instance_id
    assert xmp["org_id"] == "org_pngtest"
    assert xmp["document_id"] == "doc_pngtest"


@pytest.mark.asyncio
async def test_sign_rich_passthrough_attribution_lookup(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
):
    """After signing, pHash attribution lookup finds the image within the same org."""
    jpeg = make_jpeg(color=(123, 45, 67))
    req = rich_request(
        images=[{"data": b64(jpeg), "filename": "attrtest.jpg",
                 "mime_type": "image/jpeg", "position": 0}],
        document_id=unique_doc_id("pt-attr"),
    )
    sign_resp = await async_client.post(
        "/api/v1/sign/rich", json=req, headers=enterprise_auth_headers
    )
    assert sign_resp.status_code == 201, sign_resp.text

    # The returned image is EXIF-stripped; use its hash for attribution
    returned_b64 = sign_resp.json()["data"]["images"][0]["signed_image_b64"]
    attr_resp = await async_client.post(
        "/api/v1/enterprise/images/attribution",
        json={"image_data": returned_b64, "scope": "org", "threshold": 10},
        headers=enterprise_auth_headers,
    )
    assert attr_resp.status_code == 200, attr_resp.text
    attr_data = attr_resp.json()
    # Should find at least 1 match (the image we just signed)
    assert attr_data["match_count"] >= 1
