import api from '@/lib/api';

export interface PolicyValidation {
  id: number;
  timestamp: string;
  user_id: number;
  user_email: string;
  schema_id: number;
  schema_name: string;
  resource_id: string;
  resource_type: string;
  status: 'passed' | 'failed' | 'warning';
  details: Record<string, any>;
  department?: string;
}

export interface PolicySchema {
  id: number;
  name: string;
  description: string;
  schema: Record<string, any>;
  created_at: string;
  updated_at: string;
  created_by: number;
  version: number;
  is_active: boolean;
}

export interface PolicyValidationFilters {
  page?: number;
  limit?: number;
  status?: string;
  schema_id?: number;
  resource_type?: string;
  user_email?: string;
  from_date?: string;
  to_date?: string;
  department?: string;
}

export interface PolicyValidationResponse {
  items: PolicyValidation[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface PolicyValidationStats {
  total: number;
  passed: number;
  failed: number;
  warning: number;
  bySchema: { schema: string; count: number }[];
  byDepartment: { department: string; count: number }[];
  byDay: { date: string; count: number }[];
}

const policyValidationService = {
  /**
   * Get a paginated list of policy validations with optional filters
   */
  async getPolicyValidations(filters: PolicyValidationFilters = {}): Promise<PolicyValidationResponse> {
    const response = await api.get('/policy-validations', { params: filters });
    return response.data;
  },

  /**
   * Get a single policy validation by ID
   */
  async getPolicyValidation(id: number): Promise<PolicyValidation> {
    const response = await api.get(`/policy-validations/${id}`);
    return response.data;
  },

  /**
   * Get policy validation statistics for dashboard
   */
  async getPolicyValidationStats(): Promise<PolicyValidationStats> {
    const response = await api.get('/policy-validations/stats');
    return response.data;
  },

  /**
   * Export policy validations to CSV
   * Returns a blob URL that can be used to download the CSV
   */
  async exportPolicyValidations(filters: PolicyValidationFilters = {}): Promise<string> {
    const response = await api.get('/policy-validations/export', {
      params: filters,
      responseType: 'blob',
    });
    
    const blob = new Blob([response.data], { type: 'text/csv' });
    return URL.createObjectURL(blob);
  },

  /**
   * Get a list of all policy schemas
   */
  async getPolicySchemas(): Promise<PolicySchema[]> {
    const response = await api.get('/policy-schemas');
    return response.data;
  },

  /**
   * Get a single policy schema by ID
   */
  async getPolicySchema(id: number): Promise<PolicySchema> {
    const response = await api.get(`/policy-schemas/${id}`);
    return response.data;
  },

  /**
   * Create a new policy schema
   */
  async createPolicySchema(schema: Partial<PolicySchema>): Promise<PolicySchema> {
    const response = await api.post('/policy-schemas', schema);
    return response.data;
  },

  /**
   * Update an existing policy schema
   */
  async updatePolicySchema(id: number, schema: Partial<PolicySchema>): Promise<PolicySchema> {
    const response = await api.put(`/policy-schemas/${id}`, schema);
    return response.data;
  },

  /**
   * Delete a policy schema
   */
  async deletePolicySchema(id: number): Promise<void> {
    await api.delete(`/policy-schemas/${id}`);
  },

  /**
   * Import policy validations from CSV
   * Accepts a File object containing CSV data
   */
  async importPolicyValidations(file: File): Promise<{ count: number }> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/policy-validations/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },
};

export default policyValidationService;
