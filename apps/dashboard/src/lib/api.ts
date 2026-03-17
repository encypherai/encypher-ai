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

// All services route through the same API gateway; no separate microservice URLs.
// Use API_BASE_URL directly for all endpoints.

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
  account_type?: AccountType | null;
  display_name?: string | null;
  dashboard_layout?: DashboardLayoutPreference | null;
  publisher_platform?: PublisherPlatform | null;
  publisher_platform_custom?: string | null;
  signing_identity_mode?: SigningIdentityMode | null;
  signing_identity_custom_label?: string | null;
  anonymous_publisher?: boolean;
  add_ons?: Record<string, unknown>;
  tier: string;
  max_seats: number;
  subscription_status: string;
  created_at: string;
}

interface WordPressIntegrationStatus {
  install_id?: string;
  connection_status?: string;
  site_url?: string | null;
  admin_url?: string | null;
  site_name?: string | null;
  environment?: string | null;
  organization_id?: string | null;
  organization_name?: string | null;
  plugin_version?: string | null;
  plugin_installed?: boolean;
  connection_tested?: boolean;
  last_connection_checked_at?: string | null;
  last_signed_at?: string | null;
  last_signed_post_id?: number | null;
  last_signed_post_url?: string | null;
  signed_post_count?: number | null;
  last_verified_at?: string | null;
  verified_post_count?: number | null;
  last_verification_status?: string | null;
  install_count?: number;
  queued_action_count?: number;
  installs?: WordPressInstallStatus[];
  remote_actions?: WordPressRemoteAction[];
  recent_events?: WordPressVerificationEvent[];
  updated_at?: string | null;
}

interface WordPressInstallStatus {
  install_id: string;
  site_url?: string | null;
  admin_url?: string | null;
  site_name?: string | null;
  environment?: string | null;
  network_id?: string | null;
  blog_id?: number | null;
  is_multisite?: boolean;
  is_primary?: boolean;
  connection_status?: string | null;
  connection_tested?: boolean;
  plugin_installed?: boolean;
  plugin_version?: string | null;
  organization_id?: string | null;
  organization_name?: string | null;
  last_connection_checked_at?: string | null;
  last_signed_at?: string | null;
  last_signed_post_id?: number | null;
  last_signed_post_url?: string | null;
  signed_post_count?: number | null;
  last_verified_at?: string | null;
  verified_post_count?: number | null;
  last_verification_status?: string | null;
  updated_at?: string | null;
}

interface WordPressRemoteAction {
  action_id: string;
  install_id: string;
  action_type: string;
  note?: string | null;
  status: string;
  requested_at?: string | null;
  completed_at?: string | null;
  result_message?: string | null;
}

