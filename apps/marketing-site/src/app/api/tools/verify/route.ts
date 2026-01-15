import { NextRequest, NextResponse } from "next/server";

import { mapVerifyResponseToDecodeToolResponse } from "@/lib/enterpriseApiTools";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Use verification-service for verify requests (Enterprise API /verify is deprecated)
    const verificationServiceUrl =
      process.env.VERIFICATION_SERVICE_URL ||
      process.env.NEXT_PUBLIC_VERIFICATION_SERVICE_URL ||
      "http://localhost:8005";

    const encodedText = typeof body?.encoded_text === "string" ? body.encoded_text : "";
    if (!encodedText.trim()) {
      return NextResponse.json({ detail: "encoded_text is required" }, { status: 400 });
    }

    // Verification is a public endpoint - no API key required
    const upstream = await fetch(`${verificationServiceUrl}/api/v1/verify`, {
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
