// TEAM_156: Server-side PDF text extraction for EncypherSignedText metadata stream.
// This runs in Node.js (Next.js API route) — no browser caching or SWC escaping issues.
// Falls back to returning null if the stream is not found (caller should use
// the client-side pdfjs-dist extraction as fallback).

import zlib from 'zlib';

/**
 * Extract the original signed text from the EncypherSignedText metadata stream
 * embedded in the PDF catalog by encypher-pdf.
 *
 * Returns null if the stream is not present (non-encypher PDF).
 */
export function extractEncypherSignedTextFromPdf(pdfBytes: Buffer): string | null {
  const marker = Buffer.from('EncypherSignedText');
  const markerIdx = pdfBytes.indexOf(marker);
  if (markerIdx === -1) {
    return null;
  }

  // Parse the indirect reference: "/EncypherSignedText N 0 R"
  const afterMarker = markerIdx + marker.length;
  const refRegion = pdfBytes.subarray(afterMarker, afterMarker + 30).toString('latin1');
  const refMatch = refRegion.match(/\s+(\d+)\s+0\s+R/);
  if (!refMatch) {
    console.warn('[pdfTextExtractorServer] Could not parse obj ref from:', refRegion);
    return null;
  }
  const objNum = parseInt(refMatch[1], 10);

  // Find "N 0 obj"
  const objMarker = Buffer.from(`${objNum} 0 obj`);
  const objIdx = pdfBytes.indexOf(objMarker);
  if (objIdx === -1) {
    console.warn('[pdfTextExtractorServer] Could not find obj', objNum);
    return null;
  }

  // Find "stream\n" after the object header
  const streamMarker = Buffer.from('stream\n');
  const streamIdx = pdfBytes.indexOf(streamMarker, objIdx);
  if (streamIdx === -1) {
    console.warn('[pdfTextExtractorServer] Could not find stream marker after obj', objNum);
    return null;
  }
  const dataStart = streamIdx + streamMarker.length;

  // Find "endstream"
  const endMarker = Buffer.from('endstream');
  let endIdx = pdfBytes.indexOf(endMarker, dataStart);
  if (endIdx === -1) {
    console.warn('[pdfTextExtractorServer] Could not find endstream');
    return null;
  }
  // Strip trailing newline before endstream (PDF spec: stream data ends before EOL before endstream)
  if (endIdx > 0 && pdfBytes[endIdx - 1] === 0x0A) endIdx--;
  if (endIdx > 0 && pdfBytes[endIdx - 1] === 0x0D) endIdx--;

  const streamData = pdfBytes.subarray(dataStart, endIdx);

  // Check if the stream is compressed (has /FlateDecode filter)
  const dictRegion = pdfBytes.subarray(objIdx, streamIdx).toString('latin1');
  const isCompressed = dictRegion.includes('FlateDecode');

  let textBytes: Buffer;
  if (isCompressed) {
    try {
      textBytes = zlib.inflateSync(streamData);
    } catch {
      console.warn('[pdfTextExtractorServer] zlib inflate failed');
      return null;
    }
  } else {
    textBytes = Buffer.from(streamData);
  }

  const text = textBytes.toString('utf-8');
  console.info(
    `[pdfTextExtractorServer] Extracted EncypherSignedText: ${text.length} chars, ` +
      `${textBytes.length} UTF-8 bytes, compressed: ${isCompressed}`,
  );
  return text;
}
