import { NextRequest, NextResponse } from "next/server";

import { mapVerifyResponseToDecodeToolResponse } from "@/lib/enterpriseApiTools";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const enterpriseApiUrl =
      process.env.ENTERPRISE_API_URL ||
      process.env.NEXT_PUBLIC_ENTERPRISE_API_URL ||
      "https://enterprise-api-staging.up.railway.app";

    const apiKey = process.env.ENTERPRISE_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { detail: "Missing ENTERPRISE_API_KEY" },
        { status: 500 }
      );
    }

    const encodedText = typeof body?.encoded_text === "string" ? body.encoded_text : "";
    if (!encodedText.trim()) {
      return NextResponse.json({ detail: "encoded_text is required" }, { status: 400 });
    }

    const upstream = await fetch(`${enterpriseApiUrl}/api/v1/verify`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
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
