import { NextRequest, NextResponse } from "next/server";

import { resolvePublicEnterpriseApiUrl } from "@/lib/enterpriseApiUrl";
import { mapVerifyResponseToDecodeToolResponse } from "@/lib/enterpriseApiTools";
import { buildUpstreamTraceHeaders } from "@/lib/upstreamTraceHeaders";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  const requestId = crypto.randomUUID();
  const logPrefix = "[tools-verify]";
  try {
    const body = await request.json();

    // Use ENTERPRISE_API_URL (api.encypherai.com) - Traefik routes /api/v1/verify to verification-service
    const apiUrl = resolvePublicEnterpriseApiUrl();

    const encodedText = typeof body?.encoded_text === "string" ? body.encoded_text : "";
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

      const response = NextResponse.json({ detail }, { status: upstream.status });
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
