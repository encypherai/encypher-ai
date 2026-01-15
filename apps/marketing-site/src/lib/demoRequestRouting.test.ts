import { resolveDemoRequestEndpoint } from './demoRequestRouting';

describe('demoRequestRouting', () => {
  it('routes known contexts to the expected web-service endpoints', () => {
    expect(resolveDemoRequestEndpoint('ai')).toBe('/api/v1/ai-demo/demo-requests');
    expect(resolveDemoRequestEndpoint('publisher')).toBe('/api/v1/publisher-demo/demo-requests');
    expect(resolveDemoRequestEndpoint('enterprise')).toBe('/api/v1/sales/enterprise-requests');
    expect(resolveDemoRequestEndpoint('general')).toBe('/api/v1/sales/general-requests');
  });

  it('defaults to general when context is missing', () => {
    expect(resolveDemoRequestEndpoint()).toBe('/api/v1/sales/general-requests');
  });

  it('defaults to general when context is unknown', () => {
    expect(resolveDemoRequestEndpoint('legacy')).toBe('/api/v1/sales/general-requests');
  });
});
