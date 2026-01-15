import { NextResponse } from "next/server";

import { resolveEnterpriseApiUrl } from "@/lib/enterpriseApiUrl";

export const runtime = "nodejs";

/**
 * Debug endpoint to diagnose Enterprise API connectivity issues.
 * Returns resolved URL and connectivity status without exposing secrets.
 */
export async function GET() {
  const enterpriseApiUrl = resolveEnterpriseApiUrl();
  const hasApiKey = Boolean(process.env.ENTERPRISE_API_KEY);
  const nodeEnv = process.env.NODE_ENV;

  // Test connectivity to the Enterprise API health endpoint
  let connectivityStatus = "unknown";
  let connectivityError: string | undefined;
  let connectivityLatencyMs: number | undefined;

  try {
    const start = Date.now();
    const healthResponse = await fetch(`${enterpriseApiUrl}/health`, {
      method: "GET",
      signal: AbortSignal.timeout(10000),
    });
    connectivityLatencyMs = Date.now() - start;
    connectivityStatus = healthResponse.ok ? "ok" : `error_${healthResponse.status}`;
  } catch (error) {
    connectivityStatus = "fetch_failed";
    if (error instanceof Error) {
      connectivityError = error.message;
      if (error.cause) {
        connectivityError += ` (cause: ${String(error.cause)})`;
      }
    }
  }

  return NextResponse.json({
    enterpriseApiUrl,
    hasApiKey,
    nodeEnv,
    connectivityStatus,
    connectivityError,
    connectivityLatencyMs,
    envVars: {
      ENTERPRISE_API_URL: process.env.ENTERPRISE_API_URL ? "set" : "unset",
      NEXT_PUBLIC_ENTERPRISE_API_URL: process.env.NEXT_PUBLIC_ENTERPRISE_API_URL ? "set" : "unset",
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ? "set" : "unset",
    },
  });
}
