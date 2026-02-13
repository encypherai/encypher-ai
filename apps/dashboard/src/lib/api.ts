/**
 * Dashboard API Client
 * 
 * Handles all API calls to backend microservices.
 * Uses the access token from NextAuth session for authentication.
 */

// All API calls go through Traefik (routes to appropriate microservice based on path)
// In production: https://api.encypherai.com/api/v1
// In development: http://localhost:8000/api/v1
// 
// IMPORTANT: NEXT_PUBLIC_API_URL should include /api/v1 suffix
// e.g., http://localhost:8000/api/v1 or https://api.encypherai.com/api/v1
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === 'development'
    ? 'http://localhost:8000/api/v1'
    : 'https://api.encypherai.com/api/v1');

if (process.env.NODE_ENV === 'development') {
  console.info(`[dashboard] Using API base URL: ${API_BASE_URL}`);
}

const AUTH_SERVICE_URL = API_BASE_URL;
const KEY_SERVICE_URL = API_BASE_URL;
const ANALYTICS_SERVICE_URL = API_BASE_URL;
const BILLING_SERVICE_URL = API_BASE_URL;

interface ApiResponse<T = unknown> {
  success: boolean;
  data: T | null;
  error: {
    code: string;
    message: string;
    details?: unknown;
  } | null;
}

interface ApiKeyInfo {
  id: string;
  name: string;
  fingerprint: string;
  permissions: string[];
  created_at: string;
  last_used_at?: string;
  is_revoked: boolean;
  user_id?: string | null;
  created_by?: string | null;
}

interface ApiKeyCreateResponse {
  id: string;
  name: string;
  key: string; // Full key - only shown once!
  fingerprint: string;
  permissions: string[];
  created_at: string;
  organization_id?: string | null;
  user_id?: string | null;
  created_by?: string | null;
}

interface UsageStats {
  total_api_calls: number;
  total_documents_signed: number;
  total_verifications: number;
  success_rate: number;
  avg_response_time_ms: number;
  period_start: string;
  period_end: string;
}

// Enterprise API usage response (from /usage endpoint)
interface EnterpriseUsageMetric {
  name: string;
  used: number;
  limit: number;  // -1 for unlimited
  remaining: number;  // -1 for unlimited
  percentage_used: number;
  available: boolean;
}

interface EnterpriseUsageResponse {
  organization_id: string;
  tier: string;
  period_start: string;
  period_end: string;
  metrics: Record<string, EnterpriseUsageMetric>;
  reset_date: string;
}

interface TimeSeriesData {
  timestamp: string;
  count: number;
  value?: number;
}

interface OrganizationInfo {
  id: string;
  name: string;
  slug: string | null;
  email: string;
  tier: string;
  max_seats: number;
  subscription_status: string;
  created_at: string;
}

interface OrganizationCreateResponse {
  success: boolean;
  data: OrganizationInfo;
  error: { code: string; message: string } | null;
}

interface DomainClaimInfo {
  id: string;
  organization_id: string;
  domain: string;
  verification_email: string;
  status: string;
  dns_token: string;
  dns_verified_at: string | null;
  email_verified_at: string | null;
  verified_at: string | null;
  auto_join_enabled: boolean;
  created_at: string;
  dns_txt_record?: string;
}

interface DomainClaimResponse {
  success: boolean;
  data: DomainClaimInfo;
  error: { code: string; message: string } | null;
}

interface AnalyticsReport {
  user_id: string;
  period_start: string;
  period_end: string;
  usage_stats: UsageStats;
  time_series: TimeSeriesData[];
}

// Billing types
interface PlanInfo {
  id: string;
  name: string;
  tier: string;
  price_monthly: number;
  price_annual: number;
  features: string[];
  limits: Record<string, number>;
  coalition_rev_share?: { publisher: number; encypher: number };
  popular?: boolean;
  enterprise?: boolean;
}

interface SubscriptionInfo {
  id: string;
  user_id: string;
  organization_id?: string;
  plan_id: string;
  plan_name: string;
  tier: string;
  status: string;
  billing_cycle: string;
  amount: number;
  currency: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  created_at: string;
  features?: Record<string, boolean>;
  coalition_rev_share?: { publisher: number; encypher: number };
}

