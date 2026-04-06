"""
Video codec helpers using PyAV (libav wrapper).

Provides decode/encode functions that operate on YCbCr (YUV420p) frame arrays,
isolating the spread_spectrum module from any PyAV dependency.

PyAV availability is checked at import time. If unavailable (e.g. during
tests on a machine without ffmpeg), _av_available is False and both
decode_video / encode_video raise RuntimeError with a clear message.

Streaming API (memory-efficient):
  - decode_video_blocks(video_bytes, block_frames) -- generator, yields
    (y_block, cb_block, cr_block, meta) one block at a time. Peak memory is
    O(block_frames * H * W) instead of O(total_frames * H * W).
  - encode_video_streaming(blocks_iter, meta) -- accepts an iterator of
    (y_block, cb_block, cr_block) tuples and writes frames incrementally.

Legacy API (backward compatible):
  - decode_video(video_bytes) -- loads ALL frames; kept for tests and callers
    that still use array-based processing.
  - encode_video(y_frames, cb_frames, cr_frames, meta) -- array-based encode;
    unchanged signature so existing tests continue to pass.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterator, Optional

import numpy as np
from numpy.typing import NDArray

try:
    import av as _av

    _av_available = True
except ImportError:
    _av = None  # type: ignore[assignment]
    _av_available = False


@dataclass
class VideoMeta:
    """Metadata needed to re-encode video after watermarking."""

    width: int
    height: int
    fps_num: int
    fps_den: int
    codec_name: str  # e.g. "h264", "hevc"
    pix_fmt: str  # e.g. "yuv420p"
    total_frames: int
    duration_seconds: float
    bitrate: Optional[int]  # original bitrate, None if unknown


def _extract_meta(container: "_av.container.InputContainer", video_stream: "_av.streams.VideoStream") -> VideoMeta:
    """Extract VideoMeta from an open container and its video stream.

    Called once before frame iteration so metadata is always available.
    """
    codec_name: str = video_stream.codec_context.name or "h264"
    pix_fmt_raw: str = video_stream.codec_context.pix_fmt or "yuv420p"
    width: int = video_stream.width
    height: int = video_stream.height

    if video_stream.average_rate is not None:
        fps_num = int(video_stream.average_rate.numerator)
        fps_den = int(video_stream.average_rate.denominator)
    else:
        fps_num, fps_den = 30, 1

    bitrate: Optional[int] = None
    if video_stream.bit_rate:
        bitrate = int(video_stream.bit_rate)
    elif container.bit_rate:
        bitrate = int(container.bit_rate)

    duration_seconds: float = 0.0
    if video_stream.duration is not None and video_stream.time_base is not None:
        duration_seconds = float(video_stream.duration * video_stream.time_base)
    elif container.duration is not None:
        duration_seconds = float(container.duration / 1_000_000)

    pix_fmt = "yuv420p" if "yuv420p" in pix_fmt_raw or pix_fmt_raw == "yuv420p" else pix_fmt_raw

    # total_frames is filled in after decoding; caller may update it
    return VideoMeta(
        width=width,
        height=height,
        fps_num=fps_num,
        fps_den=fps_den,
        codec_name=codec_name,
        pix_fmt=pix_fmt,
        total_frames=0,
        duration_seconds=duration_seconds,
        bitrate=bitrate,
    )


def decode_video_blocks(
    video_bytes: bytes,
    block_frames: int = 300,
) -> Iterator[tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], VideoMeta]]:
    """Decode video in streaming blocks, yielding one block at a time.

    Yields (y_block, cb_block, cr_block, meta) where each block array has shape
    (n, H, W) for Y and (n, H//2, W//2) for Cb/Cr, with n <= block_frames.
    meta is the same VideoMeta object on every yield; its total_frames field is
    set to the number of frames in the current block (not the entire video) so
    that the encoder can use it without needing all frames up front.

    Peak memory: O(block_frames * H * W) - independent of total video length.

    Raises:
        RuntimeError: if PyAV is unavailable.
        ValueError: if no frames are decoded.
    """
    if not _av_available:
        raise RuntimeError("PyAV is not available. Install it with: uv add av (requires ffmpeg headers).")

    container = _av.open(io.BytesIO(video_bytes))
    video_stream = next(s for s in container.streams if s.type == "video")
    meta = _extract_meta(container, video_stream)
    height = meta.height
    width = meta.width

    y_buf: list[NDArray[np.float64]] = []
    cb_buf: list[NDArray[np.float64]] = []
    cr_buf: list[NDArray[np.float64]] = []
    total_yielded = 0

    for packet in container.demux(video_stream):
        for frame in packet.decode():
            yuv_frame = frame.reformat(format="yuv420p")
            arr = yuv_frame.to_ndarray(format="yuv420p")
            y_buf.append(arr[:height, :width].astype(np.float64))
            cb_buf.append(arr[height : height + height // 2, : width // 2].astype(np.float64))
            cr_buf.append(arr[height : height + height // 2, width // 2 :].astype(np.float64))

            if len(y_buf) == block_frames:
                meta.total_frames = len(y_buf)
                yield np.stack(y_buf), np.stack(cb_buf), np.stack(cr_buf), meta
                total_yielded += len(y_buf)
                y_buf = []
                cb_buf = []
                cr_buf = []

    container.close()

    # Yield the final (possibly partial) block
    if y_buf:
        meta.total_frames = len(y_buf)
        yield np.stack(y_buf), np.stack(cb_buf), np.stack(cr_buf), meta
        total_yielded += len(y_buf)

    if total_yielded == 0:
        raise ValueError("No video frames decoded from input bytes.")


def decode_video(
    video_bytes: bytes,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], VideoMeta]:
    """Decode video to Y, Cb, Cr channel arrays (loads all frames into memory).

    Kept for backward compatibility with existing tests and callers. For large
    videos use decode_video_blocks() instead to avoid OOM.

    Returns:
        y_frames:  float64 array of shape (n_frames, height, width)       - luminance
        cb_frames: float64 array of shape (n_frames, height//2, width//2) - chroma blue (4:2:0)
        cr_frames: float64 array of shape (n_frames, height//2, width//2) - chroma red (4:2:0)
        meta:      VideoMeta for re-encoding
    """
    if not _av_available:
        raise RuntimeError("PyAV is not available. Install it with: uv add av (requires ffmpeg headers).")

    container = _av.open(io.BytesIO(video_bytes))
    video_stream = next(s for s in container.streams if s.type == "video")
    meta = _extract_meta(container, video_stream)
    height = meta.height
    width = meta.width

    y_list: list[NDArray[np.float64]] = []
    cb_list: list[NDArray[np.float64]] = []
    cr_list: list[NDArray[np.float64]] = []

    for packet in container.demux(video_stream):
        for frame in packet.decode():
            yuv_frame = frame.reformat(format="yuv420p")
            arr = yuv_frame.to_ndarray(format="yuv420p")
            y_list.append(arr[:height, :width].astype(np.float64))
            cb_list.append(arr[height : height + height // 2, : width // 2].astype(np.float64))
            cr_list.append(arr[height : height + height // 2, width // 2 :].astype(np.float64))

    container.close()

    total_frames = len(y_list)
    if total_frames == 0:
        raise ValueError("No video frames decoded from input bytes.")

    meta.total_frames = total_frames
    return (
        np.stack(y_list, axis=0),
        np.stack(cb_list, axis=0),
        np.stack(cr_list, axis=0),
        meta,
    )


def _build_encoder(
    container: "_av.container.OutputContainer",
    meta: VideoMeta,
) -> "_av.streams.VideoStream":
    """Add and configure the video encode stream on an open output container."""
    encode_codec = meta.codec_name
    if encode_codec in ("h264", "avc", "avc1"):
        encode_codec = "libx264"
    elif encode_codec in ("hevc", "hvc1", "hev1"):
        encode_codec = "libx265"

    stream = container.add_stream(encode_codec, rate=Fraction(meta.fps_num, meta.fps_den))
    stream.width = meta.width
    stream.height = meta.height
    stream.pix_fmt = "yuv420p"
    if meta.bitrate:
        stream.bit_rate = meta.bitrate
    return stream


def _write_frame(
    stream: "_av.streams.VideoStream",
    container: "_av.container.OutputContainer",
    y_plane: NDArray[np.uint8],
    cb_plane: NDArray[np.uint8],
    cr_plane: NDArray[np.uint8],
    frame_idx: int,
    meta: VideoMeta,
) -> None:
    """Pack one YUV420p frame and mux it into the container."""
    height = meta.height
    width = meta.width
    # yuv420p packed layout: Y in rows 0..h-1 (full width), then Cb (left half)
    # and Cr (right half) side-by-side in rows h..h+h//2-1.
    packed = np.zeros((height + height // 2, width), dtype=np.uint8)
    packed[:height, :] = y_plane
    packed[height : height + height // 2, : width // 2] = cb_plane
    packed[height : height + height // 2, width // 2 :] = cr_plane

    frame = _av.VideoFrame.from_ndarray(packed, format="yuv420p")
    frame.pts = frame_idx
    frame.time_base = Fraction(meta.fps_den, meta.fps_num)
    for packet in stream.encode(frame):
        container.mux(packet)


def encode_video_streaming(
    blocks_iter: Iterator[tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]],
    meta: VideoMeta,
    output_format: str = "mp4",
) -> bytes:
    """Re-encode YCbCr frames from a streaming block iterator.

    Args:
        blocks_iter: Iterator of (y_block, cb_block, cr_block) tuples where
                     each block array has shape (n, H, W) or (n, H//2, W//2).
        meta:        VideoMeta (width, height, fps, codec, bitrate).
        output_format: Container format, e.g. "mp4", "matroska".

    Returns:
        Encoded video bytes.

    Peak memory: O(block_frames * H * W) - independent of total video length.
    """
    if not _av_available:
        raise RuntimeError("PyAV is not available. Install it with: uv add av (requires ffmpeg headers).")

    output_buf = io.BytesIO()
    container = _av.open(output_buf, mode="w", format=output_format)
    stream = _build_encoder(container, meta)

    frame_idx = 0
    for y_block, cb_block, cr_block in blocks_iter:
        n = y_block.shape[0]
        for i in range(n):
            _write_frame(
                stream,
                container,
                np.clip(y_block[i], 0, 255).astype(np.uint8),
                np.clip(cb_block[i], 0, 255).astype(np.uint8),
                np.clip(cr_block[i], 0, 255).astype(np.uint8),
                frame_idx,
                meta,
            )
            frame_idx += 1

    for packet in stream.encode():
        container.mux(packet)

    container.close()
    return output_buf.getvalue()


def encode_video(
    y_frames: NDArray[np.float64],
    cb_frames: NDArray[np.float64],
    cr_frames: NDArray[np.float64],
    meta: VideoMeta,
    output_format: str = "mp4",
) -> bytes:
    """Re-encode YCbCr frames back to video bytes (array-based, backward compatible).

    Args:
        y_frames:  float64 array of shape (n_frames, height, width)
        cb_frames: float64 array of shape (n_frames, height//2, width//2)
        cr_frames: float64 array of shape (n_frames, height//2, width//2)
        meta:      VideoMeta from decode_video
        output_format: Container format, e.g. "mp4", "matroska"

    Returns:
        Encoded video bytes.
    """
    if not _av_available:
        raise RuntimeError("PyAV is not available. Install it with: uv add av (requires ffmpeg headers).")

    output_buf = io.BytesIO()
    container = _av.open(output_buf, mode="w", format=output_format)
    stream = _build_encoder(container, meta)

    n_frames = y_frames.shape[0]
    for idx in range(n_frames):
        _write_frame(
            stream,
            container,
            np.clip(y_frames[idx], 0, 255).astype(np.uint8),
            np.clip(cb_frames[idx], 0, 255).astype(np.uint8),
            np.clip(cr_frames[idx], 0, 255).astype(np.uint8),
            idx,
            meta,
        )

    for packet in stream.encode():
        container.mux(packet)

    container.close()
    return output_buf.getvalue()
