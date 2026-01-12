/**
 * C2PA Manifest Structural Validator.
 *
 * Provides validation utilities to help developers ensure their C2PA manifests
 * are structurally compliant before embedding them into text.
 */

// JUMBF Constants (ISO/IEC 19566-5)
const JUMBF_SUPERBOX_TYPE = new Uint8Array([0x6a, 0x75, 0x6d, 0x62]); // "jumb"
const JUMBF_DESC_TYPE = new Uint8Array([0x6a, 0x75, 0x6d, 0x64]); // "jumd"
const C2PA_MANIFEST_STORE_UUID = new Uint8Array([
  0x63, 0x32, 0x70, 0x61, 0x00, 0x11, 0x00, 0x10,
  0x80, 0x00, 0x00, 0xaa, 0x00, 0x38, 0x9b, 0x71,
]);

// Import constants from main module
const MAGIC = new Uint8Array([0x43, 0x32, 0x50, 0x41, 0x54, 0x58, 0x54, 0x00]);
const VERSION = 1;
const HEADER_SIZE = 13;

/**
 * C2PA-compliant validation status codes for text manifests.
 */
export enum ValidationCode {
  // Success
  Valid = "valid",

  // Wrapper-level failures (from C2PA Text spec)
  CorruptedWrapper = "manifest.text.corruptedWrapper",
  MultipleWrappers = "manifest.text.multipleWrappers",

  // Extended validation codes
  InvalidMagic = "manifest.text.invalidMagic",
  UnsupportedVersion = "manifest.text.unsupportedVersion",
  LengthMismatch = "manifest.text.lengthMismatch",
  EmptyManifest = "manifest.text.emptyManifest",

  // JUMBF-level failures
  InvalidJumbfHeader = "manifest.jumbf.invalidHeader",
  InvalidJumbfBoxSize = "manifest.jumbf.invalidBoxSize",
  MissingDescriptionBox = "manifest.jumbf.missingDescriptionBox",
  InvalidC2paUuid = "manifest.jumbf.invalidC2paUuid",
  TruncatedJumbf = "manifest.jumbf.truncated",
}

/**
 * A single validation issue with location and details.
 */
export interface ValidationIssue {
  code: ValidationCode;
  message: string;
  offset?: number;
  context?: string;
}

/**
 * Result of manifest validation with detailed diagnostics.
 */
export interface ValidationResult {
  valid: boolean;
  issues: ValidationIssue[];
  manifestBytes?: Uint8Array;
  jumbfBytes?: Uint8Array;
  version?: number;
  declaredLength?: number;
  actualLength?: number;
}

function arraysEqual(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}

function bytesToString(bytes: Uint8Array): string {
  return Array.from(bytes)
    .map((b) => String.fromCharCode(b))
    .join("");
}

/**
 * Validate basic JUMBF box structure.
 */
export function validateJumbfStructure(
  jumbfBytes: Uint8Array,
  strict: boolean = false
): ValidationResult {
  const result: ValidationResult = {
    valid: true,
    issues: [],
    jumbfBytes,
  };

  const addIssue = (
    code: ValidationCode,
    message: string,
    offset?: number,
    context?: string
  ) => {
    result.issues.push({ code, message, offset, context });
    result.valid = false;
  };

  if (jumbfBytes.length === 0) {
    addIssue(ValidationCode.EmptyManifest, "JUMBF content is empty", 0);
    return result;
  }

  // Minimum JUMBF box: 8 bytes header (size + type)
  if (jumbfBytes.length < 8) {
    addIssue(
      ValidationCode.InvalidJumbfHeader,
      `JUMBF too short for box header: ${jumbfBytes.length} bytes, minimum 8`,
      0
    );
    return result;
  }

  // Parse first box header (Big Endian)
  const boxSize =
    (jumbfBytes[0] << 24) |
    (jumbfBytes[1] << 16) |
    (jumbfBytes[2] << 8) |
    jumbfBytes[3];
  const boxType = jumbfBytes.slice(4, 8);

  let effectiveSize: number;
  let headerSize: number;

  if (boxSize === 0) {
    // Size 0 means "extends to end of file"
    effectiveSize = jumbfBytes.length;
    headerSize = 8;
  } else if (boxSize === 1) {
    // Extended size (64-bit)
    if (jumbfBytes.length < 16) {
      addIssue(
        ValidationCode.TruncatedJumbf,
        "Extended box size declared but not enough bytes for 64-bit size field",
        0
      );
      return result;
    }
    // Read 64-bit size (simplified - read as two 32-bit values)
    const highBits =
      (jumbfBytes[8] << 24) |
      (jumbfBytes[9] << 16) |
      (jumbfBytes[10] << 8) |
      jumbfBytes[11];
    const lowBits =
      (jumbfBytes[12] << 24) |
      (jumbfBytes[13] << 16) |
      (jumbfBytes[14] << 8) |
      jumbfBytes[15];
    // For practical purposes, if highBits > 0, the file is > 4GB which is unlikely
    effectiveSize = highBits > 0 ? Number.MAX_SAFE_INTEGER : lowBits;
    headerSize = 16;
  } else if (boxSize < 8) {
    addIssue(
      ValidationCode.InvalidJumbfBoxSize,
      `Invalid box size: ${boxSize} (minimum is 8)`,
      0
    );
    return result;
  } else {
    effectiveSize = boxSize;
    headerSize = 8;
  }

  // Check if we have enough bytes
  if (jumbfBytes.length < effectiveSize) {
    addIssue(
      ValidationCode.TruncatedJumbf,
      `JUMBF truncated: declared size ${effectiveSize}, actual ${jumbfBytes.length}`,
      0
    );
    return result;
  }

  // Check for JUMBF superbox type
  if (!arraysEqual(boxType, JUMBF_SUPERBOX_TYPE)) {
    addIssue(
      ValidationCode.InvalidJumbfHeader,
      `Expected JUMBF superbox type 'jumb', got '${bytesToString(boxType)}'`,
      4,
      `box_type=${Array.from(boxType).map((b) => b.toString(16).padStart(2, "0")).join("")}`
    );
    return result;
  }

  if (strict) {
    // Check for description box (jumd)
    if (jumbfBytes.length < headerSize + 8) {
      addIssue(
        ValidationCode.MissingDescriptionBox,
        "JUMBF superbox too short to contain description box",
        headerSize
      );
      return result;
    }

    const descType = jumbfBytes.slice(headerSize + 4, headerSize + 8);
    if (!arraysEqual(descType, JUMBF_DESC_TYPE)) {
      addIssue(
        ValidationCode.MissingDescriptionBox,
        `Expected description box 'jumd', got '${bytesToString(descType)}'`,
        headerSize + 4
      );
      return result;
    }

    // Check for C2PA UUID
    const uuidOffset = headerSize + 8;
    if (jumbfBytes.length >= uuidOffset + 16) {
      const foundUuid = jumbfBytes.slice(uuidOffset, uuidOffset + 16);
      if (!arraysEqual(foundUuid, C2PA_MANIFEST_STORE_UUID)) {
        addIssue(
          ValidationCode.InvalidC2paUuid,
          "Invalid C2PA manifest store UUID",
          uuidOffset,
          `expected=${Array.from(C2PA_MANIFEST_STORE_UUID).map((b) => b.toString(16).padStart(2, "0")).join("")}, found=${Array.from(foundUuid).map((b) => b.toString(16).padStart(2, "0")).join("")}`
        );
      }
    }
  }

  return result;
}

