import { resolveEnterpriseApiUrl, resolvePublicEnterpriseApiUrl } from "./enterpriseApiUrl";

describe("resolveEnterpriseApiUrl", () => {
  it("prefers configured Enterprise API URL", () => {
    const url = resolveEnterpriseApiUrl({
      env: {
        ENTERPRISE_API_URL: "https://api.encypher.com",
        NEXT_PUBLIC_ENTERPRISE_API_URL: "https://fallback.example.com",
      },
      nodeEnv: "production",
    });

    expect(url).toBe("https://api.encypher.com");
  });

  it("falls back to NEXT_PUBLIC_API_URL when enterprise envs are missing", () => {
    const url = resolveEnterpriseApiUrl({
      env: {
        NEXT_PUBLIC_API_URL: "https://api.encypher.com",
      },
      nodeEnv: "production",
    });

    expect(url).toBe("https://api.encypher.com");
  });

  it("ignores localhost values in production", () => {
    const url = resolveEnterpriseApiUrl({
      env: {
        ENTERPRISE_API_URL: "http://localhost:9000",
        NEXT_PUBLIC_API_URL: "https://api.encypher.com",
      },
      nodeEnv: "production",
    });

    expect(url).toBe("https://api.encypher.com");
  });

  it("strips api path segments from configured base URLs", () => {
    const url = resolveEnterpriseApiUrl({
      env: {
        ENTERPRISE_API_URL: "https://api.encypher.com/api/v1",
      },
      nodeEnv: "production",
    });

    expect(url).toBe("https://api.encypher.com");
  });

  it("falls back to production host when env vars are missing", () => {
    const url = resolveEnterpriseApiUrl({ env: {}, nodeEnv: "production" });

    expect(url).toBe("https://api.encypher.com");
  });

  it("falls back to localhost when not in production", () => {
    const url = resolveEnterpriseApiUrl({ env: {}, nodeEnv: "development" });

    expect(url).toBe("http://localhost:9000");
  });

  it("resolves public enterprise API URL from NEXT_PUBLIC_ENTERPRISE_API_URL", () => {
    const url = resolvePublicEnterpriseApiUrl({
      env: {
        NEXT_PUBLIC_ENTERPRISE_API_URL: "https://public-api.encypher.com",
        ENTERPRISE_API_URL: "https://private-api.encypher.com",
      },
      nodeEnv: "production",
    });

    expect(url).toBe("https://public-api.encypher.com");
  });

  it("falls back to public defaults when public env vars are missing", () => {
    const url = resolvePublicEnterpriseApiUrl({ env: {}, nodeEnv: "development" });

    expect(url).toBe("http://localhost:9000");
  });
});