interface WordPressVerificationEvent {
  event_id: string;
  type: string;
  install_id: string;
  post_id?: number | null;
  post_url?: string | null;
  valid?: boolean;
  tampered?: boolean;
  status?: string | null;
  verified_at?: string | null;
  source?: string | null;
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

interface VerificationDomainInfo {
  domain: string | null;
  status: string | null;
  verified_at: string | null;
  cname_target: string | null;
  txt_record: string | null;
  txt_host: string | null;
}

interface VerificationDomainSetResponse {
  domain: string;
  status: string;
  instructions: {
    cname: { host: string; target: string; type: string };
    txt: { host: string; value: string; type: string };
  };
  note: string;
}

interface VerificationDomainVerifyResponse {
  verified: boolean;
  status: string;
  domain?: string;
  verified_at?: string;
  errors?: string[];
}

interface AnalyticsReport {
  user_id: string;
  period_start: string;
  period_end: string;
  usage_stats: UsageStats;
  time_series: TimeSeriesData[];
}

// Payment method types
interface PaymentMethod {
  id: string;
  brand: string;
  last4: string;
  exp_month: number;
  exp_year: number;
  is_default: boolean;
}

interface OveragePreferences {
  overage_enabled: boolean;
  overage_cap_cents: number | null;
  has_payment_method: boolean;
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

interface AddOnCheckoutRequest {
  add_on: string;
  quantity: number;
  success_url?: string;
  cancel_url?: string;
}

interface AddOnSubscriptionCheckoutRequest {
  add_on: string;
  success_url?: string;
  cancel_url?: string;
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

interface AdminNewsletterSubscriber {
  id: number;
  email: string;
  active: boolean;
  status: 'active' | 'unsubscribed' | 'invalid';
  status_reason?: string | null;
  source?: string | null;
  subscribed_at?: string | null;
}

interface AdminNewsletterSubscribersResponse {
  subscribers: AdminNewsletterSubscriber[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// TEAM_191: Onboarding Checklist types
interface OnboardingStep {
  step_id: string;
  title: string;
  description: string;
  completed: boolean;
  completed_at: string | null;
  action_url: string | null;
}

interface OnboardingStatusResponse {
  steps: OnboardingStep[];
  completed_count: number;
  total_count: number;
  all_completed: boolean;
  dismissed: boolean;
  completed_at: string | null;
}

// TEAM_191: Setup Wizard types
type AccountType = 'individual' | 'organization';
type DashboardLayoutPreference = 'publisher' | 'enterprise';
type WorkflowCategory = 'media_publishing' | 'enterprise' | 'ai_provenance_governance';
type PublisherPlatform = 'wordpress' | 'ghost' | 'substack' | 'medium' | 'custom' | 'custom_cms' | 'other';

interface SetupStatusResponse {
  setup_completed: boolean;
  setup_completed_at: string | null;
  account_type: AccountType | null;
  display_name: string | null;
  workflow_category: WorkflowCategory | null;
  dashboard_layout: DashboardLayoutPreference | null;
  publisher_platform: PublisherPlatform | null;
  publisher_platform_custom: string | null;
}

interface PublisherSettings {
  display_name: string | null;
  account_type: AccountType | null;
  dashboard_layout?: DashboardLayoutPreference | null;
  publisher_platform?: PublisherPlatform | null;
  publisher_platform_custom?: string | null;
  signing_identity_mode?: SigningIdentityMode | null;
  signing_identity_custom_label?: string | null;
  custom_signing_identity_enabled?: boolean;
  anonymous_publisher: boolean;
}

type SigningIdentityMode = 'organization_name' | 'organization_and_author' | 'custom';

interface MfaStatusResponse {
  totp_enabled: boolean;
  backup_codes_remaining: number;
  passkeys_count: number;
  passkeys: Array<{
    credential_id: string;
    name: string;
    sign_count?: number;
    created_at?: string;
  }>;
}

interface TotpSetupResponse {
  secret: string;
  provisioning_uri: string;
  backup_codes: string[];
}

interface MfaLoginChallenge {
  mfa_required: boolean;
  mfa_token: string;
  available_methods: string[];
}

interface PasskeyOptionsResponse {
  options_json: string;
}

class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public code?: string,
    public nextAction?: string,
    public docsUrl?: string,
    public fieldErrors?: Record<string, string[]>
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

  const startMs = Date.now();

  const response = await fetch(url, {
    ...options,
    headers,
  });

  const elapsedMs = Date.now() - startMs;

  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`;
    let code: string | undefined;
    let nextAction: string | undefined;
    let docsUrl: string | undefined;
    let fieldErrors: Record<string, string[]> | undefined;
    try {
      const errorData = await response.json();
      // Envelope format: { error: { code, message, next_action, docs_url, details } }
      const err = errorData.error;
      if (err && typeof err === 'object') {
        errorMessage = err.message || errorMessage;
        code = err.code;
        nextAction = err.next_action;
        docsUrl = err.docs_url;
        fieldErrors = err.details?.field_errors;
      } else {
        // Legacy format: { detail: "..." }
        errorMessage = errorData.detail || errorData.message || errorMessage;
      }
    } catch {
      // Ignore JSON parse errors
    }
    if (process.env.NODE_ENV === 'development') {
      console.debug(`[api] ERROR ${response.status} ${url} (${elapsedMs}ms)`);
    }
    throw new ApiError(errorMessage, response.status, code, nextAction, docsUrl, fieldErrors);
  }

  if (process.env.NODE_ENV === 'development') {
    console.debug(`[api] OK ${response.status} ${url} (${elapsedMs}ms)`);
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
      `${API_BASE_URL}/keys${query ? `?${query}` : ''}`,
      accessToken
    );
    return response;
  },

  /**
   * List domain claims for an organization
   */
  async listDomainClaims(accessToken: string, organizationId: string): Promise<DomainClaimInfo[]> {
    const response = await fetchWithAuth<{ success: boolean; data: DomainClaimInfo[] }>(
      `${API_BASE_URL}/organizations/${organizationId}/domain-claims`,
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
      `${API_BASE_URL}/organizations/${organizationId}/domain-claims`,
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
      `${API_BASE_URL}/organizations/${organizationId}/domain-claims/${claimId}/verify-dns`,
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
      `${API_BASE_URL}/organizations/${organizationId}/domain-claims/${claimId}/auto-join`,
      accessToken,
      {
        method: 'PATCH',
        body: JSON.stringify({ enabled }),
      }
    );
    return response;
  },

  /**
   * Delete a domain claim
   */
  async deleteDomainClaim(
    accessToken: string,
    organizationId: string,
    claimId: string
  ): Promise<DomainClaimResponse> {
    const response = await fetchWithAuth<DomainClaimResponse>(
      `${API_BASE_URL}/organizations/${organizationId}/domain-claims/${claimId}`,
      accessToken,
      { method: 'DELETE' }
    );
    return response;
  },

  // ── Custom Verification Domain ──

  async getVerificationDomain(
    accessToken: string,
    organizationId: string
  ): Promise<VerificationDomainInfo> {
    const response = await fetchWithAuth<VerificationDomainInfo>(
      `${API_BASE_URL}/organizations/${organizationId}/verification-domain`,
      accessToken,
    );
    return response;
  },

  async setVerificationDomain(
    accessToken: string,
    organizationId: string,
    domain: string
  ): Promise<VerificationDomainSetResponse> {
    const response = await fetchWithAuth<VerificationDomainSetResponse>(
      `${API_BASE_URL}/organizations/${organizationId}/verification-domain`,
      accessToken,
      { method: 'POST', body: JSON.stringify({ domain }) }
    );
    return response;
  },

  async verifyVerificationDomain(
    accessToken: string,
    organizationId: string
  ): Promise<VerificationDomainVerifyResponse> {
    const response = await fetchWithAuth<VerificationDomainVerifyResponse>(
      `${API_BASE_URL}/organizations/${organizationId}/verification-domain/verify`,
      accessToken,
      { method: 'POST' }
    );
    return response;
  },

  async removeVerificationDomain(
    accessToken: string,
    organizationId: string
  ): Promise<{ removed: boolean }> {
    const response = await fetchWithAuth<{ removed: boolean }>(
      `${API_BASE_URL}/organizations/${organizationId}/verification-domain`,
      accessToken,
      { method: 'DELETE' }
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
      `${API_BASE_URL}/keys/generate`,
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

  async getWordPressIntegrationStatus(accessToken: string): Promise<WordPressIntegrationStatus> {
    const response = await fetchWithAuth<{ success: boolean; data: WordPressIntegrationStatus }>(
      `${API_BASE_URL}/integrations/wordpress/status`,
      accessToken
    );
    return response.data ?? {};
  },

  async queueWordPressInstallAction(
    accessToken: string,
    installId: string,
    actionType: 'refresh_status' | 'test_connection',
    note?: string
  ): Promise<WordPressIntegrationStatus> {
    const response = await fetchWithAuth<{ success: boolean; data: WordPressIntegrationStatus }>(
      `${API_BASE_URL}/integrations/wordpress/${installId}/actions`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ action_type: actionType, note }),
      }
    );
    return response.data ?? {};
  },

  /**
   * Delete (revoke) an API key
   */
  async deleteApiKey(accessToken: string, keyId: string): Promise<void> {
    await fetchWithAuth<{ message: string }>(
      `${API_BASE_URL}/keys/${keyId}`,
      accessToken,
      { method: 'DELETE' }
    );
  },

  /**
   * Revoke all API keys created by a specific user in an organization
   */
  async revokeKeysByUser(accessToken: string, organizationId: string, userId: string): Promise<{ revoked_count: number }> {
    return fetchWithAuth<{ revoked_count: number }>(
      `${API_BASE_URL}/keys/revoke-by-user`,
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
      `${API_BASE_URL}/organizations`,
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
      `${API_BASE_URL}/keys/${keyId}/usage`,
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
      `${API_BASE_URL}/analytics/usage?days=${days}`,
      accessToken
    );
  },

  /**
   * Get comprehensive analytics report
   */
  async getAnalyticsReport(accessToken: string, days: number = 30): Promise<AnalyticsReport> {
    return fetchWithAuth<AnalyticsReport>(
      `${API_BASE_URL}/analytics/report?days=${days}`,
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
      `${API_BASE_URL}/analytics/timeseries?metric_type=${metricType}&days=${days}&interval=${interval}`,
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
      `${API_BASE_URL}/auth/verify`,
      accessToken,
      { method: 'POST' }
    );
  },

  /**
   * Logout - revoke refresh token
   */
  async logout(accessToken: string): Promise<void> {
    await fetchWithAuth(
      `${API_BASE_URL}/auth/logout`,
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
      `${API_BASE_URL}/auth/api-access-status`,
      accessToken
    );
    return response.data;
  },

  /**
   * List newsletter subscribers (super admin only)
   */
  async getAdminNewsletterSubscribers(
    accessToken: string,
    options?: {
      page?: number;
      pageSize?: number;
      activeOnly?: boolean;
    }
  ): Promise<AdminNewsletterSubscribersResponse> {
    const params = new URLSearchParams();
    if (options?.page) params.append('page', options.page.toString());
    if (options?.pageSize) params.append('page_size', options.pageSize.toString());
    if (options?.activeOnly) params.append('active_only', 'true');

    const queryString = params.toString();
    const url = `${API_BASE_URL}/auth/admin/newsletter-subscribers${queryString ? `?${queryString}` : ''}`;

    const response = await fetchWithAuth<{ success: boolean; data: AdminNewsletterSubscribersResponse }>(
      url,
      accessToken
    );
    return response.data;
  },

  async updateAdminNewsletterSubscriberStatus(
    accessToken: string,
    subscriberId: number,
    status: 'active' | 'unsubscribed' | 'invalid',
    reason?: string
  ): Promise<AdminNewsletterSubscriber> {
    const response = await fetchWithAuth<{ success: boolean; data: AdminNewsletterSubscriber }>(
      `${API_BASE_URL}/auth/admin/newsletter-subscribers/${subscriberId}/status`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ status, reason }),
      }
    );
    return response.data;
  },

  async deleteAdminNewsletterSubscriber(accessToken: string, subscriberId: number): Promise<void> {
    await fetchWithAuth<{ success: boolean; data: { deleted: boolean; id: number } }>(
      `${API_BASE_URL}/auth/admin/newsletter-subscribers/${subscriberId}`,
      accessToken,
      { method: 'DELETE' }
    );
  },

  /**
   * Request API access with a use case description
   */
  async requestApiAccess(accessToken: string, useCase: string): Promise<ApiAccessRequestResponse> {
    const response = await fetchWithAuth<{ success: boolean; data: ApiAccessRequestResponse }>(
      `${API_BASE_URL}/auth/request-api-access`,
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
        `${API_BASE_URL}/auth/admin/is-super-admin`,
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
      `${API_BASE_URL}/auth/admin/organizations/search?${params.toString()}`,
      accessToken
    );
    return response.data;
  },

  /**
   * Get pending API access requests (admin only)
   */
  async getPendingAccessRequests(accessToken: string): Promise<PendingAccessRequest[]> {
    const response = await fetchWithAuth<{ success: boolean; data: { requests: PendingAccessRequest[]; total: number } }>(
      `${API_BASE_URL}/auth/admin/pending-access-requests`,
      accessToken
    );
    return response.data.requests;
  },

  /**
   * Approve a user's API access request (admin only)
   */
  async approveApiAccess(accessToken: string, userId: string): Promise<void> {
    await fetchWithAuth(
      `${API_BASE_URL}/auth/admin/approve-api-access`,
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
      `${API_BASE_URL}/auth/admin/deny-api-access`,
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
      `${API_BASE_URL}/auth/admin/set-api-access-status`,
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
      `${API_BASE_URL}/auth/verify`,
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
        `${API_BASE_URL}/auth/profile`,
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
      `${API_BASE_URL}/auth/admin/stats`,
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
    const url = `${API_BASE_URL}/auth/admin/users${queryString ? `?${queryString}` : ''}`;

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
      `${API_BASE_URL}/auth/admin/users/update-tier`,
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
      `${API_BASE_URL}/auth/admin/users/update-status`,
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
      `${API_BASE_URL}/auth/admin/users/update-role`,
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
    const response = await fetch(`${API_BASE_URL}/billing/plans`);
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
        `${API_BASE_URL}/billing/subscription`,
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
        `${API_BASE_URL}/billing/invoices`,
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
      `${API_BASE_URL}/billing/usage`,
      accessToken
    );
  },

  /**
   * Get coalition earnings summary
   */
  async getCoalitionEarnings(accessToken: string): Promise<CoalitionSummary> {
    return fetchWithAuth<CoalitionSummary>(
      `${API_BASE_URL}/billing/coalition`,
      accessToken
    );
  },

  // ============================================
  // Publisher Value Journey (TEAM_225)
  // ============================================

  /**
   * Get publisher progression status (6-stage value journey)
   */
  async getProgressionStatus(accessToken: string): Promise<unknown> {
    return fetchWithAuth(
      `${API_BASE_URL}/onboarding/progression-status`,
      accessToken
    );
  },

  /**
   * Get content spread analytics (external domain detections)
   */
  async getContentSpread(accessToken: string, days = 30): Promise<unknown> {
    return fetchWithAuth(
      `${API_BASE_URL}/rights/analytics/content-spread?days=${days}`,
      accessToken
    );
  },

  /**
   * Get public coalition stats (no auth required)
   */
  async getPublicCoalitionStats(): Promise<{ coalition_members: number; total_signed_documents: number; as_of: string }> {
    const res = await fetch(`${API_BASE_URL}/coalition/public/stats`);
    if (!res.ok) throw new Error('Failed to fetch coalition stats');
    return res.json();
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
      `${API_BASE_URL}/billing/checkout`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ tier, billing_cycle: billingCycle }),
      }
    );
  },

  async createAddOnCheckout(
    accessToken: string,
    payload: AddOnCheckoutRequest
  ): Promise<CheckoutResponse> {
    return fetchWithAuth<CheckoutResponse>(
      `${API_BASE_URL}/billing/checkout/add-on`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    );
  },

  async createAddOnSubscriptionCheckout(
    accessToken: string,
    payload: AddOnSubscriptionCheckoutRequest
  ): Promise<CheckoutResponse> {
    return fetchWithAuth<CheckoutResponse>(
      `${API_BASE_URL}/billing/checkout/add-on-subscription`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    );
  },

  /**
   * Get Stripe Billing Portal URL
   */
  async getBillingPortal(accessToken: string): Promise<PortalResponse> {
    return fetchWithAuth<PortalResponse>(
      `${API_BASE_URL}/billing/portal`,
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
      `${API_BASE_URL}/billing/upgrade`,
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
      `${API_BASE_URL}/billing/subscription/${subscriptionId}`,
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
  // Payment Methods (billing-service)
  // ============================================

  async getPaymentMethods(accessToken: string): Promise<PaymentMethod[]> {
    return fetchWithAuth<PaymentMethod[]>(
      `${API_BASE_URL}/billing/payment-methods`,
      accessToken
    );
  },

  async createPaymentMethodSetup(accessToken: string): Promise<{ checkout_url: string }> {
    return fetchWithAuth<{ checkout_url: string }>(
      `${API_BASE_URL}/billing/payment-methods/setup`,
      accessToken,
      { method: 'POST' }
    );
  },

  async deletePaymentMethod(accessToken: string, pmId: string): Promise<void> {
    await fetchWithAuth(
      `${API_BASE_URL}/billing/payment-methods/${pmId}`,
      accessToken,
      { method: 'DELETE' }
    );
  },

  async setDefaultPaymentMethod(accessToken: string, pmId: string): Promise<void> {
    await fetchWithAuth(
      `${API_BASE_URL}/billing/payment-methods/${pmId}/default`,
      accessToken,
      { method: 'POST' }
    );
  },

  async getOveragePreferences(accessToken: string): Promise<OveragePreferences> {
    return fetchWithAuth<OveragePreferences>(
      `${API_BASE_URL}/billing/overage-preferences`,
      accessToken
    );
  },

  async updateOveragePreferences(accessToken: string, prefs: Partial<OveragePreferences>): Promise<void> {
    await fetchWithAuth(
      `${API_BASE_URL}/billing/overage-preferences`,
      accessToken,
      {
        method: 'PUT',
        body: JSON.stringify(prefs),
      }
    );
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

  // ============================================
  // Admin Analytics (Usage Counts & Activity Logs)
  // ============================================

  /**
   * Get usage counts for multiple users (admin only)
   */
  async getAdminUsageCounts(accessToken: string, userIds: string[], days: number = 30): Promise<Record<string, number>> {
    const response = await fetch(`${API_BASE_URL}/analytics/admin/usage-counts`, {
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
      `${API_BASE_URL}/analytics/user/${userId}/activity?${params.toString()}`,
      accessToken
    );

    return response;
  },

  // ============================================
  // Onboarding Checklist (auth-service) - TEAM_191
  // ============================================

  /**
   * Get the current onboarding checklist status
   */
  async getOnboardingStatus(accessToken: string): Promise<OnboardingStatusResponse> {
    const response = await fetchWithAuth<{ success: boolean; data: OnboardingStatusResponse }>(
      `${API_BASE_URL}/auth/onboarding-status`,
      accessToken
    );
    return response.data;
  },

  /**
   * Mark an onboarding step as complete
   */
  async completeOnboardingStep(accessToken: string, stepId: string): Promise<OnboardingStatusResponse> {
    const response = await fetchWithAuth<{ success: boolean; data: OnboardingStatusResponse }>(
      `${API_BASE_URL}/auth/onboarding/complete-step`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ step_id: stepId }),
      }
    );
    return response.data;
  },

  /**
   * Dismiss the onboarding checklist permanently
   */
  async dismissOnboarding(accessToken: string): Promise<OnboardingStatusResponse> {
    const response = await fetchWithAuth<{ success: boolean; data: OnboardingStatusResponse }>(
      `${API_BASE_URL}/auth/onboarding/dismiss`,
      accessToken,
      { method: 'POST' }
    );
    return response.data;
  },

  // ============================================
  // Setup Wizard (auth-service) - TEAM_191
  // ============================================

  /**
   * Check if the user has completed the mandatory setup wizard
   */
  async getSetupStatus(accessToken: string): Promise<SetupStatusResponse> {
    const response = await fetchWithAuth<{ success: boolean; data: SetupStatusResponse }>(
      `${API_BASE_URL}/auth/setup-status`,
      accessToken
    );
    return response.data;
  },

  /**
   * Complete the mandatory setup wizard with publisher identity
   */
  async completeSetup(accessToken: string, data: {
    account_type: AccountType;
    display_name: string;
    workflow_category: WorkflowCategory;
    dashboard_layout: DashboardLayoutPreference;
    publisher_platform?: PublisherPlatform;
    publisher_platform_custom?: string;
  }): Promise<SetupStatusResponse> {
    const response = await fetchWithAuth<{ success: boolean; data: SetupStatusResponse }>(
      `${API_BASE_URL}/auth/setup/complete`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
    return response.data;
  },

  /**
   * Update publisher identity settings (display name, anonymous toggle)
   */
  async updatePublisherSettings(
    accessToken: string,
    orgId: string,
    data: {
      display_name?: string;
      dashboard_layout?: DashboardLayoutPreference;
      publisher_platform?: PublisherPlatform;
      publisher_platform_custom?: string;
      signing_identity_mode?: SigningIdentityMode;
      anonymous_publisher?: boolean;
    }
  ): Promise<PublisherSettings> {
    const response = await fetchWithAuth<{ success: boolean; data: PublisherSettings }>(
      `${API_BASE_URL}/organizations/${orgId}/publisher-settings`,
      accessToken,
      {
        method: 'PATCH',
        body: JSON.stringify(data),
      }
    );
    return response.data;
  },

  async getMfaStatus(accessToken: string): Promise<MfaStatusResponse> {
    const response = await fetchWithAuth<{ success: boolean; data: MfaStatusResponse }>(
      `${API_BASE_URL}/auth/mfa/status`,
      accessToken
    );
    return response.data;
  },

  async beginTotpSetup(accessToken: string): Promise<TotpSetupResponse> {
    const response = await fetchWithAuth<{ success: boolean; data: TotpSetupResponse }>(
      `${API_BASE_URL}/auth/mfa/totp/setup`,
      accessToken,
      { method: 'POST' }
    );
    return response.data;
  },

  async confirmTotpSetup(accessToken: string, code: string): Promise<{ enabled: boolean; recovery_codes_remaining: number }> {
    const response = await fetchWithAuth<{ success: boolean; data: { enabled: boolean; recovery_codes_remaining: number } }>(
      `${API_BASE_URL}/auth/mfa/totp/confirm`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ code }),
      }
    );
    return response.data;
  },

  async disableTotp(accessToken: string, code: string): Promise<void> {
    await fetchWithAuth(
      `${API_BASE_URL}/auth/mfa/totp/disable`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ code }),
      }
    );
  },

  async completeMfaLogin(mfaToken: string, mfaCode: string): Promise<unknown> {
    const response = await fetch(`${API_BASE_URL}/auth/login/mfa/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mfa_token: mfaToken, mfa_code: mfaCode }),
    });
    const payload = await response.json();
    if (!response.ok || !payload.success) {
      throw new ApiError(payload.detail || payload.error?.message || 'MFA login failed', response.status);
    }
    return payload.data;
  },

  async startPasskeyRegistration(accessToken: string): Promise<PasskeyOptionsResponse> {
    const response = await fetchWithAuth<{ success: boolean; data: PasskeyOptionsResponse }>(
      `${API_BASE_URL}/auth/passkeys/register/options`,
      accessToken,
      { method: 'POST' }
    );
    return response.data;
  },

  async completePasskeyRegistration(accessToken: string, credential: Record<string, unknown>, name?: string): Promise<unknown> {
    const response = await fetchWithAuth<{ success: boolean; data: unknown }>(
      `${API_BASE_URL}/auth/passkeys/register/complete`,
      accessToken,
      {
        method: 'POST',
        body: JSON.stringify({ credential, name }),
      }
    );
    return response.data;
  },

  async startPasskeyAuthentication(email: string): Promise<PasskeyOptionsResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/passkeys/authenticate/options`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    const payload = await response.json();
    if (!response.ok || !payload.success) {
      throw new ApiError(payload.detail || payload.error?.message || 'Passkey start failed', response.status);
    }
    return payload.data;
  },

  async completePasskeyAuthentication(email: string, credential: Record<string, unknown>): Promise<unknown> {
    const response = await fetch(`${API_BASE_URL}/auth/passkeys/authenticate/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, credential }),
    });
    const payload = await response.json();
    if (!response.ok || !payload.success) {
      throw new ApiError(payload.detail || payload.error?.message || 'Passkey login failed', response.status);
    }
    return payload.data;
  },

  async deletePasskey(accessToken: string, credentialId: string): Promise<void> {
    await fetchWithAuth(
      `${API_BASE_URL}/auth/passkeys/${encodeURIComponent(credentialId)}`,
      accessToken,
      { method: 'DELETE' }
    );
  },

  // ============================================
  // Rights Management
  // ============================================

  async getRightsProfile(accessToken: string): Promise<RightsProfile | null> {
    try {
      return await fetchWithAuth<RightsProfile>(
        `${API_BASE_URL}/rights/profile`,
        accessToken
      );
    } catch {
      return null;
    }
  },

  async upsertRightsProfile(accessToken: string, profile: Partial<RightsProfile>): Promise<RightsProfile> {
    return fetchWithAuth<RightsProfile>(
      `${API_BASE_URL}/rights/profile`,
      accessToken,
      { method: 'PUT', body: JSON.stringify(profile) }
    );
  },

  async getRightsTemplates(accessToken: string): Promise<RightsTemplate[]> {
    const response = await fetchWithAuth<RightsTemplate[] | { success: boolean; data: RightsTemplate[] }>(
      `${API_BASE_URL}/rights/templates`,
      accessToken
    );
    return Array.isArray(response) ? response : (response.data ?? []);
  },

  async applyRightsTemplate(accessToken: string, templateId: string): Promise<RightsProfile> {
    return fetchWithAuth<RightsProfile>(
      `${API_BASE_URL}/rights/profile/from-template/${encodeURIComponent(templateId)}`,
      accessToken,
      { method: 'POST' }
    );
  },

  async getDetectionAnalytics(accessToken: string, days = 30): Promise<DetectionSummary> {
    return fetchWithAuth<DetectionSummary>(
      `${API_BASE_URL}/rights/analytics/detections?days=${days}`,
      accessToken
    );
  },

  async getCrawlerAnalytics(accessToken: string, days = 30): Promise<CrawlerAnalytics> {
    return fetchWithAuth<CrawlerAnalytics>(
      `${API_BASE_URL}/rights/analytics/crawlers?days=${days}`,
      accessToken
    );
  },

  async getCrawlerTimeseries(accessToken: string, days = 30): Promise<CrawlerTimeseries> {
    return fetchWithAuth<CrawlerTimeseries>(
      `${API_BASE_URL}/rights/analytics/crawlers/timeseries?days=${days}`,
      accessToken
    );
  },

  async getDiscoveryEvents(
    accessToken: string,
    opts: { days?: number; externalOnly?: boolean; limit?: number; offset?: number } = {}
  ): Promise<ContentDiscoveryListResponse> {
    const params = new URLSearchParams({
      days: String(opts.days ?? 30),
      external_only: String(Boolean(opts.externalOnly)),
      limit: String(opts.limit ?? 50),
      offset: String(opts.offset ?? 0),
    });
    return fetchWithAuth<ContentDiscoveryListResponse>(
      `${API_BASE_URL}/analytics/discovery/events?${params.toString()}`,
      accessToken
    );
  },

  async getDiscoveryDomains(
    accessToken: string,
    opts: { externalOnly?: boolean } = {}
  ): Promise<DomainSummaryResponse> {
    const params = new URLSearchParams({
      external_only: String(Boolean(opts.externalOnly)),
    });
    return fetchWithAuth<DomainSummaryResponse>(
      `${API_BASE_URL}/analytics/discovery/domains?${params.toString()}`,
      accessToken
    );
  },

  async getDiscoveryAlerts(accessToken: string): Promise<DomainAlertsResponse> {
    return fetchWithAuth<DomainAlertsResponse>(
      `${API_BASE_URL}/analytics/discovery/alerts`,
      accessToken
    );
  },

  async acknowledgeDiscoveryAlert(accessToken: string, alertId: string): Promise<DiscoveryResponse> {
    return fetchWithAuth<DiscoveryResponse>(
      `${API_BASE_URL}/analytics/discovery/alerts/${encodeURIComponent(alertId)}/ack`,
      accessToken,
      { method: 'POST' }
    );
  },

  async getCdnIntegration(accessToken: string): Promise<CdnIntegrationResponse | null> {
    try {
      return await fetchWithAuth<CdnIntegrationResponse>(
        `${API_BASE_URL}/cdn/cloudflare`,
        accessToken
      );
    } catch {
      return null;
    }
  },

  async saveCdnIntegration(
    accessToken: string,
    payload: CdnIntegrationCreate
  ): Promise<CdnIntegrationResponse> {
    return fetchWithAuth<CdnIntegrationResponse>(
      `${API_BASE_URL}/cdn/cloudflare`,
      accessToken,
      { method: 'POST', body: JSON.stringify(payload) }
    );
  },

  async deleteCdnIntegration(accessToken: string): Promise<void> {
    await fetchWithAuth<void>(
      `${API_BASE_URL}/cdn/cloudflare`,
      accessToken,
      { method: 'DELETE' }
    );
  },

  async listNotices(accessToken: string): Promise<FormalNotice[]> {
    const response = await fetchWithAuth<FormalNotice[]>(
      `${API_BASE_URL}/notices/`,
      accessToken
    );
    // notices endpoint returns array directly
    return Array.isArray(response) ? response : [];
  },

  async createNotice(accessToken: string, payload: {
    recipient_entity: string;
    recipient_contact?: string;
    document_ids?: string[];
    violation_type?: string;
    notice_text?: string;
  }): Promise<FormalNotice> {
    const response = await fetchWithAuth<FormalNotice>(
      `${API_BASE_URL}/notices/create`,
      accessToken,
      { method: 'POST', body: JSON.stringify(payload) }
    );
    return response;
  },

  async deliverNotice(accessToken: string, noticeId: string): Promise<FormalNotice> {
    const response = await fetchWithAuth<FormalNotice>(
      `${API_BASE_URL}/notices/${encodeURIComponent(noticeId)}/deliver`,
      accessToken,
      { method: 'POST' }
    );
    return response;
  },

  async listLicensingRequests(accessToken: string): Promise<LicensingRequest[]> {
    const response = await fetchWithAuth<LicensingRequest[]>(
      `${API_BASE_URL}/rights-licensing/requests`,
      accessToken
    );
    return Array.isArray(response) ? response : [];
  },

  async listLicensingAgreements(accessToken: string): Promise<LicensingAgreement[]> {
    const response = await fetchWithAuth<LicensingAgreement[]>(
      `${API_BASE_URL}/rights-licensing/agreements`,
      accessToken
    );
    return Array.isArray(response) ? response : [];
  },

  async respondToLicensingRequest(
    accessToken: string,
    requestId: string,
    action: 'approve' | 'counter' | 'reject',
    opts?: { message?: string; terms?: Record<string, unknown> }
  ): Promise<Record<string, unknown>> {
    return fetchWithAuth<Record<string, unknown>>(
      `${API_BASE_URL}/rights-licensing/requests/${encodeURIComponent(requestId)}/respond`,
      accessToken,
      {
        method: 'PUT',
        body: JSON.stringify({ action, message: opts?.message ?? '', terms: opts?.terms ?? {} }),
      }
    );
  },

  // ── Rights profile history ────────────────────────────────────────────────

  async getRightsProfileHistory(accessToken: string): Promise<RightsProfileVersion[]> {
    const response = await fetchWithAuth<RightsProfileVersion[] | { success: boolean; data: RightsProfileVersion[] }>(
      `${API_BASE_URL}/rights/profile/history`,
      accessToken
    );
    if (Array.isArray(response)) return response;
    const typed = response as { success: boolean; data: RightsProfileVersion[] };
    return typed.data ?? [];
  },

  // ── Governance: Attestation Policies & Attestations ──────────────────────

  async createAttestationPolicy(
    accessToken: string,
    payload: { name: string; enforcement: string; scope?: string; rules: Array<{ field: string; operator: string; value: unknown; action: string }> }
  ): Promise<any> {
    return fetchWithAuth<any>(
      `${API_BASE_URL}/attestation-policies/`,
      accessToken,
      { method: 'POST', body: JSON.stringify(payload) }
    );
  },

  async listAttestationPolicies(accessToken: string): Promise<any> {
    return fetchWithAuth<any>(`${API_BASE_URL}/attestation-policies/`, accessToken);
  },

  async deleteAttestationPolicy(accessToken: string, policyId: string): Promise<any> {
    return fetchWithAuth<any>(
      `${API_BASE_URL}/attestation-policies/${encodeURIComponent(policyId)}`,
      accessToken,
      { method: 'DELETE' }
    );
  },

  async listAttestations(accessToken: string, params?: { limit?: number }): Promise<any> {
    const query = params?.limit ? `?limit=${params.limit}` : '';
    return fetchWithAuth<any>(`${API_BASE_URL}/attestations/${query}`, accessToken);
  },

  // ── Partners ───────────────────────────────────────────────────────────────

  async getPartnerAggregate(accessToken: string): Promise<any> {
    return fetchWithAuth<any>(`${API_BASE_URL}/partner/portal/aggregate`, accessToken);
  },

  async getPartnerPublishers(accessToken: string): Promise<any> {
    return fetchWithAuth<any>(`${API_BASE_URL}/partner/portal/publishers`, accessToken);
  },

  // ── Compliance ─────────────────────────────────────────────────────────────

  async getComplianceReadiness(accessToken: string): Promise<any> {
    return fetchWithAuth<any>(`${API_BASE_URL}/compliance/readiness`, accessToken);
  },

  // ── Enforcement: Notice Detail ─────────────────────────────────────────────

  async getNoticeDetail(accessToken: string, noticeId: string): Promise<any> {
    return fetchWithAuth<any>(
      `${API_BASE_URL}/notices/${encodeURIComponent(noticeId)}`,
      accessToken
    );
  },

  // ── Quote Integrity ────────────────────────────────────────────────────────

  async verifyQuoteIntegrity(params: {
    quote: string;
    attribution: string;
    org_id?: string;
    doc_id?: string;
    fuzzy_threshold?: number;
  }): Promise<any> {
    return fetchWithAuth<any>(
      `${API_BASE_URL}/verify/quote-integrity`,
      '',
      { method: 'POST', body: JSON.stringify(params) }
    );
  },

  async getNoticeEvidence(accessToken: string, noticeId: string): Promise<EvidencePackage> {
    return fetchWithAuth<EvidencePackage>(
      `${API_BASE_URL}/notices/${encodeURIComponent(noticeId)}/evidence`,
      accessToken
    );
  },

  async downloadEvidencePackagePdf(accessToken: string, noticeId: string): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/notices/${encodeURIComponent(noticeId)}/evidence/pdf`,
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    if (!response.ok) throw new Error('Failed to generate PDF');
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `notice-${noticeId}-evidence.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  },

  // ── SAML SSO Config ──────────────────────────────────────────────────────

  async getSamlConfig(accessToken: string, orgId: string): Promise<any> {
    return fetchWithAuth<any>(
      `${API_BASE_URL}/auth/saml/config/${encodeURIComponent(orgId)}`,
      accessToken
    );
  },

  async updateSamlConfig(accessToken: string, orgId: string, config: Record<string, unknown>): Promise<any> {
    return fetchWithAuth<any>(
      `${API_BASE_URL}/auth/saml/config/${encodeURIComponent(orgId)}`,
      accessToken,
      { method: 'PUT', body: JSON.stringify(config) }
    );
  },

  // ── Bulk Invite ───────────────────────────────────────────────────────────

  async bulkInviteMembers(
    accessToken: string,
    orgId: string,
    invitations: Array<{ email: string; role: string }>
  ): Promise<any> {
    return fetchWithAuth<any>(
      `${API_BASE_URL}/org/members/invite/bulk`,
      accessToken,
      { method: 'POST', body: JSON.stringify({ invitations }) }
    );
  },
};

