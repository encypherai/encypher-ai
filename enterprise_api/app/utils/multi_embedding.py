"""
Multi-Embedding Extraction Utility (Proprietary Encypher Feature)

This module provides functionality to extract and verify multiple C2PA embeddings
from a single piece of text. This is a proprietary feature of the Encypher
Enterprise API that extends the basic c2pa_text functionality.

Use cases:
- Articles where each paragraph was signed separately
- Documents with multiple provenance markers
- Content aggregation where multiple sources are combined

This feature is NOT available in the open-source encypher-ai library.
"""
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
    

def find_all_wrappers(text: str) -> list[tuple[bytes, int, int]]:
    """Find ALL C2PA wrappers in the text.
    
    This is a proprietary Encypher feature that extends the basic c2pa_text
    functionality to handle documents with multiple embedded manifests.
    
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


def extract_all_embeddings(text: str) -> MultiEmbeddingResult:
    """Extract ALL embeddings from text without verification.
    
    Args:
        text: The text containing one or more embedded manifests.
        
    Returns:
        MultiEmbeddingResult with all found embeddings and their metadata.
    """
    result = MultiEmbeddingResult()
    wrappers = find_all_wrappers(text)
    
    if not wrappers:
        result.clean_text = text
        return result
    
    result.total_found = len(wrappers)
    
    # Build clean text by removing all wrappers
    clean_parts = []
    prev_end = 0
    
    for i, (manifest_bytes, start, end) in enumerate(wrappers):
        # Get the text segment before this wrapper
        segment_text = text[prev_end:start]
        clean_parts.append(segment_text)
        
        # Extract metadata from this embedding
        # We need to reconstruct a text with just this wrapper to extract metadata
        wrapper_text = text[start:end]
        
        try:
            # Create a minimal text with just this wrapper for extraction
            test_text = segment_text + wrapper_text
            metadata = UnicodeMetadata.extract_metadata(test_text)
        except Exception as e:
            logger.warning(f"Failed to extract metadata from embedding {i}: {e}")
            metadata = None
        
        embedding = EmbeddingInfo(
            index=i,
            manifest_bytes=manifest_bytes,
            span=(start, end),
            segment_text=segment_text,
            metadata=metadata,
        )
        
        # Extract signer_id from metadata if available
        if metadata and isinstance(metadata, dict):
            signer_id = _extract_signer_id(metadata)
            embedding.signer_id = signer_id
        
        result.embeddings.append(embedding)
        prev_end = end
    
    # Add any remaining text after the last wrapper
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
    
    # Verify each embedding independently
    for embedding in result.embeddings:
        try:
            # Reconstruct the text segment with its wrapper for verification
            segment_with_wrapper = embedding.segment_text + text[embedding.span[0]:embedding.span[1]]
            
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
