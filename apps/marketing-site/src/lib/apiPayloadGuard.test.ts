// TEAM_152: Tests for API payload size guard
import { parseJsonWithSizeLimit, MAX_PAYLOAD_BYTES } from "./apiPayloadGuard";

// Minimal mock for NextRequest — only needs headers and text()
function mockRequest(body: string, headers: Record<string, string> = {}): any {
  return {
    headers: {
      get: (key: string) => headers[key.toLowerCase()] ?? null,
    },
    text: async () => body,
  };
}

// Minimal mock for NextResponse.json used by the guard
jest.mock("next/server", () => ({
  NextRequest: class {},
  NextResponse: {
    json: (body: unknown, init?: { status?: number }) => ({
      body,
      status: init?.status ?? 200,
    }),
  },
}));

describe("apiPayloadGuard", () => {
  const opts = { requestId: "test-123", logPrefix: "[test]" };

  describe("MAX_PAYLOAD_BYTES", () => {
    it("is 2 MB", () => {
      expect(MAX_PAYLOAD_BYTES).toBe(2 * 1024 * 1024);
    });
  });

  describe("parseJsonWithSizeLimit", () => {
    it("parses valid JSON within size limit", async () => {
      const req = mockRequest(JSON.stringify({ encoded_text: "hello" }));
      const result = await parseJsonWithSizeLimit(req, opts);

      expect("body" in result).toBe(true);
      if ("body" in result) {
        expect(result.body).toEqual({ encoded_text: "hello" });
      }
    });

    it("rejects payload exceeding limit via content-length header", async () => {
      const req = mockRequest("{}", {
        "content-length": String(MAX_PAYLOAD_BYTES + 1),
      });
      const result = await parseJsonWithSizeLimit(req, opts);

      expect("error" in result).toBe(true);
      if ("error" in result) {
        expect((result.error as any).status).toBe(413);
        expect((result.error as any).body.detail).toContain("too large");
        expect((result.error as any).body.detail).toContain("2 MB");
      }
    });

    it("rejects payload exceeding limit via actual body size", async () => {
      const oversized = "x".repeat(MAX_PAYLOAD_BYTES + 100);
      const req = mockRequest(oversized);
      const result = await parseJsonWithSizeLimit(req, opts);

      expect("error" in result).toBe(true);
      if ("error" in result) {
        expect((result.error as any).status).toBe(413);
        expect((result.error as any).body.detail).toContain("too large");
      }
    });

    it("rejects invalid JSON with 400", async () => {
      const req = mockRequest("not valid json {{{");
      const result = await parseJsonWithSizeLimit(req, opts);

      expect("error" in result).toBe(true);
      if ("error" in result) {
        expect((result.error as any).status).toBe(400);
        expect((result.error as any).body.detail).toContain("Invalid JSON");
      }
    });

    it("accepts custom maxBytes override", async () => {
      const req = mockRequest(JSON.stringify({ data: "a".repeat(500) }));
      const result = await parseJsonWithSizeLimit(req, { ...opts, maxBytes: 100 });

      expect("error" in result).toBe(true);
      if ("error" in result) {
        expect((result.error as any).status).toBe(413);
      }
    });

    it("accepts empty JSON object", async () => {
      const req = mockRequest("{}");
      const result = await parseJsonWithSizeLimit(req, opts);

      expect("body" in result).toBe(true);
      if ("body" in result) {
        expect(result.body).toEqual({});
      }
    });

    it("accepts payload exactly at the limit", async () => {
      // Build a JSON string that is exactly MAX_PAYLOAD_BYTES
      const padding = "a".repeat(MAX_PAYLOAD_BYTES - 20);
      const json = JSON.stringify({ k: padding });
      // Ensure it's within limit (JSON overhead makes it slightly larger, but
      // the key point is it should not be rejected if under the byte count)
      const req = mockRequest(json);
      const result = await parseJsonWithSizeLimit(req, { ...opts, maxBytes: new TextEncoder().encode(json).length });

      expect("body" in result).toBe(true);
    });
  });
});
