package c2pa_text

import (
	"bytes"
	"encoding/binary"
	"errors"

	"golang.org/x/text/unicode/norm"
)

// Constants
const (
	Version    = 1
	HeaderSize = 13 // 8 (Magic) + 1 (Version) + 4 (Length)
	ZWNBSP     = '\ufeff'

	VSStart    = 0xFE00
	VSEnd      = 0xFE0F
	VSSupStart = 0xE0100
	VSSupEnd   = 0xE01EF
)

var Magic = []byte("C2PATXT\x00")

// Errors
var (
	ErrInvalidByte        = errors.New("byte out of range 0-255")
	ErrInvalidVS          = errors.New("invalid variation selector")
	ErrMultipleWrappers   = errors.New("multiple C2PA wrappers detected")
	ErrInvalidMagic       = errors.New("invalid magic bytes")
	ErrUnsupportedVersion = errors.New("unsupported version")
	ErrTruncated          = errors.New("wrapper truncated")
)

func byteToVS(b byte) (rune, error) {
	if b <= 15 {
		return rune(VSStart + int(b)), nil
	} else if b >= 16 { // byte is uint8, so <= 255 implicit
		return rune(VSSupStart + int(b) - 16), nil
	}
	return 0, ErrInvalidByte
}

func vsToByte(r rune) (byte, bool) {
	if r >= VSStart && r <= VSEnd {
		return byte(r - VSStart), true
	}
	if r >= VSSupStart && r <= VSSupEnd {
		return byte(r - VSSupStart + 16), true
	}
	return 0, false
}

// EncodeWrapper encodes raw bytes into a C2PA Text Manifest Wrapper string.
func EncodeWrapper(manifestBytes []byte) string {
	var buf bytes.Buffer
	buf.WriteRune(ZWNBSP)

	// Header
	for _, b := range Magic {
		r, _ := byteToVS(b)
		buf.WriteRune(r)
	}

	rVersion, _ := byteToVS(byte(Version))
	buf.WriteRune(rVersion)

	length := uint32(len(manifestBytes))
	lengthBytes := make([]byte, 4)
	binary.BigEndian.PutUint32(lengthBytes, length)

	for _, b := range lengthBytes {
		r, _ := byteToVS(b)
		buf.WriteRune(r)
	}

	// Body
	for _, b := range manifestBytes {
		r, _ := byteToVS(b)
		buf.WriteRune(r)
	}

	return buf.String()
}

// WorstCaseWrapperByteLength computes the deterministic target UTF-8 byte
// length of a padded wrapper for a manifest of manifestByteCount bytes.
// Formula: 3 + (13 + M) * 4 + 6
func WorstCaseWrapperByteLength(manifestByteCount int) int {
	return 3 + (HeaderSize+manifestByteCount)*4 + 6
}

// computePadding returns padding byte values whose VS encoding totals
// exactly gap UTF-8 bytes. Bytes 0x00 encode to 3-byte VS, 0xFF to 4-byte VS.
func computePadding(gap int) ([]byte, error) {
	if gap == 0 {
		return nil, nil
	}
	for b := gap / 4; b >= 0; b-- {
		remainder := gap - 4*b
		if remainder >= 0 && remainder%3 == 0 {
			a := remainder / 3
			result := make([]byte, 0, a+b)
			for i := 0; i < a; i++ {
				result = append(result, 0x00)
			}
			for i := 0; i < b; i++ {
				result = append(result, 0xFF)
			}
			return result, nil
		}
	}
	return nil, errors.New("cannot compute padding for given gap")
}

// EncodeWrapperPadded encodes a C2PA Text Manifest Wrapper and pads to an
// exact UTF-8 byte length. Decoders use manifestLength to extract the
// manifest and ignore trailing padding bytes.
func EncodeWrapperPadded(manifestBytes []byte, targetByteLength int) (string, error) {
	base := EncodeWrapper(manifestBytes)
	actual := len(base) // Go strings are UTF-8 byte sequences
	if targetByteLength < actual {
		return "", ErrTruncated
	}
	gap := targetByteLength - actual
	if gap == 0 {
		return base, nil
	}
	padding, err := computePadding(gap)
	if err != nil {
		return "", err
	}
	var buf bytes.Buffer
	buf.WriteString(base)
	for _, b := range padding {
		r, _ := byteToVS(b)
		buf.WriteRune(r)
	}
	return buf.String(), nil
}

// EmbedManifest embeds a C2PA manifest into text.
// Normalizes text to NFC before embedding.
func EmbedManifest(text string, manifestBytes []byte) string {
	normalized := norm.NFC.String(text)
	wrapper := EncodeWrapper(manifestBytes)
	return normalized + wrapper
}

// ExtractManifest extracts a C2PA manifest from text.
// Returns manifest bytes, clean text, offset, length, and error.
// offset and length are byte indices/lengths relative to the original text.
func ExtractManifest(text string) ([]byte, string, int, int, error) {
	// We need to scan by rune
	runes := []rune(text)

	var wrapperStart, wrapperEnd int = -1, -1
	var decodedBytes []byte

	for i := 0; i < len(runes); i++ {
		if runes[i] == ZWNBSP {
			// Potential start
			startIdx := i
			var currentBytes []byte
			j := i + 1

			for j < len(runes) {
				b, ok := vsToByte(runes[j])
				if !ok {
					break
				}
				currentBytes = append(currentBytes, b)
				j++
			}

			// Check header
			if len(currentBytes) >= HeaderSize {
				// Check Magic
				validMagic := true
				for k := 0; k < 8; k++ {
					if currentBytes[k] != Magic[k] {
						validMagic = false
						break
					}
				}

				if validMagic {
					if currentBytes[8] == byte(Version) {
						length := binary.BigEndian.Uint32(currentBytes[9:13])

						if len(currentBytes) >= HeaderSize+int(length) {
							if wrapperStart != -1 {
								return nil, norm.NFC.String(text), -1, -1, ErrMultipleWrappers
							}

							wrapperStart = startIdx
							wrapperEnd = j // j is exclusive end in rune slice

							decodedBytes = currentBytes[HeaderSize : HeaderSize+int(length)]

							// Continue searching
							i = j - 1 // -1 because loop increments
							continue
						}
					}
				}
			}
		}
	}

	if wrapperStart != -1 {
		// Convert rune indices to byte indices
		preRunes := runes[:wrapperStart]
		wrapperRunes := runes[wrapperStart:wrapperEnd]

		startByte := len(string(preRunes))
		lengthByte := len(string(wrapperRunes))

		// Reconstruct string without wrapper
		pre := string(runes[:wrapperStart])
		post := string(runes[wrapperEnd:])
		clean := norm.NFC.String(pre + post)

		// Need to copy bytes to avoid reference issues
		outBytes := make([]byte, len(decodedBytes))
		copy(outBytes, decodedBytes)

		return outBytes, clean, startByte, lengthByte, nil
	}

	return nil, norm.NFC.String(text), -1, -1, nil
}
