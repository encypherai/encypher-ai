/**
 * API client for the marketing site web-service
 */

// Web service URL for demo requests and sales forms
const WEB_SERVICE_URL = process.env.NEXT_PUBLIC_WEB_SERVICE_URL || 'http://localhost:8002';
const WEB_API_V1 = `${WEB_SERVICE_URL}/api/v1`;

// Analytics service URL (anonymous pageviews)
const ANALYTICS_SERVICE_URL = process.env.NEXT_PUBLIC_ANALYTICS_SERVICE_URL || 'http://localhost:8006';
const ANALYTICS_API_V1 = `${ANALYTICS_SERVICE_URL}/api/v1`;

// Auth service URL (separate microservice for authentication)
const AUTH_SERVICE_URL = process.env.NEXT_PUBLIC_AUTH_SERVICE_URL || 'http://localhost:8001';
const AUTH_API_V1 = `${AUTH_SERVICE_URL}/api/v1`;

export interface DemoRequestData {
  name: string;
  email: string;
  organization?: string;
  role?: string;
  message?: string;
  source?: string;
  consent: boolean;
}

export interface DemoRequestResponse {
  id: number;
  uuid: string;
  status: string;
  created_at: string;
}

export interface AnalyticsEventData {
  event_type?: string;
  event_name: string;
  session_id: string;
  page_url: string;
  page_title?: string;
  user_id?: string;
  user_agent?: string;
  referrer?: string;
  properties?: Record<string, any>;
}

export function resolveAnalyticsPath(pageUrl: string): string {
  try {
    const parsed = new URL(pageUrl);
    return `${parsed.pathname}${parsed.search}`;
  } catch {
    return pageUrl;
  }
}

export function buildAnalyticsPath(pageUrl: string, eventName?: string): string {
  const basePath = resolveAnalyticsPath(pageUrl);
  if (!eventName) {
    return basePath;
  }

  const separator = basePath.includes('?') ? '&' : '?';
  return `${basePath}${separator}event=${encodeURIComponent(eventName)}`;
}

export interface FetchApiOptions extends RequestInit {
  token?: string;
  skipJsonParse?: boolean;
}

export class AuthError extends Error {
  code: string;
  constructor(message: string, code: string) {
    super(message);
    this.code = code;
    this.name = 'AuthError';
  }
}

/**
 * Generic fetch wrapper
 * Routes /auth/* endpoints to auth-service, /analytics/* to analytics-service, all others to web-service
 */
export async function fetchApi<T>(endpoint: string, options: FetchApiOptions = {}): Promise<T> {
  let url = endpoint;
  
  // If not absolute URL, determine which service to call
  if (!endpoint.startsWith('http')) {
    // Route auth endpoints to auth-service
    if (endpoint.startsWith('/auth/')) {
      url = `${AUTH_API_V1}${endpoint}`;
    } else if (endpoint.startsWith('/analytics/')) {
      url = `${ANALYTICS_API_V1}${endpoint}`;
    } else {
      url = `${WEB_API_V1}${endpoint}`;
    }
  }
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (options.token) {
    headers['Authorization'] = `Bearer ${options.token}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `API request failed: ${response.status}`);
  }
  
  if (options.skipJsonParse) return response as unknown as T;
  
  return response.json();
}

/**
 * Submit a demo request
 */
export async function submitDemoRequest(data: DemoRequestData): Promise<DemoRequestResponse> {
  return fetchApi<DemoRequestResponse>('/demo-requests/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Track an analytics event
 */
export async function trackEvent(data: AnalyticsEventData): Promise<any> {
  const payload = {
    site_id: 'marketing-site',
    path: buildAnalyticsPath(data.page_url, data.event_name),
    referrer: data.referrer,
    user_agent: data.user_agent,
  };

  try {
    // Use relative path, fetchApi will prepend API_V1
    return await fetchApi('/analytics/pageview', {
      method: 'POST',
      body: JSON.stringify(payload),
      keepalive: true, 
    } as RequestInit);
  } catch (error) {
    console.warn('Failed to track analytics event:', error);
    return null;
  }
}