// ── Rights Management types ───────────────────────────────────────────────────

interface RightsTierPermissions {
  allowed?: boolean;
  requires_license?: boolean;
  license_url?: string | null;
  allowed_purposes?: string[];
  prohibited_purposes?: string[];
}

interface RightsTierAttribution {
  required?: boolean;
  format?: string | null;
  link_back_required?: boolean;
}

interface RightsTier {
  tier?: string;
  usage_type?: string;
  description?: string | null;
  permissions?: RightsTierPermissions;
  attribution?: RightsTierAttribution;
  contact_for_licensing?: string | null;
}

interface RightsProfile {
  id?: string;
  organization_id?: string;
  profile_version?: number;
  is_active?: boolean;
  bronze_tier?: RightsTier | null;
  silver_tier?: RightsTier | null;
  gold_tier?: RightsTier | null;
  contact_email?: string | null;
  notice_endpoint?: string | null;
  effective_date?: string | null;
  created_at?: string;
}

interface RightsTemplate {
  id: string;
  name: string;
  description: string;
  bronze_tier?: RightsTier | null;
  silver_tier?: RightsTier | null;
  gold_tier?: RightsTier | null;
}

interface DetectionSummary {
  organization_id: string;
  period_days: number;
  total_events: number;
  by_source: Record<string, number>;
  by_category: Record<string, number>;
  by_integrity_status: Record<string, number>;
  rights_served_count: number;
  rights_acknowledged_count: number;
  unique_domains: number;
  robots_txt_bypass_count: number;
}

