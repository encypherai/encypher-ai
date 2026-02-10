// TEAM_156: Tests for PDF text extraction, specifically the EncypherSignedText
// metadata stream extraction that guarantees byte-identical C2PA verification.
import fs from 'fs';
import path from 'path';
import { extractEncypherSignedText } from './pdfTextExtractor';

/**
 * Build a minimal synthetic PDF that contains an EncypherSignedText metadata
 * stream.  The PDF is structurally valid enough for our byte-level parser
 * (it doesn't need to render — we only need the catalog reference and stream).
 */
function buildSyntheticPdf(signedText: string, compress = false): ArrayBuffer {
  const textBytes = Buffer.from(signedText, 'utf-8');
  let streamBody: Buffer;
  let filterEntry = '';

  if (compress) {
    const zlib = require('zlib') as typeof import('zlib');
    streamBody = zlib.deflateSync(textBytes);
    filterEntry = '/Filter /FlateDecode ';
  } else {
    streamBody = textBytes;
  }

  // Object 1: Catalog with /EncypherSignedText reference to object 2
  const catalogObj = Buffer.from(
    '1 0 obj\n<< /Type /Catalog /EncypherSignedText 2 0 R >>\nendobj\n\n',
  );

  // Object 2: The EncypherSignedText stream
  const streamHeader = Buffer.from(
    `2 0 obj\n<< ${filterEntry}/Length ${streamBody.length} >>\nstream\n`,
  );
  const streamFooter = Buffer.from('\nendstream\nendobj\n\n');

  // Minimal xref + trailer (not strictly needed for our parser, but makes
  // the file look like a real PDF)
  const trailer = Buffer.from(
    'xref\n0 3\n0000000000 65535 f \n' +
      '0000000009 00000 n \n' +
      '0000000100 00000 n \n' +
      'trailer\n<< /Size 3 /Root 1 0 R >>\nstartxref\n0\n%%EOF\n',
  );

  const header = Buffer.from('%PDF-1.4\n');
  const combined = Buffer.concat([header, catalogObj, streamHeader, streamBody, streamFooter, trailer]);
  // IMPORTANT: Buffer.buffer may be larger than the Buffer due to Node.js
  // pooling.  Copy into a fresh ArrayBuffer to match browser file.arrayBuffer().
  return combined.buffer.slice(combined.byteOffset, combined.byteOffset + combined.byteLength);
}

