export type DemoRequestContext = 'ai' | 'publisher' | 'enterprise' | 'general';

export const DEMO_REQUEST_ENDPOINTS: Record<DemoRequestContext, string> = {
  ai: '/api/v1/ai-demo/demo-requests',
  publisher: '/api/v1/publisher-demo/demo-requests',
  enterprise: '/api/v1/sales/enterprise-requests',
  general: '/api/v1/sales/general-requests',
};

// Defaults to general sales when context is missing or unrecognized.
export function resolveDemoRequestEndpoint(context?: string): string {
  if (!context) {
    return DEMO_REQUEST_ENDPOINTS.general;
  }

  if (context in DEMO_REQUEST_ENDPOINTS) {
    return DEMO_REQUEST_ENDPOINTS[context as DemoRequestContext];
  }

  return DEMO_REQUEST_ENDPOINTS.general;
}
