"""
Tests for the video_codec module (decode/encode via PyAV).

Tests are skipped when PyAV or ffmpeg is not available on the host. The
spread_spectrum tests are the authoritative correctness tests and always run.
"""

import io
from fractions import Fraction

import numpy as np
import pytest

from app.services.video_codec import _av_available, VideoMeta

_skip_no_av = pytest.mark.skipif(not _av_available, reason="PyAV/ffmpeg not available")


def _make_synthetic_video(
    n_frames: int = 10,
    width: int = 64,
    height: int = 48,
    fps: int = 30,
    y_value: int = 128,
) -> bytes:
    """Create a synthetic video (solid color frames) in-memory via PyAV.

    Returns raw MP4 bytes.
    """
    import av

    output_buf = io.BytesIO()
    container = av.open(output_buf, mode="w", format="mp4")
    stream = container.add_stream("libx264", rate=fps)
    stream.width = width
    stream.height = height
    stream.pix_fmt = "yuv420p"
    # CRF-based encoding for consistent output
    stream.options = {"crf": "23"}

    for i in range(n_frames):
        # Build packed yuv420p array
        packed = np.zeros((height + height // 2, width), dtype=np.uint8)
        packed[:height, :] = y_value  # Y plane
        packed[height:, : width // 2] = 128  # Cb neutral
        frame = av.VideoFrame.from_ndarray(packed, format="yuv420p")
        frame.pts = i
        frame.time_base = Fraction(1, fps)
        for packet in stream.encode(frame):
            container.mux(packet)

    for packet in stream.encode():
        container.mux(packet)

    container.close()
    return output_buf.getvalue()


@_skip_no_av
def test_decode_encode_roundtrip():
    """Decode a synthetic video and re-encode; frame count and dimensions must match."""
    from app.services.video_codec import decode_video, encode_video

    n_frames = 10
    width, height = 64, 48
    video_bytes = _make_synthetic_video(n_frames=n_frames, width=width, height=height)

    y_frames, cb_frames, cr_frames, meta = decode_video(video_bytes)

    # Frame count - allow small tolerance for codec buffering (keyframe + B-frames)
    assert abs(y_frames.shape[0] - n_frames) <= 2, f"Expected ~{n_frames} frames, got {y_frames.shape[0]}"
    assert y_frames.shape[1] == height, f"Y height mismatch: {y_frames.shape[1]} != {height}"
    assert y_frames.shape[2] == width, f"Y width mismatch: {y_frames.shape[2]} != {width}"

    # Re-encode and decode again
    output_bytes = encode_video(y_frames, cb_frames, cr_frames, meta, output_format="mp4")
    assert len(output_bytes) > 0, "encoded video must be non-empty"

    y2, cb2, cr2, meta2 = decode_video(output_bytes)
    assert y2.shape[1] == height
    assert y2.shape[2] == width


@_skip_no_av
def test_y_channel_extraction():
    """Y values for a solid-gray frame must be within plausible range [0, 255]."""
    from app.services.video_codec import decode_video

    y_target = 150
    video_bytes = _make_synthetic_video(n_frames=5, y_value=y_target)

    y_frames, _cb, _cr, _meta = decode_video(video_bytes)

    # Y values must be valid pixel range
    assert y_frames.min() >= 0.0, "Y values must be >= 0"
    assert y_frames.max() <= 255.0, "Y values must be <= 255"

    # Mean should be close to the target (allow codec quantization tolerance)
    mean_y = float(np.mean(y_frames))
    assert (
        abs(mean_y - y_target) < 20
    ), f"Mean Y {mean_y:.1f} too far from target {y_target} (codec quantization tolerance is 20)"


@_skip_no_av
def test_meta_extraction():
    """VideoMeta fields must be populated with correct values."""
    from app.services.video_codec import decode_video

    fps = 30
    width, height = 64, 48
    n_frames = 15
    video_bytes = _make_synthetic_video(n_frames=n_frames, width=width, height=height, fps=fps)

    _y, _cb, _cr, meta = decode_video(video_bytes)

    assert isinstance(meta, VideoMeta)
    assert meta.width == width, f"meta.width {meta.width} != {width}"
    assert meta.height == height, f"meta.height {meta.height} != {height}"
    assert meta.fps_num > 0, "fps_num must be positive"
    assert meta.fps_den > 0, "fps_den must be positive"
    # Codec should be h264 (we encode with libx264)
    assert meta.codec_name in ("h264", "libx264"), f"unexpected codec: {meta.codec_name!r}"
    assert meta.pix_fmt == "yuv420p", f"unexpected pix_fmt: {meta.pix_fmt!r}"
    assert meta.total_frames > 0, "total_frames must be positive"


# ---------------------------------------------------------------------------
# Streaming API tests
# ---------------------------------------------------------------------------


@_skip_no_av
def test_decode_video_blocks_yields_correct_shape():
    """decode_video_blocks must yield blocks whose frames have the right shape."""
    from app.services.video_codec import decode_video_blocks

    n_frames = 12
    width, height = 64, 48
    block_frames = 5
    video_bytes = _make_synthetic_video(n_frames=n_frames, width=width, height=height)

    blocks = list(decode_video_blocks(video_bytes, block_frames=block_frames))
    assert len(blocks) >= 2, "expected at least 2 blocks for a 12-frame video with block_frames=5"

    for y_block, cb_block, cr_block, meta in blocks:
        assert y_block.ndim == 3
        assert y_block.shape[1] == height
        assert y_block.shape[2] == width
        assert cb_block.shape == (y_block.shape[0], height // 2, width // 2)
        assert cr_block.shape == (y_block.shape[0], height // 2, width // 2)
        assert isinstance(meta, VideoMeta)
        assert meta.width == width
        assert meta.height == height


@_skip_no_av
def test_decode_video_blocks_total_frame_count():
    """Total frames across all blocks must equal the legacy decode_video frame count."""
    from app.services.video_codec import decode_video, decode_video_blocks

    n_frames = 10
    width, height = 64, 48
    video_bytes = _make_synthetic_video(n_frames=n_frames, width=width, height=height)

    # Legacy decode for ground truth
    y_all, _cb, _cr, _meta = decode_video(video_bytes)
    expected_total = y_all.shape[0]

    # Streaming decode - use a block size smaller than total frames to force multiple yields
    block_frames = 3
    blocks = list(decode_video_blocks(video_bytes, block_frames=block_frames))
    streaming_total = sum(b[0].shape[0] for b in blocks)

    assert streaming_total == expected_total, f"streaming total {streaming_total} != legacy total {expected_total}"


@_skip_no_av
def test_encode_video_streaming_roundtrip():
    """encode_video_streaming must produce decodable output matching original dimensions."""
    from app.services.video_codec import decode_video, decode_video_blocks, encode_video_streaming

    n_frames = 10
    width, height = 64, 48
    video_bytes = _make_synthetic_video(n_frames=n_frames, width=width, height=height)

    # Decode in blocks, pass blocks straight to streaming encoder (no watermark)
    blocks = list(decode_video_blocks(video_bytes, block_frames=4))
    # Extract meta from the first block for the encoder
    meta = blocks[0][3]
    passthrough_blocks = ((y, cb, cr) for y, cb, cr, _m in blocks)

    output_bytes = encode_video_streaming(passthrough_blocks, meta, output_format="mp4")
    assert len(output_bytes) > 0, "encoded video must be non-empty"

    # Decode the re-encoded video and check dimensions
    y2, _cb2, _cr2, meta2 = decode_video(output_bytes)
    assert y2.shape[1] == height, f"height mismatch after streaming encode: {y2.shape[1]} != {height}"
    assert y2.shape[2] == width, f"width mismatch after streaming encode: {y2.shape[2]} != {width}"


@_skip_no_av
def test_streaming_and_legacy_produce_same_frame_count():
    """Streaming encode/decode roundtrip must yield same frame count as legacy path."""
    from app.services.video_codec import decode_video, decode_video_blocks, encode_video_streaming

    n_frames = 10
    width, height = 64, 48
    video_bytes = _make_synthetic_video(n_frames=n_frames, width=width, height=height)

    # Legacy path
    y_leg, cb_leg, cr_leg, meta_leg = decode_video(video_bytes)
    legacy_count = y_leg.shape[0]

    # Streaming path
    blocks = list(decode_video_blocks(video_bytes, block_frames=4))
    meta = blocks[0][3]
    passthrough_blocks = ((y, cb, cr) for y, cb, cr, _m in blocks)
    output_bytes = encode_video_streaming(passthrough_blocks, meta, output_format="mp4")
    y_stream, _cb, _cr, _meta = decode_video(output_bytes)
    streaming_count = y_stream.shape[0]

    assert streaming_count == legacy_count, f"streaming frame count {streaming_count} != legacy {legacy_count}"
