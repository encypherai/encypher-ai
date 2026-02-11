// TEAM_154: Client-side PDF text extraction using pdfjs-dist loaded from CDN.
// pdfjs-dist v4 uses Promise.withResolvers (ES2024) which crashes Node SSR.
// We use /* webpackIgnore: true */ with a full CDN URL so webpack skips the import
// and the browser's native ESM loader fetches it directly at runtime.
//
// IMPORTANT: We use the operator list API (getOperatorList) instead of
// getTextContent() because pdfjs-dist's text extraction unconditionally
// strips Unicode "Format" characters (\p{Cf}) including ZWNJ (U+200C),
// ZWJ (U+200D), CGJ (U+034F), and MVS (U+180E). These characters are
// used by EncypherAI's ZW embedding for invisible provenance data and
// MUST be preserved for verification to work.

const PDFJS_CDN = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.8.69';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let cachedPdfjs: any = null;

async function loadPdfjs() {
  if (!cachedPdfjs) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    cachedPdfjs = await import(/* webpackIgnore: true */ `${PDFJS_CDN}/pdf.min.mjs`);
    cachedPdfjs.GlobalWorkerOptions.workerSrc = `${PDFJS_CDN}/pdf.worker.min.mjs`;
  }
  return cachedPdfjs;
}

export async function extractTextFromPdf(data: ArrayBuffer): Promise<string> {
  if (typeof window === 'undefined') {
    throw new Error('extractTextFromPdf can only be called in the browser');
  }

  // TEAM_156: First try to extract the signed text from the
  // EncypherSignedText metadata stream embedded by encypher-pdf.
  // This is a lossless copy of the original signed text and guarantees
  // byte-identical extraction for C2PA hash verification.
  // Falls back to operator-list extraction for non-encypher PDFs.
  const metadataText = await extractEncypherSignedText(data);
  if (metadataText !== null) {
    console.log('[pdfTextExtractor] Using EncypherSignedText metadata stream');
    return metadataText;
  }

  const pdfjsLib = await loadPdfjs();
  const pdf = await pdfjsLib.getDocument({ data }).promise;
  const OPS = pdfjsLib.OPS;

  // Fallback: concatenate all glyph unicodes from the PDF text stream.
  // encypher-pdf embeds \n as zero-width glyphs and preserves trailing
  // spaces at word-wrap boundaries, so simple concatenation reproduces
  // the original text for encypher-generated PDFs.  For third-party PDFs
  // this gives a best-effort extraction that preserves invisible chars.
  const allChars: string[] = [];

  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const opList = await page.getOperatorList();

    for (let j = 0; j < opList.fnArray.length; j++) {
      const fn = opList.fnArray[j];
      const args = opList.argsArray[j];

      // showText (Tj) and showSpacedText (TJ) — the only ops with glyphs
      if (fn !== OPS.showText && fn !== OPS.showSpacedText) {
        continue;
      }
      const items = args[0];
      if (!Array.isArray(items)) continue;

      for (const item of items) {
        if (item && typeof item === 'object' && 'unicode' in item) {
          allChars.push(item.unicode as string);
        }
      }
    }
  }

  return allChars.join('');
}

/**
 * TEAM_156: Extract the original signed text from the EncypherSignedText
 * metadata stream embedded in the PDF catalog by encypher-pdf.
 *
 * The stream is a FlateDecode-compressed UTF-8 blob stored as a custom
 * key on the PDF catalog object.  We parse the raw PDF bytes to find it
 * because pdfjs-dist does not expose arbitrary catalog entries.
 *
 * Returns null if the stream is not present (non-encypher PDF).
 */
