import { NextRequest, NextResponse } from "next/server";

import { resolveEnterpriseApiUrl } from "@/lib/enterpriseApiUrl";
import { buildSignBasicRequest } from "@/lib/enterpriseApiTools";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  const requestId = crypto.randomUUID();
  const logPrefix = "[tools-sign]";
  try {
    const body = await request.json();

    const originalText = typeof body?.original_text === "string" ? body.original_text : "";
    if (!originalText.trim()) {
      console.warn(`${logPrefix} invalid payload`, {
        requestId,
        hasText: Boolean(originalText.trim()),
        metadataKeys: body?.custom_metadata ? Object.keys(body.custom_metadata) : [],
        hasAiInfo: Boolean(body?.ai_info),
      });
      return NextResponse.json({ detail: "original_text is required" }, { status: 400 });
    }

    const enterpriseApiUrl = resolveEnterpriseApiUrl();

    const apiKey = process.env.ENTERPRISE_API_KEY;
    if (!apiKey) {
      console.error(`${logPrefix} missing ENTERPRISE_API_KEY`, { requestId });
      return NextResponse.json(
        { detail: "Missing ENTERPRISE_API_KEY" },
        { status: 500 }
      );
    }

    // Use basic /sign endpoint (works with Starter tier)
    const signRequest = buildSignBasicRequest({
      original_text: originalText,
      custom_metadata: body.custom_metadata || {},
      ai_info: body.ai_info || null,
    });

    console.info(`${logPrefix} forwarding request`, {
      requestId,
      upstreamHost: enterpriseApiUrl,
      hasMetadata: Boolean(body.custom_metadata && Object.keys(body.custom_metadata).length),
      hasAiInfo: Boolean(body.ai_info),
      textLength: originalText.length,
    });

    const upstream = await fetch(`${enterpriseApiUrl}/api/v1/sign`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
        "X-Request-Id": requestId,
      },
      body: JSON.stringify(signRequest),
    });

    const data = await upstream
      .json()
      .catch(() => ({ detail: "Upstream returned invalid JSON" }));

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

      return NextResponse.json({ detail }, { status: upstream.status });
    }

    console.info(`${logPrefix} upstream success`, {
      requestId,
      status: upstream.status,
      hasSignedText: Boolean(data?.signed_text || data?.signed_content || data?.embedded_content),
    });

    return NextResponse.json({
      encoded_text: data.signed_text || data.signed_content || data.embedded_content,
      metadata: data.metadata,
    });
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
    return NextResponse.json({
      detail: message,
      cause: cause || undefined,
    }, { status: 500 });
  }
}