interface Invoice {
  id: string;
  invoice_number: string;
  status: string;
  amount_due: number;
  amount_paid: number;
  currency: string;
  period_start: string;
  period_end: string;
  due_date?: string;
  paid_at?: string;
  created_at: string;
}

interface CheckoutResponse {
  checkout_url: string;
  session_id: string;
}

interface PortalResponse {
  portal_url: string;
}

interface UpgradeResponse {
  success: boolean;
  checkout_url?: string;
  message: string;
  new_tier?: string;
  effective_date?: string;
}

interface UsageMetric {
  name: string;
  limit: number | 'unlimited';
  used: number;
  remaining: number | 'unlimited';
  percentage_used: number;
  available: boolean;
}

interface BillingUsageStats {
  organization_id: string;
  tier: string;
  period_start: string;
  period_end: string;
  metrics: Record<string, UsageMetric>;
  reset_date: string;
}

interface CoalitionSummary {
  member: boolean;
  opted_out: boolean;
  publisher_share_percent: number;
  encypher_share_percent: number;
  total_content: number;
  total_earnings: number;
  pending_earnings: number;
  last_payout_date: string | null;
  earnings_history: Array<{
    period: string;
    amount: number;
    status: string;
  }>;
  payout_account_connected: boolean;
  payout_account_url: string | null;
}

// C2PA Template types (TEAM_044)
interface C2PATemplate {
  id: string;
  name: string;
  description: string | null;
  schema_id: string;
  template_data: Record<string, unknown>;
  category: string | null;
  organization_id: string;
  is_default: boolean;
  is_active: boolean;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

interface C2PATemplateListResponse {
  templates: C2PATemplate[];
  total: number;
  page: number;
  page_size: number;
}

// TEAM_006: API Access Gating types
type ApiAccessStatusType = 'not_requested' | 'pending' | 'approved' | 'denied' | 'suspended';

interface ApiAccessStatusResponse {
  status: ApiAccessStatusType;
  requested_at: string | null;
  decided_at: string | null;
  use_case: string | null;
  denial_reason: string | null;
  message: string | null;
}

interface ApiAccessRequestResponse {
  status: ApiAccessStatusType;
  message: string;
}

interface PendingAccessRequest {
  user_id: string;
  email: string;
  name: string | null;
  use_case: string;
  requested_at: string;
}

class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }

  /**
   * Check if this error indicates an expired or invalid session
   */
  isAuthError(): boolean {
    return this.statusCode === 401 || this.statusCode === 403;
  }
}

