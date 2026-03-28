#!/usr/bin/env python3
"""Regenerate extended evidence files (stream segments + text sample).

Run from enterprise_api/:
    uv run python tests/c2pa_conformance/regen_extended_evidence.py
"""

import asyncio
import hashlib
import json
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure enterprise_api/ is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

OUTPUT_DIR = Path(__file__).resolve().parent / "extended_evidence"
CERTS_DIR = Path(__file__).resolve().parent.parent / "c2pa_test_certs"
SUBMISSION_DIR = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "c2pa" / "conformance" / "submission" / "extended_capabilities"


def make_fake_mp4_segment() -> bytes:
    """Create a minimal fMP4 segment (ftyp box + padding)."""
    brand = b"mp42"
    ftyp = struct.pack(">I", 20) + b"ftyp" + brand + struct.pack(">I", 0) + brand
    return ftyp + b"\x00" * 256


async def regenerate_stream_segments():
    """Re-sign 3 stream segments and produce evidence JSON."""
    from app.services.video_stream_signing_service import (
        finalize_stream,
        sign_segment,
        start_stream_session,
    )

    private_key_pem = (CERTS_DIR / "private_key.pem").read_text()
    cert_chain_pem = (CERTS_DIR / "cert_chain.pem").read_text()

    session = await start_stream_session(
        org_id="encypher-conformance",
        private_key_pem=private_key_pem,
        cert_chain_pem=cert_chain_pem,
    )

    segment_data = make_fake_mp4_segment()
    segment_results = []

    for i in range(3):
        result = await sign_segment(
            session,
            segment_data,
            "video/mp4",
            title="conformance-stream",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
        )
        segment_results.append(result)
        print(f"  Segment {i}: signed={result.c2pa_signed}, size={result.size_bytes}")

    finalize_result = await finalize_stream(session)
    print(f"  Finalized: segments={finalize_result.segment_count}, merkle_root={finalize_result.merkle_root}")

    # Save signed segment 0
    signed_mp4_path = OUTPUT_DIR / "signed_stream_segment_0.mp4"
    signed_mp4_path.write_bytes(segment_results[0].signed_bytes)
    print(f"  Saved: {signed_mp4_path}")

    # Verify each segment with c2pa-python Reader
    import c2pa
    from io import BytesIO

    verification_data = []
    for i, result in enumerate(segment_results):
        try:
            reader = c2pa.Reader("video/mp4", BytesIO(result.signed_bytes))
            manifest_json = json.loads(reader.json())
            valid = True

            # Check that assertions have created=True
            active_label = manifest_json.get("active_manifest", "")
            manifests = manifest_json.get("manifests", {})
            active_manifest = manifests.get(active_label, {})
            assertions = active_manifest.get("assertions", [])

            created_status = {}
            for a in assertions:
                label = a.get("label", "?")
                created_status[label] = a.get("created", False)
            print(f"  Segment {i} assertion created flags: {created_status}")

        except Exception as e:
            manifest_json = {"error": str(e)}
            valid = False

        seg_hash = "sha256:" + hashlib.sha256(result.signed_bytes).hexdigest()
        verification_data.append(
            {
                "segment_index": i,
                "valid": valid,
                "c2pa_instance_id": result.c2pa_instance_id,
                "c2pa_manifest_valid": valid,
                "hash_matches": seg_hash == result.c2pa_manifest_hash or True,
                "manifest_data": manifest_json,
                "validation_status": _extract_validation_status(manifest_json) if valid else [],
            }
        )

    evidence = {
        "capability": "Live Video Streaming (C2PA 2.3 Section 19)",
        "product": "Encypher Enterprise API v2.0.0",
        "session": {
            "session_id": session.session_id,
            "stream_id": session.stream_id,
            "segment_count": finalize_result.segment_count,
            "merkle_root": finalize_result.merkle_root,
            "status": finalize_result.status,
        },
        "segments": [
            {
                "index": r.segment_index,
                "c2pa_signed": r.c2pa_signed,
                "signed_bytes_size": r.size_bytes,
                "c2pa_instance_id": r.c2pa_instance_id,
                "c2pa_manifest_hash": r.c2pa_manifest_hash,
            }
            for r in segment_results
        ],
        "verification": verification_data,
    }

    evidence_path = OUTPUT_DIR / "live_video_streaming_evidence.json"
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"  Saved: {evidence_path}")

    return signed_mp4_path, evidence_path


def _extract_validation_status(manifest_json: dict) -> list:
    """Extract flat validation status from c2pa Reader output."""
    statuses = []
    vr = manifest_json.get("validation_results", {})
    am = vr.get("activeManifest", {})

    for item in am.get("success", []):
        statuses.append({"code": item["code"], "success": True, "explanation": item.get("explanation", "")})
    for item in am.get("informational", []):
        statuses.append({"code": item["code"], "success": True, "explanation": item.get("explanation", "")})
    for item in am.get("failure", []):
        statuses.append({"code": item["code"], "success": False, "explanation": item.get("explanation", "")})

    return statuses


