"""C2PA Claim v2 builder for document signing.

Builds the CBOR claim structure required by the C2PA specification,
including the assertion references (hashed URIs), claim generator info,
and content binding assertions.

This is used for document formats (PDF, ZIP-based) where c2pa-python's
Builder does not support embedding.
"""

import hashlib
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

import cbor2

from app.utils import jumbf

_PRODUCT_NAME = "Encypher Enterprise API"
_PRODUCT_VERSION = "2.0"
_SPEC_VERSION = "2.1"
_TS_FMT = "%Y-%m-%dT%H:%M:%SZ"

# Hash algorithm identifiers per C2PA spec
HASH_ALG_SHA256 = "sha256"
HASH_ALG_SHA384 = "sha384"
HASH_ALG_SHA512 = "sha512"


def _compute_hash(data: bytes, alg: str = HASH_ALG_SHA256) -> bytes:
    """Compute hash of data using the specified algorithm."""
    h = hashlib.new(alg)
    h.update(data)
    return h.digest()


def build_actions_assertion(
    action: str = "c2pa.created",
    digital_source_type: Optional[str] = None,
) -> dict:
    """Build a c2pa.actions.v2 assertion data dict."""
    now_iso = datetime.now(timezone.utc).strftime(_TS_FMT)
    action_entry = {
        "action": action,
        "when": now_iso,
        "softwareAgent": {
            "name": _PRODUCT_NAME,
            "version": _PRODUCT_VERSION,
        },
    }
    if action == "c2pa.created":
        dst = digital_source_type or "http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture"
        if not dst.startswith("http"):
            dst = f"http://cv.iptc.org/newscodes/digitalsourcetype/{dst}"
        action_entry["digitalSourceType"] = dst

    return {"actions": [action_entry]}


def build_collection_data_hash(
    file_hashes: list[dict],
    zip_central_directory_hash: bytes,
    alg: str = HASH_ALG_SHA256,
) -> dict:
    """Build a c2pa.hash.collection.data assertion for ZIP-based formats.

    Args:
        file_hashes: List of {"uri": str, "hash": bytes} for each file in ZIP.
        zip_central_directory_hash: Hash of the ZIP central directory.
        alg: Hash algorithm identifier.
    """
    uris = []
    for fh in file_hashes:
        entry = {"uri": fh["uri"], "hash": fh["hash"]}
        if "dc:format" in fh:
            entry["dc:format"] = fh["dc:format"]
        uris.append(entry)

    return {
        "uris": uris,
        "alg": alg,
        "zip_central_directory_hash": zip_central_directory_hash,
    }


def build_data_hash(
    hash_value: bytes,
    exclusions: list[dict],
    alg: str = HASH_ALG_SHA256,
) -> dict:
    """Build a c2pa.hash.data assertion for PDF format.

    Args:
        hash_value: Hash of the asset data (with exclusions applied).
        exclusions: List of {"start": int, "length": int} byte ranges to exclude.
        alg: Hash algorithm identifier.
    """
    return {
        "exclusions": [{"start": e["start"], "length": e["length"]} for e in exclusions],
        "alg": alg,
        "hash": hash_value,
    }


def build_provenance_assertion(
    org_id: str,
    document_id: str,
    asset_id: str,
) -> dict:
    """Build the com.encypher.provenance assertion."""
    return {
        "organization_id": org_id,
        "document_id": document_id,
        "document_asset_id": asset_id,
        "signed_at": datetime.now(timezone.utc).strftime(_TS_FMT),
    }


def build_claim_cbor(
    manifest_label: str,
    assertion_data: list[tuple[str, bytes]],
    *,
    dc_format: str,
    title: Optional[str] = None,
    alg: str = HASH_ALG_SHA256,
) -> bytes:
    """Build the CBOR-encoded C2PA claim v2.

    Args:
        manifest_label: The manifest URN, e.g. "urn:c2pa:<uuid>".
        assertion_data: List of (label, jumbf_content_bytes) for each assertion.
            The assertion JUMBF content (description + content boxes, without
            superbox header) must already be built so we can hash them.
        dc_format: MIME type of the asset (required per C2PA spec).
        title: Optional asset title.
        alg: Hash algorithm for assertion hashing.

    Returns:
        CBOR-encoded claim bytes.
    """
    instance_id = f"urn:uuid:{uuid.uuid4()}"

    # Build hashed assertion references
    # Per C2PA spec 14.2.3: hash is over the referenced box's content
    # (description + content boxes, excluding the superbox LBox+TBox header)
    assertion_refs = []
    for label, assertion_jumbf_content in assertion_data:
        h = _compute_hash(assertion_jumbf_content, alg)
        assertion_refs.append(
            {
                "url": f"self#jumbf=c2pa.assertions/{label}",
                "hash": h,
                "alg": alg,
            }
        )

    # All assertions originate from this generator product, so they are
    # listed in created_assertions per C2PA conformance requirements.
    # The assertions array references all assertions (both created and
    # gathered); created_assertions identifies those made by the signer.
    claim = {
        "claim_generator": f"{_PRODUCT_NAME}/{_PRODUCT_VERSION}",
        "claim_generator_info": [
            {
                "name": "Encypher",
                "version": _PRODUCT_VERSION,
            }
        ],
        "dc:title": title or "Untitled Document",
        "dc:format": dc_format,
        "instanceID": instance_id,
        "alg": alg,
        "assertions": assertion_refs,
        "created_assertions": assertion_refs,
        "signature": f"self#jumbf={manifest_label}/c2pa.signature",
    }

    return cbor2.dumps(claim)
