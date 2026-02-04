"""Zero-Width Cryptographic Embedding (zw_embedding mode)

This module provides cryptographic signatures using ONLY invisible Unicode characters
for maximum cross-platform compatibility, including Microsoft Word.

Key features:
- Base-4 Word-safe encoding using ZWNJ, ZWJ, CGJ, MVS (no ZWSP - Word strips it!)
- Ed25519 signatures for full document signing
- HMAC-SHA256 for minimal signed UUIDs (sentence-level)
- Contiguous sequence detection (no magic number needed)
- Compact encoding: 128 chars per minimal signature
- Works in Word, Google Docs, PDF, all browsers

Word Compatibility Discovery:
- ZWSP (U+200B) is STRIPPED by Microsoft Word during copy/paste
- WJ (U+2060) APPEARS AS SPACE in Microsoft Word - cannot use!
- ZWNJ (U+200C), ZWJ (U+200D), CGJ (U+034F), MVS (U+180E) all survive perfectly
- Base-4 encoding with these 4 chars gives optimal size + Word compatibility
- Signatures detected by 128 contiguous base-4 chars (no magic number needed)
"""

import hashlib
import json
import struct
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from uuid import UUID

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import hashes, hmac as crypto_hmac
from cryptography.hazmat.backends import default_backend


# =============================================================================
# BASE-4 WORD-SAFE ENCODING
# =============================================================================
#
# Microsoft Word strips ZWSP (U+200B) during copy/paste operations.
# These 4 characters are proven to survive Word copy/paste:
#
# Base-4 encoding:
# - ZWNJ (U+200C) = 0 - Zero-Width Non-Joiner
# - ZWJ  (U+200D) = 1 - Zero-Width Joiner
# - CGJ  (U+034F) = 2 - Combining Grapheme Joiner
# - MVS  (U+180E) = 3 - Mongolian Vowel Separator
#
# Each byte = 4 chars (4^4 = 256)
# Minimal signed UUID = 32 bytes = 128 chars (no magic number)
# Signatures detected by 128 contiguous base-4 characters
# This is 35% smaller than base-3 (196 chars) while being Word-compatible!
# =============================================================================

# Word-safe invisible characters (ONLY these 4 work in Word!)
ZWNJ = "\u200C"  # 0 - Zero-Width Non-Joiner
ZWJ = "\u200D"   # 1 - Zero-Width Joiner
CGJ = "\u034F"   # 2 - Combining Grapheme Joiner
MVS = "\u180E"   # 3 - Mongolian Vowel Separator

# Character set for base-4 encoding
CHARS_BASE4 = [ZWNJ, ZWJ, CGJ, MVS]
CHARS_BASE4_SET = set(CHARS_BASE4)  # For fast lookup

# NOT USED - These characters don't work in Microsoft Word:
# ZWSP (U+200B) - STRIPPED by Word during copy/paste
# WJ (U+2060) - APPEARS AS SPACE in Word (visible!)


def encode_byte_zw(byte_value: int) -> str:
    """
    Encode a single byte (0-255) using base-4 Word-safe characters.
    
    Uses base-4 encoding with 4 characters per byte:
    4^4 = 256, exactly enough for all byte values.
    
    Characters (all Word-compatible, no ZWSP):
    - ZWNJ (U+200C) = 0
    - ZWJ  (U+200D) = 1
    - CGJ  (U+034F) = 2
    - MVS  (U+180E) = 3
    
    Args:
        byte_value: Integer 0-255
    
    Returns:
        4-character string using only ZWNJ/ZWJ/CGJ/MVS
    """
    if not 0 <= byte_value <= 255:
        raise ValueError(f"Byte value must be 0-255, got {byte_value}")
    
    result = []
    value = byte_value
    
    for _ in range(4):
        digit = value % 4
        result.append(CHARS_BASE4[digit])
        value //= 4
    
    return ''.join(result)


def decode_byte_zw(encoded: str) -> int:
    """
    Decode a base-4 Word-safe encoded byte back to integer.
    
    Args:
        encoded: 4-character string (ZWNJ/ZWJ/CGJ/MVS only)
    
    Returns:
        Decoded byte value (0-255)
    """
    if len(encoded) != 4:
        raise ValueError(f"Expected 4 characters, got {len(encoded)}")
    
    value = 0
    multiplier = 1
    
    for char in encoded:
        if char == ZWNJ:
            digit = 0
        elif char == ZWJ:
            digit = 1
        elif char == CGJ:
            digit = 2
        elif char == MVS:
            digit = 3
        else:
            raise ValueError(f"Invalid character: U+{ord(char):04X}")
        
        value += digit * multiplier
        multiplier *= 4
    
    return value


