"""Video stream C2PA signing service (C2PA 2.3 Section 19).

Per-segment manifest signing with backwards-linked provenance chain.
Each CMAF/fMP4 segment gets its own C2PA manifest. The manifest includes
a c2pa.ingredient.v3 assertion referencing the previous segment's manifest
hash, creating a verifiable chain across the stream.

Session storage:
- Primary: Redis via session_service.redis_client (multi-worker safe)
- Fallback: in-memory dict when Redis is unavailable (dev mode)
- PEM private keys are encrypted at rest in Redis via AESGCM
"""

import base64
import hashlib
import json
import logging
import secrets
import time
import uuid
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any, Dict, List, Optional

from app.config import settings
from app.services.video_watermark_client import SOFT_BINDING_ASSERTION_VIDEO, video_watermark_client
from app.utils.hashing import compute_sha256
from app.utils.video_utils import validate_video

logger = logging.getLogger(__name__)

# In-memory fallback (used when Redis is unavailable)
_sessions: Dict[str, "VideoStreamSession"] = {}
_SESSION_TTL = 3600  # 1 hour default
_SESSION_MAX_IDLE = 300  # 5 min idle timeout
_REDIS_SESSION_PREFIX = "encypher:vstream:"


@dataclass
class VideoStreamSession:
    """State for an active video stream signing session."""

    session_id: str
    org_id: str
    private_key_pem: str
    cert_chain_pem: str
    stream_id: str = ""
    segment_count: int = 0
    segment_manifest_hashes: List[str] = field(default_factory=list)
    prev_manifest_hash: Optional[str] = None
    prev_manifest_id: Optional[str] = None  # C2PA instance ID of previous segment
    status: str = "active"  # active | finalized | expired
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    expires_at: float = 0.0
    enable_video_watermark: bool = False
    watermark_payload: Optional[str] = None  # Computed once at session start, shared across segments

    def __post_init__(self) -> None:
        if not self.stream_id:
            self.stream_id = "urn:uuid:" + str(uuid.uuid4())
        if self.expires_at == 0.0:
            self.expires_at = self.created_at + _SESSION_TTL


@dataclass
class SignedSegmentResult:
    """Result of signing a single video segment."""

    segment_index: int
    stream_id: str
    signed_bytes: bytes
    original_hash: str
    signed_hash: str
    c2pa_instance_id: str
    c2pa_manifest_hash: str
    size_bytes: int
    mime_type: str
    c2pa_signed: bool
    watermark_applied: bool = False


@dataclass
class StreamFinalizeResult:
    """Result of finalizing a video stream session."""

    session_id: str
    stream_id: str
    segment_count: int
    merkle_root: str
    status: str


# ---------------------------------------------------------------------------
# Redis session serialization (PEM encrypted at rest)
# ---------------------------------------------------------------------------


def _get_redis() -> Any:
    """Get Redis client, or None if unavailable."""
    try:
        from app.services.session_service import session_service

        return session_service.redis_client
    except Exception:
        return None


def _serialize_session(session: VideoStreamSession) -> str:
    """Serialize session to JSON with encrypted private key."""
    data = {
        "session_id": session.session_id,
        "org_id": session.org_id,
        "cert_chain_pem": session.cert_chain_pem,
        "stream_id": session.stream_id,
        "segment_count": session.segment_count,
        "segment_manifest_hashes": session.segment_manifest_hashes,
        "prev_manifest_hash": session.prev_manifest_hash,
        "prev_manifest_id": session.prev_manifest_id,
        "status": session.status,
        "created_at": session.created_at,
        "last_activity": session.last_activity,
        "expires_at": session.expires_at,
        "enable_video_watermark": session.enable_video_watermark,
        "watermark_payload": session.watermark_payload,
    }
    # Encrypt private key before storing in Redis
    try:
        from app.utils.crypto_utils import encrypt_sensitive_value

        encrypted = encrypt_sensitive_value(session.private_key_pem)
        data["private_key_pem_encrypted"] = encrypted.hex()
    except Exception:
        logger.warning("Failed to encrypt PEM for Redis storage, skipping Redis")
        raise

    return json.dumps(data)


