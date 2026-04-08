"""JUMBF (ISO 19566-5) box serializer and parser for C2PA manifest stores.

Produces the binary JUMBF byte stream that gets embedded into text documents
via the C2PATextManifestWrapper (Unicode Variation Selector encoding).

Box format (per ISO 19566-5):
  LBox (4 bytes big-endian) | TBox (4 bytes) | payload
  If total size >= 2^32, uses extended size: LBox=1, then XLBox (8 bytes).

This module is the text-format counterpart of the JUMBF builder used by
binary formats (PDF, ZIP, Font, FLAC, JXL) in the enterprise API.
"""

from __future__ import annotations

import struct
import uuid

# ---------------------------------------------------------------------------
# C2PA JUMBF type UUIDs (ISO 19566-5 / C2PA spec)
# All follow the pattern: xxxxxxxx-0011-0010-8000-00AA00389B71
# ---------------------------------------------------------------------------

_UUID_SUFFIX = bytes.fromhex("00110010800000AA00389B71")

UUID_MANIFEST_STORE = bytes.fromhex("63327061") + _UUID_SUFFIX  # c2pa
UUID_MANIFEST = bytes.fromhex("63326D61") + _UUID_SUFFIX  # c2ma
UUID_ASSERTION_STORE = bytes.fromhex("63326173") + _UUID_SUFFIX  # c2as
UUID_CLAIM = bytes.fromhex("6332636C") + _UUID_SUFFIX  # c2cl
UUID_CLAIM_SIGNATURE = bytes.fromhex("63326373") + _UUID_SUFFIX  # c2cs
UUID_CBOR_CONTENT = bytes.fromhex("63626F72") + _UUID_SUFFIX  # cbor

# ---------------------------------------------------------------------------
# Content box types
# ---------------------------------------------------------------------------

TYPE_JUMB = b"jumb"  # JUMBF superbox
TYPE_JUMD = b"jumd"  # JUMBF description box
TYPE_CBOR = b"cbor"  # CBOR content box

# Toggle flags for description box
TOGGLE_REQUESTABLE = 0x03  # bits: xxxxxx11 (label present + requestable)


# ===================================================================
# Builder
# ===================================================================


def _box(box_type: bytes, payload: bytes) -> bytes:
    """Wrap *payload* in an ISOBMFF box with 4-byte *box_type*."""
    total = 8 + len(payload)
    if total < (1 << 32):
        return struct.pack(">I", total) + box_type + payload
    # Extended size
    return struct.pack(">I", 1) + box_type + struct.pack(">Q", total + 8) + payload


def description_box(
    type_uuid: bytes,
    label: str,
    *,
    salt: bytes | None = None,
) -> bytes:
    """Build a JUMBF Description Box (jumd).

    Args:
        type_uuid: 16-byte UUID identifying the box type.
        label: Null-terminated UTF-8 label string.
        salt: Optional 16 or 32-byte random salt for privacy.
    """
    toggles = TOGGLE_REQUESTABLE
    if salt is not None:
        toggles |= 0x10  # Private toggle

    payload = type_uuid + struct.pack("B", toggles) + label.encode("utf-8") + b"\x00"
    if salt is not None:
        payload += _box(b"c2sh", salt)
    return _box(TYPE_JUMD, payload)


def superbox(
    type_uuid: bytes,
    label: str,
    content_boxes: list[bytes],
    *,
    salt: bytes | None = None,
) -> bytes:
    """Build a JUMBF superbox (jumb) with a description box + content boxes."""
    desc = description_box(type_uuid, label, salt=salt)
    inner = desc + b"".join(content_boxes)
    return _box(TYPE_JUMB, inner)


def cbor_box(cbor_data: bytes) -> bytes:
    """Wrap CBOR-encoded data in a CBOR content box."""
    return _box(TYPE_CBOR, cbor_data)


def cose_box(cose_data: bytes) -> bytes:
    """Wrap COSE_Sign1 data in a CBOR content box.

    Per C2PA spec the claim signature is stored in a ``cbor`` content box
    inside the ``c2cs``-typed superbox.
    """
    return _box(TYPE_CBOR, cose_data)


def build_manifest_store(manifest_boxes: list[bytes]) -> bytes:
    """Build a complete C2PA Manifest Store superbox.

    Args:
        manifest_boxes: List of pre-built manifest superboxes (active last).
    """
    return superbox(UUID_MANIFEST_STORE, "c2pa", manifest_boxes)


def build_manifest(
    manifest_label: str,
    assertion_boxes: list[bytes],
    claim_cbor: bytes,
    signature_cose: bytes,
) -> bytes:
    """Build a single C2PA Manifest with assertion store, claim, and signature.

    Args:
        manifest_label: URN label, e.g. ``"urn:c2pa:<uuid>"``.
        assertion_boxes: List of pre-built assertion superboxes.
        claim_cbor: CBOR-encoded claim bytes.
        signature_cose: COSE_Sign1_Tagged bytes.
    """
    assertion_store = superbox(UUID_ASSERTION_STORE, "c2pa.assertions", assertion_boxes)
    claim = superbox(UUID_CLAIM, "c2pa.claim.v2", [cbor_box(claim_cbor)])
    sig = superbox(UUID_CLAIM_SIGNATURE, "c2pa.signature", [cose_box(signature_cose)])
    return superbox(UUID_MANIFEST, manifest_label, [assertion_store, claim, sig])