interface CrawlerSummaryEntry {
  crawler_name: string;
  user_agent_pattern?: string | null;
  company?: string | null;
  operator_org?: string | null;
  respects_rsl?: boolean;
  total_events: number;
  last_seen?: string | null;
  user_agent_category?: string;
  rsl_check_count?: number;
  rsl_check_rate?: number;
  rights_acknowledged_rate?: number;
  bypass_count?: number;
  compliance_score?: number;
  compliance_label?: 'Excellent' | 'Good' | 'Fair' | 'Poor' | 'Non-compliant';
}

export interface CdnIntegrationCreate {
  provider?: string;
  zone_id?: string | null;
  webhook_secret: string;
  enabled?: boolean;
}

export interface CdnIntegrationResponse {
  id: string;
  provider: string;
  zone_id?: string | null;
  enabled: boolean;
  created_at: string;
  updated_at: string;
  webhook_url: string;
}

interface CrawlerAnalytics {
  crawlers: CrawlerSummaryEntry[];
  total_crawler_events: number;
  known_crawlers?: CrawlerSummaryEntry[];
}

interface CrawlerTimeseries {
  dates: string[];
  by_crawler: Record<string, number[]>;
  total_by_date: number[];
}

interface DiscoveryResponse {
  success: boolean;
  data?: {
    message?: string;
    events_recorded?: number;
  } | null;
  error?: string | null;
}

