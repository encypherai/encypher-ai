import api from '@/lib/api';

export interface AuditLog {
  id: number;
  timestamp: string;
  user_id: number;
  user_email: string;
  action: string;
  resource_type: string;
  resource_id: string;
  details: Record<string, any>;
  department?: string;
  schema?: string;
}

export interface AuditLogFilters {
  page?: number;
  limit?: number;
  action?: string;
  resource_type?: string;
  user_email?: string;
  from_date?: string;
  to_date?: string;
  department?: string;
}

export interface AuditLogResponse {
  items: AuditLog[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface AuditLogStats {
  total: number;
  today: number;
  thisWeek: number;
  byDepartment: { department: string; count: number }[];
  byAction: { action: string; count: number }[];
  byDay: { date: string; count: number }[];
}

const auditLogService = {
  /**
   * Get a paginated list of audit logs with optional filters
   */
  async getAuditLogs(filters: AuditLogFilters = {}): Promise<AuditLogResponse> {
    const response = await api.get('/audit-logs', { params: filters });
    return response.data;
  },

  /**
   * Get a single audit log by ID
   */
  async getAuditLog(id: number): Promise<AuditLog> {
    const response = await api.get(`/audit-logs/${id}`);
    return response.data;
  },

  /**
   * Get audit log statistics for dashboard
   */
  async getAuditLogStats(): Promise<AuditLogStats> {
    const response = await api.get('/audit-logs/stats');
    return response.data;
  },

  /**
   * Export audit logs to CSV
   * Returns a blob URL that can be used to download the CSV
   */
  async exportAuditLogs(filters: AuditLogFilters = {}): Promise<string> {
    const response = await api.get('/audit-logs/export', {
      params: filters,
      responseType: 'blob',
    });
    
    const blob = new Blob([response.data], { type: 'text/csv' });
    return URL.createObjectURL(blob);
  },
};

export default auditLogService;
