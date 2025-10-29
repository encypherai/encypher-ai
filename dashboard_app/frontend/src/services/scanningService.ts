import api from '@/lib/api';

export type ScanOutputMode = 'sidecar' | 'overwrite';

export interface DirectoryScanPayload {
  directory_path: string;
  recursive?: boolean;
  include_extensions?: string[];
  exclude_patterns?: string[];
  encoding?: string;
  mark_unmarked?: boolean;
  sign_output_mode?: ScanOutputMode;
  schema?: Record<string, unknown>;
}

export interface ScannedFileResult {
  file_path: string;
  has_metadata: boolean;
  status: 'scanned' | 'marked' | 'error' | 'skipped';
  message?: string;
  signed_path?: string;
  document_id?: string;
  verification_url?: string;
}

export interface DirectoryScanResponse {
  total_files: number;
  scanned: number;
  marked: number;
  errors: number;
  skipped: number;
  results: ScannedFileResult[];
}

const scanningService = {
  async scanDirectory(payload: DirectoryScanPayload): Promise<DirectoryScanResponse> {
    const response = await api.post('/scanning/scan', payload);
    return response.data;
  },
};

export default scanningService;