def _deserialize_session(raw: str) -> VideoStreamSession:
    """Deserialize session from JSON, decrypting private key."""
    data = json.loads(raw)

    # Decrypt private key
    from app.utils.crypto_utils import decrypt_sensitive_value

    private_key_pem = decrypt_sensitive_value(bytes.fromhex(data["private_key_pem_encrypted"]))

    return VideoStreamSession(
        session_id=data["session_id"],
        org_id=data["org_id"],
        private_key_pem=private_key_pem,
        cert_chain_pem=data["cert_chain_pem"],
        stream_id=data["stream_id"],
        segment_count=data["segment_count"],
        segment_manifest_hashes=data["segment_manifest_hashes"],
        prev_manifest_hash=data.get("prev_manifest_hash"),
        prev_manifest_id=data.get("prev_manifest_id"),
        status=data["status"],
        created_at=data["created_at"],
        last_activity=data["last_activity"],
        expires_at=data["expires_at"],
        enable_video_watermark=data.get("enable_video_watermark", False),
        watermark_payload=data.get("watermark_payload"),
    )


async def _redis_save_session(session: VideoStreamSession) -> bool:
    """Save session to Redis. Returns True on success."""
    redis_client = _get_redis()
    if not redis_client:
        return False
    try:
        remaining_ttl = max(1, int(session.expires_at - time.time()))
        serialized = _serialize_session(session)
        await redis_client.setex(
            f"{_REDIS_SESSION_PREFIX}{session.session_id}",
            remaining_ttl,
            serialized,
        )
        return True
    except Exception as exc:
        logger.debug("Redis session save failed: %s", exc)
        return False


async def _redis_get_session(session_id: str) -> Optional[VideoStreamSession]:
    """Load session from Redis. Returns None if not found."""
    redis_client = _get_redis()
    if not redis_client:
        return None
    try:
        raw = await redis_client.get(f"{_REDIS_SESSION_PREFIX}{session_id}")
        if raw is None:
            return None
        return _deserialize_session(raw)
    except Exception as exc:
        logger.debug("Redis session load failed: %s", exc)
        return None


async def _redis_delete_session(session_id: str) -> None:
    """Delete session from Redis."""
    redis_client = _get_redis()
    if redis_client:
        try:
            await redis_client.delete(f"{_REDIS_SESSION_PREFIX}{session_id}")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# In-memory fallback
# ---------------------------------------------------------------------------


def _cleanup_expired_sessions() -> None:
    """Remove expired/idle sessions from in-memory fallback."""
    now = time.time()
    expired = [sid for sid, s in _sessions.items() if now > s.expires_at or (s.status == "active" and now - s.last_activity > _SESSION_MAX_IDLE)]
    for sid in expired:
        s = _sessions.pop(sid, None)
        if s and s.status == "active":
            s.status = "expired"
            logger.info("Stream session expired: %s (segments=%d)", sid, s.segment_count)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _compute_merkle_root(hashes: List[str]) -> str:
    """Compute Merkle root over a list of hash strings.

    Each hash is a 'sha256:hex' string. Returns a 'sha256:hex' Merkle root.
    Leaf nodes are the hashes themselves. Empty list returns a zero hash.
    """
    if not hashes:
        return "sha256:" + "0" * 64

    # Strip 'sha256:' prefix for computation
    nodes = [bytes.fromhex(h.removeprefix("sha256:")) for h in hashes]

    while len(nodes) > 1:
        next_level = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1] if i + 1 < len(nodes) else left  # duplicate last if odd
            combined = hashlib.sha256(left + right).digest()
            next_level.append(combined)
        nodes = next_level

    return "sha256:" + nodes[0].hex()


