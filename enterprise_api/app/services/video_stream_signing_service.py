"""Video stream C2PA signing service (C2PA 2.3 Section 19).

Per-segment manifest signing with backwards-linked provenance chain.
Each CMAF/fMP4 segment gets its own C2PA manifest. The manifest includes
a c2pa.ingredient.v3 assertion referencing the previous segment's manifest
hash, creating a verifiable chain across the stream.
"""

import hashlib
import logging
import secrets
import time
import uuid
from dataclasses import dataclass, field
from io import BytesIO
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# In-memory session store (Redis-backed in production)
_sessions: Dict[str, "VideoStreamSession"] = {}
_SESSION_TTL = 3600  # 1 hour default
_SESSION_MAX_IDLE = 300  # 5 min idle timeout


@dataclass
class VideoStreamSession:
    """State for an active video stream signing session."""

    session_id: str
    org_id: str
    private_key_pem: str
    cert_chain_pem: str
    segment_count: int = 0
    segment_manifest_hashes: List[str] = field(default_factory=list)
    prev_manifest_hash: Optional[str] = None
    status: str = "active"  # active | finalized | expired
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    expires_at: float = 0.0

    def __post_init__(self) -> None:
        if self.expires_at == 0.0:
            self.expires_at = self.created_at + _SESSION_TTL


@dataclass
class SignedSegmentResult:
    """Result of signing a single video segment."""

    segment_index: int
    signed_bytes: bytes
    original_hash: str
    signed_hash: str
    c2pa_instance_id: str
    c2pa_manifest_hash: str
    size_bytes: int
    mime_type: str
    c2pa_signed: bool


@dataclass
class StreamFinalizeResult:
    """Result of finalizing a video stream session."""

    session_id: str
    segment_count: int
    merkle_root: str
    status: str


def _cleanup_expired_sessions() -> None:
    """Remove expired/idle sessions."""
    now = time.time()
    expired = [sid for sid, s in _sessions.items() if now > s.expires_at or (s.status == "active" and now - s.last_activity > _SESSION_MAX_IDLE)]
    for sid in expired:
        s = _sessions.pop(sid, None)
        if s and s.status == "active":
            s.status = "expired"
            logger.info("Stream session expired: %s (segments=%d)", sid, s.segment_count)


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
) -> VideoStreamSession:
    """Create a new video stream signing session.

    Credentials are cached for the session lifetime to avoid per-segment DB reads.
    """
    _cleanup_expired_sessions()
    session_id = f"vstream_{secrets.token_hex(12)}"
    session = VideoStreamSession(
        session_id=session_id,
        org_id=org_id,
        private_key_pem=private_key_pem,
        cert_chain_pem=cert_chain_pem,
    )
    _sessions[session_id] = session
    logger.info("Stream session started: %s org=%s", session_id, org_id)
    return session


def get_session(session_id: str, org_id: str) -> Optional[VideoStreamSession]:
    """Get a session by ID, validating org ownership."""
    _cleanup_expired_sessions()
    session = _sessions.get(session_id)
    if session is None:
        return None
    if session.org_id != org_id:
        return None
    return session


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

    from app.utils.hashing import compute_sha256
    from app.utils.video_utils import validate_video

    canonical_mime, file_size = validate_video(segment_data, mime_type)
    original_hash = compute_sha256(segment_data)

    segment_index = session.segment_count
    video_id = f"vseg_{session.session_id}_{segment_index}"

    # Build assertions list including chain reference
    all_assertions = list(custom_assertions or [])
    if session.prev_manifest_hash is not None:
        all_assertions.append(
            {
                "label": "com.encypher.stream.chain.v1",
                "data": {
                    "prev_segment_index": segment_index - 1,
                    "prev_manifest_hash": session.prev_manifest_hash,
                    "session_id": session.session_id,
                },
            }
        )

    passthrough = not (session.private_key_pem and session.cert_chain_pem)

    from app.config import settings

    passthrough = passthrough or settings.signing_passthrough

    if passthrough:
        instance_id = "urn:uuid:" + str(uuid.uuid4())
        manifest_hash = "sha256:" + "0" * 64

        session.segment_count += 1
        session.segment_manifest_hashes.append(manifest_hash)
        session.prev_manifest_hash = manifest_hash
        session.last_activity = time.time()

        return SignedSegmentResult(
            segment_index=segment_index,
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

    session.segment_count += 1
    session.segment_manifest_hashes.append(manifest_hash)
    session.prev_manifest_hash = manifest_hash
    session.last_activity = time.time()

    logger.info(
        "Stream segment signed: session=%s index=%d size=%d",
        session.session_id,
        segment_index,
        len(signed_bytes),
    )

    return SignedSegmentResult(
        segment_index=segment_index,
        signed_bytes=signed_bytes,
        original_hash=original_hash,
        signed_hash=signed_hash,
        c2pa_instance_id=c2pa_instance_id,
        c2pa_manifest_hash=manifest_hash,
        size_bytes=len(signed_bytes),
        mime_type=canonical_mime,
        c2pa_signed=True,
    )


async def finalize_stream(session: VideoStreamSession) -> StreamFinalizeResult:
    """Finalize a stream session and compute Merkle root over segment hashes."""
    if session.status != "active":
        raise ValueError(f"Session {session.session_id} is already {session.status}")

    merkle_root = _compute_merkle_root(session.segment_manifest_hashes)
    session.status = "finalized"
    session.last_activity = time.time()

    logger.info(
        "Stream finalized: session=%s segments=%d merkle_root=%s",
        session.session_id,
        session.segment_count,
        merkle_root[:20] + "...",
    )

    return StreamFinalizeResult(
        session_id=session.session_id,
        segment_count=session.segment_count,
        merkle_root=merkle_root,
        status="finalized",
    )
