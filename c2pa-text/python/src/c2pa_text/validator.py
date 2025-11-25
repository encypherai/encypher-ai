"""
C2PA Manifest Structural Validator.

This module provides validation utilities to help developers ensure their
C2PA manifests are structurally compliant before embedding them into text.

Validation Levels:
1. Wrapper Structure - Validates the C2PATextManifestWrapper format
2. JUMBF Structure - Validates basic JUMBF box structure
3. Manifest Store - Validates C2PA Manifest Store requirements

Status codes follow the C2PA specification for text manifests.
"""

import struct
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

# JUMBF Constants (ISO/IEC 19566-5)
JUMBF_SUPERBOX_TYPE = b"jumb"
JUMBF_DESC_TYPE = b"jumd"
C2PA_MANIFEST_STORE_UUID = bytes.fromhex("6332706100110010800000AA00389B71")  # c2pa UUID


class ValidationCode(Enum):
    """C2PA-compliant validation status codes for text manifests."""

    # Success
    VALID = "valid"

    # Wrapper-level failures (from C2PA Text spec)
    CORRUPTED_WRAPPER = "manifest.text.corruptedWrapper"
    MULTIPLE_WRAPPERS = "manifest.text.multipleWrappers"

    # Extended validation codes for developer guidance
    INVALID_MAGIC = "manifest.text.invalidMagic"
    UNSUPPORTED_VERSION = "manifest.text.unsupportedVersion"
    LENGTH_MISMATCH = "manifest.text.lengthMismatch"
    EMPTY_MANIFEST = "manifest.text.emptyManifest"

    # JUMBF-level failures
    INVALID_JUMBF_HEADER = "manifest.jumbf.invalidHeader"
    INVALID_JUMBF_BOX_SIZE = "manifest.jumbf.invalidBoxSize"
    MISSING_DESCRIPTION_BOX = "manifest.jumbf.missingDescriptionBox"
    INVALID_C2PA_UUID = "manifest.jumbf.invalidC2paUuid"
    TRUNCATED_JUMBF = "manifest.jumbf.truncated"


