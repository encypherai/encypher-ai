'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { toast } from 'sonner';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Input,
  Badge,
} from '@encypher/design-system';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import apiClient from '../../lib/api';

// API base URL - NEXT_PUBLIC_API_URL already includes /api/v1
const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'https://api.encypherai.com/api/v1').replace(/\/$/, '');

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

// Tier definitions for feature gating
type Tier = 'starter' | 'professional' | 'business' | 'enterprise';

interface ApiEndpoint {
  id: string;
  name: string;
  method: HttpMethod;
  path: string;
  description: string;
  category: string;
  requiresAuth: boolean;
  sampleBody?: string;
  authType?: 'session' | 'apikey' | 'both';
  minTier?: Tier; // Minimum tier required (undefined = all tiers)
  docsUrl?: string; // Link to documentation
}

// Tier hierarchy for comparison
const tierOrder: Record<Tier, number> = {
  starter: 0,
  professional: 1,
  business: 2,
  enterprise: 3,
};

const hasTierAccess = (userTier: Tier, requiredTier?: Tier): boolean => {
  if (!requiredTier) return true;
  return tierOrder[userTier] >= tierOrder[requiredTier];
};

const endpoints: ApiEndpoint[] = [
  // ============================================
  // SIGNING & VERIFICATION (Core - All Tiers)
  // ============================================
  {
    id: 'sign',
    name: 'Sign Content',
    method: 'POST',
    path: '/sign',
    description: 'Sign text content with C2PA-compliant cryptographic metadata',
    category: 'Signing',
    requiresAuth: true,
    authType: 'apikey',
    docsUrl: 'https://api.encypherai.com/docs',
    sampleBody: JSON.stringify({
      text: "Hello, this is AI-generated content that needs authentication.",
      model_id: "gpt-4",
      custom_metadata: { author: "Encypher" }
    }, null, 2),
  },
  {
    id: 'verify',
    name: 'Verify Content',
    method: 'POST',
    path: '/verify',
    description: 'Verify signed content and extract C2PA metadata',
    category: 'Verification',
    requiresAuth: true,
    authType: 'apikey',
    docsUrl: 'https://api.encypherai.com/docs',
    sampleBody: JSON.stringify({
      text: "Paste signed content here to verify..."
    }, null, 2),
  },
  {
    id: 'lookup',
    name: 'Lookup Signature',
    method: 'POST',
    path: '/lookup',
    description: 'Look up signature details by document ID or hash',
    category: 'Verification',
    requiresAuth: true,
    authType: 'apikey',
    docsUrl: 'https://api.encypherai.com/docs',
    sampleBody: JSON.stringify({
      document_id: "doc_example_id"
    }, null, 2),
  },
  
  // ============================================
  // STREAMING (Professional+)
  // ============================================
  {
    id: 'streaming-start',
    name: 'Start Streaming Session',
    method: 'POST',
    path: '/streaming/start',
    description: 'Start a streaming signing session for real-time content',
    category: 'Streaming',
    requiresAuth: true,
    authType: 'apikey',
    minTier: 'professional',
    docsUrl: 'https://api.encypherai.com/docs',
    sampleBody: JSON.stringify({
      model_id: "gpt-4",
      session_metadata: { conversation_id: "conv_123" }
    }, null, 2),
  },
  {
    id: 'streaming-chunk',
    name: 'Send Streaming Chunk',
    method: 'POST',
    path: '/streaming/chunk',
    description: 'Send a chunk of content in an active streaming session',
    category: 'Streaming',
    requiresAuth: true,
    authType: 'apikey',
    minTier: 'professional',
    sampleBody: JSON.stringify({
      session_id: "sess_example",
      chunk: "This is a chunk of streaming content...",
      sequence: 1
    }, null, 2),
  },
  {
    id: 'streaming-end',
    name: 'End Streaming Session',
    method: 'POST',
    path: '/streaming/end',
    description: 'Finalize a streaming session and get the signed document',
    category: 'Streaming',
    requiresAuth: true,
    authType: 'apikey',
    minTier: 'professional',
    sampleBody: JSON.stringify({
      session_id: "sess_example"
    }, null, 2),
  },
  
  // ============================================
  // BATCH OPERATIONS (Business+)
  // ============================================
  {
    id: 'batch-sign',
    name: 'Batch Sign',
    method: 'POST',
    path: '/api/v1/batch/sign',
    description: 'Sign multiple documents in a single request',
    category: 'Batch',
    requiresAuth: true,
    authType: 'apikey',
    minTier: 'business',
    docsUrl: 'https://api.encypherai.com/docs',
    sampleBody: JSON.stringify({
      documents: [
        { text: "First document to sign", document_id: "doc_1" },
        { text: "Second document to sign", document_id: "doc_2" }
      ],
      model_id: "gpt-4"
    }, null, 2),
  },
  {
    id: 'batch-verify',
    name: 'Batch Verify',
    method: 'POST',
    path: '/api/v1/batch/verify',
    description: 'Verify multiple documents in a single request',
    category: 'Batch',
    requiresAuth: true,
    authType: 'apikey',
    minTier: 'business',
    sampleBody: JSON.stringify({
      documents: [
        { text: "First signed document..." },
        { text: "Second signed document..." }
      ]
    }, null, 2),
  },
  
  // ============================================
  // MERKLE TREE (Professional+)
  // ============================================
  {
    id: 'merkle-encode',
    name: 'Merkle Encode',
    method: 'POST',
    path: '/merkle/encode',
    description: 'Encode document with sentence-level Merkle tree for granular verification',
    category: 'Merkle',
    requiresAuth: true,
    authType: 'apikey',
    minTier: 'professional',
    docsUrl: 'https://api.encypherai.com/docs',
    sampleBody: JSON.stringify({
      text: "This is a document with multiple sentences. Each sentence gets its own hash. This enables sentence-level verification.",
      document_id: "doc_merkle_example"
    }, null, 2),
  },
  {
    id: 'merkle-attribution',
    name: 'Merkle Attribution',
    method: 'POST',
    path: '/merkle/attribution',
    description: 'Check if content matches any registered sentences',
    category: 'Merkle',
    requiresAuth: true,
    authType: 'apikey',
    minTier: 'professional',
    sampleBody: JSON.stringify({
      text: "Check if this sentence appears in any registered documents."
    }, null, 2),
  },
  
  // ============================================
  // USAGE & ANALYTICS
  // ============================================
  {
    id: 'usage-stats',
    name: 'Get Usage Stats',
    method: 'GET',
    path: '/usage',
    description: 'Get your current API usage and quota information',
    category: 'Usage',
    requiresAuth: true,
    authType: 'apikey',
  },
  
  // ============================================
  // TEAM MANAGEMENT (Business+)
  // ============================================
  {
    id: 'team-list',
    name: 'List Team Members',
    method: 'GET',
    path: '/team/members',
    description: 'List all members of your organization',
    category: 'Team',
    requiresAuth: true,
    authType: 'apikey',
    minTier: 'business',
    docsUrl: 'https://api.encypherai.com/docs',
  },
  {
    id: 'team-invite',
    name: 'Invite Team Member',
    method: 'POST',
    path: '/team/invite',
    description: 'Invite a new member to your organization',
    category: 'Team',
    requiresAuth: true,
    authType: 'apikey',
    minTier: 'business',
    sampleBody: JSON.stringify({
      email: "colleague@example.com",
      role: "member"
    }, null, 2),
  },
  
  // ============================================
  // AUDIT LOGS (Business+)
  // ============================================
  {
    id: 'audit-logs',
    name: 'Get Audit Logs',
    method: 'GET',
    path: '/audit/logs',
    description: 'Retrieve audit logs for compliance and security review',
    category: 'Audit',
    requiresAuth: true,
    authType: 'apikey',
    minTier: 'business',
    docsUrl: 'https://api.encypherai.com/docs',
  },
  
  // ============================================
  // COALITION (All Tiers)
  // ============================================
  {
    id: 'coalition-status',
    name: 'Coalition Status',
    method: 'GET',
    path: '/coalition/status',
    description: 'Get your Publisher Coalition membership status and revenue share',
    category: 'Coalition',
    requiresAuth: true,
    authType: 'apikey',
  },
  
  // ============================================
  // API KEYS (Dashboard - Session Auth)
  // ============================================
  {
    id: 'list-keys',
    name: 'List API Keys',
    method: 'GET',
    path: '/keys',
    description: 'Get all API keys for your account',
    category: 'API Keys',
    requiresAuth: true,
    authType: 'session',
  },
  {
    id: 'create-key',
    name: 'Create API Key',
    method: 'POST',
    path: '/keys/generate',
    description: 'Generate a new API key',
    category: 'API Keys',
    requiresAuth: true,
    authType: 'session',
    sampleBody: JSON.stringify({
      name: "My New API Key",
      permissions: ["sign", "verify", "read"]
    }, null, 2),
  },
  {
    id: 'validate-key',
    name: 'Validate API Key',
    method: 'POST',
    path: '/keys/validate',
    description: 'Validate an API key and get organization context (public endpoint)',
    category: 'API Keys',
    requiresAuth: false,
    sampleBody: JSON.stringify({
      key: "ency_your_api_key_here"
    }, null, 2),
  },
  
  // ============================================
  // AUTH (Dashboard - Session Auth)
  // ============================================
  {
    id: 'verify-token',
    name: 'Verify Token',
    method: 'POST',
    path: '/auth/verify',
    description: 'Verify your session token and get user info',
    category: 'Auth',
    requiresAuth: true,
    authType: 'session',
  },
  {
    id: 'user-profile',
    name: 'Get Profile',
    method: 'GET',
    path: '/auth/me',
    description: 'Get your user profile information',
    category: 'Auth',
    requiresAuth: true,
    authType: 'session',
  },
];

