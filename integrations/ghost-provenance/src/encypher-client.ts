import pino from 'pino';
import { Config } from './config';

const logger = pino({ name: 'encypher-client' });

export interface EmbeddingPlanOperation {
  insert_after_index: number;
  marker: string;
}

export interface EmbeddingPlan {
  index_unit?: string;
  operations?: EmbeddingPlanOperation[];
}

export interface SignRequest {
  text: string;
  document_id: string;
  document_title?: string;
  document_url?: string;
  metadata?: Record<string, unknown>;
  options?: {
    document_type?: string;
    claim_generator?: string;
    action?: string;
    manifest_mode?: string;
    segmentation_level?: string;
    ecc?: boolean;
    embed_c2pa?: boolean;
    index_for_attribution?: boolean;
    return_embedding_plan?: boolean;
    previous_instance_id?: string;
    license?: {
      type: string;
      url: string;
    };
  };
}

export interface SignResponse {
  success: boolean;
  data?: {
    document?: {
      signed_text?: string;
      embedded_content?: string;
      document_id?: string;
      instance_id?: string;
      total_segments?: number;
      total_sentences?: number;
      metadata?: Record<string, unknown>;
      embedding_plan?: EmbeddingPlan;
    };
  };
  // Legacy flat format
  signed_text?: string;
  embedded_content?: string;
  document_id?: string;
  instance_id?: string;
  total_segments?: number;
  total_sentences?: number;
  embedding_plan?: EmbeddingPlan;
}

export interface VerifyRequest {
  text: string;
  segmentation_level?: string;
  search_scope?: string;
  include_attribution?: boolean;
  detect_plagiarism?: boolean;
  include_heat_map?: boolean;
  min_match_percentage?: number;
}

export interface VerifyResponse {
  success: boolean;
  data?: {
    valid?: boolean;
    tampered?: boolean;
    reason_code?: string;
    signer_id?: string;
    signer_name?: string;
    timestamp?: string;
    details?: {
      manifest?: Record<string, unknown>;
    };
  };
  correlation_id?: string;
}

export class EncypherClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(config: Config) {
    this.baseUrl = config.encypher.apiBaseUrl.replace(/\/+$/, '');
    this.apiKey = config.encypher.apiKey;
  }

  private async request<T>(endpoint: string, body: unknown, requireAuth: boolean = true): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const parsedUrl = new URL(url);
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      // When running inside Docker and reaching the host via host.docker.internal,
      // the Host header must be set to localhost to pass allowed-host checks.
      'Host': parsedUrl.hostname === 'host.docker.internal'
        ? `localhost:${parsedUrl.port || '80'}`
        : parsedUrl.host,
    };

    if (requireAuth) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    logger.debug({ url, endpoint }, 'Calling Encypher API');

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      const error = new Error(`Encypher API error ${response.status}: ${errorText}`);
      logger.error({ status: response.status, endpoint, errorText }, 'Encypher API request failed');
      throw error;
    }

    return response.json() as Promise<T>;
  }

  /**
   * Sign text content with C2PA-compliant invisible embeddings.
   */
  async sign(payload: SignRequest): Promise<SignResponse> {
    return this.request<SignResponse>('/sign', payload, true);
  }

  /**
   * Verify text content for C2PA embeddings (advanced endpoint).
   */
  async verifyAdvanced(payload: VerifyRequest): Promise<VerifyResponse> {
    return this.request<VerifyResponse>('/verify/advanced', payload, true);
  }

  /**
   * Public verification (no auth required).
   */
  async verifyPublic(payload: { text: string }): Promise<VerifyResponse> {
    return this.request<VerifyResponse>('/public/extract-and-verify', payload, false);
  }

  /**
   * Extract the signed text from the API response, handling both
   * new unified format and legacy flat format.
   */
  static extractSignedText(response: SignResponse): string | null {
    if (response.data?.document?.signed_text) {
      return response.data.document.signed_text;
    }
    if (response.data?.document?.embedded_content) {
      return response.data.document.embedded_content;
    }
    if (response.signed_text) {
      return response.signed_text;
    }
    if (response.embedded_content) {
      return response.embedded_content;
    }
    return null;
  }

  /**
   * Extract embedding plan from response when requested.
   */
  static extractEmbeddingPlan(response: SignResponse): EmbeddingPlan | null {
    if (response.data?.document?.embedding_plan) {
      return response.data.document.embedding_plan;
    }
    if (response.embedding_plan) {
      return response.embedding_plan;
    }
    return null;
  }

  /**
   * Extract document metadata from the API response.
   */
  static extractMetadata(response: SignResponse): {
    documentId: string;
    instanceId: string;
    totalSegments: number;
  } {
    const doc = response.data?.document || response;
    return {
      documentId: (doc as Record<string, unknown>).document_id as string || '',
      instanceId: (doc as Record<string, unknown>).instance_id as string || '',
      totalSegments:
        ((doc as Record<string, unknown>).total_segments as number) ||
        ((doc as Record<string, unknown>).total_sentences as number) ||
        0,
    };
  }
}
