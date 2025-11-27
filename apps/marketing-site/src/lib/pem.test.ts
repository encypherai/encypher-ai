import { toPem } from "./pem";

describe("toPem utility", () => {
  it("formats a base64 public key as PEM", () => {
    const base64 = "MCowBQYDK2VwAyEAbSK8YiaPuf6NUbtK2Nv6t6k1thKaBoieKY0ThUPhuDA=";
    const pem = toPem(base64, "public");
    expect(pem).toContain("-----BEGIN PUBLIC KEY-----");
    expect(pem).toContain(base64);
    expect(pem).toContain("-----END PUBLIC KEY-----");
  });

  it("formats a base64 private key as PEM", () => {
    const base64 = "MC4CAQAwBQYDK2VwBCIEICGeW0O3XQrBVMiYr5JBcWrsmSWAyI9NcLMsiDRD6bg8";
    const pem = toPem(base64, "private");
    expect(pem).toContain("-----BEGIN PRIVATE KEY-----");
    expect(pem).toContain(base64);
    expect(pem).toContain("-----END PRIVATE KEY-----");
  });

  it("inserts line breaks every 64 chars", () => {
    const base64 = "A".repeat(130);
    const pem = toPem(base64, "public");
    // 130 chars = 2 lines of 64 and 1 of 2
    expect(pem.split("\n").length).toBeGreaterThan(4); // header + 2 lines + 1 short + footer
  });
});
