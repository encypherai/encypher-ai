"""Shared C2PA manifest definition builder.

Used by both image and audio signing pipelines. Produces the manifest dict
consumed by c2pa.Builder.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Literal

_TS_FMT = "%Y-%m-%dT%H:%M:%SZ"


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
) -> dict:
    """Build a C2PA manifest definition dict for signing.

    Args:
        title: Human-readable title for the manifest.
        org_id: Organization identifier.
        document_id: Parent document identifier.
        asset_id: Unique asset identifier (image_id, audio_id, etc.).
        asset_id_key: Key name in provenance assertion ("image_id", "audio_id", "video_id").
        action: C2PA action string (e.g. "c2pa.created").
        custom_assertions: Additional C2PA assertions to embed.
        rights_data: Rights metadata dict for com.encypher.rights.v1 assertion.

    Returns:
        Dict suitable for passing to c2pa.Builder().
    """
    now_iso = datetime.now(timezone.utc).strftime(_TS_FMT)
    instance_id = "urn:uuid:" + str(uuid.uuid4())

    assertions = [
        {
            "label": "c2pa.actions",
            "data": {
                "actions": [
                    {
                        "action": action,
                        "when": now_iso,
                    }
                ]
            },
        },
    ]

    if rights_data:
        assertions.append(
            {
                "label": "com.encypher.rights.v1",
                "data": rights_data,
            }
        )

    for ca in custom_assertions:
        assertions.append(ca)

    assertions.append(
        {
            "label": "com.encypher.provenance.v1",
            "data": {
                "organization_id": org_id,
                "document_id": document_id,
                asset_id_key: asset_id,
                "signed_at": now_iso,
            },
        }
    )

    return {
        "claim_generator": "encypher-ai/1.0",
        "claim_generator_info": [{"name": "Encypher", "version": "1.0"}],
        "title": title,
        "instance_id": instance_id,
        "assertions": assertions,
    }