interface DomainSummaryItem {
  id: string;
  page_domain: string;
  discovery_count: number;
  verified_count: number;
  invalid_count: number;
  is_owned_domain: boolean;
  first_seen_at: string;
  last_seen_at: string;
}

interface DomainSummaryResponse {
  success: boolean;
  data: DomainSummaryItem[];
  total: number;
}

interface DomainAlertItem {
  id: string;
  page_domain: string;
  discovery_count: number;
  first_seen_at: string;
  last_seen_at: string;
}

interface DomainAlertsResponse {
  success: boolean;
  data: DomainAlertItem[];
  total: number;
}

interface ContentDiscoveryItem {
  id: string;
  page_url: string;
  page_domain: string;
  page_title?: string | null;
  signer_name?: string | null;
  document_id?: string | null;
  original_domain?: string | null;
  verified: boolean;
  verification_status?: string | null;
  marker_type?: string | null;
  is_external_domain: boolean;
  discovered_at: string;
}

interface ContentDiscoveryListResponse {
  success: boolean;
  data: ContentDiscoveryItem[];
  total: number;
  limit: number;
  offset: number;
}

interface FormalNotice {
  id: string;
  organization_id: string;
  recipient_entity?: string | null;
  recipient_contact?: string | null;
  violation_type?: string | null;
  notice_text?: string | null;
  notice_type?: string | null;
  target_entity_name?: string | null;
  target_contact_email?: string | null;
  status: string;
  delivered_at?: string | null;
  content_hash?: string | null;
  created_at: string;
}

