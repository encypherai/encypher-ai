/**
 * API client for the marketing site web-service
 */

// Base URL for the web-service
// Default to localhost for dev, but in prod this should be the service URL
const API_BASE_URL = process.env.NEXT_PUBLIC_WEB_SERVICE_URL || 'http://localhost:8002';
const API_V1 = `${API_BASE_URL}/api/v1`;

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
 */
export async function fetchApi<T>(endpoint: string, options: FetchApiOptions = {}): Promise<T> {
  let url = endpoint;
  
  // If not absolute URL, prepend API_V1 (unless it starts with http)
  if (!endpoint.startsWith('http')) {
      url = `${API_V1}${endpoint}`;
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
    event_type: 'custom',
    ...data,
  };

  try {
    // Use relative path, fetchApi will prepend API_V1
    return await fetchApi('/analytics/', {
      method: 'POST',
      body: JSON.stringify(payload),
      keepalive: true, 
    } as RequestInit);
  } catch (error) {
    console.warn('Failed to track analytics event:', error);
    return null;
  }
}
