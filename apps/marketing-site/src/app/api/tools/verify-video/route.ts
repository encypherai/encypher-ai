import { NextRequest, NextResponse } from "next/server";
import { resolveEnterpriseApiUrl } from "@/lib/enterpriseApiUrl";
import { buildUpstreamTraceHeaders } from "@/lib/upstreamTraceHeaders";

export const runtime = "nodejs";

// 100 MB max for video uploads
const MAX_VIDEO_BYTES = 100 * 1024 * 1024;

export async function POST(request: NextRequest) {
  const requestId = crypto.randomUUID();
  const logPrefix = "[tools-verify-video]";

  try {
    const formData = await request.formData();
    const file = formData.get("file");
    const mimeType = formData.get("mime_type");

    if (!file || !(file instanceof Blob)) {
      return NextResponse.json({ detail: "file is required" }, { status: 400 });
    }

    if (file.size > MAX_VIDEO_BYTES) {
      return NextResponse.json(
        { detail: `File too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Maximum is 100 MB.` },
        { status: 413 },
      );
    }

    const mime = typeof mimeType === "string" ? mimeType : "video/mp4";
    const apiUrl = resolveEnterpriseApiUrl();

    console.info(`${logPrefix} forwarding to verify/video`, {
      requestId,
      mimeType: mime,
      fileSize: file.size,
    });

    // Forward as multipart/form-data to backend
    const upstreamForm = new FormData();
    upstreamForm.append("file", file);
    upstreamForm.append("mime_type", mime);

    const upstream = await fetch(`${apiUrl}/api/v1/verify/video`, {
      method: "POST",
      headers: {
        "X-Request-Id": requestId,
      },
      body: upstreamForm,
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
