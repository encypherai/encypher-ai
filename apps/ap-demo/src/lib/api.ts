// API client for Encypher Enterprise API
// Uses authenticated /sign and /verify endpoints with API key

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.encypherai.com';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

export interface EncodeRequest {
  document_id: string;
  text: string;
  document_title?: string;
  document_url?: string;
  document_type?: 'article' | 'legal_brief' | 'contract' | 'ai_output';
  metadata?: Record<string, unknown>;
}

export interface EncodeResponse {
  success: boolean;
  document_id: string;
  embedded_content: string;
  verification_url?: string;
  total_sentences?: number;
}

export interface VerifyResponse {
  valid: boolean;
  tampered: boolean;
  signer_id?: string;
  signer_name?: string;
  reason_code: string;
  metadata?: Record<string, unknown>;
  manifest?: Record<string, unknown>;
  original_text?: string;
  error?: string;
}

/**
 * Sign content using the authenticated /sign endpoint.
 * Requires a valid API key.
 */
export async function encodeContent(request: EncodeRequest): Promise<EncodeResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/sign`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
    },
    body: JSON.stringify({
      text: request.text,
      document_id: request.document_id,
      document_title: request.document_title || 'AP News Article',
      document_type: request.document_type || 'article',
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail?.message || error.detail || `API error: ${response.status}`);
  }

  const data = await response.json();
  
  return {
    success: data.success,
    document_id: data.document_id,
    embedded_content: data.signed_text,
    verification_url: data.verification_url,
    total_sentences: data.total_sentences,
  };
}

/**
 * Verify content using the authenticated /verify endpoint.
 * Requires a valid API key.
 */
export async function verifyContent(text: string): Promise<VerifyResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/verify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail?.message || error.detail || `API error: ${response.status}`);
  }

  const data = await response.json();
  const verdict = data.data || {};
  
  return {
    valid: verdict.valid || false,
    tampered: verdict.tampered || false,
    signer_id: verdict.signer_id,
    signer_name: verdict.signer_name,
    reason_code: verdict.reason_code || 'UNKNOWN',
    metadata: data.metadata,
    manifest: verdict.details?.manifest,
    original_text: data.original_text,
    error: data.error,
  };
}