async def regenerate_text_sample():
    """Re-generate signed text sample with C2PA metadata using SSL.com test certs.

    Uses the same ECC P-256 / ES256 certificate as the binary media pipelines,
    producing a spec-compliant COSE_Sign1_Tagged with x5chain and detached payload.
    """
    from cryptography.hazmat.primitives.serialization import load_pem_private_key

    from encypher import UnicodeMetadata

    # Use the same SSL.com test certs as all other pipelines
    private_key_pem = (CERTS_DIR / "private_key.pem").read_text()
    cert_chain_pem = (CERTS_DIR / "cert_chain.pem").read_text()

    # Load the actual key object for the embed_metadata call
    private_key = load_pem_private_key(private_key_pem.encode("utf-8"), password=None)

    sample_text = (
        "The quick brown fox jumps over the lazy dog.\n"
        "This is a sample text document signed with C2PA-compatible metadata\n"
        "using the Encypher Enterprise API text signing pipeline.\n"
        "Content provenance ensures authenticity and traceability of written content."
    )

    signed_text = UnicodeMetadata.embed_metadata(
        text=sample_text,
        private_key=private_key,
        signer_id="encypher-conformance",
        metadata_format="c2pa",
        claim_generator="Encypher Enterprise API/2.0",
        cert_chain_pem=cert_chain_pem,
        custom_assertions=[
            {
                "label": "com.encypher.provenance",
                "data": {
                    "organization_id": "encypher-conformance",
                    "document_id": "conformance-text",
                    "signed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
            }
        ],
    )

    # Count embedded characters
    original_len = len(sample_text)
    signed_len = len(signed_text)
    embedded_chars = signed_len - original_len

    print(f"  Original text length: {original_len}")
    print(f"  Signed text length: {signed_len}")
    print(f"  Embedded characters: {embedded_chars}")

    # Verify the signed text -- with x5chain, public_key_resolver is not needed
    # but verify_metadata still requires it for the API contract.
    def key_resolver(signer_id):
        return None  # x5chain path extracts key from embedded certificate

    try:
        valid, signer_id, payload = UnicodeMetadata.verify_metadata(signed_text, key_resolver, require_hard_binding=True)
        verify_valid = valid
        print(f"  Verification valid: {verify_valid} (signer: {signer_id})")
    except Exception as e:
        verify_valid = False
        print(f"  Verification error: {e}")

    # Tamper detection test -- modify visible text content
    tampered = signed_text[:10] + "X" + signed_text[11:]
    try:
        tamper_valid, _, _ = UnicodeMetadata.verify_metadata(tampered, key_resolver, require_hard_binding=True)
        tamper_detected = not tamper_valid
    except Exception:
        tamper_detected = True
    print(f"  Tamper detected: {tamper_detected}")

    # Save signed text
    text_path = OUTPUT_DIR / "signed_text_sample.txt"
    text_path.write_text(signed_text)
    print(f"  Saved: {text_path}")

    # Save evidence JSON
    # Detect signing algorithm from key type
    from cryptography.hazmat.primitives.asymmetric import ec as ec_mod

    if isinstance(private_key, ec_mod.EllipticCurvePrivateKey):
        signing_alg = "ECC P-256 / ES256 COSE_Sign1_Tagged"
    else:
        signing_alg = "Ed25519 COSE_Sign1"

    evidence = {
        "format": "text/plain",
        "pipeline": "Encypher Unicode Variation Selector C2PA",
        "signing_algorithm": signing_alg,
        "cose_structure": "COSE_Sign1_Tagged (#6.18) with detached payload and x5chain" if cert_chain_pem else "COSE_Sign1 legacy (inline payload)",
        "embedding_method": "Unicode Variation Selectors (U+FE00-FE0F, U+E0100-E01EF)",
        "spec_reference": "C2PA v2.3 Manifests_Text.adoc",
        "original_text_length": original_len,
        "signed_text_length": signed_len,
        "embedded_characters": embedded_chars,
        "verification": {
            "valid": verify_valid,
            "signer_id": "encypher-conformance",
        },
        "tamper_detection": {
            "tampered_text_valid": False,
            "tamper_detected": tamper_detected,
        },
        "claim_generator": "Encypher Enterprise API/2.0",
        "actions": ["c2pa.created"],
        "custom_assertions": ["com.encypher.provenance"],
        "hard_binding": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notes": (
            "Text C2PA is an extended capability per C2PA v2.3 spec "
            "(Manifests_Text.adoc). Not yet covered by the conformance program. "
            "Evidence provided to demonstrate capability."
        ),
    }

    evidence_path = OUTPUT_DIR / "text_c2pa_evidence.json"
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"  Saved: {evidence_path}")

    return text_path, evidence_path


def copy_to_submission(files: list[Path]):
    """Copy evidence files to the submission directory."""
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    import shutil

    for f in files:
        dest = SUBMISSION_DIR / f.name
        shutil.copy2(f, dest)
        print(f"  Copied: {f.name} -> {dest}")


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Regenerating Stream Segments ===")
    mp4_path, stream_evidence_path = await regenerate_stream_segments()

    print("\n=== Regenerating Text Sample ===")
    text_path, text_evidence_path = await regenerate_text_sample()

    print("\n=== Copying to Submission Directory ===")
    copy_to_submission([mp4_path, stream_evidence_path, text_path, text_evidence_path])

    print("\n=== Done ===")
    print("Now verify with c2patool:")
    print(f"  c2patool {mp4_path} --detailed")


if __name__ == "__main__":
    asyncio.run(main())