async def start_stream_session(
    *,
    org_id: str,
    private_key_pem: str,
    cert_chain_pem: str,
    enable_video_watermark: bool = False,
) -> VideoStreamSession:
    """Create a new video stream signing session.

    Credentials are cached for the session lifetime to avoid per-segment DB reads.
    If enable_video_watermark is True, the watermark payload is computed once here
    and stored on the session so all segments share the same payload.
    """
    session_id = f"vstream_{secrets.token_hex(12)}"

    watermark_payload: Optional[str] = None
    if enable_video_watermark:
        from app.services.video_watermark_client import compute_video_watermark_payload

        watermark_payload = compute_video_watermark_payload(session_id, org_id)
        logger.info("Video watermark payload computed for session %s", session_id)

    session = VideoStreamSession(
        session_id=session_id,
        org_id=org_id,
        private_key_pem=private_key_pem,
        cert_chain_pem=cert_chain_pem,
        enable_video_watermark=enable_video_watermark,
        watermark_payload=watermark_payload,
    )

    saved = await _redis_save_session(session)
    if not saved:
        _cleanup_expired_sessions()
        _sessions[session_id] = session

    logger.info(
        "Stream session started: %s org=%s redis=%s watermark=%s",
        session_id,
        org_id,
        saved,
        enable_video_watermark,
    )
    return session


async def get_session(session_id: str, org_id: str) -> Optional[VideoStreamSession]:
    """Get a session by ID, validating org ownership."""
    # Try Redis first
    session = await _redis_get_session(session_id)
    if session is not None:
        if session.org_id != org_id:
            return None
        # Check idle timeout
        now = time.time()
        if session.status == "active" and now - session.last_activity > _SESSION_MAX_IDLE:
            session.status = "expired"
            await _redis_save_session(session)
            return None
        return session

    # Fallback to in-memory
    _cleanup_expired_sessions()
    session = _sessions.get(session_id)
    if session is None:
        return None
    if session.org_id != org_id:
        return None
    return session


async def _persist_session(session: VideoStreamSession) -> None:
    """Save session state after mutation (segment signed, finalized, etc.)."""
    saved = await _redis_save_session(session)
    if not saved:
        # In-memory: session object is already mutated in place
        _sessions[session.session_id] = session


