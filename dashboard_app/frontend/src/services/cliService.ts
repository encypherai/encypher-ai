import api from '@/lib/api';

export interface CliScan {
  id: number;
  scan_type: 'audit_log' | 'policy_validation';
  status: 'queued' | 'running' | 'completed' | 'failed';
  started_at: string;
  completed_at?: string;
  user_id: number;
  user_email: string;
  target_path?: string;
  parameters?: Record<string, any>;
  output?: string;
  error_message?: string;
  progress?: number;
}

export interface CliScanFilters {
  page?: number;
  limit?: number;
  scan_type?: string;
  status?: string;
  user_id?: number;
  activeOnly?: boolean;
}

export interface CliScanResponse {
  items: CliScan[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface StartScanParams {
  scan_type: 'audit_log' | 'policy_validation';
  target_path?: string;
  parameters?: Record<string, any>;
}

const cliService = {
  /**
   * Get a paginated list of CLI scans with optional filters
   */
  async getScans(filters: CliScanFilters = {}): Promise<CliScanResponse> {
    const response = await api.get('/cli/scans', { params: filters });
    return response.data;
  },

  /**
   * Get a single CLI scan by ID
   */
  async getScan(id: number): Promise<CliScan> {
    const response = await api.get(`/cli/scans/${id}`);
    return response.data;
  },

  /**
   * Start a new CLI scan
   */
  async startScan(params: StartScanParams): Promise<CliScan> {
    const response = await api.post('/cli/scans', params);
    return response.data;
  },

  /**
   * Stop a running CLI scan
   */
  async stopScan(id: number): Promise<CliScan> {
    const response = await api.post(`/cli/scans/${id}/stop`);
    return response.data;
  },

  /**
   * Get the current active scans (running or queued)
   */
  async getActiveScans(): Promise<CliScanResponse> {
    const response = await api.get('/cli/scans/active');
    // Handle both response formats: array of scans or paginated response
    if (Array.isArray(response.data)) {
      // Convert array to CliScanResponse format
      return {
        items: response.data,
        total: response.data.length,
        page: 1,
        limit: response.data.length,
        totalPages: 1
      };
    }
    return response.data;
  },

  /**
   * Get the scan output for a specific scan
   * This is useful for streaming the output as the scan progresses
   */
  async getScanOutput(id: number): Promise<string> {
    const response = await api.get(`/cli/scans/${id}/output`);
    return response.data.output || '';
  },
};

export default cliService;
