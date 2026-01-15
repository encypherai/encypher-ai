import { resolveEnterpriseApiUrl } from "./enterpriseApiUrl";

describe("resolveEnterpriseApiUrl", () => {
  it("prefers configured Enterprise API URL", () => {
    const url = resolveEnterpriseApiUrl({
      env: {
        ENTERPRISE_API_URL: "https://api.encypherai.com",
        NEXT_PUBLIC_ENTERPRISE_API_URL: "https://fallback.example.com",
      },
      nodeEnv: "production",
    });

    expect(url).toBe("https://api.encypherai.com");
  });

  it("falls back to production host when env vars are missing", () => {
    const url = resolveEnterpriseApiUrl({ env: {}, nodeEnv: "production" });

    expect(url).toBe("https://api.encypherai.com");
  });

  it("falls back to localhost when not in production", () => {
    const url = resolveEnterpriseApiUrl({ env: {}, nodeEnv: "development" });

    expect(url).toBe("http://localhost:9000");
  });
});
