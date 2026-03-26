"""Tests for SignedVideo SQLAlchemy model."""

import uuid

from app.models.signed_video import SignedVideo


class TestSignedVideoModel:
    def test_instantiation(self):
        row = SignedVideo(
            organization_id="org_test",
            document_id="doc_test",
            video_id="vid_abc123",
            title="test-video.mp4",
            mime_type="video/mp4",
            original_hash="sha256:aabbccdd",
            signed_hash="sha256:eeff0011",
            size_bytes=1024,
            c2pa_signed=True,
        )
        assert row.video_id == "vid_abc123"
        assert row.mime_type == "video/mp4"
        assert row.c2pa_signed is True
        assert row.phash is None
        assert row.digital_source_type is None

    def test_defaults(self):
        row = SignedVideo(
            organization_id="org_test",
            document_id="doc_test",
            video_id="vid_def456",
            mime_type="video/mp4",
            original_hash="sha256:00",
            signed_hash="sha256:00",
            size_bytes=100,
        )
        # Defaults apply at DB flush time, not at Python instantiation
        # c2pa_signed default=False, but before flush it may be None
        assert row.c2pa_signed in (False, None)

    def test_repr(self):
        row = SignedVideo(
            organization_id="org_test",
            document_id="doc_test",
            video_id="vid_repr",
            mime_type="video/mp4",
            original_hash="sha256:00",
            signed_hash="sha256:00",
            size_bytes=100,
        )
        r = repr(row)
        assert "vid_repr" in r
        assert "doc_test" in r

    def test_tablename(self):
        assert SignedVideo.__tablename__ == "signed_videos"

    def test_id_has_default(self):
        # The column default should be a callable (uuid.uuid4)
        assert SignedVideo.id.default is not None
        assert callable(SignedVideo.id.default.arg)
