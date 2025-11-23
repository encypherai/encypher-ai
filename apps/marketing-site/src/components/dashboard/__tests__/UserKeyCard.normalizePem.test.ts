import { describe, it, expect } from "vitest";

// Inline normalizePem from UserKeyCard
function normalizePem(pem: string): string {
  const lines = pem.trim().split(/\r?\n/);
  const contentLines = lines.filter(
    (line, idx, arr) =>
      !(line.startsWith('-----BEGIN') && idx !== 0) &&
      !(line.startsWith('-----END') && idx !== arr.length - 1)
  );
  const cleaned = contentLines.join('\n').replace(/\n{2,}/g, '\n');
  return cleaned;
}

describe("normalizePem utility", () => {
  it("removes duplicate PEM headers/footers", () => {
    const input = `-----BEGIN PUBLIC KEY-----\n-----BEGIN PUBLIC KEY-----\nABC123==\n-----END PUBLIC KEY-----\n-----END PUBLIC KEY-----`;
    const expected = `-----BEGIN PUBLIC KEY-----\nABC123==\n-----END PUBLIC KEY-----`;
    expect(normalizePem(input)).toBe(expected);
  });

  it("handles extra blank lines", () => {
    const input = `-----BEGIN PUBLIC KEY-----\n\nABC123==\n\n-----END PUBLIC KEY-----\n`;
    const expected = `-----BEGIN PUBLIC KEY-----\nABC123==\n-----END PUBLIC KEY-----`;
    expect(normalizePem(input)).toBe(expected);
  });

  it("returns clean PEM if already correct", () => {
    const input = `-----BEGIN PUBLIC KEY-----\nABC123==\n-----END PUBLIC KEY-----`;
    expect(normalizePem(input)).toBe(input);
  });
});