interface LicensingRequest {
  id: string;
  publisher_org_id?: string | null;
  requester_org_id?: string | null;
  tier?: string | null;
  scope?: Record<string, unknown> | null;
  proposed_terms?: Record<string, unknown> | null;
  requester_info?: Record<string, unknown> | null;
  status: string;
  response?: Record<string, unknown> | null;
  responded_at?: string | null;
  agreement_id?: string | null;
  created_at: string;
  updated_at?: string | null;
}

interface RightsProfileVersion {
  id: string;
  profile_version: number;
  effective_date: string;
  created_at: string;
  changed_by?: string | null;
  change_summary?: string | null;
  bronze_tier?: RightsTier | null;
  silver_tier?: RightsTier | null;
  gold_tier?: RightsTier | null;
}

interface EvidencePackage {
  notice: {
    id: string;
    notice_hash: string;
    notice_text?: string | null;
    target_entity_name?: string | null;
    status: string;
    delivered_at?: string | null;
    [key: string]: unknown;
  };
  evidence_chain: Array<{
    id: string;
    event_type: string;
    event_hash: string;
    previous_hash: string | null;
    created_at: string;
    event_data?: Record<string, unknown> | null;
    hash_verified?: boolean;
  }>;
  chain_integrity_verified: boolean;
  package_hash: string;
  generated_at: string;
}

