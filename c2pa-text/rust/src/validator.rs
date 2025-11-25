//! C2PA Manifest Structural Validator.
//!
//! Provides validation utilities to help developers ensure their C2PA manifests
//! are structurally compliant before embedding them into text.

use std::fmt;

/// JUMBF Constants (ISO/IEC 19566-5)
const JUMBF_SUPERBOX_TYPE: &[u8; 4] = b"jumb";
const JUMBF_DESC_TYPE: &[u8; 4] = b"jumd";
const C2PA_MANIFEST_STORE_UUID: [u8; 16] = [
    0x63, 0x32, 0x70, 0x61, 0x00, 0x11, 0x00, 0x10,
    0x80, 0x00, 0x00, 0xAA, 0x00, 0x38, 0x9B, 0x71,
];

/// C2PA-compliant validation status codes for text manifests.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ValidationCode {
    /// Manifest is valid
    Valid,
    /// Wrapper-level failures (from C2PA Text spec)
    CorruptedWrapper,
    MultipleWrappers,
    /// Extended validation codes
    InvalidMagic,
    UnsupportedVersion,
    LengthMismatch,
    EmptyManifest,
    /// JUMBF-level failures
    InvalidJumbfHeader,
    InvalidJumbfBoxSize,
    MissingDescriptionBox,
    InvalidC2paUuid,
    TruncatedJumbf,
}

impl ValidationCode {
    /// Returns the C2PA-compliant status code string.
    pub fn as_str(&self) -> &'static str {
        match self {
            ValidationCode::Valid => "valid",
            ValidationCode::CorruptedWrapper => "manifest.text.corruptedWrapper",
            ValidationCode::MultipleWrappers => "manifest.text.multipleWrappers",
            ValidationCode::InvalidMagic => "manifest.text.invalidMagic",
            ValidationCode::UnsupportedVersion => "manifest.text.unsupportedVersion",
            ValidationCode::LengthMismatch => "manifest.text.lengthMismatch",
            ValidationCode::EmptyManifest => "manifest.text.emptyManifest",
            ValidationCode::InvalidJumbfHeader => "manifest.jumbf.invalidHeader",
            ValidationCode::InvalidJumbfBoxSize => "manifest.jumbf.invalidBoxSize",
            ValidationCode::MissingDescriptionBox => "manifest.jumbf.missingDescriptionBox",
            ValidationCode::InvalidC2paUuid => "manifest.jumbf.invalidC2paUuid",
            ValidationCode::TruncatedJumbf => "manifest.jumbf.truncated",
        }
    }
}

impl fmt::Display for ValidationCode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

/// A single validation issue with location and details.
#[derive(Debug, Clone)]
pub struct ValidationIssue {
    pub code: ValidationCode,
    pub message: String,
    pub offset: Option<usize>,
    pub context: Option<String>,
}

impl fmt::Display for ValidationIssue {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}] {}", self.code, self.message)
    }
}

/// Result of manifest validation with detailed diagnostics.
#[derive(Debug, Clone)]
pub struct ValidationResult {
    pub valid: bool,
    pub issues: Vec<ValidationIssue>,
    pub manifest_bytes: Option<Vec<u8>>,
    pub jumbf_bytes: Option<Vec<u8>>,
    pub version: Option<u8>,
    pub declared_length: Option<u32>,
    pub actual_length: Option<usize>,
}

impl ValidationResult {
    /// Create a new valid result.
    pub fn new() -> Self {
        Self {
            valid: true,
            issues: Vec::new(),
            manifest_bytes: None,
            jumbf_bytes: None,
            version: None,
            declared_length: None,
            actual_length: None,
        }
    }

    /// Add a validation issue.
    pub fn add_issue(
        &mut self,
        code: ValidationCode,
        message: impl Into<String>,
        offset: Option<usize>,
        context: Option<String>,
    ) {
        self.issues.push(ValidationIssue {
            code,
            message: message.into(),
            offset,
            context,
        });
        self.valid = false;
    }

    /// Returns the most severe validation code.
    pub fn primary_code(&self) -> ValidationCode {
        self.issues
            .first()
            .map(|i| i.code.clone())
            .unwrap_or(ValidationCode::Valid)
    }
}

impl Default for ValidationResult {
    fn default() -> Self {
        Self::new()
    }
}

impl fmt::Display for ValidationResult {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if self.valid {
            write!(f, "Validation passed: manifest is structurally compliant")
        } else {
            writeln!(f, "Validation failed:")?;
            for issue in &self.issues {
                writeln!(f, "  - {}", issue)?;
            }
            Ok(())
        }
    }
}

