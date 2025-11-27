// Admin API client functions for the admin dashboard
import { fetchApi } from './api';

// Base URL for API requests
const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

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
 * Fetches a paginated list of investor access records with optional filtering
 */
export async function getInvestorAccessRecords(
  token: string,
  page: number = 1,
  limit: number = 10,
  status?: string
): Promise<InvestorAccessListResponse> {
  const skip = (page - 1) * limit;
  let url = `/api/v1/admin/investor-access?skip=${skip}&limit=${limit}`;
  
  // Only add status filter if it's not empty and not 'ALL'
  if (status && status !== 'ALL') {
    url += `&status=${status}`;
    console.log(`[admin-api] Adding status filter: ${status}`);
  } else {
    console.log('[admin-api] No status filter applied or using ALL');
  }
  
  console.log(`[admin-api] Fetching investor records with URL: ${url}`);
  
  return fetchApi<InvestorAccessListResponse>(url, {
    method: 'GET',
    token,
  });
}

/**
 * Fetches a single investor access record by ID
 */
export async function getInvestorAccessById(
  token: string,
  accessId: string
): Promise<InvestorAccessRecord> {
  return fetchApi<InvestorAccessRecord>(`/api/v1/admin/investor-access/${accessId}`, {
    method: 'GET',
    token,
  });
}

/**
 * Approves an investor access request
 */
export async function approveInvestorAccess(
  token: string,
  accessId: string
): Promise<AdminActionResponse> {
  return fetchApi<AdminActionResponse>(`/api/v1/admin/investor-access/${accessId}/approve`, {
    method: 'POST',
    token,
  });
}

/**
 * Rejects an investor access request
 */
export async function rejectInvestorAccess(
  token: string,
  accessId: string
): Promise<AdminActionResponse> {
  return fetchApi<AdminActionResponse>(`/api/v1/admin/investor-access/${accessId}/disapprove`, {
    method: 'POST',
    token,
  });
}

/**
 * Updates an investor access record
 */
export async function updateInvestorAccess(
  token: string,
  accessId: string,
  data: Partial<InvestorAccessRecord>
): Promise<InvestorAccessRecord> {
  return fetchApi<InvestorAccessRecord>(`/api/v1/admin/investor-access/${accessId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
    token,
  });
}

/**
 * Deletes an investor access record (soft delete)
 */
export async function deleteInvestorAccess(
  token: string,
  accessId: string
): Promise<AdminActionResponse> {
  return fetchApi<AdminActionResponse>(`/api/v1/admin/investor-access/${accessId}`, {
    method: 'DELETE',
    token,
  });
}

/**
 * Creates a new investor access record
 */
export async function createInvestorAccess(
  token: string,
  data: {
    investor_name: string;
    investor_email: string;
    investor_company?: string;
    status?: string;
  }
): Promise<InvestorAccessRecord> {
  return fetchApi<InvestorAccessRecord>('/api/v1/admin/investor-access', {
    method: 'POST',
    body: JSON.stringify(data),
    token,
  });
}

/**
 * Gets dashboard statistics for investor access
 */
export async function getInvestorAccessStats(
  token: string
): Promise<{
  total: number;
  pending: number;
  active: number;
  rejected: number;
  revoked: number;
  expired: number;
}> {
  return fetchApi<{
    total: number;
    pending: number;
    active: number;
    rejected: number;
    revoked: number;
    expired: number;
  }>('/api/v1/admin/investor-access/stats', {
    method: 'GET',
    token,
  });
}