async function fetchWithAuth<T>(
  url: string,
  accessToken: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`,
    ...options.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // Ignore JSON parse errors
    }
    throw new ApiError(errorMessage, response.status);
  }

  return response.json();
}

const apiClient = {
  // ============================================
  // API Keys (key-service)
  // ============================================
  
  /**
   * Get all API keys for the current user
   */
  async getApiKeys(accessToken: string, organizationId?: string | null): Promise<ApiKeyInfo[]> {
    const params = new URLSearchParams();
    if (organizationId) {
      params.append('organization_id', organizationId);
    }
    const query = params.toString();
    const response = await fetchWithAuth<ApiKeyInfo[]>(
      `${KEY_SERVICE_URL}/keys${query ? `?${query}` : ''}`,
      accessToken
    );
    return response;
  },

  /**
   * List domain claims for an organization
   */
  async listDomainClaims(accessToken: string, organizationId: string): Promise<DomainClaimInfo[]> {
    const response = await fetchWithAuth<{ success: boolean; data: DomainClaimInfo[] }>(
      `${AUTH_SERVICE_URL}/organizations/${organizationId}/domain-claims`,
      accessToken
    );
    return response.data ?? [];
  },

  /**
   * Create a new domain claim
   */
  async createDomainClaim(
    accessToken: string,
    organizationId: string,
    payload: { domain: string; verification_email: string }
  ): Promise<DomainClaimResponse> {
    const response = await fetchWithAuth<DomainClaimResponse>(
      `${AUTH_SERVICE_URL}/organizations/${organizationId}/domain-claims`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    );
    return response;
  },

  /**
   * Verify domain claim via DNS TXT
   */
  async verifyDomainClaimDns(
    accessToken: string,
    organizationId: string,
    claimId: string
  ): Promise<DomainClaimResponse> {
    const response = await fetchWithAuth<DomainClaimResponse>(
      `${AUTH_SERVICE_URL}/organizations/${organizationId}/domain-claims/${claimId}/verify-dns`,
      accessToken,
      { method: 'POST' }
    );
    return response;
  },

  /**
   * Toggle auto-join for a domain claim
   */
  async updateDomainAutoJoin(
    accessToken: string,
    organizationId: string,
    claimId: string,
    enabled: boolean
  ): Promise<DomainClaimResponse> {
    const response = await fetchWithAuth<DomainClaimResponse>(
      `${AUTH_SERVICE_URL}/organizations/${organizationId}/domain-claims/${claimId}/auto-join`,
      accessToken,
      {
        method: 'PATCH',
        body: JSON.stringify({ enabled }),
      }
    );
    return response;
  },

  /**
   * Create a new API key
   */
  async createApiKey(
    accessToken: string,
    name: string,
    permissions: string[] = ['sign', 'verify', 'read'],
    organizationId?: string | null
  ): Promise<ApiResponse<ApiKeyCreateResponse>> {
    const payload: { name: string; permissions: string[]; organization_id?: string } = {
      name,
      permissions,
    };
    if (organizationId) {
      payload.organization_id = organizationId;
    }
    const response = await fetchWithAuth<ApiKeyCreateResponse>(
      `${KEY_SERVICE_URL}/keys/generate`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    );
    return {
      success: true,
      data: response,
      error: null,
    };
  },

  /**
   * Delete (revoke) an API key
   */
  async deleteApiKey(accessToken: string, keyId: string): Promise<void> {
    await fetchWithAuth<{ message: string }>(
      `${KEY_SERVICE_URL}/keys/${keyId}`,
      accessToken,
      { method: 'DELETE' }
    );
  },

  /**
   * Revoke all API keys created by a specific user in an organization
   */
  async revokeKeysByUser(accessToken: string, organizationId: string, userId: string): Promise<{ revoked_count: number }> {
    return fetchWithAuth<{ revoked_count: number }>(
      `${KEY_SERVICE_URL}/keys/revoke-by-user`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ organization_id: organizationId, user_id: userId }),
      }
    );
  },

  // ============================================
  // Organizations (auth-service)
  // ============================================

  /**
   * Create a new organization
   */
  async createOrganization(
    accessToken: string,
    payload: { name: string; email: string }
  ): Promise<OrganizationCreateResponse> {
    const response = await fetchWithAuth<OrganizationCreateResponse>(
      `${AUTH_SERVICE_URL}/organizations`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    );
    return response;
  },

  /**
   * Get usage stats for a specific key
   */
  async getKeyUsage(accessToken: string, keyId: string): Promise<unknown> {
    return fetchWithAuth(
      `${KEY_SERVICE_URL}/keys/${keyId}/usage`,
      accessToken
    );
  },

  // ============================================
  // Analytics (analytics-service)
  // ============================================

  /**
   * Get usage statistics for the current user
   */
  async getUsageStats(accessToken: string, days: number = 30): Promise<UsageStats> {
    return fetchWithAuth<UsageStats>(
      `${ANALYTICS_SERVICE_URL}/analytics/usage?days=${days}`,
      accessToken
    );
  },

  /**
   * Get comprehensive analytics report
   */
  async getAnalyticsReport(accessToken: string, days: number = 30): Promise<AnalyticsReport> {
    return fetchWithAuth<AnalyticsReport>(
      `${ANALYTICS_SERVICE_URL}/analytics/report?days=${days}`,
      accessToken
    );
  },

  /**
   * Get time series data for a specific metric
   */
  async getTimeSeries(
    accessToken: string,
    metricType: string,
    days: number = 7,
    interval: 'hour' | 'day' = 'day'
  ): Promise<TimeSeriesData[]> {
    return fetchWithAuth<TimeSeriesData[]>(
      `${ANALYTICS_SERVICE_URL}/analytics/timeseries?metric_type=${metricType}&days=${days}&interval=${interval}`,
      accessToken
    );
  },

  // ============================================
  // User Profile (auth-service)
  // ============================================

  /**
   * Get current user profile
   */
  async getUserProfile(accessToken: string): Promise<unknown> {
    return fetchWithAuth(
      `${AUTH_SERVICE_URL}/auth/verify`,
      accessToken,
      { method: 'POST' }
    );
  },

  /**
   * Logout - revoke refresh token
   */
  async logout(accessToken: string): Promise<void> {
    await fetchWithAuth(
      `${AUTH_SERVICE_URL}/auth/logout`,
      accessToken,
      { method: 'POST' }
    );
  },

  // ============================================
  // API Access Gating (auth-service) - TEAM_006
  // ============================================

  /**
   * Get current API access status for the authenticated user
   */
  async getApiAccessStatus(accessToken: string): Promise<ApiAccessStatusResponse> {
    const response = await fetchWithAuth<{ success: boolean; data: ApiAccessStatusResponse }>(
      `${AUTH_SERVICE_URL}/auth/api-access-status`,
      accessToken
    );
    return response.data;
  },

  /**
   * Request API access with a use case description
   */
  async requestApiAccess(accessToken: string, useCase: string): Promise<ApiAccessRequestResponse> {
    const response = await fetchWithAuth<{ success: boolean; data: ApiAccessRequestResponse }>(
      `${AUTH_SERVICE_URL}/auth/request-api-access`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ use_case: useCase }),
      }
    );
    return response.data;
  },

  /**
   * Check if current user is a super admin
   */
  async isSuperAdmin(accessToken: string): Promise<boolean> {
    try {
      const response = await fetchWithAuth<{ success: boolean; data: { is_super_admin: boolean } }>(
        `${AUTH_SERVICE_URL}/auth/admin/is-super-admin`,
        accessToken
      );
      return response.data.is_super_admin;
    } catch {
      return false;
    }
  },

  /**
   * Search organizations for admin typeahead
   */
  async searchAdminOrganizations(accessToken: string, query: string, limit = 10): Promise<unknown[]> {
    const params = new URLSearchParams({ query, limit: limit.toString() });
    const response = await fetchWithAuth<{ success: boolean; data: unknown[] }>(
      `${AUTH_SERVICE_URL}/auth/admin/organizations/search?${params.toString()}`,
      accessToken
    );
    return response.data;
  },

  /**
   * Get pending API access requests (admin only)
   */
  async getPendingAccessRequests(accessToken: string): Promise<PendingAccessRequest[]> {
    const response = await fetchWithAuth<{ success: boolean; data: { requests: PendingAccessRequest[]; total: number } }>(
      `${AUTH_SERVICE_URL}/auth/admin/pending-access-requests`,
      accessToken
    );
    return response.data.requests;
  },

  /**
   * Approve a user's API access request (admin only)
   */
  async approveApiAccess(accessToken: string, userId: string): Promise<void> {
    await fetchWithAuth(
      `${AUTH_SERVICE_URL}/auth/admin/approve-api-access`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ user_id: userId }),
      }
    );
  },

  /**
   * Deny a user's API access request (admin only)
   */
  async denyApiAccess(accessToken: string, userId: string, reason: string): Promise<void> {
    await fetchWithAuth(
      `${AUTH_SERVICE_URL}/auth/admin/deny-api-access`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, reason }),
      }
    );
  },

  /**
   * TEAM_164: Directly set a user's API access status (admin only)
   * Supports: not_requested, pending, approved, denied, suspended
   */
  async setApiAccessStatus(
    accessToken: string,
    userId: string,
    status: ApiAccessStatusType,
    reason?: string
  ): Promise<void> {
    await fetchWithAuth(
      `${AUTH_SERVICE_URL}/auth/admin/set-api-access-status`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, status, reason }),
      }
    );
  },

  // ============================================
  // Profile Management
  // ============================================

  /**
   * Get user profile
   */
  async getProfile(accessToken: string): Promise<unknown> {
    const response = await fetchWithAuth<{ success: boolean; data: unknown }>(
      `${AUTH_SERVICE_URL}/auth/verify`,
      accessToken,
      { method: 'POST' }
    );
    return response;
  },

  /**
   * Update user profile
   */
  async updateProfile(accessToken: string, data: {
    name?: string;
    company?: string;
    phone?: string;
    job_title?: string;
    notifications?: {
      emailAlerts?: boolean;
      usageAlerts?: boolean;
      securityAlerts?: boolean;
      marketingEmails?: boolean;
    };
  }): Promise<unknown> {
    // Note: This endpoint may need to be implemented in auth-service
    // For now, we'll make the call and handle gracefully if it doesn't exist
    try {
      return await fetchWithAuth(
        `${AUTH_SERVICE_URL}/auth/profile`,
        accessToken,
        {
          method: 'PUT',
          body: JSON.stringify(data),
        }
      );
    } catch (error) {
      // If profile update endpoint doesn't exist, return success silently
      console.warn('Profile update endpoint not available:', error);
      return { success: true, data: null };
    }
  },
  // ============================================
  // Admin (Enterprise API /api/v1/admin/*)
  // ============================================

  /**
   * Get platform statistics (super admin only)
   */
  async getAdminStats(accessToken: string): Promise<unknown> {
    const response = await fetchWithAuth<{ success: boolean; data: unknown }>(
      `${AUTH_SERVICE_URL}/auth/admin/stats`,
      accessToken
    );
    return response.data;
  },

  /**
   * List all users with optional filtering (super admin only)
   */
  async getAdminUsers(
    accessToken: string,
    search?: string,
    tier?: string,
    page?: number,
    pageSize?: number
  ): Promise<unknown> {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (tier) params.append('tier', tier);
    if (page) params.append('page', page.toString());
    if (pageSize) params.append('page_size', pageSize.toString());
    
    const queryString = params.toString();
    const url = `${AUTH_SERVICE_URL}/auth/admin/users${queryString ? `?${queryString}` : ''}`;
    
    const response = await fetchWithAuth<{ success: boolean; data: unknown }>(
      url,
      accessToken
    );
    return response.data;
  },

  /**
   * Update a user's tier (super admin only)
   */
  async updateUserTier(accessToken: string, userId: string, newTier: string, reason?: string): Promise<unknown> {
    const response = await fetchWithAuth<{ success: boolean; data: unknown }>(
      `${AUTH_SERVICE_URL}/auth/admin/users/update-tier`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, new_tier: newTier, reason }),
      }
    );
    return response.data;
  },

  /**
   * Update a user's status (suspend/activate) - super admin only
   */
  async toggleUserStatus(accessToken: string, userId: string, enabled: boolean, reason?: string): Promise<unknown> {
    const response = await fetchWithAuth<{ success: boolean; data: unknown }>(
      `${AUTH_SERVICE_URL}/auth/admin/users/update-status`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ 
          user_id: userId, 
          status: enabled ? 'active' : 'suspended',
          reason 
        }),
      }
    );
    return response.data;
  },

  /**
   * Get error logs (super admin only)
   */
  async getErrorLogs(accessToken: string, options?: {
    userId?: string;
    statusCode?: number;
    page?: number;
    pageSize?: number;
  }): Promise<unknown> {
    const params = new URLSearchParams();
    if (options?.userId) params.append('user_id', options.userId);
    if (options?.statusCode) params.append('status_code', options.statusCode.toString());
    if (options?.page) params.append('page', options.page.toString());
    if (options?.pageSize) params.append('page_size', options.pageSize.toString());
    
    const queryString = params.toString();
    const url = `${API_BASE_URL}/admin/error-logs${queryString ? `?${queryString}` : ''}`;
    
    const response = await fetchWithAuth<{ success: boolean; data: unknown }>(
      url,
      accessToken
    );
    return response.data;
  },

  /**
   * Update a user's role (super admin only)
   */
  async updateUserRole(accessToken: string, userId: string, newRole: string): Promise<unknown> {
    const response = await fetchWithAuth<{ success: boolean; data: unknown }>(
      `${AUTH_SERVICE_URL}/auth/admin/users/update-role`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, new_role: newRole }),
      }
    );
    return response.data;
  },

  /**
   * Legacy method for backward compatibility
   */
  async updateAdminUser(accessToken: string, userId: string, data: { tier?: string; role?: string }): Promise<unknown> {
    if (data.tier) {
      return this.updateUserTier(accessToken, userId, data.tier);
    }
    if (data.role) {
      return this.updateUserRole(accessToken, userId, data.role);
    }
    return { success: true };
  },

  // ============================================
  // C2PA Templates (TEAM_044)
  // ============================================

  /**
   * List available C2PA assertion templates (Enterprise tier)
   */
  async getC2PATemplates(accessToken: string, options?: {
    page?: number;
    pageSize?: number;
    category?: string;
  }): Promise<C2PATemplateListResponse> {
    const params = new URLSearchParams();
    if (options?.page) params.append('page', options.page.toString());
    if (options?.pageSize) params.append('page_size', options.pageSize.toString());
    if (options?.category) params.append('category', options.category);
    
    const queryString = params.toString();
    const url = `${API_BASE_URL}/enterprise/c2pa/templates${queryString ? `?${queryString}` : ''}`;
    
    return fetchWithAuth<C2PATemplateListResponse>(url, accessToken);
  },

  /**
   * Get a specific C2PA template by ID (Enterprise tier)
   */
  async getC2PATemplate(accessToken: string, templateId: string): Promise<C2PATemplate> {
    return fetchWithAuth<C2PATemplate>(
      `${API_BASE_URL}/enterprise/c2pa/templates/${templateId}`,
      accessToken
    );
  },

  // ============================================
  // BYOK Public Key Management
  // ============================================

  /**
   * Register a public key for BYOK verification (enterprise tier)
   */
  async registerPublicKey(accessToken: string, publicKeyPem: string, keyName?: string, keyAlgorithm?: string): Promise<unknown> {
    const response = await fetchWithAuth<{ success: boolean; data: unknown }>(
      `${API_BASE_URL}/admin/public-keys`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ 
          public_key_pem: publicKeyPem, 
          key_name: keyName,
          key_algorithm: keyAlgorithm || 'Ed25519'
        }),
      }
    );
    return response;
  },

  /**
   * List organization's public keys
   */
  async listPublicKeys(accessToken: string, includeRevoked?: boolean): Promise<unknown> {
    const params = new URLSearchParams();
    if (includeRevoked) params.append('include_revoked', 'true');
    
    const queryString = params.toString();
    const url = `${API_BASE_URL}/admin/public-keys${queryString ? `?${queryString}` : ''}`;
    
    const response = await fetchWithAuth<{ success: boolean; data: unknown }>(
      url,
      accessToken
    );
    return response.data;
  },

  /**
   * Revoke a public key
   */
  async revokePublicKey(accessToken: string, keyId: string, reason?: string): Promise<unknown> {
    const params = new URLSearchParams();
    if (reason) params.append('reason', reason);
    
    const queryString = params.toString();
    const url = `${API_BASE_URL}/admin/public-keys/${keyId}${queryString ? `?${queryString}` : ''}`;
    
    return fetchWithAuth(
      url,
      accessToken,
      { method: 'DELETE' }
    );
  },

  // ============================================
  // Billing (billing-service)
  // ============================================

  /**
   * Get all available subscription plans
   */
  async getPlans(): Promise<PlanInfo[]> {
    const response = await fetch(`${BILLING_SERVICE_URL}/billing/plans`);
    if (!response.ok) {
      throw new ApiError('Failed to fetch plans', response.status);
    }
    return response.json();
  },

  /**
   * Get current subscription info
   */
  async getSubscription(accessToken: string): Promise<SubscriptionInfo | null> {
    try {
      return await fetchWithAuth<SubscriptionInfo>(
        `${BILLING_SERVICE_URL}/billing/subscription`,
        accessToken
      );
    } catch (error) {
      // 404 means no subscription - return null
      if (error instanceof ApiError && error.statusCode === 404) {
        return null;
      }
      throw error;
    }
  },

  /**
   * Get billing info (subscription + plans for display)
   */
  async getBillingInfo(accessToken: string): Promise<{
    subscription: SubscriptionInfo | null;
    plans: PlanInfo[];
  }> {
    const [subscription, plans] = await Promise.all([
      this.getSubscription(accessToken).catch(() => null),
      this.getPlans(),
    ]);
    return { subscription, plans };
  },

  /**
   * Get invoices for the current user
   */
  async getInvoices(accessToken: string): Promise<Invoice[]> {
    try {
      return await fetchWithAuth<Invoice[]>(
        `${BILLING_SERVICE_URL}/billing/invoices`,
        accessToken
      );
    } catch (error) {
      console.warn('Failed to fetch invoices:', error);
      return [];
    }
  },

  /**
   * Get current billing period usage statistics
   */
  async getBillingUsage(accessToken: string): Promise<BillingUsageStats> {
    return fetchWithAuth<BillingUsageStats>(
      `${BILLING_SERVICE_URL}/billing/usage`,
      accessToken
    );
  },

  /**
   * Get coalition earnings summary
   */
  async getCoalitionEarnings(accessToken: string): Promise<CoalitionSummary> {
    return fetchWithAuth<CoalitionSummary>(
      `${BILLING_SERVICE_URL}/billing/coalition`,
      accessToken
    );
  },

  /**
   * Create a Stripe Checkout session for upgrading
   */
  async createCheckout(
    accessToken: string,
    tier: string,
    billingCycle: 'monthly' | 'annual'
  ): Promise<CheckoutResponse> {
    return fetchWithAuth<CheckoutResponse>(
      `${BILLING_SERVICE_URL}/billing/checkout`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ tier, billing_cycle: billingCycle }),
      }
    );
  },

  /**
   * Get Stripe Billing Portal URL
   */
  async getBillingPortal(accessToken: string): Promise<PortalResponse> {
    return fetchWithAuth<PortalResponse>(
      `${BILLING_SERVICE_URL}/billing/portal`,
      accessToken
    );
  },

  /**
   * Upgrade subscription
   */
  async upgradeSubscription(
    accessToken: string,
    targetTier: string,
    billingCycle: 'monthly' | 'annual'
  ): Promise<UpgradeResponse> {
    return fetchWithAuth<UpgradeResponse>(
      `${BILLING_SERVICE_URL}/billing/upgrade`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ target_tier: targetTier, billing_cycle: billingCycle }),
      }
    );
  },

  /**
   * Cancel subscription
   */
  async cancelSubscription(accessToken: string, subscriptionId: string): Promise<void> {
    await fetchWithAuth(
      `${BILLING_SERVICE_URL}/billing/subscription/${subscriptionId}`,
      accessToken,
      { method: 'DELETE' }
    );
  },

  /**
   * Legacy method for backward compatibility
   */
  async updateSubscription(accessToken: string, plan: string): Promise<UpgradeResponse> {
    // Extract tier and billing cycle from plan ID (e.g., "pro-monthly" -> "professional", "monthly")
    const [tierPart, cyclePart] = plan.split('-');
    const tier = tierPart === 'pro' ? 'professional' : tierPart;
    const billingCycle = (cyclePart as 'monthly' | 'annual') || 'monthly';
    
    return this.upgradeSubscription(accessToken, tier, billingCycle);
  },
  // ============================================
  // Ghost Integration (enterprise-api)
  // ============================================

  async getGhostIntegration(accessToken: string): Promise<GhostIntegrationResponse | null> {
    try {
      return await fetchWithAuth<GhostIntegrationResponse>(
        `${API_BASE_URL}/integrations/ghost`,
        accessToken
      );
    } catch (error) {
      if (error instanceof ApiError && error.statusCode === 404) {
        return null;
      }
      throw error;
    }
  },

  async createGhostIntegration(
    accessToken: string,
    payload: GhostIntegrationCreatePayload
  ): Promise<GhostIntegrationResponse> {
    return fetchWithAuth<GhostIntegrationResponse>(
      `${API_BASE_URL}/integrations/ghost`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    );
  },

  async deleteGhostIntegration(accessToken: string): Promise<void> {
    await fetch(`${API_BASE_URL}/integrations/ghost`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
    });
  },

  async regenerateGhostToken(accessToken: string): Promise<GhostTokenRegenerateResponse> {
    return fetchWithAuth<GhostTokenRegenerateResponse>(
      `${API_BASE_URL}/integrations/ghost/regenerate-token`,
      accessToken,
      { method: 'POST' }
    );
  },

  // Generic HTTP methods for flexibility
  async get<T = unknown>(url: string, accessToken?: string): Promise<{ data: T }> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'GET',
      headers,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Request failed' }));
      throw new ApiError(error.message || 'Request failed', response.status);
    }
    
    const data = await response.json();
    return { data };
  },

  async post<T = unknown>(url: string, body?: unknown, accessToken?: string): Promise<{ data: T }> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'POST',
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Request failed' }));
      throw new ApiError(error.message || 'Request failed', response.status);
    }
    
    const data = await response.json();
    return { data };
  },

  async patch<T = unknown>(url: string, body?: unknown, accessToken?: string): Promise<{ data: T }> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'PATCH',
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Request failed' }));
      throw new ApiError(error.message || 'Request failed', response.status);
    }
    
    const data = await response.json();
    return { data };
  },

  async delete<T = unknown>(url: string, accessToken?: string): Promise<{ data: T }> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'DELETE',
      headers,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Request failed' }));
      throw new ApiError(error.message || 'Request failed', response.status);
    }
    
    const data = await response.json().catch(() => ({}));
    return { data };
  },

  // ============================================
  // Admin Analytics (Usage Counts & Activity Logs)
  // ============================================

  /**
   * Get usage counts for multiple users (admin only)
   */
  async getAdminUsageCounts(accessToken: string, userIds: string[], days: number = 30): Promise<Record<string, number>> {
    const response = await fetch(`${ANALYTICS_SERVICE_URL}/analytics/admin/usage-counts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ user_ids: userIds, days }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch usage counts');
    }
    
    const data = await response.json();
    return data.usage_counts || {};
  },

  /**
   * Get activity logs for a specific user (admin only)
   */
  async getUserActivityLogs(
    accessToken: string,
    userId: string,
    options: { days?: number; limit?: number; offset?: number; metricType?: string } = {}
  ): Promise<{
    activities: Array<{
      id: string;
      type: string;
      description: string;
      timestamp: string;
      metadata: Record<string, any>;
    }>;
    total: number;
    limit: number;
    offset: number;
    has_more: boolean;
  }> {
    const params = new URLSearchParams();
    if (options.days) params.append('days', options.days.toString());
    if (options.limit) params.append('limit', options.limit.toString());
    if (options.offset) params.append('offset', options.offset.toString());
    if (options.metricType) params.append('metric_type', options.metricType);

    const response = await fetchWithAuth<any>(
      `${ANALYTICS_SERVICE_URL}/analytics/user/${userId}/activity?${params.toString()}`,
      accessToken
    );
    
    return response;
  },
};