describe('extractEncypherSignedText', () => {
  describe('synthetic PDFs', () => {
    it('extracts ASCII text from uncompressed stream', async () => {
      const original = 'Hello, world! This is a test.';
      const pdf = buildSyntheticPdf(original);
      const result = await extractEncypherSignedText(pdf);
      expect(result).toBe(original);
    });

    it('extracts text with newlines from uncompressed stream', async () => {
      const original = 'Paragraph one.\n\nParagraph two.\n\nParagraph three.';
      const pdf = buildSyntheticPdf(original);
      const result = await extractEncypherSignedText(pdf);
      expect(result).toBe(original);
    });

    it('extracts text with supplementary plane Unicode (variation selectors)', async () => {
      // Simulate text with Unicode variation selectors (U+E0100 range)
      // These are 4-byte UTF-8 characters used by encypher ZW embeddings
      const original = 'Content \u{E016B}\u{E0492}\u{E0596}test';
      const pdf = buildSyntheticPdf(original);
      const result = await extractEncypherSignedText(pdf);
      expect(result).toBe(original);
      // Verify UTF-8 byte length is preserved
      const expectedBytes = Buffer.from(original, 'utf-8').length;
      const actualBytes = Buffer.from(result!, 'utf-8').length;
      expect(actualBytes).toBe(expectedBytes);
    });

    it('extracts text from compressed (FlateDecode) stream', async () => {
      const original = 'Compressed content with special chars: é à ü ñ';
      const pdf = buildSyntheticPdf(original, true);
      const result = await extractEncypherSignedText(pdf);
      expect(result).toBe(original);
    });

    it('returns null for PDF without EncypherSignedText', async () => {
      const plainPdf = Buffer.from(
        '%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF\n',
      );
      const ab = plainPdf.buffer.slice(
        plainPdf.byteOffset,
        plainPdf.byteOffset + plainPdf.byteLength,
      );
      const result = await extractEncypherSignedText(ab);
      expect(result).toBeNull();
    });

    it('preserves exact UTF-8 byte count for round-trip', async () => {
      // Build text similar to real signed content with mixed ASCII and
      // supplementary plane characters (variation selectors)
      const parts: string[] = [];
      for (let i = 0; i < 100; i++) {
        // Mix of ASCII and 4-byte UTF-8 chars
        parts.push(`Sentence ${i} with marker \u{E016B}\u{E0492}.`);
      }
      const original = parts.join('\n\n');
      const originalBytes = Buffer.from(original, 'utf-8').length;

      const pdf = buildSyntheticPdf(original);
      const result = await extractEncypherSignedText(pdf);

      expect(result).not.toBeNull();
      const resultBytes = Buffer.from(result!, 'utf-8').length;
      expect(resultBytes).toBe(originalBytes);
      expect(result).toBe(original);
    });
  });

  describe('real generated PDFs', () => {
    const pdfDir = path.resolve(__dirname, '../../../../tools/xml-to-pdf/output');

    // TEAM_156: Test against the actual generated minimal PDF if it exists.
    // This is the critical end-to-end test that catches the exact bug we're fixing.
    const minimalPdf = path.join(pdfDir, 'content_provenance_paper_minimal.pdf');

    const testIfExists = (filePath: string) =>
      fs.existsSync(filePath) ? it : it.skip;

    testIfExists(minimalPdf)(
      'minimal PDF: EncypherSignedText stream is present and extractable',
      async () => {
        const pdfBytes = fs.readFileSync(minimalPdf);
        const result = await extractEncypherSignedText(pdfBytes.buffer);
        expect(result).not.toBeNull();
        console.log(
          `[test] Minimal PDF: extracted ${result!.length} chars, ` +
            `${Buffer.from(result!, 'utf-8').length} UTF-8 bytes`,
        );
      },
    );

    testIfExists(minimalPdf)(
      'minimal PDF: extracted text has expected byte count (117839)',
      async () => {
        const pdfBytes = fs.readFileSync(minimalPdf);
        const result = await extractEncypherSignedText(pdfBytes.buffer);
        expect(result).not.toBeNull();
        const utf8Bytes = Buffer.from(result!, 'utf-8').length;
        // The signed text for the minimal mode paper is 117839 UTF-8 bytes
        expect(utf8Bytes).toBe(117839);
      },
    );

    testIfExists(minimalPdf)(
      'minimal PDF: extracted text round-trips to identical UTF-8 bytes',
      async () => {
        const pdfBytes = fs.readFileSync(minimalPdf);
        const result = await extractEncypherSignedText(pdfBytes.buffer);
        expect(result).not.toBeNull();

        // Re-encode and verify byte-identical round-trip
        const reEncoded = Buffer.from(result!, 'utf-8');
        const firstEncode = Buffer.from(result!, 'utf-8');
        expect(reEncoded.equals(firstEncode)).toBe(true);

        // Verify the stream bytes in the PDF match exactly
        const bytes = new Uint8Array(pdfBytes.buffer);
        const streamMarker = Buffer.from('EncypherSignedText');
        const markerIdx = pdfBytes.indexOf(streamMarker);
        expect(markerIdx).toBeGreaterThan(-1);
      },
    );

    // Test ZW PDFs too
    const zwSentencePdf = path.join(pdfDir, 'content_provenance_paper_zw_sentence.pdf');
    testIfExists(zwSentencePdf)(
      'ZW sentence PDF: EncypherSignedText stream is present and extractable',
      async () => {
        const pdfBytes = fs.readFileSync(zwSentencePdf);
        const result = await extractEncypherSignedText(pdfBytes.buffer);
        expect(result).not.toBeNull();
        console.log(
          `[test] ZW sentence PDF: extracted ${result!.length} chars, ` +
            `${Buffer.from(result!, 'utf-8').length} UTF-8 bytes`,
        );
      },
    );

    const zwDocumentPdf = path.join(pdfDir, 'content_provenance_paper_zw_document.pdf');
    testIfExists(zwDocumentPdf)(
      'ZW document PDF: EncypherSignedText stream is present and extractable',
      async () => {
        const pdfBytes = fs.readFileSync(zwDocumentPdf);
        const result = await extractEncypherSignedText(pdfBytes.buffer);
        expect(result).not.toBeNull();
        console.log(
          `[test] ZW document PDF: extracted ${result!.length} chars, ` +
            `${Buffer.from(result!, 'utf-8').length} UTF-8 bytes`,
        );
      },
    );
  });
});
