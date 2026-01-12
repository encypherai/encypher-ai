package c2pa_text

import (
	"encoding/binary"
	"fmt"
)

// JUMBF Constants (ISO/IEC 19566-5)
var (
	JumbfSuperboxType      = []byte("jumb")
	JumbfDescType          = []byte("jumd")
	C2PAManifestStoreUUID  = []byte{
		0x63, 0x32, 0x70, 0x61, 0x00, 0x11, 0x00, 0x10,
		0x80, 0x00, 0x00, 0xAA, 0x00, 0x38, 0x9B, 0x71,
	}
)

// ValidationCode represents C2PA-compliant validation status codes.
type ValidationCode string

const (
	// Success
	ValidationCodeValid ValidationCode = "valid"

	// Wrapper-level failures (from C2PA Text spec)
	ValidationCodeCorruptedWrapper ValidationCode = "manifest.text.corruptedWrapper"
	ValidationCodeMultipleWrappers ValidationCode = "manifest.text.multipleWrappers"

	// Extended validation codes
	ValidationCodeInvalidMagic       ValidationCode = "manifest.text.invalidMagic"
	ValidationCodeUnsupportedVersion ValidationCode = "manifest.text.unsupportedVersion"
	ValidationCodeLengthMismatch     ValidationCode = "manifest.text.lengthMismatch"
	ValidationCodeEmptyManifest      ValidationCode = "manifest.text.emptyManifest"

	// JUMBF-level failures
	ValidationCodeInvalidJumbfHeader    ValidationCode = "manifest.jumbf.invalidHeader"
	ValidationCodeInvalidJumbfBoxSize   ValidationCode = "manifest.jumbf.invalidBoxSize"
	ValidationCodeMissingDescriptionBox ValidationCode = "manifest.jumbf.missingDescriptionBox"
	ValidationCodeInvalidC2paUuid       ValidationCode = "manifest.jumbf.invalidC2paUuid"
	ValidationCodeTruncatedJumbf        ValidationCode = "manifest.jumbf.truncated"
)

// ValidationIssue represents a single validation issue.
type ValidationIssue struct {
	Code    ValidationCode
	Message string
	Offset  int
	Context string
}

func (i ValidationIssue) String() string {
	return fmt.Sprintf("[%s] %s", i.Code, i.Message)
}

// ValidationResult contains the result of manifest validation.
type ValidationResult struct {
	Valid          bool
	Issues         []ValidationIssue
	ManifestBytes  []byte
	JumbfBytes     []byte
	Version        int
	DeclaredLength uint32
	ActualLength   int
}

// NewValidationResult creates a new valid result.
func NewValidationResult() *ValidationResult {
	return &ValidationResult{
		Valid:  true,
		Issues: make([]ValidationIssue, 0),
	}
}

// AddIssue adds a validation issue and marks the result as invalid.
func (r *ValidationResult) AddIssue(code ValidationCode, message string, offset int, context string) {
	r.Issues = append(r.Issues, ValidationIssue{
		Code:    code,
		Message: message,
		Offset:  offset,
		Context: context,
	})
	r.Valid = false
}

// PrimaryCode returns the most severe validation code.
func (r *ValidationResult) PrimaryCode() ValidationCode {
	if len(r.Issues) == 0 {
		return ValidationCodeValid
	}
	return r.Issues[0].Code
}

func (r *ValidationResult) String() string {
	if r.Valid {
		return "Validation passed: manifest is structurally compliant"
	}
	result := "Validation failed:\n"
	for _, issue := range r.Issues {
		result += fmt.Sprintf("  - %s\n", issue.String())
	}
	return result
}

func bytesEqual(a, b []byte) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

