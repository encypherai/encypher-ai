import { useApiClient } from './useApiClient';
import { useState, useCallback } from 'react';

// Types
export interface InvestorAccessRecord {
  id: string;
  investor_name: string | null;
  investor_email: string;
  investor_company: string | null;
  status: string;
  visit_count: number;
  last_visited_at: string | null;
  email_verified_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface InvestorAccessListResponse {
  data: InvestorAccessRecord[];
  total: number;
}

export interface AdminActionResponse {
  success: boolean;
  message: string;
}

/**
 * Custom hook for admin API operations
 * Uses the authenticated API client from useApiClient
 */
export function useAdminApi() {
  const { apiCall, isAuthenticated, session } = useApiClient();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetches a paginated list of investor access records with optional filtering
   */
  const getInvestorAccessRecords = useCallback(async (
    page: number = 1,
    limit: number = 10,
    status?: string,
    searchQuery?: string
  ): Promise<InvestorAccessListResponse> => {
    setLoading(true);
    setError(null);
    
    try {
      const skip = (page - 1) * limit;
      let url = `/api/v1/admin/investor-access?skip=${skip}&limit=${limit}`;
      
      // Only add status filter if it's not empty and not 'ALL'
      if (status && status !== 'ALL') {
        url += `&status=${status}`;
        console.log(`[admin-api] Adding status filter: ${status}`);
      } else {
        console.log('[admin-api] No status filter applied or using ALL');
      }
      if (searchQuery && searchQuery.trim() !== '') {
        url += `&search=${encodeURIComponent(searchQuery.trim())}`;
      }
      
      console.log(`[admin-api] Fetching investor records with URL: ${url}`);
      
      const response = await apiCall<InvestorAccessListResponse>(url);
      return response;
    } catch (err) {
      console.error('[admin-api] Error fetching investor records:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch investor records');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  /**
   * Fetches a single investor access record by ID
   */
  const getInvestorAccessById = useCallback(async (accessId: string): Promise<InvestorAccessRecord> => {
    setLoading(true);
    setError(null);
    
    try {
      return await apiCall<InvestorAccessRecord>(`/api/v1/admin/investor-access/${accessId}`);
    } catch (err) {
      console.error(`[admin-api] Error fetching investor record ${accessId}:`, err);
      setError(err instanceof Error ? err.message : 'Failed to fetch investor record');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  /**
   * Approves an investor access request
   */
  const approveInvestorAccess = useCallback(async (accessId: string): Promise<AdminActionResponse> => {
    setLoading(true);
    setError(null);
    
    try {
      return await apiCall<AdminActionResponse>(
        `/api/v1/admin/investor-access/${accessId}/approve`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}), // Send empty JSON object
        }
      );
    } catch (err) {
      console.error(`[admin-api] Error approving investor access ${accessId}:`, err);
      setError(err instanceof Error ? err.message : 'Failed to approve investor access');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  /**
   * Rejects an investor access request
   */
  const rejectInvestorAccess = useCallback(async (accessId: string): Promise<AdminActionResponse> => {
    setLoading(true);
    setError(null);
    
    try {
      return await apiCall<AdminActionResponse>(
        `/api/v1/admin/investor-access/${accessId}/disapprove`,
        { method: 'POST' }
      );
    } catch (err) {
      console.error(`[admin-api] Error rejecting investor access ${accessId}:`, err);
      setError(err instanceof Error ? err.message : 'Failed to reject investor access');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  /**
   * Updates an investor access record
   */
  const updateInvestorAccess = useCallback(async (
    accessId: string,
    data: Partial<InvestorAccessRecord>
  ): Promise<InvestorAccessRecord> => {
    setLoading(true);
    setError(null);
    
    try {
      return await apiCall<InvestorAccessRecord>(
        `/api/v1/admin/investor-access/${accessId}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        }
      );
    } catch (err) {
      console.error(`[admin-api] Error updating investor access ${accessId}:`, err);
      setError(err instanceof Error ? err.message : 'Failed to update investor access');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  /**
   * Creates a new investor access record
   */
  const createInvestorAccess = useCallback(async (
    data: {
      investor_name: string;
      investor_email: string;
      investor_company?: string;
      status?: string;
    }
  ): Promise<InvestorAccessRecord> => {
    setLoading(true);
    setError(null);
    
    try {
      return await apiCall<InvestorAccessRecord>(
        '/api/v1/admin/investor-access',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        }
      );
    } catch (err) {
      console.error('[admin-api] Error creating investor access:', err);
      setError(err instanceof Error ? err.message : 'Failed to create investor access');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  /**
   * Gets dashboard statistics for investor access
   */
  const getInvestorAccessStats = useCallback(async (): Promise<{
    total: number;
    pending: number;
    active: number;
    rejected: number;
    revoked: number;
    expired: number;
    pending_verification: number;
  }> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiCall<{
        total: number;
        pending: number;
        active: number;
        rejected: number;
        revoked: number;
        expired: number;
        pending_verification: number;
      }>('/api/v1/admin/investor-access/stats');
      return response;
    } catch (err) {
      console.error('[admin-api] Error fetching investor access stats:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch stats');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  return {
    loading,
    error,
    isAuthenticated,
    session,
    getInvestorAccessRecords,
    getInvestorAccessById,
    approveInvestorAccess,
    rejectInvestorAccess,
    updateInvestorAccess,
    createInvestorAccess,
    getInvestorAccessStats,
  };
}
