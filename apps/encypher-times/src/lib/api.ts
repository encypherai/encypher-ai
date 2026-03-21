const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

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

  return {
    valid: verdict.valid ?? false,
    tampered: verdict.tampered ?? false,
    signerName: verdict.signer_name || verdict.signerName || "Unknown",
    signerId: verdict.signer_id || verdict.signerId || "",
    organizationId: verdict.organization_id || verdict.organizationId || "",
    documentTitle: verdict.document_info?.title || verdict.documentTitle || "",
    reasonCode: verdict.reason_code || verdict.reasonCode || "UNKNOWN",
    signedAt: verdict.signed_at || verdict.signedAt || "",
    manifest: verdict.c2pa_info || verdict.manifest,
  };
}
