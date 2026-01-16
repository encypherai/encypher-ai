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

  // Test connectivity to the Enterprise API docs endpoint (known to work)
  let connectivityStatus = "unknown";
  let connectivityError: string | undefined;
  let connectivityLatencyMs: number | undefined;
  let responseStatus: number | undefined;

  const testUrl = `${enterpriseApiUrl}/docs`;

  try {
    const start = Date.now();
    const response = await fetch(testUrl, {
      method: "GET",
      signal: AbortSignal.timeout(10000),
    });
    connectivityLatencyMs = Date.now() - start;
    responseStatus = response.status;
    connectivityStatus = response.ok ? "ok" : `http_${response.status}`;
  } catch (error) {
    connectivityStatus = "fetch_failed";
    if (error instanceof Error) {
      connectivityError = `${error.name}: ${error.message}`;
      if (error.cause) {
        const causeStr = error.cause instanceof Error 
          ? `${error.cause.name}: ${error.cause.message}`
          : String(error.cause);
        connectivityError += ` | cause: ${causeStr}`;
      }
    } else {
      connectivityError = String(error);
    }
  }

  // Also test a simple external fetch to rule out general network issues
  let externalConnectivity = "unknown";
  let externalError: string | undefined;
  try {
    const extResponse = await fetch("https://httpbin.org/get", {
      method: "GET",
      signal: AbortSignal.timeout(5000),
    });
    externalConnectivity = extResponse.ok ? "ok" : `http_${extResponse.status}`;
  } catch (error) {
    externalConnectivity = "fetch_failed";
    if (error instanceof Error) {
      externalError = error.message;
    }
  }

  // Check account info if API key is available
  let accountInfo: Record<string, unknown> | undefined;
  let accountError: string | undefined;
  const apiKey = process.env.ENTERPRISE_API_KEY;
  if (apiKey) {
    try {
      const accountResponse = await fetch(`${enterpriseApiUrl}/api/v1/account`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
        signal: AbortSignal.timeout(10000),
      });
      if (accountResponse.ok) {
        const data = await accountResponse.json();
        accountInfo = {
          org_id: data.org_id || data.organization_id,
          org_name: data.org_name || data.organization_name || data.name,
          tier: data.tier || data.subscription_tier,
        };
      } else {
        accountError = `HTTP ${accountResponse.status}`;
      }
    } catch (error) {
      accountError = error instanceof Error ? error.message : String(error);
    }
  }

  return NextResponse.json({
    enterpriseApiUrl,
    testUrl,
    hasApiKey,
    nodeEnv,
    connectivityStatus,
    connectivityError,
    connectivityLatencyMs,
    responseStatus,
    externalConnectivity,
    externalError,
    accountInfo,
    accountError,
    envVars: {
      ENTERPRISE_API_URL: process.env.ENTERPRISE_API_URL || "unset",
      NEXT_PUBLIC_ENTERPRISE_API_URL: process.env.NEXT_PUBLIC_ENTERPRISE_API_URL || "unset",
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "unset",
    },
    timestamp: new Date().toISOString(),
  });
}