@dataclass
class ValidationIssue:
    """A single validation issue with location and details."""

    code: ValidationCode
    message: str
    offset: Optional[int] = None
    context: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of manifest validation with detailed diagnostics."""

    valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    manifest_bytes: Optional[bytes] = None
    jumbf_bytes: Optional[bytes] = None

    # Parsed metadata (if validation succeeded far enough)
    version: Optional[int] = None
    declared_length: Optional[int] = None
    actual_length: Optional[int] = None

    def add_issue(
        self,
        code: ValidationCode,
        message: str,
        offset: Optional[int] = None,
        context: Optional[str] = None,
    ) -> None:
        """Add a validation issue."""
        self.issues.append(ValidationIssue(code, message, offset, context))
        self.valid = False

    @property
    def primary_code(self) -> ValidationCode:
        """Return the most severe validation code."""
        if not self.issues:
            return ValidationCode.VALID
        return self.issues[0].code

    def __str__(self) -> str:
        if self.valid:
            return "Validation passed: manifest is structurally compliant"
        issues_str = "\n".join(f"  - [{i.code.value}] {i.message}" for i in self.issues)
        return f"Validation failed:\n{issues_str}"


def validate_jumbf_structure(jumbf_bytes: bytes, strict: bool = False) -> ValidationResult:
    """
    Validate basic JUMBF box structure.

    This performs structural validation of the JUMBF container format,
    checking box headers, sizes, and the presence of required elements.

    Args:
        jumbf_bytes: Raw JUMBF bytes (the manifest store).
        strict: If True, perform additional C2PA-specific checks.

    Returns:
        ValidationResult with detailed diagnostics.
    """
    result = ValidationResult(valid=True, jumbf_bytes=jumbf_bytes)

    if not jumbf_bytes:
        result.add_issue(ValidationCode.EMPTY_MANIFEST, "JUMBF content is empty")
        return result

    # Minimum JUMBF box: 8 bytes header (size + type)
    if len(jumbf_bytes) < 8:
        result.add_issue(
            ValidationCode.INVALID_JUMBF_HEADER,
            f"JUMBF too short for box header: {len(jumbf_bytes)} bytes, minimum 8",
            offset=0,
        )
        return result

    # Parse first box header
    try:
        box_size = struct.unpack(">I", jumbf_bytes[0:4])[0]
        box_type = jumbf_bytes[4:8]
    except struct.error as e:
        result.add_issue(
            ValidationCode.INVALID_JUMBF_HEADER,
            f"Failed to parse JUMBF box header: {e}",
            offset=0,
        )
        return result

    # Validate box size
    if box_size == 0:
        # Size 0 means "extends to end of file" - valid but we note it
        pass
    elif box_size == 1:
        # Extended size (64-bit) - need 16 bytes minimum
        if len(jumbf_bytes) < 16:
            result.add_issue(
                ValidationCode.TRUNCATED_JUMBF,
                "Extended box size declared but not enough bytes for 64-bit size field",
                offset=0,
            )
            return result
        box_size = struct.unpack(">Q", jumbf_bytes[8:16])[0]
    elif box_size < 8:
        result.add_issue(
            ValidationCode.INVALID_JUMBF_BOX_SIZE,
            f"Invalid box size: {box_size} (minimum is 8)",
            offset=0,
        )
        return result

    # Check if we have enough bytes
    if box_size > 0 and len(jumbf_bytes) < box_size:
        result.add_issue(
            ValidationCode.TRUNCATED_JUMBF,
            f"JUMBF truncated: declared size {box_size}, actual {len(jumbf_bytes)}",
            offset=0,
        )
        return result

    # Check for JUMBF superbox type
    if box_type != JUMBF_SUPERBOX_TYPE:
        result.add_issue(
            ValidationCode.INVALID_JUMBF_HEADER,
            f"Expected JUMBF superbox type 'jumb', got '{box_type!r}'",
            offset=4,
            context=f"box_type={box_type.hex()}",
        )
        return result

    if strict:
        # Check for description box (jumd) which should follow immediately
        # after the superbox header
        header_size = 8 if box_size != 1 else 16
        if len(jumbf_bytes) < header_size + 8:
            result.add_issue(
                ValidationCode.MISSING_DESCRIPTION_BOX,
                "JUMBF superbox too short to contain description box",
                offset=header_size,
            )
            return result

        _desc_size = struct.unpack(">I", jumbf_bytes[header_size : header_size + 4])[0]  # noqa: F841
        desc_type = jumbf_bytes[header_size + 4 : header_size + 8]

        if desc_type != JUMBF_DESC_TYPE:
            result.add_issue(
                ValidationCode.MISSING_DESCRIPTION_BOX,
                f"Expected description box 'jumd', got '{desc_type!r}'",
                offset=header_size + 4,
            )
            return result

        # Check for C2PA UUID in description box
        # UUID is at offset 8 within the description box content
        uuid_offset = header_size + 8  # After desc box header
        if len(jumbf_bytes) >= uuid_offset + 16:
            found_uuid = jumbf_bytes[uuid_offset : uuid_offset + 16]
            if found_uuid != C2PA_MANIFEST_STORE_UUID:
                result.add_issue(
                    ValidationCode.INVALID_C2PA_UUID,
                    "Invalid C2PA manifest store UUID",
                    offset=uuid_offset,
                    context=f"expected={C2PA_MANIFEST_STORE_UUID.hex()}, found={found_uuid.hex()}",
                )

    return result


def validate_manifest(
    manifest_bytes: bytes,
    validate_jumbf: bool = True,
    strict: bool = False,
) -> ValidationResult:
    """
    Validate a C2PA manifest before embedding.

    This is the main validation entry point. It checks that the provided
    bytes represent a valid structure that can be embedded using c2pa-text.

    Args:
        manifest_bytes: The raw manifest bytes to validate.
        validate_jumbf: If True, also validate JUMBF structure.
        strict: If True, perform additional C2PA-specific checks.

    Returns:
        ValidationResult with detailed diagnostics.

    Example:
        >>> from c2pa_text import validate_manifest
        >>> result = validate_manifest(my_manifest_bytes)
        >>> if result.valid:
        ...     watermarked = embed_manifest(text, my_manifest_bytes)
        ... else:
        ...     print(result)  # Shows all issues
    """
    result = ValidationResult(valid=True, manifest_bytes=manifest_bytes)

    # Check for empty input
    if not manifest_bytes:
        result.add_issue(ValidationCode.EMPTY_MANIFEST, "Manifest bytes are empty")
        return result

    result.actual_length = len(manifest_bytes)

    # If validate_jumbf is enabled, validate the JUMBF structure
    if validate_jumbf:
        jumbf_result = validate_jumbf_structure(manifest_bytes, strict=strict)
        if not jumbf_result.valid:
            result.issues.extend(jumbf_result.issues)
            result.valid = False

    return result


def validate_wrapper_bytes(wrapper_bytes: bytes) -> ValidationResult:
    """
    Validate a pre-encoded C2PATextManifestWrapper.

    Use this to validate wrapper bytes that have already been encoded
    (e.g., extracted from text and decoded from variation selectors).

    Args:
        wrapper_bytes: The decoded wrapper bytes (header + JUMBF).

    Returns:
        ValidationResult with detailed diagnostics.
    """
    from . import _HEADER_SIZE, _HEADER_STRUCT, MAGIC, VERSION

    result = ValidationResult(valid=True)

    # Check minimum length
    if len(wrapper_bytes) < _HEADER_SIZE:
        result.add_issue(
            ValidationCode.CORRUPTED_WRAPPER,
            f"Wrapper too short: {len(wrapper_bytes)} bytes, minimum {_HEADER_SIZE}",
            offset=0,
        )
        return result

    # Parse header
    try:
        magic, version, length = _HEADER_STRUCT.unpack(wrapper_bytes[:_HEADER_SIZE])
    except struct.error as e:
        result.add_issue(
            ValidationCode.CORRUPTED_WRAPPER,
            f"Failed to parse wrapper header: {e}",
            offset=0,
        )
        return result

    result.version = version
    result.declared_length = length
    result.actual_length = len(wrapper_bytes) - _HEADER_SIZE

    # Validate magic
    if magic != MAGIC:
        result.add_issue(
            ValidationCode.INVALID_MAGIC,
            f"Invalid magic: expected 'C2PATXT\\0', got {magic!r}",
            offset=0,
            context=f"expected={MAGIC.hex()}, found={magic.hex()}",
        )
        return result

    # Validate version
    if version != VERSION:
        result.add_issue(
            ValidationCode.UNSUPPORTED_VERSION,
            f"Unsupported version: {version}, expected {VERSION}",
            offset=8,
        )
        return result

    # Validate length
    actual_jumbf_length = len(wrapper_bytes) - _HEADER_SIZE
    if length != actual_jumbf_length:
        result.add_issue(
            ValidationCode.LENGTH_MISMATCH,
            f"Length mismatch: declares {length} bytes, actual {actual_jumbf_length}",
            offset=9,
        )
        return result

    # Extract and validate JUMBF
    jumbf_bytes = wrapper_bytes[_HEADER_SIZE:]
    result.jumbf_bytes = jumbf_bytes
    result.manifest_bytes = jumbf_bytes

    jumbf_result = validate_jumbf_structure(jumbf_bytes)
    if not jumbf_result.valid:
        result.issues.extend(jumbf_result.issues)
        result.valid = False

    return result


# Convenience aliases
validate = validate_manifest
