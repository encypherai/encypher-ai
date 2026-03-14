import { NextRequest, NextResponse } from "next/server";

import { resolveEnterpriseApiUrl } from "@/lib/enterpriseApiUrl";
import { buildSignBasicRequest } from "@/lib/enterpriseApiTools";
import { parseJsonWithSizeLimit } from "@/lib/apiPayloadGuard";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  const requestId = crypto.randomUUID();
  const logPrefix = "[tools-sign]";
  try {
    // TEAM_152: Enforce payload size limit before parsing
    const parsed = await parseJsonWithSizeLimit(request, { requestId, logPrefix });
    if ("error" in parsed) return parsed.error;
    const body = parsed.body;

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
      custom_metadata: (body.custom_metadata as Record<string, unknown>) || {},
      ai_info: (body.ai_info as { claim_generator?: string; provenance?: string; [key: string]: unknown } | null) || null,
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

    const rawBody = await upstream.text();
    let data: Record<string, unknown> | null = null;
    if (rawBody) {
      try {
        data = JSON.parse(rawBody) as Record<string, unknown>;
      } catch (parseError) {
        console.error(`${logPrefix} upstream invalid json`, {
          requestId,
          status: upstream.status,
          parseError: parseError instanceof Error ? parseError.message : String(parseError),
          rawBody,
        });
      }
    }

    if (!upstream.ok) {
      console.error(`${logPrefix} upstream error`, {
        requestId,
        status: upstream.status,
        detail: data?.detail || (data?.error as any)?.message || data?.error || rawBody,
      });
      const detail =
        (typeof data?.detail === "string" && data.detail) ||
        (data?.detail as any)?.message ||
        (data?.error as any)?.message ||
        rawBody ||
        `Request failed with status ${upstream.status}`;

      const nextAction = (data?.error as any)?.next_action;
      return NextResponse.json(
        { detail, ...(nextAction ? { next_action: nextAction } : {}) },
        { status: upstream.status }
      );
    }

    if (!data) {
      return NextResponse.json(
        { detail: "Upstream returned invalid JSON", raw: rawBody || null },
        { status: 502 }
      );
    }

    // Unified /sign returns nested: { success, data: { document: { signed_text, ... } } }
    const documentResult = (data as any)?.data?.document;
    const signedText = documentResult?.signed_text
      || data?.signed_text || data?.signed_content || data?.embedded_content;

    console.info(`${logPrefix} upstream success`, {
      requestId,
      status: upstream.status,
      hasSignedText: Boolean(signedText),
    });

    if (!signedText) {
      console.error(`${logPrefix} no signed text in upstream response`, {
        requestId,
        topLevelKeys: Object.keys(data),
      });
      return NextResponse.json(
        { detail: "Upstream returned no signed text" },
        { status: 502 }
      );
    }

    return NextResponse.json({
      encoded_text: signedText,
      metadata: documentResult?.metadata || data?.metadata,
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
