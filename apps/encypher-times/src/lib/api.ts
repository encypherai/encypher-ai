const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export interface VerifyResult {
  valid: boolean;
  tampered: boolean;
  signerName: string;
  signerId: string;
  organizationId: string;
  documentTitle: string;
  reasonCode: string;
  signedAt?: string;
  manifest?: Record<string, unknown>;
}

/**
 * Strip invisible embedding characters (Tag chars, variation selectors,
 * zero-width chars) to recover the visible text.
 */
function stripInvisible(text: string): string {
  const chars: string[] = [];
  for (const char of text) {
    const cp = char.codePointAt(0)!;
    if (cp >= 0xe0000) continue;
    if (cp >= 0xfe00 && cp <= 0xfe0f) continue;
    if (cp >= 0x200b && cp <= 0x200f) continue;
    if (cp >= 0x2060 && cp <= 0x2069) continue;
    if (cp === 0x034f || cp === 0x180e || cp === 0xfeff) continue;
    chars.push(char);
  }
  return chars.join("");
}

/**
 * Compute SHA-256 hex digest of a string (NFC-normalized, UTF-8 encoded).
 */
async function sha256Hex(text: string): Promise<string> {
  const normalized = text.normalize("NFC");
  const encoded = new TextEncoder().encode(normalized);
  const hash = await crypto.subtle.digest("SHA-256", encoded);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

/**
 * Client-side content integrity check: compare visible text hash against
 * the leaf_hash from the embedded metadata. The signing pipeline may
 * include trailing whitespace in the hashed segment, so we try several
 * whitespace variations.
 */
async function checkContentIntegrity(
  submittedText: string,
  leafHash: string
): Promise<boolean> {
  const visible = stripInvisible(submittedText);
  const candidates = [
    visible,
    visible.trim(),
    visible + "\n",
    visible + "\n\n",
    visible.trim() + "\n",
    visible.trim() + "\n\n",
  ];
  for (const candidate of candidates) {
    const h = await sha256Hex(candidate);
    if (h === leafHash) return true;
  }
  return false;
}

export async function verifyContent(text: string): Promise<VerifyResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error(`Verification failed: ${response.status}`);
  }

  const data = await response.json();
  const verdict = data.data || data;

  let valid = verdict.valid ?? false;
  let tampered = verdict.tampered ?? false;

  // Client-side content integrity check: if the server says valid but
  // doesn't detect tamper (server fix pending deployment), verify the
  // visible text hash against the embedded leaf_hash ourselves.
  if (valid && !tampered) {
    const leafHash =
      verdict.details?.manifest?.custom_metadata?.leaf_hash as
        | string
        | undefined;
    if (leafHash) {
      const contentOk = await checkContentIntegrity(text, leafHash);
      if (!contentOk) {
        valid = false;
        tampered = true;
      }
    }
  }

  return {
    valid,
    tampered,
    signerName: verdict.signer_name || verdict.signerName || "Unknown",
    signerId: verdict.signer_id || verdict.signerId || "",
    organizationId: verdict.organization_id || verdict.organizationId || "",
    documentTitle: verdict.document_info?.title || verdict.documentTitle || "",
    reasonCode: tampered
      ? "CONTENT_MODIFIED"
      : verdict.reason_code || verdict.reasonCode || "UNKNOWN",
    signedAt:
      verdict.details?.manifest?.timestamp ||
      verdict.signed_at ||
      verdict.signedAt ||
      "",
    manifest: verdict.c2pa_info || verdict.manifest,
  };
}
