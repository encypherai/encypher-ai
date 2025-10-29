import api from '@/lib/api';

export type OutputMode = 'sidecar' | 'overwrite' | 'dry_run';

export interface DirectorySigningPayload {
  directory_path: string;
  recursive?: boolean;
  include_extensions?: string[];
  exclude_patterns?: string[];
  output_mode?: OutputMode;
  schema?: Record<string, unknown>;
  encoding?: string;
}

export interface SignedFileResult {
  file_path: string;
  status: 'success' | 'skipped' | 'error';
  document_id?: string;
  verification_url?: string;
  signed_path?: string;
  message?: string;
}

export interface DirectorySigningResponse {
  total_files: number;
  processed_files: number;
  successful: number;
  failed: number;
  skipped: number;
  results: SignedFileResult[];
}

const signingService = {
  async signDirectory(payload: DirectorySigningPayload): Promise<DirectorySigningResponse> {
    const response = await api.post('/signing/directory', payload);
    return response.data;
  },
};

export default signingService;