/// Validate basic JUMBF box structure.
pub fn validate_jumbf_structure(jumbf_bytes: &[u8], strict: bool) -> ValidationResult {
    let mut result = ValidationResult::new();
    result.jumbf_bytes = Some(jumbf_bytes.to_vec());

    if jumbf_bytes.is_empty() {
        result.add_issue(
            ValidationCode::EmptyManifest,
            "JUMBF content is empty",
            Some(0),
            None,
        );
        return result;
    }

    // Minimum JUMBF box: 8 bytes header (size + type)
    if jumbf_bytes.len() < 8 {
        result.add_issue(
            ValidationCode::InvalidJumbfHeader,
            format!(
                "JUMBF too short for box header: {} bytes, minimum 8",
                jumbf_bytes.len()
            ),
            Some(0),
            None,
        );
        return result;
    }

    // Parse first box header
    let box_size = u32::from_be_bytes([
        jumbf_bytes[0],
        jumbf_bytes[1],
        jumbf_bytes[2],
        jumbf_bytes[3],
    ]);
    let box_type = &jumbf_bytes[4..8];

    // Validate box size
    let (effective_size, header_size) = if box_size == 0 {
        // Size 0 means "extends to end of file"
        (jumbf_bytes.len(), 8)
    } else if box_size == 1 {
        // Extended size (64-bit)
        if jumbf_bytes.len() < 16 {
            result.add_issue(
                ValidationCode::TruncatedJumbf,
                "Extended box size declared but not enough bytes for 64-bit size field",
                Some(0),
                None,
            );
            return result;
        }
        let extended_size = u64::from_be_bytes([
            jumbf_bytes[8],
            jumbf_bytes[9],
            jumbf_bytes[10],
            jumbf_bytes[11],
            jumbf_bytes[12],
            jumbf_bytes[13],
            jumbf_bytes[14],
            jumbf_bytes[15],
        ]) as usize;
        (extended_size, 16)
    } else if box_size < 8 {
        result.add_issue(
            ValidationCode::InvalidJumbfBoxSize,
            format!("Invalid box size: {} (minimum is 8)", box_size),
            Some(0),
            None,
        );
        return result;
    } else {
        (box_size as usize, 8)
    };

    // Check if we have enough bytes
    if jumbf_bytes.len() < effective_size {
        result.add_issue(
            ValidationCode::TruncatedJumbf,
            format!(
                "JUMBF truncated: declared size {}, actual {}",
                effective_size,
                jumbf_bytes.len()
            ),
            Some(0),
            None,
        );
        return result;
    }

    // Check for JUMBF superbox type
    if box_type != JUMBF_SUPERBOX_TYPE {
        result.add_issue(
            ValidationCode::InvalidJumbfHeader,
            format!(
                "Expected JUMBF superbox type 'jumb', got '{}'",
                String::from_utf8_lossy(box_type)
            ),
            Some(4),
            Some(format!("box_type={:02x?}", box_type)),
        );
        return result;
    }

    if strict {
        // Check for description box (jumd)
        if jumbf_bytes.len() < header_size + 8 {
            result.add_issue(
                ValidationCode::MissingDescriptionBox,
                "JUMBF superbox too short to contain description box",
                Some(header_size),
                None,
            );
            return result;
        }

        let desc_type = &jumbf_bytes[header_size + 4..header_size + 8];
        if desc_type != JUMBF_DESC_TYPE {
            result.add_issue(
                ValidationCode::MissingDescriptionBox,
                format!(
                    "Expected description box 'jumd', got '{}'",
                    String::from_utf8_lossy(desc_type)
                ),
                Some(header_size + 4),
                None,
            );
            return result;
        }

        // Check for C2PA UUID
        let uuid_offset = header_size + 8;
        if jumbf_bytes.len() >= uuid_offset + 16 {
            let found_uuid = &jumbf_bytes[uuid_offset..uuid_offset + 16];
            if found_uuid != C2PA_MANIFEST_STORE_UUID {
                result.add_issue(
                    ValidationCode::InvalidC2paUuid,
                    "Invalid C2PA manifest store UUID",
                    Some(uuid_offset),
                    Some(format!(
                        "expected={:02x?}, found={:02x?}",
                        C2PA_MANIFEST_STORE_UUID, found_uuid
                    )),
                );
            }
        }
    }

    result
}

