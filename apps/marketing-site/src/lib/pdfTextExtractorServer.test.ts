// TEAM_156: Tests for server-side PDF text extraction (EncypherSignedText metadata stream).
import fs from 'fs';
import path from 'path';
import zlib from 'zlib';
import { extractEncypherSignedTextFromPdf } from './pdfTextExtractorServer';

function buildSyntheticPdf(signedText: string, compress = false): Buffer {
  const textBytes = Buffer.from(signedText, 'utf-8');
  let streamBody: Buffer;
  let filterEntry = '';

  if (compress) {
    streamBody = zlib.deflateSync(textBytes);
    filterEntry = '/Filter /FlateDecode ';
  } else {
    streamBody = textBytes;
  }

  const header = Buffer.from('%PDF-1.4\n');
  const catalog = Buffer.from(
    '1 0 obj\n<< /Type /Catalog /EncypherSignedText 2 0 R >>\nendobj\n\n',
  );
  const streamHeader = Buffer.from(
    `2 0 obj\n<< ${filterEntry}/Length ${streamBody.length} >>\nstream\n`,
  );
  const streamFooter = Buffer.from('\nendstream\nendobj\n\n');
  const trailer = Buffer.from(
    'xref\n0 3\ntrailer\n<< /Size 3 /Root 1 0 R >>\nstartxref\n0\n%%EOF\n',
  );

  return Buffer.concat([header, catalog, streamHeader, streamBody, streamFooter, trailer]);
}

describe('extractEncypherSignedTextFromPdf (server)', () => {
  describe('synthetic PDFs', () => {
    it('extracts ASCII text from uncompressed stream', () => {
      const original = 'Hello, world! This is a test.';
      const pdf = buildSyntheticPdf(original);
      expect(extractEncypherSignedTextFromPdf(pdf)).toBe(original);
    });

    it('extracts text with newlines from uncompressed stream', () => {
      const original = 'Paragraph one.\n\nParagraph two.\n\nParagraph three.';
      const pdf = buildSyntheticPdf(original);
      expect(extractEncypherSignedTextFromPdf(pdf)).toBe(original);
    });

    it('extracts text with supplementary plane Unicode', () => {
      const original = 'Content \u{E016B}\u{E0492}\u{E0596}test';
      const pdf = buildSyntheticPdf(original);
      const result = extractEncypherSignedTextFromPdf(pdf);
      expect(result).toBe(original);
      expect(Buffer.from(result!, 'utf-8').length).toBe(Buffer.from(original, 'utf-8').length);
    });

    it('extracts text from compressed (FlateDecode) stream', () => {
      const original = 'Compressed content with special chars: é à ü ñ';
      const pdf = buildSyntheticPdf(original, true);
      expect(extractEncypherSignedTextFromPdf(pdf)).toBe(original);
    });

    it('returns null for PDF without EncypherSignedText', () => {
      const plain = Buffer.from('%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF\n');
      expect(extractEncypherSignedTextFromPdf(plain)).toBeNull();
    });

    it('preserves exact UTF-8 byte count for round-trip', () => {
      const parts: string[] = [];
      for (let i = 0; i < 100; i++) {
        parts.push(`Sentence ${i} with marker \u{E016B}\u{E0492}.`);
      }
      const original = parts.join('\n\n');
      const pdf = buildSyntheticPdf(original);
      const result = extractEncypherSignedTextFromPdf(pdf);
      expect(result).toBe(original);
      expect(Buffer.from(result!, 'utf-8').length).toBe(Buffer.from(original, 'utf-8').length);
    });
  });

  describe('real generated PDFs', () => {
    const pdfDir = path.resolve(__dirname, '../../../../tools/xml-to-pdf/output');
    const testIfExists = (filePath: string) => fs.existsSync(filePath) ? it : it.skip;

    const minimalPdf = path.join(pdfDir, 'content_provenance_paper_minimal.pdf');

    testIfExists(minimalPdf)('minimal PDF: extracts 117839 UTF-8 bytes', () => {
      const pdf = fs.readFileSync(minimalPdf);
      const result = extractEncypherSignedTextFromPdf(pdf);
      expect(result).not.toBeNull();
      const utf8Bytes = Buffer.from(result!, 'utf-8').length;
      expect(utf8Bytes).toBe(117839);
    });

    const zwSentencePdf = path.join(pdfDir, 'content_provenance_paper_zw_sentence.pdf');
    testIfExists(zwSentencePdf)('ZW sentence PDF: extracts text', () => {
      const pdf = fs.readFileSync(zwSentencePdf);
      const result = extractEncypherSignedTextFromPdf(pdf);
      expect(result).not.toBeNull();
    });

    const zwDocumentPdf = path.join(pdfDir, 'content_provenance_paper_zw_document.pdf');
    testIfExists(zwDocumentPdf)('ZW document PDF: extracts text', () => {
      const pdf = fs.readFileSync(zwDocumentPdf);
      const result = extractEncypherSignedTextFromPdf(pdf);
      expect(result).not.toBeNull();
    });
  });
});
