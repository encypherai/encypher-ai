export type EncodeToolRequestLike = {
  original_text: string;
  target?: string;
  custom_metadata?: Record<string, unknown> | null;
  metadata_format?: string | null;
  ai_info?: {
    claim_generator?: string;
    provenance?: string;
    [key: string]: unknown;
  } | null;
};

export type SignAdvancedRequest = {
  document_id: string;
  text: string;
  segmentation_level: "sentence";
  action: "c2pa.created";
  metadata?: Record<string, unknown>;
  custom_assertions?: Array<{ label: string; data: Record<string, unknown> }>;
  validate_assertions: false;
  embedding_options: {
    format: "plain";
    method: "data-attribute";
    include_text: true;
  };
};

export type SignBasicRequest = {
  document_id: string;
  text: string;
  action: "c2pa.created";
  metadata?: Record<string, unknown>;
  custom_assertions?: Array<{ label: string; data: Record<string, unknown> }>;
};

export type VerifyResponseLike = {
  success: boolean;
  correlation_id: string;
  error: null | { code: string; message: string; hint?: string | null };
  data:
    | null
    | {
        valid: boolean;
        tampered: boolean;
        reason_code: string;
        signer_id?: string | null;
        signer_name?: string | null;
        timestamp?: string | null;
        details?: { manifest?: Record<string, unknown> } & Record<string, unknown>;
        embeddings_found?: number;
        all_embeddings?:
          | null
          | Array<{
              index: number;
              valid: boolean;
              tampered: boolean;
              reason_code: string;
              signer_id?: string | null;
              signer_name?: string | null;
              timestamp?: string | null;
              text_span?: [number, number] | null;
              clean_text?: string | null;
              manifest?: Record<string, unknown> | null;
            }>;
      };
};

export type DecodeToolResponseLike = {
  metadata?: Record<string, unknown> | null;
  verification_status: "Success" | "Failure" | "Key Not Found" | "Not Attempted" | "Error";
  error?: string | { message: string } | null;
  raw_hidden_data?: Record<string, unknown> | null;
  embeddings_found?: number;
  all_embeddings?: Array<Record<string, unknown>> | null;
};

function randomDocId(): string {
  return `doc_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

export function buildSignBasicRequest(input: EncodeToolRequestLike): SignBasicRequest {
  const metadataPayload: Record<string, unknown> = {
    ...(input.custom_metadata || {}),
  };

  const customAssertions: Array<{ label: string; data: Record<string, unknown> }> = [];
  const provenance = input.ai_info?.provenance;

  if (provenance) {
    customAssertions.push({
      label: "org.encypher.provenance",
      data: {
        text: provenance,
      },
    });
  }

  return {
    document_id: randomDocId(),
    text: input.original_text,
    action: "c2pa.created",
    metadata: Object.keys(metadataPayload).length ? metadataPayload : undefined,
    custom_assertions: customAssertions.length ? customAssertions : undefined,
  };
}

export function buildSignAdvancedRequest(input: EncodeToolRequestLike): SignAdvancedRequest {
  const metadata_payload: Record<string, unknown> = {
    ...(input.custom_metadata || {}),
    ...(input.ai_info || {}),
  };

  const custom_assertions: Array<{ label: string; data: Record<string, unknown> }> = [];

  const claim_generator = input.ai_info?.claim_generator;
  const provenance = input.ai_info?.provenance;

  if (claim_generator || provenance) {
    custom_assertions.push({
      label: "c2pa.generative-ai",
      data: {
        softwareAgent: claim_generator || "Encypher Demo UI",
        description: provenance || "AI-assisted content generation",
      },
    });
  }

  return {
    document_id: randomDocId(),
    text: input.original_text,
    segmentation_level: "sentence",
    action: "c2pa.created",
    metadata: Object.keys(metadata_payload).length ? metadata_payload : undefined,
    custom_assertions: custom_assertions.length ? custom_assertions : undefined,
    validate_assertions: false,
    embedding_options: {
      format: "plain",
      method: "data-attribute",
      include_text: true,
    },
  };
}

export function mapVerifyResponseToDecodeToolResponse(
  verify: VerifyResponseLike
): DecodeToolResponseLike {
  if (!verify.success) {
    const message = verify.error?.message || "Verification failed";
    return {
      metadata: null,
      verification_status: "Error",
      error: message,
      raw_hidden_data: null,
      embeddings_found: 0,
      all_embeddings: null,
    };
  }

  const data = verify.data;
  const verdict = data || {
    valid: false,
    tampered: false,
    reason_code: "UNKNOWN",
  };

  const manifest = (data && data.details && (data.details as any).manifest) || undefined;

  const embeddingsFound = data?.embeddings_found ?? (manifest ? 1 : 0);

  const allEmbeddings = data?.all_embeddings
    ? data.all_embeddings.map((emb) => ({
        index: emb.index,
        metadata: emb.manifest || null,
        verification_status: emb.valid ? "Success" : "Failure",
        error: null,
        verdict: {
          valid: emb.valid,
          tampered: emb.tampered,
          reason_code: emb.reason_code,
          signer_id: emb.signer_id || undefined,
          signer_name: emb.signer_name || undefined,
          timestamp: emb.timestamp || undefined,
        },
        text_span: emb.text_span || null,
        clean_text: emb.clean_text || null,
      }))
    : null;

  return {
    metadata: manifest ? { manifest } : null,
    verification_status: verdict.valid ? "Success" : "Failure",
    error: null,
    raw_hidden_data: {
      valid: verdict.valid,
      tampered: verdict.tampered,
      reason_code: verdict.reason_code,
      signer_id: (verdict as any).signer_id,
      signer_name: (verdict as any).signer_name,
      timestamp: (verdict as any).timestamp,
      details: (verdict as any).details,
    },
    embeddings_found: embeddingsFound,
    all_embeddings: allEmbeddings,
  };
}
