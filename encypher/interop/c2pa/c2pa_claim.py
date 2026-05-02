"""C2PA Claim v2 builder for text document signing.

Builds the CBOR claim structure required by the C2PA specification,
including hashed assertion references (``created_assertions``), claim
generator info, and content binding.

The claim v2 format uses ``created_assertions`` with JUMBF URI references
and per-assertion hashes, unlike v1 which inlined assertion data.

This module is a thin implementation layer. All policy values (spec version,
product version, product name) are passed by the caller. The enterprise API
is the SSOT for these constants.
"""

from __future__ import annotations

import hashlib
import uuid

import cbor2

# Hash algorithm identifiers per C2PA spec
HASH_ALG_SHA256 = "sha256"
HASH_ALG_SHA384 = "sha384"
HASH_ALG_SHA512 = "sha512"


def _compute_hash(data: bytes, alg: str = HASH_ALG_SHA256) -> bytes:
    """Compute hash of *data* using the specified algorithm."""
    h = hashlib.new(alg)
    h.update(data)
    return h.digest()


def build_claim_cbor(
    manifest_label: str,
    assertion_data: list[tuple[str, bytes]],
    *,
    dc_format: str,
    title: str | None = None,
    claim_generator: str | None = None,
    alg: str = HASH_ALG_SHA256,
    spec_version: str | None = None,
    product_version: str | None = None,
) -> bytes:
    """Build the CBOR-encoded C2PA claim v2.

    Args:
        manifest_label: The manifest URN, e.g. ``"urn:c2pa:<uuid>"``.
        assertion_data: List of ``(label, jumbf_content_bytes)`` for each
            assertion.  The JUMBF content (description + content boxes,
            without the superbox header) must already be built so we can
            hash them.
        dc_format: MIME type of the asset (required per C2PA spec).
        title: Optional asset title.
        claim_generator: Claim generator name. Required by callers; falls
            back to ``"encypher"`` only as a last resort.
        alg: Hash algorithm for assertion hashing.
        spec_version: C2PA spec version (e.g. ``"2.4"``). Included in
            ``claim_generator_info`` when provided; omitted otherwise.
        product_version: Product version string for ``claim_generator_info``.
            Omitted when ``None``.

    Returns:
        CBOR-encoded claim bytes.
    """
    instance_id = f"urn:uuid:{uuid.uuid4()}"

    # Build hashed assertion references.
    # Per C2PA spec 14.2.3: hash covers the referenced box's content
    # (description + content boxes, excluding the superbox LBox+TBox header).
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

    # c2pa.claim.v2 fields (c2pa-rs enforces strictly):
    #   instanceID, claim_generator_info, signature, created_assertions,
    #   gathered_assertions, dc:title, redacted_assertions, alg, alg_soft,
    #   metadata
    # Fields like claim_generator, dc:format, assertions are v1-only and
    # cause "unsupported claim version" or "unknown V2 claim field" errors.
    generator_name = claim_generator or "encypher"
    gen_info: dict = {"name": generator_name}
    if product_version is not None:
        gen_info["version"] = product_version
    if spec_version is not None:
        gen_info["specVersion"] = spec_version

    claim: dict = {
        "instanceID": instance_id,
        "claim_generator_info": gen_info,
        "signature": f"self#jumbf={manifest_label}/c2pa.signature",
        "created_assertions": assertion_refs,
        "alg": alg,
    }

    if title:
        claim["dc:title"] = title

    return cbor2.dumps(claim)
