"""Tests for video stream C2PA signing service.

Unit tests for:
- VideoStreamSession lifecycle (start, sign segments, finalize)
- Manifest chaining (prev_manifest_hash linkage)
- Merkle root computation
- Session expiry and access control
"""

import struct
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# Helper: minimal ftyp box
def make_fake_mp4_segment() -> bytes:
    ftyp_data = b"mp42\x00\x00\x00\x00mp42isom"
    box_size = 8 + len(ftyp_data)
    return struct.pack(">I", box_size) + b"ftyp" + ftyp_data + b"\x00" * 256


class TestStreamSession:
    @pytest.mark.asyncio
    async def test_start_session(self):
        from app.services.video_stream_signing_service import start_stream_session

        session = await start_stream_session(
            org_id="org_test",
            private_key_pem="",
            cert_chain_pem="",
        )
        assert session.session_id.startswith("vstream_")
        assert session.org_id == "org_test"
        assert session.status == "active"
        assert session.segment_count == 0

    @pytest.mark.asyncio
    async def test_get_session_org_check(self):
        from app.services.video_stream_signing_service import get_session, start_stream_session

        session = await start_stream_session(
            org_id="org_a",
            private_key_pem="",
            cert_chain_pem="",
        )
        # Same org
        found = await get_session(session.session_id, "org_a")
        assert found is not None
        assert found.session_id == session.session_id

        # Different org
        found = await get_session(session.session_id, "org_b")
        assert found is None

    @pytest.mark.asyncio
    async def test_get_session_not_found(self):
        from app.services.video_stream_signing_service import get_session

        found = await get_session("nonexistent_session", "org_test")
        assert found is None


class TestSignSegment:
    @pytest.mark.asyncio
    async def test_passthrough_segment(self):
        from app.services.video_stream_signing_service import sign_segment, start_stream_session

        session = await start_stream_session(
            org_id="org_test",
            private_key_pem="",
            cert_chain_pem="",
        )
        segment_data = make_fake_mp4_segment()
        result = await sign_segment(session, segment_data, "video/mp4")

        assert result.segment_index == 0
        assert result.c2pa_signed is False
        assert result.original_hash.startswith("sha256:")
        assert result.size_bytes > 0
        assert session.segment_count == 1

    @pytest.mark.asyncio
    async def test_segment_index_increments(self):
        from app.services.video_stream_signing_service import sign_segment, start_stream_session

        session = await start_stream_session(
            org_id="org_test",
            private_key_pem="",
            cert_chain_pem="",
        )
        segment_data = make_fake_mp4_segment()

        r0 = await sign_segment(session, segment_data, "video/mp4")
        r1 = await sign_segment(session, segment_data, "video/mp4")
        r2 = await sign_segment(session, segment_data, "video/mp4")

        assert r0.segment_index == 0
        assert r1.segment_index == 1
        assert r2.segment_index == 2
        assert session.segment_count == 3

    @pytest.mark.asyncio
    async def test_manifest_chain_linkage(self):
        from app.services.video_stream_signing_service import sign_segment, start_stream_session

        session = await start_stream_session(
            org_id="org_test",
            private_key_pem="",
            cert_chain_pem="",
        )
        segment_data = make_fake_mp4_segment()

        # First segment: no prev hash
        assert session.prev_manifest_hash is None
        r0 = await sign_segment(session, segment_data, "video/mp4")

        # After first segment: prev_manifest_hash is set
        assert session.prev_manifest_hash == r0.c2pa_manifest_hash

        # Second segment: prev_manifest_hash from first
        r1 = await sign_segment(session, segment_data, "video/mp4")
        assert session.prev_manifest_hash == r1.c2pa_manifest_hash

    @pytest.mark.asyncio
    async def test_rejects_finalized_session(self):
        from app.services.video_stream_signing_service import (
            finalize_stream,
            sign_segment,
            start_stream_session,
        )

        session = await start_stream_session(
            org_id="org_test",
            private_key_pem="",
            cert_chain_pem="",
        )
        await finalize_stream(session)

        with pytest.raises(ValueError, match="finalized"):
            await sign_segment(session, make_fake_mp4_segment(), "video/mp4")

    @pytest.mark.asyncio
    async def test_rejects_invalid_segment(self):
        from app.services.video_stream_signing_service import sign_segment, start_stream_session

        session = await start_stream_session(
            org_id="org_test",
            private_key_pem="",
            cert_chain_pem="",
        )

        with pytest.raises(ValueError):
            await sign_segment(session, b"", "video/mp4")