interface LicensingAgreement {
  id: string;
  request_id?: string | null;
  publisher_org_id?: string | null;
  licensee_org_id?: string | null;
  licensee_name?: string | null;
  tier?: string | null;
  scope?: Record<string, unknown> | null;
  terms?: Record<string, unknown> | null;
  effective_date?: string | null;
  expiry_date?: string | null;
  auto_renew?: boolean | null;
  status: string;
  usage_metrics?: Record<string, unknown> | null;
  created_at: string;
}

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
  AdminNewsletterSubscriber,
  AdminNewsletterSubscribersResponse,
  // TEAM_044: C2PA Templates
  C2PATemplate,
  C2PATemplateListResponse,
  // TEAM_191: Onboarding Checklist
  OnboardingStep,
  OnboardingStatusResponse,
  // TEAM_191: Setup Wizard
  AccountType,
  DashboardLayoutPreference,
  WorkflowCategory,
  PublisherPlatform,
  SetupStatusResponse,
  WordPressInstallStatus,
  WordPressIntegrationStatus,
  WordPressRemoteAction,
  WordPressVerificationEvent,
  PublisherSettings,
  MfaStatusResponse,
  TotpSetupResponse,
  MfaLoginChallenge,
  PasskeyOptionsResponse,
  // TEAM_187: Ghost Integration
  GhostIntegrationCreatePayload,
  GhostIntegrationResponse,
  GhostTokenRegenerateResponse,
  // Rights Management
  RightsProfile,
  RightsTemplate,
  RightsTier,
  DetectionSummary,
  CrawlerSummaryEntry,
  CrawlerAnalytics,
  ContentDiscoveryItem,
  ContentDiscoveryListResponse,
  DomainAlertItem,
  DomainAlertsResponse,
  DomainSummaryItem,
  DomainSummaryResponse,
  FormalNotice,
  LicensingRequest,
  LicensingAgreement,
  RightsProfileVersion,
  EvidencePackage,
  // Payment Methods
  PaymentMethod,
  OveragePreferences,
  // Custom Verification Domain
  VerificationDomainInfo,
  VerificationDomainSetResponse,
  VerificationDomainVerifyResponse,
};
