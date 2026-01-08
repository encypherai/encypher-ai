"""
Multi-Embedding Extraction Utility (Proprietary Encypher Feature)

This module provides functionality to extract and verify multiple embeddings
from a single piece of text. This includes:
- C2PA wrappers (full manifests with JUMBF structure)
- Basic format embeddings (JSON payloads with variation selectors)

The /sign/advanced endpoint creates:
- Per-sentence "basic" format embeddings (variation selector blocks)
- One document-level C2PA wrapper at the end

This feature is NOT available in the open-source encypher-ai library.
"""
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import c2pa_text
from encypher.core.unicode_metadata import UnicodeMetadata

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingInfo:
    """Information about a single embedding found in text."""
    
    index: int
    manifest_bytes: bytes
    span: tuple[int, int]  # (start, end) in original text
    segment_text: str  # The text content associated with this embedding
    embedding_type: str = "c2pa"  # "c2pa" or "basic"
    metadata: Optional[dict] = None
    verification_status: str = "Not Attempted"
    error: Optional[str] = None
    signer_id: Optional[str] = None
    signer_name: Optional[str] = None
    signature_valid: bool = False


@dataclass
class MultiEmbeddingResult:
    """Result of extracting multiple embeddings from text."""
    
    total_found: int = 0
    embeddings: list[EmbeddingInfo] = field(default_factory=list)
    all_valid: bool = False
    any_valid: bool = False
    clean_text: str = ""  # Full text with all wrappers removed
    

# Variation selector ranges used by encypher-ai
VS_START = 0xFE00
VS_END = 0xFE0F
VS_SUPPLEMENT_START = 0xE0100
VS_SUPPLEMENT_END = 0xE01EF


def _is_variation_selector(code_point: int) -> bool:
    """Check if a code point is a variation selector."""
    return (VS_START <= code_point <= VS_END) or (VS_SUPPLEMENT_START <= code_point <= VS_SUPPLEMENT_END)


def _vs_to_byte(code_point: int) -> Optional[int]:
    """Convert a variation selector code point to a byte value."""
    if VS_START <= code_point <= VS_END:
        return code_point - VS_START
    elif VS_SUPPLEMENT_START <= code_point <= VS_SUPPLEMENT_END:
        return code_point - VS_SUPPLEMENT_START + 16
    return None


def find_all_vs_blocks(text: str, min_length: int = 16) -> list[tuple[int, int, bytes]]:
    """Find ALL variation selector blocks in the text.
    
    This finds contiguous runs of variation selectors that represent
    embedded metadata (basic format embeddings from /sign/advanced).
    
    Args:
        text: The text to search.
        min_length: Minimum number of VS characters to consider a valid block.
        
    Returns:
        List of tuples (start_index, end_index, decoded_bytes) for each
        VS block found, in order of appearance.
    """
    results = []
    i = 0
    n = len(text)
    
    while i < n:
        code_point = ord(text[i])
        if _is_variation_selector(code_point):
            # Found start of a VS block
            block_start = i
            decoded_bytes = []
            
            while i < n:
                cp = ord(text[i])
                byte_val = _vs_to_byte(cp)
                if byte_val is not None:
                    decoded_bytes.append(byte_val)
                    i += 1
                else:
                    break
            
            # Only include blocks that meet minimum length
            if len(decoded_bytes) >= min_length:
                results.append((block_start, i, bytes(decoded_bytes)))
        else:
            i += 1
    
    return results


def find_all_c2pa_wrappers(text: str) -> list[tuple[bytes, int, int]]:
    """Find ALL C2PA wrappers in the text.
    
    C2PA wrappers use the C2PATextManifestWrapper format with FEFF prefix
    and contain JUMBF-encoded manifests.
    
    Args:
        text: The text to search for wrappers.
        
    Returns:
        List of tuples (manifest_bytes, start_index, end_index) for each
        wrapper found, in order of appearance. Empty list if no wrappers found.
    """
    if not hasattr(c2pa_text, "find_wrapper_info"):
        logger.warning("c2pa_text.find_wrapper_info not available")
        return []
    
    results = []
    remaining_text = text
    offset = 0
    
    while True:
        info = c2pa_text.find_wrapper_info(remaining_text)
        if not info:
            break
            
        manifest_bytes, start, end = info
        # Adjust indices to account for offset from previous iterations
        absolute_start = offset + start
        absolute_end = offset + end
        results.append((manifest_bytes, absolute_start, absolute_end))
        
        # Move past this wrapper and continue searching
        remaining_text = remaining_text[end:]
        offset = absolute_end
    
    return results


