import { NextRequest, NextResponse } from "next/server";
import { resolveEnterpriseApiUrl } from "@/lib/enterpriseApiUrl";
import { parseJsonWithSizeLimit } from "@/lib/apiPayloadGuard";
import { buildUpstreamTraceHeaders } from "@/lib/upstreamTraceHeaders";

export const runtime = "nodejs";

// 14 MB limit: 10 MB image + ~33% base64 overhead
const MAX_PAYLOAD_BYTES = 14 * 1024 * 1024;

export async function POST(request: NextRequest) {
  const requestId = crypto.randomUUID();
  const logPrefix = "[tools-verify-image]";

  try {
    const parsed = await parseJsonWithSizeLimit(request, {
      requestId,
      logPrefix,
      maxBytes: MAX_PAYLOAD_BYTES,
    });
    if ("error" in parsed) return parsed.error;
    const body = parsed.body;

    const imageData = typeof body?.image_data === "string" ? body.image_data : "";
    const mimeType = typeof body?.mime_type === "string" ? body.mime_type : "image/jpeg";

    if (!imageData) {
      return NextResponse.json({ detail: "image_data is required" }, { status: 400 });
    }

    const apiUrl = resolveEnterpriseApiUrl();

    console.info(`${logPrefix} forwarding to verify/image`, {
      requestId,
      mimeType,
      base64Len: imageData.length,
    });

    const upstream = await fetch(`${apiUrl}/api/v1/verify/image`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Request-Id": requestId,
      },
      body: JSON.stringify({ image_data: imageData, mime_type: mimeType }),
    });

    const data = await upstream.json().catch(() => ({
      success: false,
      valid: false,
      error: "Upstream returned invalid JSON",
    }));

    const traceHeaders = buildUpstreamTraceHeaders(upstream.headers, data);

    if (!upstream.ok) {
      console.error(`${logPrefix} upstream error`, {
        requestId,
        status: upstream.status,
        detail: data?.detail || data?.error,
      });
      const detail =
        (typeof data?.detail === "string" && data.detail) ||
        data?.error?.message ||
        `Request failed with status ${upstream.status}`;
      const resp = NextResponse.json({ detail }, { status: upstream.status });
      Object.entries(traceHeaders).forEach(([k, v]) => resp.headers.set(k, v));
      return resp;
    }

    console.info(`${logPrefix} upstream success`, {
      requestId,
      valid: data?.valid,
      imageId: data?.image_id,
    });

    const resp = NextResponse.json(data);
    Object.entries(traceHeaders).forEach(([k, v]) => resp.headers.set(k, v));
    return resp;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    console.error(`${logPrefix} unexpected error`, { requestId, message });
    return NextResponse.json({ detail: message }, { status: 500 });
  }
}