const methodColors: Record<HttpMethod, string> = {
  GET: 'bg-green-100 text-green-700',
  POST: 'bg-blue-100 text-blue-700',
  PUT: 'bg-amber-100 text-amber-700',
  DELETE: 'bg-red-100 text-red-700',
};

// Tier badge colors
const tierColors: Record<Tier, string> = {
  starter: 'bg-slate-100 text-slate-600',
  professional: 'bg-blue-100 text-blue-700',
  business: 'bg-purple-100 text-purple-700',
  enterprise: 'bg-amber-100 text-amber-700',
};

const tierLabels: Record<Tier, string> = {
  starter: 'Free',
  professional: 'Pro',
  business: 'Business',
  enterprise: 'Enterprise',
};

export default function PlaygroundPage() {
  const { data: session, status } = useSession();
  const accessToken = (session?.user as Record<string, unknown>)?.accessToken as string | undefined;
  // Get user tier from session (default to starter for new users)
  const userTier = ((session?.user as Record<string, unknown>)?.tier as Tier) || 'starter';

  const [selectedEndpoint, setSelectedEndpoint] = useState<ApiEndpoint>(endpoints[0]);
  const [customPath, setCustomPath] = useState('');
  const [requestBody, setRequestBody] = useState('');
  const [response, setResponse] = useState<string | null>(null);
  const [responseStatus, setResponseStatus] = useState<number | null>(null);
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeCategory, setActiveCategory] = useState<string>('Signing');

  // Get API keys for the dropdown
  const apiKeysQuery = useQuery({
    queryKey: ['api-keys'],
    queryFn: async () => {
      if (!accessToken) return [];
      return apiClient.getApiKeys(accessToken);
    },
    enabled: Boolean(accessToken),
  });

  const [selectedApiKey, setSelectedApiKey] = useState<string>('session');
  const [customApiKey, setCustomApiKey] = useState<string>('');

  // Check if user has access to the selected endpoint
  const hasAccess = hasTierAccess(userTier, selectedEndpoint.minTier);

  // Update request body when endpoint changes
  useEffect(() => {
    setRequestBody(selectedEndpoint.sampleBody || '');
    setCustomPath(selectedEndpoint.path);
    setResponse(null);
    setResponseStatus(null);
    setResponseTime(null);
  }, [selectedEndpoint]);

  const categories = [...new Set(endpoints.map(e => e.category))];

  const handleSendRequest = async () => {
    setIsLoading(true);
    setResponse(null);
    setResponseStatus(null);
    setResponseTime(null);

    const startTime = performance.now();

    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      // Determine which auth to use based on endpoint and selection
      if (selectedEndpoint.requiresAuth) {
        const authType = selectedEndpoint.authType || 'both';
        
        if (selectedApiKey === 'session' && accessToken) {
          // Session token - always use Bearer format
          headers['Authorization'] = `Bearer ${accessToken}`;
        } else if (selectedApiKey === 'custom' && customApiKey.trim()) {
          // API Key - use Bearer format (enterprise API expects this)
          headers['Authorization'] = `Bearer ${customApiKey.trim()}`;
        }
        
        // Show warning if using wrong auth type
        if (authType === 'session' && selectedApiKey === 'custom') {
          toast.warning('This endpoint works best with session auth');
        } else if (authType === 'apikey' && selectedApiKey === 'session') {
          toast.warning('This endpoint requires an API key for full functionality');
        }
      }

      const url = `${API_BASE}${customPath}`;
      const options: RequestInit = {
        method: selectedEndpoint.method,
        headers,
      };

      if (['POST', 'PUT'].includes(selectedEndpoint.method) && requestBody.trim()) {
        try {
          // Validate JSON
          JSON.parse(requestBody);
          options.body = requestBody;
        } catch {
          toast.error('Invalid JSON in request body');
          setIsLoading(false);
          return;
        }
      }

      const res = await fetch(url, options);
      const endTime = performance.now();
      setResponseTime(Math.round(endTime - startTime));
      setResponseStatus(res.status);

      const contentType = res.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        const data = await res.json();
        setResponse(JSON.stringify(data, null, 2));
      } else {
        const text = await res.text();
        setResponse(text);
      }
    } catch (err) {
      const endTime = performance.now();
      setResponseTime(Math.round(endTime - startTime));
      setResponse(JSON.stringify({ error: (err as Error).message }, null, 2));
      setResponseStatus(0);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const copySelection = () => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim()) {
      navigator.clipboard.writeText(selection.toString());
      toast.success('Selection copied to clipboard');
    } else {
      toast.info('Select some text first');
    }
  };

  const getStatusColor = (status: number | null) => {
    if (!status) return 'text-slate-500';
    if (status >= 200 && status < 300) return 'text-green-600';
    if (status >= 400 && status < 500) return 'text-amber-600';
    return 'text-red-600';
  };

  return (
    <DashboardLayout>
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-delft-blue dark:text-white mb-1">API Playground</h2>
            <p className="text-muted-foreground">
              Test API endpoints interactively with your credentials
            </p>
          </div>
          <a
            href="https://api.encypherai.com/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-ncs hover:underline flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            View Full API Docs
          </a>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Panel - Endpoint Selection */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Endpoints</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {/* Category Tabs */}
              <div className="flex flex-wrap gap-1 px-4 pb-3 border-b">
                {categories.map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setActiveCategory(cat)}
                    className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                      activeCategory === cat
                        ? 'bg-blue-ncs text-white'
                        : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>

              {/* Endpoint List */}
              <div className="max-h-96 overflow-y-auto">
                {endpoints
                  .filter((e) => e.category === activeCategory)
                  .map((endpoint) => {
                    const endpointHasAccess = hasTierAccess(userTier, endpoint.minTier);
                    return (
                      <button
                        key={endpoint.id}
                        onClick={() => setSelectedEndpoint(endpoint)}
                        className={`w-full text-left px-4 py-3 border-b last:border-0 transition-colors ${
                          selectedEndpoint.id === endpoint.id
                            ? 'bg-blue-50 dark:bg-blue-900/30'
                            : 'hover:bg-slate-50 dark:hover:bg-slate-700'
                        } ${!endpointHasAccess ? 'opacity-60' : ''}`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-0.5 text-xs font-bold rounded ${methodColors[endpoint.method]}`}>
                            {endpoint.method}
                          </span>
                          <span className="font-medium text-sm flex-1">{endpoint.name}</span>
                          {endpoint.minTier && (
                            <span className={`px-1.5 py-0.5 text-[10px] font-medium rounded ${tierColors[endpoint.minTier]}`}>
                              {!endpointHasAccess && '🔒 '}{tierLabels[endpoint.minTier]}+
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground truncate">{endpoint.path}</p>
                      </button>
                    );
                  })}
              </div>
            </CardContent>
          </Card>

          {/* Authentication */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Authentication</CardTitle>
              {selectedEndpoint.authType && (
                <p className="text-xs text-muted-foreground mt-1">
                  {selectedEndpoint.authType === 'session' && '⚡ This endpoint uses session auth'}
                  {selectedEndpoint.authType === 'apikey' && '🔑 This endpoint requires an API key'}
                  {selectedEndpoint.authType === 'both' && '✓ Supports both session and API key'}
                </p>
              )}
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Authentication Method</label>
                <select
                  value={selectedApiKey}
                  onChange={(e) => setSelectedApiKey(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 dark:bg-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-ncs"
                >
                  <option value="session">Session Token (Current Login)</option>
                  <option value="custom">API Key (Paste Below)</option>
                </select>
              </div>
              
              {selectedApiKey === 'custom' && (
                <div>
                  <label className="block text-sm font-medium mb-2">Your API Key</label>
                  <Input
                    type="text"
                    value={customApiKey}
                    onChange={(e) => setCustomApiKey(e.target.value)}
                    placeholder="ency_..."
                    className="font-mono text-sm"
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    Paste the API key you received when creating it. Keys start with <code className="bg-muted px-1 rounded">ency_</code>
                  </p>
                </div>
              )}
              
              {selectedApiKey === 'session' && (
                <div className="space-y-2">
                  {accessToken ? (
                    <p className="text-xs text-green-600 dark:text-green-400">
                      ✓ Session token available. This works for dashboard endpoints (API Keys, Auth).
                    </p>
                  ) : (
                    <p className="text-xs text-amber-600 dark:text-amber-400">
                      ⚠ No session token available. You may have logged in via OAuth. Use an API key for authentication, or log out and log in with email/password.
                    </p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    Note: Signing/verification endpoints require API keys, not session tokens.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Panel - Request/Response */}
        <div className="lg:col-span-2 space-y-4">
          {/* Request */}
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Request</CardTitle>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 text-xs font-bold rounded ${methodColors[selectedEndpoint.method]}`}>
                    {selectedEndpoint.method}
                  </span>
                </div>
              </div>
              <CardDescription>{selectedEndpoint.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* URL */}
              <div>
                <label className="block text-sm font-medium mb-1">URL</label>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">{API_BASE}</span>
                  <Input
                    value={customPath}
                    onChange={(e) => setCustomPath(e.target.value)}
                    className="flex-1 font-mono text-sm"
                  />
                </div>
              </div>

              {/* Request Body */}
              {['POST', 'PUT'].includes(selectedEndpoint.method) && (
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="block text-sm font-medium">Request Body (JSON)</label>
                    <button
                      onClick={() => copyToClipboard(requestBody)}
                      className="text-xs text-blue-ncs hover:underline"
                    >
                      Copy
                    </button>
                  </div>
                  <textarea
                    value={requestBody}
                    onChange={(e) => setRequestBody(e.target.value)}
                    rows={8}
                    className="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-ncs resize-y"
                    placeholder="Enter JSON request body..."
                    style={{ WebkitUserSelect: 'text', userSelect: 'text' }}
                  />
                </div>
              )}

              {/* Tier Access Warning */}
              {!hasAccess && selectedEndpoint.minTier && (
                <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <span className="text-amber-500 text-xl">🔒</span>
                    <div>
                      <h4 className="font-medium text-amber-800 dark:text-amber-200">
                        {tierLabels[selectedEndpoint.minTier]}+ Feature
                      </h4>
                      <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
                        This endpoint requires the {tierLabels[selectedEndpoint.minTier]} plan or higher.
                        You can still view the API structure and documentation.
                      </p>
                      <a
                        href="/billing"
                        className="inline-block mt-2 text-sm font-medium text-amber-800 dark:text-amber-200 hover:underline"
                      >
                        Upgrade your plan →
                      </a>
                    </div>
                  </div>
                </div>
              )}

              {/* Send Button */}
              <Button
                variant="primary"
                onClick={handleSendRequest}
                disabled={isLoading || !hasAccess || (!accessToken && selectedApiKey === 'session') || (selectedApiKey === 'custom' && !customApiKey.trim())}
                className="w-full"
              >
                {isLoading ? (
                  <>
                    <svg className="w-4 h-4 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Sending...
                  </>
                ) : !hasAccess ? (
                  <>
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                    Upgrade to Test
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Send Request
                  </>
                )}
              </Button>

              {/* Documentation Link */}
              {selectedEndpoint.docsUrl && (
                <a
                  href={selectedEndpoint.docsUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-center text-sm text-blue-ncs hover:underline"
                >
                  View full documentation for this endpoint →
                </a>
              )}
            </CardContent>
          </Card>

          {/* Response */}
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Response</CardTitle>
                {responseStatus !== null && (
                  <div className="flex items-center gap-3">
                    <span className={`text-sm font-medium ${getStatusColor(responseStatus)}`}>
                      Status: {responseStatus || 'Error'}
                    </span>
                    {responseTime !== null && (
                      <span className="text-sm text-muted-foreground">
                        {responseTime}ms
                      </span>
                    )}
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {response ? (
                <div className="relative">
                  <div className="absolute top-2 right-2 flex gap-2 z-10">
                    <button
                      onClick={copySelection}
                      className="text-xs bg-slate-700 hover:bg-slate-600 text-slate-200 px-2 py-1 rounded transition-colors"
                    >
                      Copy Selection
                    </button>
                    <button
                      onClick={() => copyToClipboard(response)}
                      className="text-xs bg-blue-600 hover:bg-blue-500 text-white px-2 py-1 rounded transition-colors"
                    >
                      Copy All
                    </button>
                  </div>
                  <pre 
                    className="bg-slate-900 text-slate-100 p-4 pt-10 rounded-lg overflow-auto max-h-96 text-sm font-mono"
                    style={{ 
                      WebkitUserSelect: 'text', 
                      userSelect: 'text',
                      cursor: 'text',
                    }}
                  >
                    {response}
                  </pre>
                </div>
              ) : (
                <div className="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-8 text-center">
                  <svg className="w-12 h-12 mx-auto mb-3 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <p className="text-muted-foreground">
                    Send a request to see the response here
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}