// ValidateJumbfStructure validates basic JUMBF box structure.
func ValidateJumbfStructure(jumbfBytes []byte, strict bool) *ValidationResult {
	result := NewValidationResult()
	result.JumbfBytes = jumbfBytes

	if len(jumbfBytes) == 0 {
		result.AddIssue(ValidationCodeEmptyManifest, "JUMBF content is empty", 0, "")
		return result
	}

	// Minimum JUMBF box: 8 bytes header (size + type)
	if len(jumbfBytes) < 8 {
		result.AddIssue(
			ValidationCodeInvalidJumbfHeader,
			fmt.Sprintf("JUMBF too short for box header: %d bytes, minimum 8", len(jumbfBytes)),
			0, "",
		)
		return result
	}

	// Parse first box header (Big Endian)
	boxSize := binary.BigEndian.Uint32(jumbfBytes[0:4])
	boxType := jumbfBytes[4:8]

	var effectiveSize int
	var headerSize int

	if boxSize == 0 {
		// Size 0 means "extends to end of file"
		effectiveSize = len(jumbfBytes)
		headerSize = 8
	} else if boxSize == 1 {
		// Extended size (64-bit)
		if len(jumbfBytes) < 16 {
			result.AddIssue(
				ValidationCodeTruncatedJumbf,
				"Extended box size declared but not enough bytes for 64-bit size field",
				0, "",
			)
			return result
		}
		effectiveSize = int(binary.BigEndian.Uint64(jumbfBytes[8:16]))
		headerSize = 16
	} else if boxSize < 8 {
		result.AddIssue(
			ValidationCodeInvalidJumbfBoxSize,
			fmt.Sprintf("Invalid box size: %d (minimum is 8)", boxSize),
			0, "",
		)
		return result
	} else {
		effectiveSize = int(boxSize)
		headerSize = 8
	}

	// Check if we have enough bytes
	if len(jumbfBytes) < effectiveSize {
		result.AddIssue(
			ValidationCodeTruncatedJumbf,
			fmt.Sprintf("JUMBF truncated: declared size %d, actual %d", effectiveSize, len(jumbfBytes)),
			0, "",
		)
		return result
	}

	// Check for JUMBF superbox type
	if !bytesEqual(boxType, JumbfSuperboxType) {
		result.AddIssue(
			ValidationCodeInvalidJumbfHeader,
			fmt.Sprintf("Expected JUMBF superbox type 'jumb', got '%s'", string(boxType)),
			4,
			fmt.Sprintf("box_type=%x", boxType),
		)
		return result
	}

	if strict {
		// Check for description box (jumd)
		if len(jumbfBytes) < headerSize+8 {
			result.AddIssue(
				ValidationCodeMissingDescriptionBox,
				"JUMBF superbox too short to contain description box",
				headerSize, "",
			)
			return result
		}

		descType := jumbfBytes[headerSize+4 : headerSize+8]
		if !bytesEqual(descType, JumbfDescType) {
			result.AddIssue(
				ValidationCodeMissingDescriptionBox,
				fmt.Sprintf("Expected description box 'jumd', got '%s'", string(descType)),
				headerSize+4, "",
			)
			return result
		}

		// Check for C2PA UUID
		uuidOffset := headerSize + 8
		if len(jumbfBytes) >= uuidOffset+16 {
			foundUuid := jumbfBytes[uuidOffset : uuidOffset+16]
			if !bytesEqual(foundUuid, C2PAManifestStoreUUID) {
				result.AddIssue(
					ValidationCodeInvalidC2paUuid,
					"Invalid C2PA manifest store UUID",
					uuidOffset,
					fmt.Sprintf("expected=%x, found=%x", C2PAManifestStoreUUID, foundUuid),
				)
			}
		}
	}

	return result
}

// ValidateManifest validates a C2PA manifest before embedding.
func ValidateManifest(manifestBytes []byte, validateJumbf bool, strict bool) *ValidationResult {
	result := NewValidationResult()
	result.ManifestBytes = manifestBytes

	if len(manifestBytes) == 0 {
		result.AddIssue(ValidationCodeEmptyManifest, "Manifest bytes are empty", -1, "")
		return result
	}

	result.ActualLength = len(manifestBytes)

	if validateJumbf {
		jumbfResult := ValidateJumbfStructure(manifestBytes, strict)
		if !jumbfResult.Valid {
			result.Issues = append(result.Issues, jumbfResult.Issues...)
			result.Valid = false
		}
	}

	return result
}

// ValidateWrapperBytes validates a pre-encoded C2PATextManifestWrapper.
func ValidateWrapperBytes(wrapperBytes []byte) *ValidationResult {
	result := NewValidationResult()

	if len(wrapperBytes) < HeaderSize {
		result.AddIssue(
			ValidationCodeCorruptedWrapper,
			fmt.Sprintf("Wrapper too short: %d bytes, minimum %d", len(wrapperBytes), HeaderSize),
			0, "",
		)
		return result
	}

	// Check magic
	magic := wrapperBytes[0:8]
	if !bytesEqual(magic, Magic) {
		result.AddIssue(
			ValidationCodeInvalidMagic,
			fmt.Sprintf("Invalid magic: expected 'C2PATXT\\0', got '%s'", string(magic)),
			0, "",
		)
		return result
	}

	// Check version
	version := int(wrapperBytes[8])
	result.Version = version
	if version != Version {
		result.AddIssue(
			ValidationCodeUnsupportedVersion,
			fmt.Sprintf("Unsupported version: %d, expected %d", version, Version),
			8, "",
		)
		return result
	}

	// Check length
	declaredLength := binary.BigEndian.Uint32(wrapperBytes[9:13])
	result.DeclaredLength = declaredLength

	actualJumbfLength := len(wrapperBytes) - HeaderSize
	result.ActualLength = actualJumbfLength

	if int(declaredLength) != actualJumbfLength {
		result.AddIssue(
			ValidationCodeLengthMismatch,
			fmt.Sprintf("Length mismatch: declares %d bytes, actual %d", declaredLength, actualJumbfLength),
			9, "",
		)
		return result
	}

	// Validate JUMBF
	jumbfBytes := wrapperBytes[HeaderSize:]
	result.JumbfBytes = jumbfBytes
	result.ManifestBytes = jumbfBytes

	jumbfResult := ValidateJumbfStructure(jumbfBytes, false)
	if !jumbfResult.Valid {
		result.Issues = append(result.Issues, jumbfResult.Issues...)
		result.Valid = false
	}

	return result
}