// Ghost Integration types (TEAM_187)
interface GhostIntegrationCreatePayload {
  ghost_url: string;
  ghost_admin_api_key: string;
  auto_sign_on_publish?: boolean;
  auto_sign_on_update?: boolean;
  manifest_mode?: string;
  segmentation_level?: string;
  badge_enabled?: boolean;
}

interface GhostIntegrationResponse {
  id: string;
  organization_id: string;
  ghost_url: string;
  ghost_admin_api_key_masked: string;
  auto_sign_on_publish: boolean;
  auto_sign_on_update: boolean;
  manifest_mode: string;
  segmentation_level: string;
  badge_enabled: boolean;
  is_active: boolean;
  webhook_url: string;
  webhook_token: string | null;
  last_webhook_at: string | null;
  last_sign_at: string | null;
  sign_count: string;
  created_at: string | null;
  updated_at: string | null;
}

interface GhostTokenRegenerateResponse {
  webhook_url: string;
  webhook_token: string;
}

export default apiClient;
export { ApiError };
export type { 
  ApiKeyInfo, 
  ApiKeyCreateResponse, 
  OrganizationInfo,
  OrganizationCreateResponse,
  DomainClaimInfo,
  DomainClaimResponse,
  UsageStats, 
  AnalyticsReport, 
  TimeSeriesData,
  PlanInfo,
  SubscriptionInfo,
  Invoice,
  CheckoutResponse,
  PortalResponse,
  UpgradeResponse,
  UsageMetric,
  BillingUsageStats,
  CoalitionSummary,
  // TEAM_006: API Access Gating
  ApiAccessStatusType,
  ApiAccessStatusResponse,
  ApiAccessRequestResponse,
  PendingAccessRequest,
  // TEAM_044: C2PA Templates
  C2PATemplate,
  C2PATemplateListResponse,
  // TEAM_187: Ghost Integration
  GhostIntegrationCreatePayload,
  GhostIntegrationResponse,
  GhostTokenRegenerateResponse,
};
