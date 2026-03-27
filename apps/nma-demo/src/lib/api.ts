// API client for Encypher Enterprise API
// Uses unified /sign endpoint with tier-gated options

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.encypher.com';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

export interface EncodeRequest {
  document_id: string;
  text: string;
  document_title?: string;
  document_url?: string;
  document_type?: 'article' | 'legal_brief' | 'contract' | 'ai_output';
  metadata?: Record<string, unknown>;
  segmentation_level?: 'document' | 'sentence' | 'paragraph';
}

export interface EmbeddingInfo {
  leaf_index: number;
  text?: string;
  leaf_hash: string;
}

export interface MerkleTreeInfo {
  root_hash: string;
  total_leaves: number;
  tree_depth: number;
}

export interface EncodeResponse {
  success: boolean;
  document_id: string;
  embedded_content: string;
  verification_url?: string;
  total_sentences?: number;
  merkle_tree?: MerkleTreeInfo;
  embeddings?: EmbeddingInfo[];
  metadata?: Record<string, unknown>;
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
 * Encode content with sentence-level provenance using unified /sign endpoint.
 *
 * If API_KEY is provided, uses /sign with options for full Merkle tree + sentence-level embeddings.
 * If no API_KEY (local dev), falls back to /tools/encode for basic C2PA embedding.
 */
export async function encodeContent(request: EncodeRequest): Promise<EncodeResponse> {
  // Use authenticated endpoint if API key is available, otherwise use public tools endpoint
  const useSignEndpoint = !!API_KEY;
  const endpoint = useSignEndpoint ? '/api/v1/sign' : '/api/v1/tools/encode';

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (API_KEY) {
    headers['Authorization'] = `Bearer ${API_KEY}`;
  }

  const body = useSignEndpoint
    ? {
        text: request.text,
        document_id: request.document_id,
        document_title: request.document_title || 'News Article',
        metadata: {
          document_type: request.document_type || 'article',
          source: 'NMA Demo',
          ...request.metadata,
        },
        options: {
          segmentation_level: request.segmentation_level || 'sentence',
          action: 'c2pa.created',
          embedding_options: {
            format: 'plain',
            method: 'invisible',
            include_text: true,
          },
        },
      }
    : {
        original_text: request.text,
        target: 'first_letter',
        metadata_format: 'c2pa_v2_2',
      };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail?.message || error.detail || error.error?.message || `API error: ${response.status}`);
  }

  const data = await response.json();

  // Handle different response formats from /sign vs /tools/encode
  if (useSignEndpoint) {
    // Unified /sign response format
    const result = data.data?.document || data.data || data;
    return {
      success: data.success,
      document_id: result.document_id,
      embedded_content: result.signed_text || result.embedded_content,
      verification_url: result.verification_url,
      total_sentences: result.total_segments || result.total_sentences,
      merkle_root: result.merkle_root,
      embeddings: result.embeddings,
      metadata: result.metadata,
    };
  } else {
    // /tools/encode response format - simpler, just encoded_text
    return {
      success: true,
      document_id: request.document_id,
      embedded_content: data.encoded_text,
      total_sentences: 1,  // Basic encoding doesn't do sentence-level
      embeddings: undefined,
      metadata: data.metadata,
    };
  }
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