def build_assertion_box(
    label: str,
    cbor_data: bytes,
    *,
    salt: bytes | None = None,
) -> bytes:
    """Build an assertion superbox containing a CBOR content box."""
    return superbox(UUID_CBOR_CONTENT, label, [cbor_box(cbor_data)], salt=salt)


def generate_manifest_label() -> str:
    """Generate a unique manifest URN label."""
    return f"urn:c2pa:{uuid.uuid4()}"


# ===================================================================
# Parser
# ===================================================================


def parse_box(data: bytes, offset: int = 0) -> tuple[bytes, bytes, int]:
    """Parse a single ISOBMFF box at *offset*.

    Returns:
        ``(box_type, payload, next_offset)``
    """
    if offset + 8 > len(data):
        raise ValueError(f"Not enough data for box header at offset {offset}")
    size = struct.unpack(">I", data[offset : offset + 4])[0]
    box_type = data[offset + 4 : offset + 8]
    if size == 1:
        if offset + 16 > len(data):
            raise ValueError("Not enough data for extended box size")
        size = struct.unpack(">Q", data[offset + 8 : offset + 16])[0]
        payload = data[offset + 16 : offset + size]
        return box_type, payload, offset + size
    elif size == 0:
        payload = data[offset + 8 :]
        return box_type, payload, len(data)
    else:
        payload = data[offset + 8 : offset + size]
        return box_type, payload, offset + size


def parse_superbox(data: bytes) -> dict:
    """Parse a JUMBF superbox, returning its description and content boxes.

    Returns:
        Dict with ``'label'``, ``'type_uuid'``, ``'content_boxes'``
        (list of ``(type, payload)`` tuples).
    """
    box_type, payload, _ = parse_box(data)
    if box_type != TYPE_JUMB:
        raise ValueError(f"Expected 'jumb' superbox, got {box_type!r}")
    return _parse_superbox_payload(payload)


def _parse_superbox_payload(payload: bytes) -> dict:
    """Parse the inner payload of a ``jumb`` superbox."""
    desc_type, desc_payload, pos = parse_box(payload)
    if desc_type != TYPE_JUMD:
        raise ValueError(f"Expected 'jumd' description box, got {desc_type!r}")

    type_uuid = desc_payload[:16]
    # toggles = desc_payload[16]  -- unused in parse path
    label_bytes = desc_payload[17:]
    null_idx = label_bytes.find(b"\x00")
    label = label_bytes[:null_idx].decode("utf-8") if null_idx >= 0 else label_bytes.decode("utf-8")

    content_boxes: list[tuple[bytes, bytes]] = []
    while pos < len(payload):
        ctype, cpayload, pos = parse_box(payload, pos)
        content_boxes.append((ctype, cpayload))

    return {
        "label": label,
        "type_uuid": type_uuid,
        "content_boxes": content_boxes,
    }


def parse_manifest_store(data: bytes) -> dict:
    """Parse a C2PA manifest store from JUMBF bytes.

    Returns:
        Dict with ``'manifests'`` (list of parsed manifest dicts).
        Each manifest has ``'label'``, ``'assertions'`` (dict of
        label -> cbor_bytes), ``'assertion_jumbf'`` (dict of label ->
        raw JUMBF content for hash verification), ``'claim_cbor'``,
        ``'signature_cose'``.
    """
    store = parse_superbox(data)
    if store["type_uuid"] != UUID_MANIFEST_STORE:
        raise ValueError("Not a C2PA manifest store")

    manifests: list[dict] = []
    for ctype, cpayload in store["content_boxes"]:
        if ctype == TYPE_JUMB:
            manifest = _parse_manifest_box(cpayload)
            if manifest:
                manifests.append(manifest)

    return {"manifests": manifests}


def _parse_manifest_box(payload: bytes) -> dict | None:
    """Parse a single manifest superbox payload."""
    parsed = _parse_superbox_payload(payload)
    if parsed["type_uuid"] != UUID_MANIFEST:
        return None

    result: dict = {
        "label": parsed["label"],
        "assertions": {},
        "assertion_jumbf": {},
        "claim_cbor": None,
        "signature_cose": None,
    }

    for ctype, cpayload in parsed["content_boxes"]:
        if ctype != TYPE_JUMB:
            continue
        inner = _parse_superbox_payload(cpayload)

        if inner["type_uuid"] == UUID_ASSERTION_STORE:
            for atype, apayload in inner["content_boxes"]:
                if atype == TYPE_JUMB:
                    assertion = _parse_superbox_payload(apayload)
                    result["assertion_jumbf"][assertion["label"]] = apayload
                    for actype, acpayload in assertion["content_boxes"]:
                        if actype == TYPE_CBOR:
                            result["assertions"][assertion["label"]] = acpayload
                            break

        elif inner["type_uuid"] == UUID_CLAIM:
            for actype, acpayload in inner["content_boxes"]:
                if actype == TYPE_CBOR:
                    result["claim_cbor"] = acpayload
                    break

        elif inner["type_uuid"] == UUID_CLAIM_SIGNATURE:
            for actype, acpayload in inner["content_boxes"]:
                if actype == TYPE_CBOR:
                    result["signature_cose"] = acpayload
                    break

    return result