/**
 * Validate a C2PA manifest before embedding.
 *
 * This is the main validation entry point.
 */
export function validateManifest(
  manifestBytes: Uint8Array,
  validateJumbf: boolean = true,
  strict: boolean = false
): ValidationResult {
  const result: ValidationResult = {
    valid: true,
    issues: [],
    manifestBytes,
  };

  const addIssue = (
    code: ValidationCode,
    message: string,
    offset?: number,
    context?: string
  ) => {
    result.issues.push({ code, message, offset, context });
    result.valid = false;
  };

  if (manifestBytes.length === 0) {
    addIssue(ValidationCode.EmptyManifest, "Manifest bytes are empty");
    return result;
  }

  result.actualLength = manifestBytes.length;

  if (validateJumbf) {
    const jumbfResult = validateJumbfStructure(manifestBytes, strict);
    if (!jumbfResult.valid) {
      result.issues.push(...jumbfResult.issues);
      result.valid = false;
    }
  }

  return result;
}

/**
 * Validate a pre-encoded C2PATextManifestWrapper.
 */
export function validateWrapperBytes(wrapperBytes: Uint8Array): ValidationResult {
  const result: ValidationResult = {
    valid: true,
    issues: [],
  };

  const addIssue = (
    code: ValidationCode,
    message: string,
    offset?: number,
    context?: string
  ) => {
    result.issues.push({ code, message, offset, context });
    result.valid = false;
  };

  if (wrapperBytes.length < HEADER_SIZE) {
    addIssue(
      ValidationCode.CorruptedWrapper,
      `Wrapper too short: ${wrapperBytes.length} bytes, minimum ${HEADER_SIZE}`,
      0
    );
    return result;
  }

  // Check magic
  const magic = wrapperBytes.slice(0, 8);
  if (!arraysEqual(magic, MAGIC)) {
    addIssue(
      ValidationCode.InvalidMagic,
      `Invalid magic: expected 'C2PATXT\\0', got '${bytesToString(magic)}'`,
      0
    );
    return result;
  }

  // Check version
  const version = wrapperBytes[8];
  result.version = version;
  if (version !== VERSION) {
    addIssue(
      ValidationCode.UnsupportedVersion,
      `Unsupported version: ${version}, expected ${VERSION}`,
      8
    );
    return result;
  }

  // Check length
  const declaredLength =
    (wrapperBytes[9] << 24) |
    (wrapperBytes[10] << 16) |
    (wrapperBytes[11] << 8) |
    wrapperBytes[12];
  result.declaredLength = declaredLength;

  const actualJumbfLength = wrapperBytes.length - HEADER_SIZE;
  result.actualLength = actualJumbfLength;

  if (declaredLength !== actualJumbfLength) {
    addIssue(
      ValidationCode.LengthMismatch,
      `Length mismatch: declares ${declaredLength} bytes, actual ${actualJumbfLength}`,
      9
    );
    return result;
  }

  // Validate JUMBF
  const jumbfBytes = wrapperBytes.slice(HEADER_SIZE);
  result.jumbfBytes = jumbfBytes;
  result.manifestBytes = jumbfBytes;

  const jumbfResult = validateJumbfStructure(jumbfBytes, false);
  if (!jumbfResult.valid) {
    result.issues.push(...jumbfResult.issues);
    result.valid = false;
  }

  return result;
}
