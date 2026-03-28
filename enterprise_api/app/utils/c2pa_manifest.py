"""Shared C2PA manifest definition builder.

Used by image, audio, and video signing pipelines. Produces the manifest dict
consumed by c2pa.Builder.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Literal, Optional

_TS_FMT = "%Y-%m-%dT%H:%M:%SZ"

_PRODUCT_NAME = "Encypher Enterprise API"
_PRODUCT_VERSION = "1.0"

# IPTC digital source type vocabulary (short name -> full URI)
DIGITAL_SOURCE_TYPES = {
    "trainedAlgorithmicMedia": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
    "compositeWithTrainedAlgorithmicMedia": "http://cv.iptc.org/newscodes/digitalsourcetype/compositeWithTrainedAlgorithmicMedia",
    "algorithmicMedia": "http://cv.iptc.org/newscodes/digitalsourcetype/algorithmicMedia",
    "digitalCapture": "http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture",
    "digitalArt": "http://cv.iptc.org/newscodes/digitalsourcetype/digitalArt",
    "humanCurated": "http://cv.iptc.org/newscodes/digitalsourcetype/humanCurated",
}


def build_c2pa_manifest_dict(
    *,
    title: str,
    org_id: str,
    document_id: str,
    asset_id: str,
    asset_id_key: Literal["image_id", "audio_id", "video_id"],
    action: str,
    custom_assertions: List[dict],
    rights_data: dict,
    digital_source_type: Optional[str] = None,
) -> dict:
    """Build a C2PA manifest definition dict for signing.

    Args:
        title: Human-readable title for the manifest.
        org_id: Organization identifier.
        document_id: Parent document identifier.
        asset_id: Unique asset identifier (image_id, audio_id, etc.).
        asset_id_key: Key name in provenance assertion.
        action: C2PA action string (e.g. "c2pa.created").
        custom_assertions: Additional C2PA assertions to embed.
        rights_data: Rights metadata dict for com.encypher.rights.v1 assertion.
        digital_source_type: IPTC digital source type (short name or full URI).
            Required on "c2pa.created" actions per AC-005. Defaults to "digitalCapture".

    Returns:
        Dict suitable for passing to c2pa.Builder().
    """
    now_iso = datetime.now(timezone.utc).strftime(_TS_FMT)
    instance_id = "urn:uuid:" + str(uuid.uuid4())

    action_entry = {
        "action": action,
        "when": now_iso,
        "softwareAgent": {
            "name": _PRODUCT_NAME,
            "version": _PRODUCT_VERSION,
        },
    }

    # digitalSourceType is mandatory on c2pa.created actions (AC-005)
    if action == "c2pa.created":
        dst = digital_source_type or "digitalCapture"
        if not dst.startswith("http"):
            dst = DIGITAL_SOURCE_TYPES.get(
                dst,
                f"http://cv.iptc.org/newscodes/digitalsourcetype/{dst}",
            )
        action_entry["digitalSourceType"] = dst

    # Every assertion must have "created": True so c2pa-rs places it in
    # created_assertions (not gathered_assertions) in the claim CBOR.
    # The per-assertion flag is the only mechanism c2pa-rs respects;
    # a top-level "createdAssertions" field is silently ignored.
    assertions = [
        {
            "label": "c2pa.actions.v2",
            "data": {
                "actions": [action_entry],
            },
            "created": True,
        },
    ]

    if rights_data:
        assertions.append(
            {
                "label": "com.encypher.rights.v1",
                "data": rights_data,
                "created": True,
            }
        )

    for ca in custom_assertions:
        ca_copy = dict(ca)
        ca_copy["created"] = True
        assertions.append(ca_copy)

    assertions.append(
        {
            "label": "com.encypher.provenance",
            "data": {
                "organization_id": org_id,
                "document_id": document_id,
                asset_id_key: asset_id,
                "signed_at": now_iso,
            },
            "created": True,
        }
    )

    return {
        "claim_generator": f"{_PRODUCT_NAME}/{_PRODUCT_VERSION}",
        "claim_generator_info": [{"name": "Encypher", "version": _PRODUCT_VERSION}],
        "title": title,
        "instance_id": instance_id,
        "assertions": assertions,
    }
