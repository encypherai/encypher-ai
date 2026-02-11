// TEAM_152: Server-side payload size guard for API routes.
// Prevents oversized payloads from consuming server memory before
// being forwarded to upstream services.

import { NextRequest, NextResponse } from "next/server";

/** Maximum allowed request body size in bytes (2 MB, matching upstream limit). */
export const MAX_PAYLOAD_BYTES = 2 * 1024 * 1024;

/**
 * Read and parse a JSON request body, rejecting payloads that exceed
 * {@link MAX_PAYLOAD_BYTES}.
 *
 * Returns either the parsed body or an early `NextResponse` error that the
 * caller should return immediately.
 */
export async function parseJsonWithSizeLimit(
  request: NextRequest,
  opts: { requestId: string; logPrefix: string; maxBytes?: number },
): Promise<{ body: Record<string, unknown> } | { error: NextResponse }> {
  const maxBytes = opts.maxBytes ?? MAX_PAYLOAD_BYTES;

  // Content-Length is not always present (chunked encoding), but when it is
  // we can reject early without reading the body at all.
  const contentLength = request.headers.get("content-length");
  if (contentLength && parseInt(contentLength, 10) > maxBytes) {
    console.warn(`${opts.logPrefix} payload too large (content-length)`, {
      requestId: opts.requestId,
      contentLength,
      maxBytes,
    });
    return {
      error: NextResponse.json(
        {
          detail: `Request payload too large. Maximum size is ${(maxBytes / (1024 * 1024)).toFixed(0)} MB.`,
        },
        { status: 413 },
      ),
    };
  }

  // Read the raw body to enforce the byte limit even without Content-Length.
  const rawBody = await request.text();
  const bodyBytes = new TextEncoder().encode(rawBody).length;

  if (bodyBytes > maxBytes) {
    console.warn(`${opts.logPrefix} payload too large (body bytes)`, {
      requestId: opts.requestId,
      bodyBytes,
      maxBytes,
    });
    return {
      error: NextResponse.json(
        {
          detail: `Request payload too large (${(bodyBytes / (1024 * 1024)).toFixed(1)} MB). Maximum size is ${(maxBytes / (1024 * 1024)).toFixed(0)} MB.`,
        },
        { status: 413 },
      ),
    };
  }

  try {
    const body = JSON.parse(rawBody) as Record<string, unknown>;
    return { body };
  } catch {
    console.warn(`${opts.logPrefix} invalid JSON`, {
      requestId: opts.requestId,
      bodyBytes,
    });
    return {
      error: NextResponse.json(
        { detail: "Invalid JSON in request body." },
        { status: 400 },
      ),
    };
  }
}
