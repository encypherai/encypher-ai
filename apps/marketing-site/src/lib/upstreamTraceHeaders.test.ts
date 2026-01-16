import { buildUpstreamTraceHeaders } from "./upstreamTraceHeaders";

function headersFrom(entries: Record<string, string>): { get: (name: string) => string | null } {
  return {
    get: (name: string) => {
      const key = Object.keys(entries).find((k) => k.toLowerCase() === name.toLowerCase());
      return key ? entries[key] : null;
    },
  };
}

describe("buildUpstreamTraceHeaders", () => {
  it("maps upstream X-Request-ID, x-railway-request-id, and correlation_id into proxy headers", () => {
    const upstreamHeaders = headersFrom({
      "X-Request-ID": "verifier-req-123",
      "x-railway-request-id": "railway-upstream-456",
    });

    const result = buildUpstreamTraceHeaders(upstreamHeaders, {
      correlation_id: "req-deadbeef",
    });

    expect(result).toEqual(
      expect.objectContaining({
        "x-upstream-request-id": "verifier-req-123",
        "x-upstream-railway-request-id": "railway-upstream-456",
        "x-upstream-correlation-id": "req-deadbeef",
      })
    );
  });

  it("omits headers when upstream values are missing", () => {
    const upstreamHeaders = headersFrom({});

    const result = buildUpstreamTraceHeaders(upstreamHeaders, { success: true });

    expect(result).toEqual({});
  });
});