async def sign_segment(
    session: VideoStreamSession,
    segment_data: bytes,
    mime_type: str,
    *,
    title: str = "stream-segment",
    action: str = "c2pa.created",
    custom_assertions: Optional[list] = None,
    rights_data: Optional[dict] = None,
) -> SignedSegmentResult:
    """Sign a single video segment with a C2PA manifest.

    The manifest includes a reference to the previous segment's manifest hash
    via a custom assertion, creating a backwards-linked provenance chain.
    """
    if session.status != "active":
        raise ValueError(f"Session {session.session_id} is {session.status}, cannot sign new segments")

    canonical_mime, file_size = validate_video(segment_data, mime_type)
    original_hash = compute_sha256(segment_data)

    segment_index = session.segment_count
    video_id = f"vseg_{session.session_id}_{segment_index}"

    # Build assertions list including c2pa.livevideo.segment (C2PA 2.3 Section 19)
    all_assertions = list(custom_assertions or [])
    livevideo_assertion: dict = {
        "label": "c2pa.livevideo.segment",
        "data": {
            "sequenceNumber": segment_index,
            "streamId": session.stream_id,
            "continuityMethod": "c2pa.manifestId",
        },
    }
    if session.prev_manifest_id is not None:
        livevideo_assertion["data"]["previousManifestId"] = session.prev_manifest_id
    all_assertions.append(livevideo_assertion)

    # Declare soft-binding watermark in the manifest when watermarking is enabled
    if session.enable_video_watermark:
        all_assertions.append(SOFT_BINDING_ASSERTION_VIDEO)

    passthrough = not (session.private_key_pem and session.cert_chain_pem)

    passthrough = passthrough or settings.signing_passthrough

    if passthrough:
        instance_id = "urn:uuid:" + str(uuid.uuid4())
        manifest_hash = "sha256:" + "0" * 64

        session.segment_count += 1
        session.segment_manifest_hashes.append(manifest_hash)
        session.prev_manifest_hash = manifest_hash
        session.prev_manifest_id = instance_id
        session.last_activity = time.time()
        await _persist_session(session)

        return SignedSegmentResult(
            segment_index=segment_index,
            stream_id=session.stream_id,
            signed_bytes=segment_data,
            original_hash=original_hash,
            signed_hash=original_hash,
            c2pa_instance_id=instance_id,
            c2pa_manifest_hash=manifest_hash,
            size_bytes=file_size,
            mime_type=canonical_mime,
            c2pa_signed=False,
        )

    import c2pa

    from app.utils.c2pa_manifest import build_c2pa_manifest_dict
    from app.utils.c2pa_signer import create_signer_from_pem

    manifest_dict = build_c2pa_manifest_dict(
        title=f"{title}-seg{segment_index:06d}",
        org_id=session.org_id,
        document_id=session.session_id,
        asset_id=video_id,
        asset_id_key="video_id",
        action=action,
        custom_assertions=all_assertions,
        rights_data=rights_data or {},
        digital_source_type="digitalCapture",
    )
    c2pa_instance_id = manifest_dict["instance_id"]

    signer = create_signer_from_pem(session.private_key_pem, session.cert_chain_pem)
    try:
        builder = c2pa.Builder(manifest_dict)
        dest = BytesIO()
        manifest_bytes = builder.sign(signer, canonical_mime, BytesIO(segment_data), dest)
        dest.seek(0)
        signed_bytes = dest.read()
        del dest
    finally:
        signer.close()

    signed_hash = compute_sha256(signed_bytes)
    manifest_hash = compute_sha256(manifest_bytes)

    # Apply spread-spectrum watermark after C2PA signing when enabled
    watermark_applied = False
    if session.enable_video_watermark and session.watermark_payload is not None:
        signed_b64 = base64.b64encode(signed_bytes).decode()
        wm_result = await video_watermark_client.apply_watermark(signed_b64, canonical_mime, session.watermark_payload)
        if wm_result is not None:
            watermarked_b64, _confidence = wm_result
            signed_bytes = base64.b64decode(watermarked_b64)
            signed_hash = compute_sha256(signed_bytes)
            watermark_applied = True
            logger.info(
                "Video watermark applied: session=%s index=%d",
                session.session_id,
                segment_index,
            )
        else:
            logger.warning(
                "Video watermark failed for session=%s index=%d, continuing without watermark",
                session.session_id,
                segment_index,
            )

    session.segment_count += 1
    session.segment_manifest_hashes.append(manifest_hash)
    session.prev_manifest_hash = manifest_hash
    session.prev_manifest_id = c2pa_instance_id
    session.last_activity = time.time()
    await _persist_session(session)

    logger.info(
        "Stream segment signed: session=%s index=%d size=%d",
        session.session_id,
        segment_index,
        len(signed_bytes),
    )

    return SignedSegmentResult(
        segment_index=segment_index,
        sequence_number=segment_index,
        stream_id=session.stream_id,
        signed_bytes=signed_bytes,
        original_hash=original_hash,
        signed_hash=signed_hash,
        c2pa_instance_id=c2pa_instance_id,
        c2pa_manifest_hash=manifest_hash,
        size_bytes=len(signed_bytes),
        mime_type=canonical_mime,
        c2pa_signed=True,
        watermark_applied=watermark_applied,
    )


async def finalize_stream(session: VideoStreamSession) -> StreamFinalizeResult:
    """Finalize a stream session and compute Merkle root over segment hashes."""
    if session.status != "active":
        raise ValueError(f"Session {session.session_id} is already {session.status}")

    merkle_root = _compute_merkle_root(session.segment_manifest_hashes)
    session.status = "finalized"
    session.last_activity = time.time()
    await _persist_session(session)

    logger.info(
        "Stream finalized: session=%s segments=%d merkle_root=%s",
        session.session_id,
        session.segment_count,
        merkle_root[:20] + "...",
    )

    return StreamFinalizeResult(
        session_id=session.session_id,
        stream_id=session.stream_id,
        segment_count=session.segment_count,
        merkle_root=merkle_root,
        status="finalized",
    )
