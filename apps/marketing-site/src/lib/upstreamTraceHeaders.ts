type HeaderLike = {
  get: (name: string) => string | null;
};

export function buildUpstreamTraceHeaders(
  upstreamHeaders: HeaderLike,
  upstreamBody: unknown
): Record<string, string> {
  const out: Record<string, string> = {};

  const requestId = upstreamHeaders.get("x-request-id");
  if (requestId) {
    out["x-upstream-request-id"] = requestId;
  }

  const railwayRequestId = upstreamHeaders.get("x-railway-request-id");
  if (railwayRequestId) {
    out["x-upstream-railway-request-id"] = railwayRequestId;
  }

  const correlationId =
    typeof upstreamBody === "object" && upstreamBody !== null && "correlation_id" in upstreamBody
      ? (upstreamBody as any).correlation_id
      : null;
  if (typeof correlationId === "string" && correlationId) {
    out["x-upstream-correlation-id"] = correlationId;
  }

  return out;
}
