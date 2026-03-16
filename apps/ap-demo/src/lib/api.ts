// API client for Encypher Enterprise API
// Uses unified /sign endpoint with tier-gated options

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.encypherai.com';
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
  merkle_root?: string;
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
 * Creates Merkle tree + C2PA manifest with invisible embeddings per sentence.
 * Requires a valid API key with sign permission. Features gated by tier.
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
      metadata: {
        document_type: request.document_type || 'article',
        source: 'AP Demo',
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
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail?.message || error.detail || error.error?.message || `API error: ${response.status}`);
  }

  const data = await response.json();

  // Handle new unified response format
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
