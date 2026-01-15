import { NextRequest, NextResponse } from "next/server";

import { resolveEnterpriseApiUrl } from "@/lib/enterpriseApiUrl";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const enterpriseApiUrl = resolveEnterpriseApiUrl();

    const apiKey = process.env.ENTERPRISE_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { detail: "Missing ENTERPRISE_API_KEY" },
        { status: 500 }
      );
    }

    // Use basic /sign endpoint (works with Starter tier)
    const signRequest = {
      document_id: `doc_${Date.now()}_${Math.random().toString(16).slice(2)}`,
      text: body.original_text,
      action: "c2pa.created",
      metadata: body.custom_metadata || {},
      custom_assertions: body.ai_info ? [{
        label: "c2pa.generative-ai",
        data: {
          softwareAgent: body.ai_info.claim_generator || "Encypher Marketing Site",
          description: body.ai_info.provenance || "Content signed via marketing site tools",
        }
      }] : undefined,
    };

    const upstream = await fetch(`${enterpriseApiUrl}/api/v1/sign`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify(signRequest),
    });

    const data = await upstream
      .json()
      .catch(() => ({ detail: "Upstream returned invalid JSON" }));

    if (!upstream.ok) {
      const detail =
        (typeof data?.detail === "string" && data.detail) ||
        data?.detail?.message ||
        data?.error?.message ||
        `Request failed with status ${upstream.status}`;

      return NextResponse.json({ detail }, { status: upstream.status });
    }

    return NextResponse.json({
      encoded_text: data.signed_text || data.signed_content || data.embedded_content,
      metadata: data.metadata,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({ detail: message }, { status: 500 });
  }
}