def find_all_embeddings_raw(text: str) -> list[tuple[str, bytes, int, int]]:
    """Find ALL embeddings in text - both C2PA wrappers and basic format.
    
    Args:
        text: The text to search.
        
    Returns:
        List of tuples (embedding_type, payload_bytes, start_index, end_index)
        sorted by start_index. embedding_type is "c2pa" or "basic".
    """
    all_embeddings = []
    
    # Find C2PA wrappers
    c2pa_wrappers = find_all_c2pa_wrappers(text)
    for manifest_bytes, start, end in c2pa_wrappers:
        all_embeddings.append(("c2pa", manifest_bytes, start, end))
    
    # Find basic format VS blocks
    vs_blocks = find_all_vs_blocks(text)
    for start, end, decoded_bytes in vs_blocks:
        # Check if this VS block overlaps with any C2PA wrapper
        # (C2PA wrappers also use VS, so we need to exclude them)
        overlaps_c2pa = any(
            not (end <= c_start or start >= c_end)
            for _, c_start, c_end in c2pa_wrappers
        )
        if not overlaps_c2pa:
            # Try to parse as JSON to verify it's a basic format embedding
            try:
                json_str = decoded_bytes.decode("utf-8").lstrip("\ufeff")
                payload = json.loads(json_str)
                if isinstance(payload, dict) and "format" in payload:
                    all_embeddings.append(("basic", decoded_bytes, start, end))
            except (UnicodeDecodeError, json.JSONDecodeError):
                # Not a valid basic format embedding, skip
                pass
    
    # Sort by start index
    all_embeddings.sort(key=lambda x: x[2])
    return all_embeddings


def extract_all_embeddings(text: str) -> MultiEmbeddingResult:
    """Extract ALL embeddings from text without verification.
    
    Finds both C2PA wrappers and basic format embeddings from /sign/advanced.
    
    Args:
        text: The text containing one or more embedded manifests.
        
    Returns:
        MultiEmbeddingResult with all found embeddings and their metadata.
    """
    result = MultiEmbeddingResult()
    all_raw = find_all_embeddings_raw(text)
    
    if not all_raw:
        result.clean_text = text
        return result
    
    result.total_found = len(all_raw)
    
    # Build clean text by removing all embeddings
    clean_parts = []
    prev_end = 0
    
    for i, (embedding_type, payload_bytes, start, end) in enumerate(all_raw):
        # Get the text segment before this embedding
        segment_text = text[prev_end:start]
        clean_parts.append(segment_text)
        
        # Extract metadata from this embedding
        wrapper_text = text[start:end]
        metadata = None
        
        try:
            if embedding_type == "c2pa":
                # For C2PA, use UnicodeMetadata to extract
                test_text = segment_text + wrapper_text
                metadata = UnicodeMetadata.extract_metadata(test_text)
            else:
                # For basic format, parse the JSON payload directly
                json_str = payload_bytes.decode("utf-8").lstrip("\ufeff")
                outer_payload = json.loads(json_str)
                if isinstance(outer_payload, dict):
                    metadata = outer_payload.get("payload", outer_payload)
        except Exception as e:
            logger.warning(f"Failed to extract metadata from embedding {i}: {e}")
            metadata = None
        
        embedding = EmbeddingInfo(
            index=i,
            manifest_bytes=payload_bytes,
            span=(start, end),
            segment_text=segment_text,
            embedding_type=embedding_type,
            metadata=metadata,
        )
        
        # Extract signer_id from metadata if available
        if metadata and isinstance(metadata, dict):
            signer_id = _extract_signer_id(metadata)
            embedding.signer_id = signer_id
        
        result.embeddings.append(embedding)
        prev_end = end
    
    # Add any remaining text after the last embedding
    if prev_end < len(text):
        clean_parts.append(text[prev_end:])
    
    result.clean_text = "".join(clean_parts)
    return result