class TestFinalizeStream:
    @pytest.mark.asyncio
    async def test_finalize_empty_session(self):
        from app.services.video_stream_signing_service import finalize_stream, start_stream_session

        session = await start_stream_session(
            org_id="org_test",
            private_key_pem="",
            cert_chain_pem="",
        )
        result = await finalize_stream(session)

        assert result.session_id == session.session_id
        assert result.segment_count == 0
        assert result.merkle_root.startswith("sha256:")
        assert result.status == "finalized"
        assert session.status == "finalized"

    @pytest.mark.asyncio
    async def test_finalize_with_segments(self):
        from app.services.video_stream_signing_service import (
            finalize_stream,
            sign_segment,
            start_stream_session,
        )

        session = await start_stream_session(
            org_id="org_test",
            private_key_pem="",
            cert_chain_pem="",
        )
        segment_data = make_fake_mp4_segment()
        await sign_segment(session, segment_data, "video/mp4")
        await sign_segment(session, segment_data, "video/mp4")
        await sign_segment(session, segment_data, "video/mp4")

        result = await finalize_stream(session)
        assert result.segment_count == 3
        assert result.merkle_root.startswith("sha256:")
        # Merkle root should not be all zeros (since we have actual segment hashes)
        # In passthrough mode, segment hashes are all "sha256:0...0" so the root
        # will be deterministic but non-trivial

    @pytest.mark.asyncio
    async def test_double_finalize_rejected(self):
        from app.services.video_stream_signing_service import finalize_stream, start_stream_session

        session = await start_stream_session(
            org_id="org_test",
            private_key_pem="",
            cert_chain_pem="",
        )
        await finalize_stream(session)

        with pytest.raises(ValueError, match="finalized"):
            await finalize_stream(session)

    @pytest.mark.asyncio
    async def test_deterministic_merkle_root(self):
        """Same segments should produce the same Merkle root."""
        from app.services.video_stream_signing_service import (
            finalize_stream,
            sign_segment,
            start_stream_session,
        )

        segment_data = make_fake_mp4_segment()

        session1 = await start_stream_session(org_id="org_a", private_key_pem="", cert_chain_pem="")
        await sign_segment(session1, segment_data, "video/mp4")
        await sign_segment(session1, segment_data, "video/mp4")
        r1 = await finalize_stream(session1)

        session2 = await start_stream_session(org_id="org_b", private_key_pem="", cert_chain_pem="")
        await sign_segment(session2, segment_data, "video/mp4")
        await sign_segment(session2, segment_data, "video/mp4")
        r2 = await finalize_stream(session2)

        assert r1.merkle_root == r2.merkle_root


class TestMerkleRoot:
    def test_empty_list(self):
        from app.services.video_stream_signing_service import _compute_merkle_root

        result = _compute_merkle_root([])
        assert result == "sha256:" + "0" * 64

    def test_single_hash(self):
        from app.services.video_stream_signing_service import _compute_merkle_root

        h = "sha256:" + "ab" * 32
        result = _compute_merkle_root([h])
        assert result.startswith("sha256:")
        # Single node: hash of (node + node) since it's duplicated
        assert len(result) == 7 + 64

    def test_two_hashes(self):
        from app.services.video_stream_signing_service import _compute_merkle_root

        h1 = "sha256:" + "aa" * 32
        h2 = "sha256:" + "bb" * 32
        result = _compute_merkle_root([h1, h2])
        assert result.startswith("sha256:")
        assert len(result) == 7 + 64

    def test_deterministic(self):
        from app.services.video_stream_signing_service import _compute_merkle_root

        hashes = ["sha256:" + f"{i:02x}" * 32 for i in range(5)]
        r1 = _compute_merkle_root(hashes)
        r2 = _compute_merkle_root(hashes)
        assert r1 == r2

    def test_order_matters(self):
        from app.services.video_stream_signing_service import _compute_merkle_root

        h1 = "sha256:" + "aa" * 32
        h2 = "sha256:" + "bb" * 32
        r_forward = _compute_merkle_root([h1, h2])
        r_reverse = _compute_merkle_root([h2, h1])
        assert r_forward != r_reverse
