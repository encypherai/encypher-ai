import { NextRequest, NextResponse } from "next/server";

import { resolveEnterpriseApiUrl } from "@/lib/enterpriseApiUrl";
import { mapVerifyResponseToDecodeToolResponse } from "@/lib/enterpriseApiTools";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Use ENTERPRISE_API_URL (api.encypherai.com) - Traefik routes /api/v1/verify to verification-service
    const apiUrl = resolveEnterpriseApiUrl();

    const encodedText = typeof body?.encoded_text === "string" ? body.encoded_text : "";
    if (!encodedText.trim()) {
      return NextResponse.json({ detail: "encoded_text is required" }, { status: 400 });
    }

    // Verification is a public endpoint - no API key required
    // Traefik routes /api/v1/verify to the verification-service
    const upstream = await fetch(`${apiUrl}/api/v1/verify`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
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

    if (!upstream.ok) {
      const detail =
        (typeof data?.detail === "string" && data.detail) ||
        data?.detail?.message ||
        data?.error?.message ||
        `Request failed with status ${upstream.status}`;

      return NextResponse.json({ detail }, { status: upstream.status });
    }

    return NextResponse.json(mapVerifyResponseToDecodeToolResponse(data));
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({ detail: message }, { status: 500 });
  }
}
