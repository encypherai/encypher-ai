import { NextRequest, NextResponse } from "next/server";

import { resolveEnterpriseApiUrl } from "@/lib/enterpriseApiUrl";
import { mapVerifyResponseToDecodeToolResponse } from "@/lib/enterpriseApiTools";
import { buildUpstreamTraceHeaders } from "@/lib/upstreamTraceHeaders";
import { parseJsonWithSizeLimit } from "@/lib/apiPayloadGuard";
import { extractEncypherSignedTextFromPdf } from "@/lib/pdfTextExtractorServer";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  const requestId = crypto.randomUUID();
  const logPrefix = "[tools-verify]";
  try {
    // TEAM_152: Enforce payload size limit before parsing
    // TEAM_156: Increased limit to 10 MB to accommodate base64-encoded PDF bytes
    const parsed = await parseJsonWithSizeLimit(request, { requestId, logPrefix, maxBytes: 10 * 1024 * 1024 });
    if ("error" in parsed) return parsed.error;
    const body = parsed.body;

    // Use ENTERPRISE_API_URL (api.encypherai.com) - Traefik routes /api/v1/verify to verification-service
    const apiUrl = resolveEnterpriseApiUrl();

    // TEAM_156: For PDF files, the browser sends raw PDF bytes as base64.
    // We extract the EncypherSignedText metadata stream server-side (Node.js)
    // to guarantee lossless extraction without browser caching issues.
    // Falls back to the browser-extracted text (encoded_text) if no PDF or
    // no EncypherSignedText stream found.
    let encodedText = typeof body?.encoded_text === "string" ? body.encoded_text : "";
    const pdfBase64 = typeof body?.pdf_base64 === "string" ? body.pdf_base64 : "";
    let extractionSource = "client";

    if (pdfBase64) {
      try {
        const pdfBuffer = Buffer.from(pdfBase64, "base64");
        const serverText = extractEncypherSignedTextFromPdf(pdfBuffer);
        if (serverText) {
          encodedText = serverText;
          extractionSource = "server_EncypherSignedText";
        } else {
          console.info(`${logPrefix} no EncypherSignedText in PDF, using client-extracted text`, { requestId });
        }
      } catch (e) {
        console.warn(`${logPrefix} server-side PDF extraction failed, using client text`, {
          requestId,
          error: e instanceof Error ? e.message : String(e),
        });
      }
    }

    if (!encodedText.trim()) {
      console.warn(`${logPrefix} invalid payload`, {
        requestId,
        hasText: Boolean(encodedText.trim()),
      });
      return NextResponse.json({ detail: "encoded_text is required" }, { status: 400 });
    }

    // Verification is a public endpoint - no API key required
    // Traefik routes /api/v1/verify to the verification-service
    console.info(`${logPrefix} forwarding request`, {
      requestId,
      upstreamHost: apiUrl,
      textLength: encodedText.length,
      extractionSource,
      utf8Bytes: Buffer.from(encodedText, "utf-8").length,
    });
    const upstream = await fetch(`${apiUrl}/api/v1/verify`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Request-Id": requestId,
      },
      body: JSON.stringify({ text: encodedText }),
    });

    const data = await upstream
      .json()
      .catch(() => ({
        success: false,
        data: null,
        error: { message: "Upstream returned invalid JSON" },
      }));

    const upstreamTraceHeaders = buildUpstreamTraceHeaders(upstream.headers, data);

    if (!upstream.ok) {
      console.error(`${logPrefix} upstream error`, {
        requestId,
        status: upstream.status,
        detail: data?.detail || data?.error?.message || data?.error,
      });
      const detail =
        (typeof data?.detail === "string" && data.detail) ||
        data?.detail?.message ||
        data?.error?.message ||
        `Request failed with status ${upstream.status}`;

      const nextAction = data?.error?.next_action;
      const response = NextResponse.json(
        { detail, ...(nextAction ? { next_action: nextAction } : {}) },
        { status: upstream.status }
      );
      Object.entries(upstreamTraceHeaders).forEach(([key, value]) => {
        response.headers.set(key, value);
      });
      return response;
    }

    console.info(`${logPrefix} upstream success`, {
      requestId,
      status: upstream.status,
      embeddingsFound: data?.data?.embeddings_found,
    });
    const response = NextResponse.json(mapVerifyResponseToDecodeToolResponse(data));
    Object.entries(upstreamTraceHeaders).forEach(([key, value]) => {
      response.headers.set(key, value);
    });
    return response;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    const cause = error instanceof Error && error.cause ? String(error.cause) : undefined;
    const stack = error instanceof Error ? error.stack : undefined;
    console.error(`${logPrefix} unexpected error`, {
      requestId,
      message,
      cause,
      stack,
      errorName: error instanceof Error ? error.name : typeof error,
    });
    return NextResponse.json({ detail: message, cause: cause || undefined }, { status: 500 });
  }
}