export async function extractEncypherSignedText(data: ArrayBuffer): Promise<string | null> {
  try {
    const bytes = new Uint8Array(data);
    const marker = new TextEncoder().encode('EncypherSignedText');
    const markerIdx = findBytes(bytes, marker);
    if (markerIdx === -1) {
      console.log('[pdfTextExtractor] No EncypherSignedText marker found');
      return null;
    }
    console.log('[pdfTextExtractor] Found EncypherSignedText marker at byte', markerIdx);

    // Parse the indirect reference: "/EncypherSignedText N 0 R"
    const afterMarker = markerIdx + marker.length;
    const refRegion = new TextDecoder('latin1').decode(
      bytes.slice(afterMarker, afterMarker + 30),
    );
    const refMatch = refRegion.match(/\s+(\d+)\s+0\s+R/);
    if (!refMatch) {
      console.warn('[pdfTextExtractor] Could not parse obj ref from:', refRegion);
      return null;
    }
    const objNum = parseInt(refMatch[1], 10);
    console.log('[pdfTextExtractor] EncypherSignedText references obj', objNum);

    // Find "N 0 obj"
    const objMarker = new TextEncoder().encode(`${objNum} 0 obj`);
    const objIdx = findBytes(bytes, objMarker);
    if (objIdx === -1) {
      console.warn('[pdfTextExtractor] Could not find obj', objNum);
      return null;
    }

    // Find the stream data after the object header
    // NOTE: Cannot use TextEncoder('stream\n') because SWC double-escapes
    // the \n to \\n in compiled output. Use a byte array literal instead.
    const streamMarker = new Uint8Array([0x73, 0x74, 0x72, 0x65, 0x61, 0x6D, 0x0A]); // "stream" + LF
    const streamIdx = findBytes(bytes, streamMarker, objIdx);
    if (streamIdx === -1) {
      console.warn('[pdfTextExtractor] Could not find stream marker after obj', objNum);
      return null;
    }
    const dataStart = streamIdx + streamMarker.length;

    // Find endstream
    const endMarker = new TextEncoder().encode('endstream');
    let endIdx = findBytes(bytes, endMarker, dataStart);
    if (endIdx === -1) {
      console.warn('[pdfTextExtractor] Could not find endstream');
      return null;
    }
    // Strip trailing newline before endstream
    if (endIdx > 0 && bytes[endIdx - 1] === 0x0A) endIdx--;
    if (endIdx > 0 && bytes[endIdx - 1] === 0x0D) endIdx--;

    const streamData = bytes.slice(dataStart, endIdx);

    // Check if the stream is compressed (has /FlateDecode filter)
    // by inspecting the object dict between "obj" and "stream"
    const dictRegion = new TextDecoder('latin1').decode(
      bytes.slice(objIdx, streamIdx),
    );
    const isCompressed = dictRegion.includes('FlateDecode');
    console.log('[pdfTextExtractor] Stream:', streamData.length, 'bytes, compressed:', isCompressed);

    let textBytes: Uint8Array;
    if (isCompressed) {
      textBytes = await inflateZlib(streamData);
    } else {
      textBytes = streamData;
    }
    const text = new TextDecoder('utf-8').decode(textBytes);
    console.log('[pdfTextExtractor] EncypherSignedText:', text.length, 'chars');
    return text;
  } catch (e) {
    console.warn('[pdfTextExtractor] EncypherSignedText extraction failed:', e);
    return null;
  }
}

// TEAM_160: Render the first page of a PDF as a thumbnail data URL.
export async function renderPdfThumbnail(
  data: ArrayBuffer,
  maxWidth = 300,
): Promise<string> {
  if (typeof window === 'undefined') {
    throw new Error('renderPdfThumbnail can only be called in the browser');
  }
  const pdfjsLib = await loadPdfjs();
  const pdf = await pdfjsLib.getDocument({ data }).promise;
  const page = await pdf.getPage(1);
  const unscaledViewport = page.getViewport({ scale: 1 });
  const scale = maxWidth / unscaledViewport.width;
  const viewport = page.getViewport({ scale });

  const canvas = document.createElement('canvas');
  canvas.width = viewport.width;
  canvas.height = viewport.height;
  const ctx = canvas.getContext('2d')!;
  await page.render({ canvasContext: ctx, viewport }).promise;
  return canvas.toDataURL('image/png');
}

/** Decompress zlib (FlateDecode) data using the browser's DecompressionStream. */
async function inflateZlib(data: Uint8Array): Promise<Uint8Array> {
  const ds = new DecompressionStream('deflate');
  const writer = ds.writable.getWriter();
  writer.write(new Uint8Array(data) as unknown as ArrayBuffer);
  writer.close();
  const reader = ds.readable.getReader();
  const chunks: Uint8Array[] = [];
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }
  const totalLen = chunks.reduce((sum, c) => sum + c.length, 0);
  const result = new Uint8Array(totalLen);
  let offset = 0;
  for (const chunk of chunks) {
    result.set(chunk, offset);
    offset += chunk.length;
  }
  return result;
}

/** Find needle bytes in haystack starting from offset. Returns -1 if not found. */
function findBytes(haystack: Uint8Array, needle: Uint8Array, offset = 0): number {
  outer: for (let i = offset; i <= haystack.length - needle.length; i++) {
    for (let j = 0; j < needle.length; j++) {
      if (haystack[i + j] !== needle[j]) continue outer;
    }
    return i;
  }
  return -1;
}