/// Validate a C2PA manifest before embedding.
///
/// This is the main validation entry point.
pub fn validate_manifest(manifest_bytes: &[u8], validate_jumbf: bool, strict: bool) -> ValidationResult {
    let mut result = ValidationResult::new();
    result.manifest_bytes = Some(manifest_bytes.to_vec());

    if manifest_bytes.is_empty() {
        result.add_issue(
            ValidationCode::EmptyManifest,
            "Manifest bytes are empty",
            None,
            None,
        );
        return result;
    }

    result.actual_length = Some(manifest_bytes.len());

    if validate_jumbf {
        let jumbf_result = validate_jumbf_structure(manifest_bytes, strict);
        if !jumbf_result.valid {
            result.issues.extend(jumbf_result.issues);
            result.valid = false;
        }
    }

    result
}

/// Validate a pre-encoded C2PATextManifestWrapper.
pub fn validate_wrapper_bytes(wrapper_bytes: &[u8]) -> ValidationResult {
    use crate::{MAGIC, VERSION, HEADER_SIZE};

    let mut result = ValidationResult::new();

    if wrapper_bytes.len() < HEADER_SIZE {
        result.add_issue(
            ValidationCode::CorruptedWrapper,
            format!(
                "Wrapper too short: {} bytes, minimum {}",
                wrapper_bytes.len(),
                HEADER_SIZE
            ),
            Some(0),
            None,
        );
        return result;
    }

    // Check magic
    if &wrapper_bytes[0..8] != MAGIC {
        result.add_issue(
            ValidationCode::InvalidMagic,
            format!(
                "Invalid magic: expected 'C2PATXT\\0', got {:?}",
                &wrapper_bytes[0..8]
            ),
            Some(0),
            None,
        );
        return result;
    }

    // Check version
    let version = wrapper_bytes[8];
    result.version = Some(version);
    if version != VERSION {
        result.add_issue(
            ValidationCode::UnsupportedVersion,
            format!("Unsupported version: {}, expected {}", version, VERSION),
            Some(8),
            None,
        );
        return result;
    }

    // Check length
    let declared_length = u32::from_be_bytes([
        wrapper_bytes[9],
        wrapper_bytes[10],
        wrapper_bytes[11],
        wrapper_bytes[12],
    ]);
    result.declared_length = Some(declared_length);

    let actual_jumbf_length = wrapper_bytes.len() - HEADER_SIZE;
    result.actual_length = Some(actual_jumbf_length);

    if declared_length as usize != actual_jumbf_length {
        result.add_issue(
            ValidationCode::LengthMismatch,
            format!(
                "Length mismatch: declares {} bytes, actual {}",
                declared_length, actual_jumbf_length
            ),
            Some(9),
            None,
        );
        return result;
    }

    // Validate JUMBF
    let jumbf_bytes = &wrapper_bytes[HEADER_SIZE..];
    result.jumbf_bytes = Some(jumbf_bytes.to_vec());
    result.manifest_bytes = Some(jumbf_bytes.to_vec());

    let jumbf_result = validate_jumbf_structure(jumbf_bytes, false);
    if !jumbf_result.valid {
        result.issues.extend(jumbf_result.issues);
        result.valid = false;
    }

    result
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_manifest_fails() {
        let result = validate_manifest(&[], true, false);
        assert!(!result.valid);
        assert_eq!(result.primary_code(), ValidationCode::EmptyManifest);
    }

    #[test]
    fn test_minimal_valid_jumbf() {
        // Minimal JUMBF superbox: size (4) + type (4) = 8 bytes
        let mut jumbf = vec![0, 0, 0, 8]; // size = 8
        jumbf.extend_from_slice(b"jumb");
        let result = validate_manifest(&jumbf, true, false);
        assert!(result.valid);
    }

    #[test]
    fn test_invalid_box_type_fails() {
        let mut invalid = vec![0, 0, 0, 8];
        invalid.extend_from_slice(b"xxxx");
        let result = validate_manifest(&invalid, true, false);
        assert!(!result.valid);
        assert_eq!(result.primary_code(), ValidationCode::InvalidJumbfHeader);
    }

    #[test]
    fn test_truncated_jumbf_fails() {
        let mut truncated = vec![0, 0, 0, 100]; // claims 100 bytes
        truncated.extend_from_slice(b"jumb");
        let result = validate_manifest(&truncated, true, false);
        assert!(!result.valid);
        assert_eq!(result.primary_code(), ValidationCode::TruncatedJumbf);
    }
}