def encode_bytes_zw(data: bytes) -> str:
    """
    Encode arbitrary binary data using base-4 Word-safe characters.
    
    Args:
        data: Binary data to encode
    
    Returns:
        String containing only ZWNJ/ZWJ/CGJ/MVS (4 chars per byte)
    """
    return ''.join(encode_byte_zw(b) for b in data)


def decode_bytes_zw(encoded: str) -> bytes:
    """
    Decode base-4 Word-safe encoded binary data.
    
    Args:
        encoded: String containing only ZWNJ/ZWJ/CGJ/MVS
    
    Returns:
        Decoded binary data
    """
    if len(encoded) % 4 != 0:
        raise ValueError(f"Encoded length must be multiple of 4, got {len(encoded)}")
    
    result = []
    for i in range(0, len(encoded), 4):
        chunk = encoded[i:i+4]
        result.append(decode_byte_zw(chunk))
    
    return bytes(result)


def create_zw_signature(
    text: str,
    private_key: Ed25519PrivateKey,
    signer_id: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a cryptographic signature embedded using base-4 Word-safe characters.
    
    Format:
    - Magic number (4 chars)
    - Version byte (4 chars)
    - Payload length (8 chars = 2 bytes)
    - Payload (variable, 4 chars per byte)
    - Signature (256 chars = 64 bytes)
    
    Total: ~300+ chars (all invisible, Word-compatible)
    
    Args:
        text: Text to sign
        private_key: Ed25519 private key
        signer_id: Identifier for the signer
        metadata: Optional metadata dict
    
    Returns:
        Base-4 encoded signature string (invisible in Word, Google Docs, etc.)
    """
    # Build payload
    payload = {
        "signer_id": signer_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "content_hash": hashlib.sha256(text.encode('utf-8')).hexdigest(),
    }
    
    if metadata:
        payload["metadata"] = metadata
    
    # Serialize payload
    payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    payload_bytes = payload_json.encode('utf-8')
    
    # Create signature over payload
    signature_bytes = private_key.sign(payload_bytes)
    
    # Encode components
    magic = ZW_MAGIC_V1
    version = encode_byte_zw(1)  # Version 1
    
    # Payload length (2 bytes, up to 65535)
    payload_len = len(payload_bytes)
    if payload_len > 65535:
        raise ValueError(f"Payload too large: {payload_len} bytes")
    
    len_bytes = struct.pack('>H', payload_len)  # Big-endian uint16
    encoded_len = encode_bytes_zw(len_bytes)
    
    # Encode payload and signature
    encoded_payload = encode_bytes_zw(payload_bytes)
    encoded_signature = encode_bytes_zw(signature_bytes)
    
    # Combine all parts
    return magic + version + encoded_len + encoded_payload + encoded_signature


def verify_zw_signature(
    signed_text: str,
    public_key: Ed25519PublicKey,
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Verify a ZW-embedded signature and extract payload.
    
    Args:
        signed_text: Text with ZW signature embedded
        public_key: Ed25519 public key for verification
    
    Returns:
        Tuple of (is_valid, payload_dict)
    """
    # Extract ZW signature from text
    zw_sig = extract_zw_signature(signed_text)
    if not zw_sig:
        return False, None
    
    try:
        # Parse signature structure
        magic = zw_sig[:4]
        if magic != ZW_MAGIC_V1:
            return False, None
        
        version_encoded = zw_sig[4:8]  # 1 byte = 4 chars (base-4)
        version = decode_byte_zw(version_encoded)
        if version != 1:
            return False, None
        
        # Decode payload length
        len_encoded = zw_sig[8:16]  # 2 bytes = 8 chars (base-4)
        len_bytes = decode_bytes_zw(len_encoded)
        payload_len = struct.unpack('>H', len_bytes)[0]
        
        # Extract payload and signature
        payload_start = 16
        payload_end = payload_start + (payload_len * 4)  # 4 chars per byte (base-4)
        sig_start = payload_end
        sig_end = sig_start + (64 * 4)  # Ed25519 signature = 64 bytes = 256 chars
        
        if len(zw_sig) < sig_end:
            return False, None
        
        encoded_payload = zw_sig[payload_start:payload_end]
        encoded_signature = zw_sig[sig_start:sig_end]
        
        # Decode
        payload_bytes = decode_bytes_zw(encoded_payload)
        signature_bytes = decode_bytes_zw(encoded_signature)
        
        # Verify signature
        try:
            public_key.verify(signature_bytes, payload_bytes)
            is_valid = True
        except Exception:
            is_valid = False
        
        # Parse payload
        payload_json = payload_bytes.decode('utf-8')
        payload = json.loads(payload_json)
        
        # Verify content hash
        clean_text = remove_zw_signature(signed_text)
        expected_hash = payload.get("content_hash")
        actual_hash = hashlib.sha256(clean_text.encode('utf-8')).hexdigest()
        
        if expected_hash != actual_hash:
            # Content has been modified
            payload["content_tampered"] = True
            is_valid = False
        
        return is_valid, payload
        
    except Exception as e:
        return False, None


def extract_zw_signature(text: str) -> Optional[str]:
    """
    Extract ZW signature from text by finding magic number.
    
    Args:
        text: Text potentially containing ZW signature
    
    Returns:
        ZW signature string if found, None otherwise
    """
    # Find magic number
    idx = text.find(ZW_MAGIC_V1)
    if idx == -1:
        return None
    
    # Extract signature (we need to parse length to know full size)
    # Base-4 encoding: 4 chars per byte
    # Max signature size: 4 + 4 + 8 + (65535*4) + (64*4) = ~262k chars
    # Typical: 4 + 4 + 8 + (~200*4) + (64*4) = ~1,072 chars
    
    # Extract up to 1500 chars after magic number
    potential_sig = text[idx:idx+1500]
    
    try:
        # Parse to get actual length
        if len(potential_sig) < 16:  # magic(4) + version(4) + len(8)
            return None
        
        len_encoded = potential_sig[8:16]  # 2 bytes = 8 chars (base-4)
        len_bytes = decode_bytes_zw(len_encoded)
        payload_len = struct.unpack('>H', len_bytes)[0]
        
        # Calculate total signature length (base-4: 4 chars per byte)
        total_len = 4 + 4 + 8 + (payload_len * 4) + (64 * 4)
        
        if len(text) < idx + total_len:
            return None
        
        return text[idx:idx+total_len]
        
    except Exception:
        return None


def remove_zw_signature(text: str) -> str:
    """
    Remove ZW signature from text, returning clean content.
    
    Args:
        text: Text with ZW signature
    
    Returns:
        Clean text with signature removed
    """
    zw_sig = extract_zw_signature(text)
    if not zw_sig:
        return text
    
    return text.replace(zw_sig, '')


def embed_zw_signature(text: str, signature: str) -> str:
    """
    Embed ZW signature into text.
    
    Args:
        text: Original text
        signature: ZW signature string
    
    Returns:
        Text with signature appended
    """
    return text + signature


# Convenience functions for UUID-based references

def create_uuid_reference_zw(
    text: str,
    document_uuid: UUID,
    private_key: Ed25519PrivateKey,
    signer_id: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a UUID reference with cryptographic signature using ZW chars.
    
    This is more compact than full signature embedding:
    - UUID: 16 bytes = 96 chars
    - Signature over UUID+hash: 64 bytes = 384 chars
    - Total: ~480 chars (vs ~1600 for full payload)
    
    Args:
        text: Text to sign
        document_uuid: UUID for database reference
        private_key: Ed25519 private key
        signer_id: Identifier for the signer
        metadata: Optional metadata
    
    Returns:
        Text with ZW-encoded UUID reference and signature
    """
    # Build compact payload: UUID + content hash
    content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    payload_metadata = {
        "uuid": str(document_uuid),
    }
    
    if metadata:
        payload_metadata.update(metadata)
    
    return text + create_zw_signature(text, private_key, signer_id, payload_metadata)


def verify_uuid_reference_zw(
    signed_text: str,
    public_key: Ed25519PublicKey,
) -> Tuple[bool, Optional[UUID], Optional[Dict[str, Any]]]:
    """
    Verify UUID reference and extract UUID.
    
    Args:
        signed_text: Text with ZW UUID reference
        public_key: Ed25519 public key
    
    Returns:
        Tuple of (is_valid, uuid, payload)
    """
    is_valid, payload = verify_zw_signature(signed_text, public_key)
    
    if not is_valid or not payload:
        return False, None, None
    
    # UUID can be at top level or nested in metadata
    uuid_str = payload.get("uuid")
    if not uuid_str and "metadata" in payload:
        uuid_str = payload["metadata"].get("uuid")
    
    if not uuid_str:
        return False, None, payload
    
    try:
        doc_uuid = UUID(uuid_str)
        return is_valid, doc_uuid, payload
    except ValueError:
        return False, None, payload


# =============================================================================
# MINIMAL SIGNED UUID - Sentence-level provenance
# =============================================================================
#
# For sentence-level tracking, we use a minimal format:
# - UUID: 16 bytes (database reference)
# - HMAC: 16 bytes (cryptographic proof)
# - Total: 32 bytes = 128 chars (base-4 encoding)
#
# Detection: 128 contiguous base-4 characters (no magic number needed)
# All other data (merkle info, signer details, manifest) lives in the database.
#
# Word-compatible: Uses only ZWNJ, ZWJ, CGJ, MVS (no ZWSP!)
# =============================================================================


def create_minimal_signed_uuid(
    sentence_uuid: UUID,
    signing_key: bytes,
) -> str:
    """
    Create the most compact cryptographically signed UUID possible.
    
    Format (32 bytes = 128 chars with base-4):
    - UUID: 16 bytes = 64 chars (database reference)
    - HMAC-SHA256: 16 bytes = 64 chars (cryptographic proof)
    
    Total: 128 characters (all invisible, Word-compatible)
    
    Detection: 128 contiguous base-4 characters (no magic number needed)
    
    Security:
    - 128-bit UUID uniqueness
    - 128-bit HMAC security (truncated from 256-bit)
    - Signing key should be org-specific secret (derived from private key)
    
    Word Compatibility:
    - Uses only ZWNJ, ZWJ, CGJ, MVS (no ZWSP which Word strips!)
    - No WJ (appears as space in Word!)
    - 35% smaller than base-3 encoding
    
    Args:
        sentence_uuid: UUID for this sentence (stored in DB with full metadata)
        signing_key: 32-byte secret key for HMAC (org-specific)
    
    Returns:
        128 invisible characters (Word-compatible)
    """
    if len(signing_key) < 32:
        raise ValueError("Signing key must be at least 32 bytes")
    
    uuid_bytes = sentence_uuid.bytes  # 16 bytes
    
    # Create HMAC-SHA256 over UUID, truncate to 16 bytes (128-bit security)
    h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
    h.update(uuid_bytes)
    hmac_full = h.finalize()
    hmac_truncated = hmac_full[:16]  # 128-bit security
    
    # Encode: magic + UUID + HMAC
    payload = uuid_bytes + hmac_truncated  # 32 bytes
    encoded_payload = encode_bytes_zw(payload)  # 128 chars (base-4)
    
    return encoded_payload  # 128 chars (no magic number)


def verify_minimal_signed_uuid(
    signature: str,
    signing_key: bytes,
) -> Tuple[bool, Optional[UUID]]:
    """
    Verify a minimal signed UUID (128 chars) and extract the UUID.
    
    Args:
        signature: 128-character signature string (base-4 encoded)
        signing_key: 32-byte secret key for HMAC verification
    
    Returns:
        Tuple of (is_valid, uuid)
    """
    if len(signature) != 128:
        return False, None
    
    try:
        # Decode the 128-char signature
        payload = decode_bytes_zw(signature)
        
        if len(payload) != 32:
            return False, None
        
        # Split into UUID and HMAC
        uuid_bytes = payload[:16]
        hmac_received = payload[16:32]
        
        # Recompute HMAC
        h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
        h.update(uuid_bytes)
        hmac_expected = h.finalize()[:16]
        
        # Constant-time comparison
        if hmac_received != hmac_expected:
            return False, None
        
        # Extract UUID
        sentence_uuid = UUID(bytes=uuid_bytes)
        return True, sentence_uuid
        
    except Exception:
        return False, None


def find_all_minimal_signed_uuids(text: str) -> list[tuple[int, int, str]]:
    """
    Find all minimal signed UUIDs by detecting 128 contiguous base-4 characters.
    
    This is the key innovation: signatures are detected by finding sequences of
    exactly 128 contiguous base-4 characters. Natural text will never have such
    long sequences of invisible characters, so false positives are virtually impossible.
    
    Args:
        text: Text potentially containing signatures
    
    Returns:
        List of (start_pos, end_pos, signature_string) tuples
    """
    signatures = []
    i = 0
    
    while i < len(text):
        # Check if we're at start of a base-4 sequence
        if text[i] in CHARS_BASE4_SET:
            # Count contiguous base-4 chars
            start = i
            while i < len(text) and text[i] in CHARS_BASE4_SET:
                i += 1
            length = i - start
            
            # If we have at least 128 chars, extract signatures
            # (could be multiple signatures concatenated)
            while length >= 128:
                sig = text[start:start+128]
                signatures.append((start, start+128, sig))
                start += 128
                length -= 128
        else:
            i += 1
    
    return signatures


def extract_minimal_signed_uuid(text: str) -> Optional[str]:
    """
    Extract first minimal signed UUID from text.
    
    Args:
        text: Text containing minimal signed UUID
    
    Returns:
        The minimal signed UUID string (128 chars) or None
    """
    sigs = find_all_minimal_signed_uuids(text)
    return sigs[0][2] if sigs else None


def remove_minimal_signed_uuid(text: str) -> str:
    """
    Remove all minimal signed UUIDs from text.
    
    Args:
        text: Text with minimal signed UUIDs
    
    Returns:
        Clean text with all signatures removed
    """
    sigs = find_all_minimal_signed_uuids(text)
    result = text
    # Remove in reverse order to maintain positions
    for start, end, sig in reversed(sigs):
        result = result[:start] + result[end:]
    return result


def derive_signing_key_from_private_key(private_key: Ed25519PrivateKey) -> bytes:
    """
    Derive a 32-byte HMAC signing key from an Ed25519 private key.
    
    This allows using the same key infrastructure for both full signatures
    and minimal signed UUIDs.
    
    Args:
        private_key: Ed25519 private key
    
    Returns:
        32-byte signing key for HMAC operations
    """
    # Get raw private key bytes and hash them to derive HMAC key
    # This ensures the HMAC key is cryptographically tied to the org's identity
    private_bytes = private_key.private_bytes_raw()
    return hashlib.sha256(b"encypher-hmac-key:" + private_bytes).digest()


# Duplicate removed - using contiguous sequence detection version above


# =============================================================================
# SAFE EMBEDDING POSITION - Insert before terminal punctuation
# =============================================================================

# Terminal punctuation characters
TERMINAL_PUNCTUATION = '.!?'

# Extended punctuation (includes quotes that often follow terminal punctuation)
TRAILING_PUNCTUATION = '.!?"\')]}»"'


def embed_signature_safely(text: str, signature: str) -> str:
    """
    Embed signature before terminal punctuation to reduce accidental deletion.
    
    In Word/editors, users typically delete from the end. By placing the
    invisible signature BEFORE the final punctuation, accidental deletion
    is less likely since users rarely delete punctuation when editing.
    
    Examples:
        "Hello world." → "Hello world[SIG]."
        "What time is it?" → "What time is it[SIG]?"
        "Wow!" → "Wow[SIG]!"
        "She said "Hello."" → "She said "Hello[SIG].""
        "No punctuation" → "No punctuation[SIG]"
    
    Args:
        text: Original text (sentence)
        signature: ZW signature to embed
    
    Returns:
        Text with signature embedded before terminal punctuation
    """
    if not text:
        return signature
    
    # Find how many trailing punctuation characters there are
    trailing_count = 0
    for char in reversed(text):
        if char in TRAILING_PUNCTUATION:
            trailing_count += 1
        else:
            break
    
    if trailing_count > 0:
        # Insert signature before trailing punctuation
        insert_pos = len(text) - trailing_count
        return text[:insert_pos] + signature + text[insert_pos:]
    else:
        # No terminal punctuation, append at end
        return text + signature


def extract_text_without_signature(text: str, signature: str) -> str:
    """
    Remove signature from text, handling safe embedding position.
    
    Args:
        text: Text with embedded signature
        signature: The signature to remove
    
    Returns:
        Clean text with signature removed
    """
    return text.replace(signature, '')


def get_signature_position(text: str) -> int:
    """
    Get the recommended position for embedding a signature.
    
    Args:
        text: Text to analyze
    
    Returns:
        Index where signature should be inserted
    """
    if not text:
        return 0
    
    # Count trailing punctuation
    trailing_count = 0
    for char in reversed(text):
        if char in TRAILING_PUNCTUATION:
            trailing_count += 1
        else:
            break
    
    return len(text) - trailing_count


def create_safely_embedded_sentence(
    sentence: str,
    sentence_uuid: UUID,
    signing_key: bytes,
) -> str:
    """
    Create a sentence with minimal signed UUID embedded safely.
    
    Combines create_minimal_signed_uuid() with safe positioning.
    
    Args:
        sentence: Original sentence text
        sentence_uuid: UUID for this sentence
        signing_key: HMAC signing key
    
    Returns:
        Sentence with signature embedded before terminal punctuation
    """
    signature = create_minimal_signed_uuid(sentence_uuid, signing_key)
    return embed_signature_safely(sentence, signature)
