package c2pa_text

import (
	"encoding/binary"
	"testing"

	"golang.org/x/text/unicode/norm"
)

func TestExtractManifestOffsetsAreNFCUtf8ByteOffsets(t *testing.T) {
	manifest := make([]byte, 8)
	binary.BigEndian.PutUint32(manifest[0:4], 8)
	copy(manifest[4:8], []byte("jumb"))

	decomposed := "e\u0301"
	embedded := EmbedManifest(decomposed, manifest)

	extracted, clean, offset, length, err := ExtractManifest(embedded)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}
	if extracted == nil {
		t.Fatalf("expected extracted bytes")
	}
	if string(extracted) != string(manifest) {
		t.Fatalf("extracted manifest mismatch")
	}

	normalized := norm.NFC.String(decomposed)
	expectedOffset := len([]byte(normalized))
	expectedLength := len([]byte(embedded)) - expectedOffset

	if clean != normalized {
		t.Fatalf("clean text mismatch: got %q expected %q", clean, normalized)
	}
	if offset != expectedOffset {
		t.Fatalf("offset mismatch: got %d expected %d", offset, expectedOffset)
	}
	if length != expectedLength {
		t.Fatalf("length mismatch: got %d expected %d", length, expectedLength)
	}
}

func TestExtractManifestMultipleWrappersErrors(t *testing.T) {
	manifest := make([]byte, 8)
	binary.BigEndian.PutUint32(manifest[0:4], 8)
	copy(manifest[4:8], []byte("jumb"))

	base := EmbedManifest("hello", manifest)
	double := base + EncodeWrapper(manifest)

	_, _, _, _, err := ExtractManifest(double)
	if err == nil {
		t.Fatalf("expected error")
	}
	if err != ErrMultipleWrappers {
		t.Fatalf("expected ErrMultipleWrappers, got %v", err)
	}
}
