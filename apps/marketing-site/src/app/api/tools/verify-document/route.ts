import { NextRequest, NextResponse } from "next/server";
import { resolveEnterpriseApiUrl } from "@/lib/enterpriseApiUrl";
import { parseJsonWithSizeLimit } from "@/lib/apiPayloadGuard";
import { buildUpstreamTraceHeaders } from "@/lib/upstreamTraceHeaders";

export const runtime = "nodejs";

// 35 MB limit: 25 MB document + ~33% base64 overhead
const MAX_PAYLOAD_BYTES = 35 * 1024 * 1024;

export async function POST(request: NextRequest) {
  const requestId = crypto.randomUUID();
  const logPrefix = "[tools-verify-document]";

  try {
    const parsed = await parseJsonWithSizeLimit(request, {
      requestId,
      logPrefix,
      maxBytes: MAX_PAYLOAD_BYTES,
    });
    if ("error" in parsed) return parsed.error;
    const body = parsed.body;

    const documentData = typeof body?.document_data === "string" ? body.document_data : "";
    const mimeType = typeof body?.mime_type === "string" ? body.mime_type : "application/pdf";

    if (!documentData) {
      return NextResponse.json({ detail: "document_data is required" }, { status: 400 });
    }

    const apiUrl = resolveEnterpriseApiUrl();

    console.info(`${logPrefix} forwarding to verify/media`, {
      requestId,
      mimeType,
      base64Len: documentData.length,
    });

    // Decode base64 to binary and send as multipart to unified verify/media
    const binaryData = Buffer.from(documentData, "base64");
    const formData = new FormData();
    formData.append("file", new Blob([binaryData], { type: mimeType }), "upload");
    formData.append("mime_type", mimeType);

    const upstream = await fetch(`${apiUrl}/api/v1/public/verify/media`, {
      method: "POST",
      headers: {
        "X-Request-Id": requestId,
      },
      body: formData,
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