def _extract_signer_id(metadata: dict) -> Optional[str]:
    """Extract signer_id from metadata dict, checking multiple paths."""
    # Path 1: manifest.signer_id
    manifest = metadata.get("manifest", {})
    if isinstance(manifest, dict) and manifest.get("signer_id"):
        return manifest.get("signer_id")
    
    # Path 2: direct signer_id
    if metadata.get("signer_id"):
        return metadata.get("signer_id")
    
    # Path 3: claim_generator_info.signer_id (C2PA format)
    claim_info = metadata.get("claim_generator_info", {})
    if isinstance(claim_info, dict) and claim_info.get("signer_id"):
        return claim_info.get("signer_id")
    
    return None


async def extract_and_verify_all_embeddings(
    text: str,
    public_key_resolver: Callable[[str], Any],
    demo_signer_ids: Optional[set[str]] = None,
) -> MultiEmbeddingResult:
    """Extract and verify ALL embeddings in text.
    
    This is the main entry point for multi-embedding extraction and verification.
    Each embedding is verified independently against its signer's public key.
    
    Args:
        text: The text containing one or more embedded manifests.
        public_key_resolver: Async or sync function that takes signer_id and returns public key.
        demo_signer_ids: Set of signer IDs that should use the demo key.
        
    Returns:
        MultiEmbeddingResult with all embeddings and their verification status.
    """
    if demo_signer_ids is None:
        demo_signer_ids = {"org_demo", "demo-signer-id", "c2pa-demo-signer-001"}
    
    # First extract all embeddings
    result = extract_all_embeddings(text)
    
    if result.total_found == 0:
        return result
    
    valid_count = 0
    
    # Verify each embedding independently against its own normalized text segment
    # Each embedding should be verified against ONLY its segment + its wrapper,
    # without any other embeddings' wrappers interfering with the hash calculation.
    for embedding in result.embeddings:
        try:
            # Get the wrapper text for this embedding
            wrapper_text = text[embedding.span[0]:embedding.span[1]]
            
            # The segment_text is already clean (text between previous wrapper end and this wrapper start)
            # We need to verify against: clean_segment + this_wrapper
            # This matches what was signed: the original sentence text + its wrapper
            segment_with_wrapper = embedding.segment_text + wrapper_text
            
            # Verify using UnicodeMetadata
            verification_result = UnicodeMetadata.verify_metadata(
                text=segment_with_wrapper,
                public_key_resolver=public_key_resolver,
                return_payload_on_failure=True,
            )
            
            # Parse verification result
            if isinstance(verification_result, tuple) and len(verification_result) == 3:
                signature_valid, signer_id, payload = verification_result
            elif isinstance(verification_result, dict):
                signature_valid = verification_result.get("valid", False)
                signer_id = verification_result.get("signer_id")
                payload = verification_result.get("payload")
            else:
                signature_valid = False
                signer_id = embedding.signer_id
                payload = embedding.metadata
            
            embedding.signature_valid = signature_valid
            embedding.signer_id = signer_id or embedding.signer_id
            
            if signature_valid:
                embedding.verification_status = "Success"
                embedding.metadata = payload if isinstance(payload, dict) else embedding.metadata
                valid_count += 1
                
                # Determine signer name
                if signer_id in demo_signer_ids:
                    embedding.signer_name = f"{signer_id} (Demo Key)"
                else:
                    embedding.signer_name = f"{signer_id} (Verified via Trust Anchor)"
            else:
                embedding.verification_status = "Failure"
                if signer_id in demo_signer_ids:
                    embedding.signer_name = f"{signer_id} (Demo Key)"
                    embedding.error = "Content has been modified since signing. The signature is no longer valid."
                elif signer_id:
                    embedding.signer_name = f"{signer_id} (Unknown Signer)"
                    embedding.error = f"Signer '{signer_id}' is not in our Trust Anchor database."
                else:
                    embedding.error = "Signature verification failed."
                    
        except Exception as e:
            logger.warning(f"Verification failed for embedding {embedding.index}: {e}")
            embedding.verification_status = "Error"
            embedding.error = str(e)
    
    result.any_valid = valid_count > 0
    result.all_valid = valid_count == result.total_found
    
    return result
