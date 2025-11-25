//! C2PA Text Manifest Wrapper Reference Implementation.
//!
//! This module implements the C2PA Text Embedding Standard, allowing binary data
//! (typically a C2PA JUMBF Manifest) to be embedded into valid UTF-8 strings using
//! invisible Unicode Variation Selectors.
//!
//! # Validation
//!
//! Use [`validate_manifest`] to check manifest structure before embedding.
//! This helps catch issues early and provides detailed diagnostics.

use std::char;
use unicode_normalization::UnicodeNormalization;

pub mod validator;
pub use validator::{
    validate_jumbf_structure, validate_manifest, validate_wrapper_bytes,
    ValidationCode, ValidationIssue, ValidationResult,
};

// ---------------------- Constants -------------------------------------------

const MAGIC: &[u8; 8] = b"C2PATXT\0";
const VERSION: u8 = 1;
const HEADER_SIZE: usize = 13; // 8 (Magic) + 1 (Version) + 4 (Length)
const ZWNBSP: char = '\u{feff}';

// Variation Selector Ranges
const VS_START: u32 = 0xFE00;
const VS_END: u32 = 0xFE0F;
const VS_SUP_START: u32 = 0xE0100;
const VS_SUP_END: u32 = 0xE01EF;

#[derive(Debug)]
pub enum Error {
    InvalidByte(u8),
    InvalidVariationSelector(char),
    TooShort,
    InvalidMagic,
    UnsupportedVersion,
    Truncated,
    MultipleWrappers,
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Error::InvalidByte(b) => write!(f, "Byte out of range: {}", b),
            Error::InvalidVariationSelector(c) => write!(f, "Invalid variation selector: {}", c),
            Error::TooShort => write!(f, "Sequence too short for header"),
            Error::InvalidMagic => write!(f, "Invalid magic bytes"),
            Error::UnsupportedVersion => write!(f, "Unsupported version"),
            Error::Truncated => write!(f, "Wrapper truncated before end of manifest"),
            Error::MultipleWrappers => write!(f, "Multiple C2PA wrappers detected"),
        }
    }
}

impl std::error::Error for Error {}

fn byte_to_vs(byte: u8) -> char {
    if byte <= 15 {
        char::from_u32(VS_START + byte as u32).unwrap()
    } else {
        char::from_u32(VS_SUP_START + (byte as u32) - 16).unwrap()
    }
}

fn vs_to_byte(c: char) -> Option<u8> {
    let code = c as u32;
    if code >= VS_START && code <= VS_END {
        Some((code - VS_START) as u8)
    } else if code >= VS_SUP_START && code <= VS_SUP_END {
        Some(((code - VS_SUP_START) + 16) as u8)
    } else {
        None
    }
}

/// Encode raw bytes into a C2PA Text Manifest Wrapper string.
pub fn encode_wrapper(manifest_bytes: &[u8]) -> String {
    let len = manifest_bytes.len() as u32;
    
    // Estimate capacity: 1 (ZWNBSP) + HEADER_SIZE + len
    let mut out = String::with_capacity(1 + HEADER_SIZE + manifest_bytes.len());
    out.push(ZWNBSP);

    // Encode Header
    for &b in MAGIC {
        out.push(byte_to_vs(b));
    }
    out.push(byte_to_vs(VERSION));
    
    // Length (Big Endian)
    out.push(byte_to_vs(((len >> 24) & 0xFF) as u8));
    out.push(byte_to_vs(((len >> 16) & 0xFF) as u8));
    out.push(byte_to_vs(((len >> 8) & 0xFF) as u8));
    out.push(byte_to_vs((len & 0xFF) as u8));

    // Encode Body
    for &b in manifest_bytes {
        out.push(byte_to_vs(b));
    }

    out
}

/// Embed a C2PA manifest into text.
/// Normalizes the text to NFC and appends the invisible wrapper.
pub fn embed_manifest(text: &str, manifest_bytes: &[u8]) -> String {
    let normalized: String = text.nfc().collect();
    let wrapper = encode_wrapper(manifest_bytes);
    format!("{}{}", normalized, wrapper)
}

/// Result of extracting a manifest
#[derive(Debug)]
pub struct ExtractionResult {
    pub manifest: Option<Vec<u8>>,
    pub clean_text: String,
    pub offset: Option<usize>, // Byte offset of the wrapper start
    pub length: Option<usize>, // Byte length of the wrapper
}

/// Extract a C2PA manifest from text.
/// Returns ExtractionResult.
pub fn extract_manifest(text: &str) -> Result<ExtractionResult, Error> {
    // Simple scan for ZWNBSP
    let mut wrapper_start = None;
    let mut wrapper_end = None;
    let mut decoded_bytes = Vec::new();

    // Iterate chars to find potential wrapper
    let chars: Vec<(usize, char)> = text.char_indices().collect();
    let mut i = 0;
    
    while i < chars.len() {
        let (idx, c) = chars[i];
        if c == ZWNBSP {
            // Potential start
            let start_idx = idx;
            let mut current_bytes = Vec::new();
            let mut j = i + 1;
            
            while j < chars.len() {
                let (_, vc) = chars[j];
                if let Some(b) = vs_to_byte(vc) {
                    current_bytes.push(b);
                    j += 1;
                } else {
                    break; // End of sequence
                }
            }

            // Check header if we have enough bytes
            if current_bytes.len() >= HEADER_SIZE {
                // Check Magic
                if &current_bytes[0..8] == MAGIC {
                    // Check Version
                    if current_bytes[8] == VERSION {
                        // Check Length
                        let len = u32::from_be_bytes([
                            current_bytes[9],
                            current_bytes[10],
                            current_bytes[11],
                            current_bytes[12],
                        ]) as usize;

                        if current_bytes.len() >= HEADER_SIZE + len {
                            // Found valid wrapper
                            if wrapper_start.is_some() {
                                return Err(Error::MultipleWrappers);
                            }
                            wrapper_start = Some(start_idx);
                            // Calculate end index in bytes
                            if j < chars.len() {
                                wrapper_end = Some(chars[j].0);
                            } else {
                                wrapper_end = Some(text.len());
                            }
                            
                            decoded_bytes = current_bytes[HEADER_SIZE..HEADER_SIZE + len].to_vec();
                            
                            // We found one, but spec says we must ensure no others exist.
                            // Continue searching from j
                            i = j;
                            continue;
                        }
                    }
                }
            }
        }
        i += 1;
    }

    if let (Some(start), Some(end)) = (wrapper_start, wrapper_end) {
        let pre = &text[..start];
        let post = &text[end..];
        let clean: String = format!("{}{}", pre, post).nfc().collect();
        Ok(ExtractionResult {
            manifest: Some(decoded_bytes),
            clean_text: clean,
            offset: Some(start),
            length: Some(end - start),
        })
    } else {
        Ok(ExtractionResult {
            manifest: None,
            clean_text: text.nfc().collect(),
            offset: None,
            length: None,
        })
    }
}
