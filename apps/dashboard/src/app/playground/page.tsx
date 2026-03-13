'use client';

import { useState, useEffect, useMemo, useRef } from 'react';
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
import { TemplateSelector } from '../../components/TemplateSelector';
import { TourSpotlight } from '../../components/TourSpotlight';
import apiClient from '../../lib/api';
import { buildRequestBodyJson, parseRequestBodyJson } from '../../lib/playgroundRequestBuilder.mjs';
import { PLAYGROUND_ENDPOINTS } from '../../lib/playgroundEndpoints.mjs';
import { extractSignedTextFromResponse } from '../../lib/playgroundSignedText.mjs';

// API base URL - NEXT_PUBLIC_API_URL already includes /api/v1
const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'https://api.encypherai.com/api/v1').replace(/\/$/, '');

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

// Tier definitions for feature gating
type Tier = 'free' | 'enterprise';

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

type RequestEditorMode = 'form' | 'json';

type PlaygroundFormState = {
  text: string;
  document_title: string;
  document_type: string;
  template_id: string;
  sentence_text: string;
  segmentation_level: string;
  manifest_mode: string;
  embedding_strategy: string;
  enable_print_fingerprint: boolean;
};

// Tier hierarchy for comparison
const tierOrder: Record<Tier, number> = {
  free: 0,
  enterprise: 1,
};

const hasTierAccess = (userTier: Tier, requiredTier?: Tier): boolean => {
  if (!requiredTier) return true;
  return tierOrder[userTier] >= tierOrder[requiredTier];
};

// Field documentation for inline tooltips
const fieldDocs: Record<string, Record<string, string>> = {
  sign: {
    text: 'The content to sign. Each sentence gets its own invisible cryptographic signature.',
    document_title: 'A human-readable title for the document.',
    segmentation_level: 'How to split text for signing. Sentence = each sentence signed individually (recommended).',
    manifest_mode: 'micro = compact per-sentence markers (default: ECC + C2PA embedded). Use ecc/embed_c2pa flags to control.',
    document_type: 'Type of content: article, legal_brief, contract, ai_output.',
    embedding_strategy: 'Where to place invisible signatures: single_point (default), distributed, distributed_redundant.',
    template_id: 'Optional: ID of a rights template to embed licensing terms (Business+).',
  },
  verify: {
    text: 'The signed content to verify. Paste the full text — invisible signatures travel with the text via copy-paste.',
  },
  lookup: {
    sentence_text: 'A sentence to look up in the provenance database.',
  },
  'status-document': {
    document_id: 'Path param. The document ID assigned at signing time.',
  },
  'status-revoke': {
    document_id: 'Path param. The document ID assigned at signing time.',
    reason: 'Revocation reason (e.g., factual_error, legal_takedown, content_policy).',
    reason_detail: 'Optional free-form explanation for audit logs.',
  },
  'status-reinstate': {
    document_id: 'Path param. The document ID assigned at signing time.',
  },
  'status-list': {
    organization_id: 'Path param. Organization ID that owns the status list.',
    list_index: 'Path param. Integer list index for the status list shard.',
  },
};

// Demo sample for instant success in sign flow
const DEMO_SIGN_SAMPLE = {
  text: 'Scientists at CERN have detected high-energy particles originating from a distant galaxy. The discovery could reshape our understanding of cosmic ray propagation. Researchers plan to publish their findings in Nature next month.',
  document_title: 'CERN Cosmic Ray Discovery',
  document_type: 'article',
  segmentation_level: 'sentence',
  manifest_mode: 'micro',
  embedding_strategy: 'single_point',
};

const endpoints: ApiEndpoint[] = PLAYGROUND_ENDPOINTS as ApiEndpoint[];

const methodColors: Record<HttpMethod, string> = {
  GET: 'bg-green-100 text-green-700',
  POST: 'bg-blue-100 text-blue-700',
  PUT: 'bg-amber-100 text-amber-700',
  DELETE: 'bg-red-100 text-red-700',
};

// Tier badge colors
const tierColors: Record<Tier, string> = {
  free: 'bg-slate-100 text-slate-600',
  enterprise: 'bg-amber-100 text-amber-700',
};

const tierLabels: Record<Tier, string> = {
  free: 'Free',
  enterprise: 'Enterprise',
};

function CopyPasteSurvivalTester({ apiKey }: { apiKey: string }) {
  const [inputText, setInputText] = useState('');
  const [signedText, setSignedText] = useState('');
  const [pastedText, setPastedText] = useState('');
  const [survivalResult, setSurvivalResult] = useState<null | { survived: boolean; message: string }>(null);
  const [signing, setSigning] = useState(false);
  const [testing, setTesting] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleSign = async () => {
    if (!inputText.trim()) return;
    setSigning(true);
    setSurvivalResult(null);
    try {
      const resp = await fetch(`${API_BASE}/sign`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey,
        },
        body: JSON.stringify({ text: inputText }),
      });
      const data = await resp.json();
      const signed = data?.data?.signed_text ?? data?.signed_text ?? '';
      setSignedText(signed);
      toast.success('Text signed. Copy it, paste elsewhere, then test survival.');
    } catch {
      toast.error('Signing failed.');
    } finally {
      setSigning(false);
    }
  };

  const handleCopy = async () => {
    if (!signedText) return;
    await navigator.clipboard.writeText(signedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleTestSurvival = async () => {
    const textToTest = pastedText || signedText;
    if (!textToTest.trim()) return;
    setTesting(true);
    setSurvivalResult(null);
    try {
      const resp = await fetch(`${API_BASE}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToTest }),
      });
      const data = await resp.json();
      const isSignedField = data?.data?.is_signed ?? data?.is_signed ?? false;
      const embeddingsFound = data?.data?.embeddings_found ?? false;
      const survived = isSignedField || embeddingsFound;
      setSurvivalResult({
        survived,
        message: survived
          ? 'Watermark survived -- invisible embeddings detected in pasted text.'
          : 'Watermark lost -- no embeddings detected. The copy-paste process may have stripped invisible characters.',
      });
    } catch {
      toast.error('Verification failed.');
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100">Copy-Paste Survival Test</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
          Prove that invisible watermarks survive copy-paste operations. Sign text, copy it to your clipboard, paste it somewhere (email, Word, Slack), then paste it back here and test.
        </p>
      </div>

      <div className="space-y-3">
        <label className="text-xs font-medium text-slate-700 dark:text-slate-300">1. Enter text to sign</label>
        <textarea
          rows={4}
          placeholder="Paste or type any article, paragraph, or AI output here..."
          value={inputText}
          onChange={e => setInputText(e.target.value)}
          className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 resize-y font-mono"
        />
        <Button
          onClick={handleSign}
          disabled={signing || !inputText.trim() || !apiKey}
          size="sm"
        >
          {signing ? 'Signing...' : 'Sign text'}
        </Button>
      </div>

      {signedText && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-slate-700 dark:text-slate-300">2. Signed text (copy this)</label>
            <button
              onClick={handleCopy}
              className="text-xs px-3 py-1 rounded-md bg-blue-50 dark:bg-blue-950/30 text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors font-medium"
            >
              {copied ? 'Copied!' : 'Copy to clipboard'}
            </button>
          </div>
          <textarea
            rows={4}
            readOnly
            value={signedText}
            className="w-full rounded-lg border border-green-200 dark:border-green-800 bg-green-50/30 dark:bg-green-950/10 px-3 py-2 text-sm font-mono resize-y"
          />
          <p className="text-xs text-slate-400">
            The text above contains invisible Unicode embeddings. Copy it, paste it into another app (email, Word, Slack, etc.), copy it back, and paste it below.
          </p>
        </div>
      )}

      {signedText && (
        <div className="space-y-3">
          <label className="text-xs font-medium text-slate-700 dark:text-slate-300">3. Paste here after copy</label>
          <textarea
            rows={4}
            placeholder="Paste the text back here after going through another app..."
            value={pastedText}
            onChange={e => setPastedText(e.target.value)}
            className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm font-mono resize-y"
          />
          <Button
            onClick={handleTestSurvival}
            disabled={testing || (!pastedText.trim() && !signedText.trim())}
            size="sm"
            variant="outline"
          >
            {testing ? 'Testing...' : 'Verify survival'}
          </Button>
        </div>
      )}

      {survivalResult && (
        <div className={`rounded-xl border p-4 ${survivalResult.survived
          ? 'bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-800'
          : 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800'
        }`}>
          <div className="flex items-start gap-3">
            <span className="text-2xl">{survivalResult.survived ? '\u2705' : '\u274C'}</span>
            <div>
              <p className={`font-semibold text-sm ${survivalResult.survived ? 'text-green-800 dark:text-green-300' : 'text-red-800 dark:text-red-300'}`}>
                {survivalResult.survived ? 'Watermark survived' : 'Watermark lost'}
              </p>
              <p className={`text-xs mt-0.5 ${survivalResult.survived ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                {survivalResult.message}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function PlaygroundPage() {
  const { data: session } = useSession();
  const accessToken = (session?.user as Record<string, unknown>)?.accessToken as string | undefined;
  // Get user tier from session (default to free for new users)
  const userTier = ((session?.user as Record<string, unknown>)?.tier as Tier) || 'free';

  const [selectedEndpoint, setSelectedEndpoint] = useState<ApiEndpoint>(endpoints[0]);
  const [customPath, setCustomPath] = useState('');
  const [requestBody, setRequestBody] = useState('');
  const [response, setResponse] = useState<string | null>(null);
  const [responseStatus, setResponseStatus] = useState<number | null>(null);
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Get API keys for the dropdown
  const apiKeysQuery = useQuery({
    queryKey: ['api-keys'],
    queryFn: async () => {
      if (!accessToken) return [];
      return apiClient.getApiKeys(accessToken);
    },
    enabled: Boolean(accessToken),
  });

  const [selectedApiKey, setSelectedApiKey] = useState<string>('custom');
  const [customApiKey, setCustomApiKey] = useState<string>('');
  const [generatedApiKey, setGeneratedApiKey] = useState<string>('');
  const [isGeneratingKey, setIsGeneratingKey] = useState<boolean>(false);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | undefined>(undefined);
  const [showQuickStart, setShowQuickStart] = useState<boolean>(true);
  const [quickStartStep, setQuickStartStep] = useState<number>(0);
  const [lastSignedContent, setLastSignedContent] = useState<string | null>(null);

  // Guided Tour State (4 steps: 0=API Key, 1=Sign, 2=Copy, 3=Verify)
  const [tourActive, setTourActive] = useState<boolean>(false);
  const [tourStep, setTourStep] = useState<number>(0);
  const [playgroundMode, setPlaygroundMode] = useState<'explorer' | 'copy-paste-test'>('explorer');
  const [endpointSearch, setEndpointSearch] = useState<string>('');
  const preserveRequestBodyOnEndpointChangeRef = useRef<boolean>(false);
  const [requestEditorMode, setRequestEditorMode] = useState<RequestEditorMode>('form');
  const [formValues, setFormValues] = useState<PlaygroundFormState>({
    text: '',
    document_title: '',
    document_type: '',
    template_id: '',
    sentence_text: '',
    segmentation_level: '',
    manifest_mode: '',
    embedding_strategy: '',
    enable_print_fingerprint: false,
  });

  const supportsFormBuilder =
    selectedEndpoint.id === 'sign' ||
    selectedEndpoint.id === 'verify' ||
    selectedEndpoint.id === 'lookup';

  // Filter endpoints by search term
  const filteredEndpoints = useMemo(() => {
    if (!endpointSearch.trim()) return endpoints;
    const search = endpointSearch.toLowerCase();
    return endpoints.filter(e =>
      e.name.toLowerCase().includes(search) ||
      e.path.toLowerCase().includes(search) ||
      e.description.toLowerCase().includes(search)
    );
  }, [endpointSearch]);

  const filteredEndpointsByCategory = useMemo(() => {
    const grouped: Record<string, ApiEndpoint[]> = {};
    for (const endpoint of filteredEndpoints) {
      if (!grouped[endpoint.category]) grouped[endpoint.category] = [];
      grouped[endpoint.category].push(endpoint);
    }
    return grouped;
  }, [filteredEndpoints]);

  // Check if user has access to the selected endpoint
  const hasAccess = hasTierAccess(userTier, selectedEndpoint.minTier);

  // JSON validation state
  const jsonValidation = useMemo(() => {
    if (!requestBody.trim()) return { valid: true, error: null };
    try {
      JSON.parse(requestBody);
      return { valid: true, error: null };
    } catch (e) {
      return { valid: false, error: (e as Error).message };
    }
  }, [requestBody]);

  // Parse response for human-readable summary
  const responseSummary = useMemo(() => {
    if (!response || responseStatus === null) return null;
    try {
      const data = JSON.parse(response);
      // Handle verification response
      if (selectedEndpoint.id === 'verify' && data.data) {
        const verdict = data.data;
        const isUntrustedSigner = verdict.reason_code === 'UNTRUSTED_SIGNER';
        return {
          type: 'verify',
          success: data.success && verdict.valid && !isUntrustedSigner,
          warning: data.success && verdict.valid && isUntrustedSigner,
          valid: verdict.valid,
          tampered: verdict.tampered,
          signerName: verdict.signer_name || verdict.signer_id || 'Unknown',
          reasonCode: verdict.reason_code,
          embeddingsFound: verdict.embeddings_found || 1,
        };
      }
      // Handle sign response — unified /sign returns data.document.signed_text
      const signDoc = data?.data?.document;
      if (selectedEndpoint.id === 'sign' && data.success && signDoc) {
        return {
          type: 'sign',
          success: true,
          documentId: signDoc.document_id,
          totalSegments: signDoc.total_segments,
          signedText: signDoc.signed_text,
          verificationUrl: signDoc.verification_url,
          merkleRoot: signDoc.merkle_root,
          instanceId: signDoc.instance_id,
        };
      }
      // Legacy sign response format (data.signed_text at top level)
      if ((selectedEndpoint.id === 'sign') && data.success && data.signed_text) {
        return {
          type: 'sign',
          success: true,
          documentId: data.document_id,
          totalSegments: data.total_sentences || data.total_segments,
          signedText: data.signed_text,
        };
      }
      // Handle lookup response
      if (selectedEndpoint.id === 'lookup' && data.success) {
        return {
          type: 'lookup',
          success: true,
          found: data.found,
          documentTitle: data.document_title,
          organizationName: data.organization_name,
        };
      }
      return null;
    } catch {
      return null;
    }
  }, [response, responseStatus, selectedEndpoint.id]);

  // Update request body when endpoint changes
  useEffect(() => {
    if (!preserveRequestBodyOnEndpointChangeRef.current) {
      const defaultMode: RequestEditorMode = supportsFormBuilder ? 'form' : 'json';
      setRequestEditorMode(defaultMode);

      if (supportsFormBuilder) {
        const parsed = parseRequestBodyJson(selectedEndpoint.id, selectedEndpoint.sampleBody || '') as
          | Partial<PlaygroundFormState>
          | null;
        const nextForm: PlaygroundFormState = {
          text: parsed?.text ?? '',
          document_title: parsed?.document_title ?? '',
          document_type: parsed?.document_type ?? '',
          template_id: parsed?.template_id ?? '',
          sentence_text: parsed?.sentence_text ?? '',
          segmentation_level: parsed?.segmentation_level ?? '',
          manifest_mode: parsed?.manifest_mode ?? '',
          embedding_strategy: parsed?.embedding_strategy ?? '',
          enable_print_fingerprint: parsed?.enable_print_fingerprint ?? false,
        };
        setFormValues(nextForm);

        try {
          setRequestBody(buildRequestBodyJson(selectedEndpoint.id, nextForm));
        } catch {
          setRequestBody(selectedEndpoint.sampleBody || '');
        }
      } else {
        setRequestBody(selectedEndpoint.sampleBody || '');
      }
    }
    setCustomPath(selectedEndpoint.path);
    setResponse(null);
    setResponseStatus(null);
    setResponseTime(null);

    if (preserveRequestBodyOnEndpointChangeRef.current) {
      preserveRequestBodyOnEndpointChangeRef.current = false;
    }
    // Reset template selection when switching away from sign endpoint
    if (selectedEndpoint.id !== 'sign') {
      setSelectedTemplateId(undefined);
    }
  }, [selectedEndpoint, supportsFormBuilder]);

  // Update request body when template is selected (for sign endpoint)
  useEffect(() => {
    if (selectedEndpoint.id !== 'sign' || requestEditorMode !== 'json') return;

    setRequestBody((prev) => {
      if (!prev) return prev;
      try {
        const body = JSON.parse(prev);
        const before = body.template_id;
        if (selectedTemplateId) {
          body.template_id = selectedTemplateId;
        } else {
          delete body.template_id;
        }

        const after = body.template_id;
        if (before === after) return prev;
        return JSON.stringify(body, null, 2);
      } catch {
        return prev;
      }
    });
  }, [requestEditorMode, selectedEndpoint.id, selectedTemplateId]);

  useEffect(() => {
    if (selectedEndpoint.id !== 'sign' || requestEditorMode !== 'form') return;
    setFormValues((prev) => ({
      ...prev,
      template_id: selectedTemplateId ?? '',
    }));
  }, [requestEditorMode, selectedEndpoint.id, selectedTemplateId]);

  useEffect(() => {
    if (!supportsFormBuilder || requestEditorMode !== 'form') return;
    try {
      setRequestBody(buildRequestBodyJson(selectedEndpoint.id, formValues));
    } catch {
      setRequestBody('');
    }
  }, [formValues, requestEditorMode, selectedEndpoint.id, supportsFormBuilder]);

  const formValidation = useMemo(() => {
    if (!supportsFormBuilder || requestEditorMode !== 'form') return { valid: true, error: null as string | null };

    if (selectedEndpoint.id === 'verify') {
      return formValues.text.trim()
        ? { valid: true, error: null }
        : { valid: false, error: 'Text is required for verification.' };
    }

    if (selectedEndpoint.id === 'lookup') {
      return formValues.sentence_text.trim()
        ? { valid: true, error: null }
        : { valid: false, error: 'Sentence text is required for lookup.' };
    }

    if (selectedEndpoint.id === 'sign') {
      return formValues.text.trim() ? { valid: true, error: null } : { valid: false, error: 'Text is required for signing.' };
    }

    return { valid: true, error: null };
  }, [formValues.sentence_text, formValues.text, requestEditorMode, selectedEndpoint.id, supportsFormBuilder]);

  const canSendRequest =
    !isLoading &&
    hasAccess &&
    jsonValidation.valid &&
    formValidation.valid &&
    (!selectedEndpoint.requiresAuth ||
      (selectedApiKey === 'custom' && customApiKey.trim()) ||
      (selectedApiKey === 'generated' && generatedApiKey.trim()) ||
      (selectedApiKey === 'session' && accessToken));

  const effectiveApiKey =
    selectedApiKey === 'generated' ? generatedApiKey.trim() : customApiKey.trim();

  // Quick Start: Copy signed content to verify
  const handleCopyToVerify = () => {
    if (lastSignedContent) {
      const verifyEndpoint = endpoints.find(e => e.id === 'verify');
      if (verifyEndpoint) {
        preserveRequestBodyOnEndpointChangeRef.current = true;
        setSelectedEndpoint(verifyEndpoint);
        setRequestEditorMode('form');
        setFormValues((prev) => ({
          ...prev,
          text: lastSignedContent,
        }));
        setRequestBody(JSON.stringify({ text: lastSignedContent }, null, 2));
        setQuickStartStep(2);
        toast.success('Signed content copied to Verify. Click Send Request!');
      }
    }
  };

  // Guided Tour: Start the 4-step tour (API Key → Sign → Copy → Verify)
  const startGuidedTour = () => {
    setTourActive(true);
    setTourStep(0);
    setQuickStartStep(0);
    setLastSignedContent(null);
    setSelectedApiKey('generated'); // Auto-select "Generate" option
    localStorage.setItem('playground_tour_active', 'true');
    toast.success('Welcome to the guided tour! Let\'s create your API key first.');
  };

  const skipTour = () => {
    setTourActive(false);
    setTourStep(0);
    localStorage.removeItem('playground_tour_active');
    toast.info('Tour skipped. You can restart it anytime from the Quick Start banner.');
  };

  const nextTourStep = () => {
    const nextStep = tourStep + 1;

    if (nextStep === 1) {
      // Step 1: Load Sign endpoint with demo content
      const signEndpoint = endpoints.find(e => e.id === 'sign');
      if (signEndpoint) {
        preserveRequestBodyOnEndpointChangeRef.current = true;
        setSelectedEndpoint(signEndpoint);
        setRequestEditorMode('form');
        setFormValues((prev) => ({
          ...prev,
          text: DEMO_SIGN_SAMPLE.text,
          document_title: DEMO_SIGN_SAMPLE.document_title,
          document_type: DEMO_SIGN_SAMPLE.document_type,
          segmentation_level: DEMO_SIGN_SAMPLE.segmentation_level,
          manifest_mode: DEMO_SIGN_SAMPLE.manifest_mode,
          embedding_strategy: DEMO_SIGN_SAMPLE.embedding_strategy,
        }));
        setRequestBody(JSON.stringify({
          text: DEMO_SIGN_SAMPLE.text,
          document_title: DEMO_SIGN_SAMPLE.document_title,
          options: {
            document_type: DEMO_SIGN_SAMPLE.document_type,
            segmentation_level: DEMO_SIGN_SAMPLE.segmentation_level,
            manifest_mode: DEMO_SIGN_SAMPLE.manifest_mode,
          },
        }, null, 2));
        setTourStep(1);
        setQuickStartStep(1);
        toast.success('Great! Now let\'s sign some content with your API key.');
      }
    } else if (nextStep === 2) {
      // Step 2: Copy to Verify (handled by handleCopyToVerify)
      setTourStep(2);
      setQuickStartStep(2);
    } else if (nextStep === 3) {
      // Step 3: Verify
      setTourStep(3);
      setQuickStartStep(3);
    } else if (nextStep === 4) {
      // Tour complete
      setTourActive(false);
      setTourStep(0);
      localStorage.removeItem('playground_tour_active');
      toast.success('🎉 Tour complete! You\'ve mastered the Sign → Verify flow.');
    }
  };

  // Legacy Demo Mode (kept for backward compatibility)
  const handleTryDemo = () => {
    startGuidedTour();
  };

  const handleGenerateKey = async () => {
    if (!accessToken) {
      toast.error('You must be logged in to generate an API key');
      return;
    }
    setIsGeneratingKey(true);
    try {
      const result = await apiClient.createApiKey(accessToken, 'Playground Key', ['sign', 'verify', 'read']);
      const key = result.data?.key;
      if (!key) {
        toast.error('Key creation succeeded but no key was returned');
        return;
      }
      setGeneratedApiKey(key);
      setSelectedApiKey('generated');
      toast.success('New API key generated for the playground');

      // Auto-advance tour if active on step 0
      if (tourActive && tourStep === 0) {
        setTimeout(() => nextTourStep(), 1000);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to generate API key');
    } finally {
      setIsGeneratingKey(false);
    }
  };

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

      // Determine which auth to use based on selection.
      // Important: even for "public" endpoints, if the user explicitly selected an API key,
      // we should still send it (some deployments/gateways may require it).
      if (selectedApiKey === 'session' && accessToken) {
        // Session token - always use Bearer format
        headers['Authorization'] = `Bearer ${accessToken}`;
      } else if ((selectedApiKey === 'custom' || selectedApiKey === 'generated') && effectiveApiKey) {
        // API Key - use Bearer format
        headers['Authorization'] = `Bearer ${effectiveApiKey}`;
      }

      if (selectedEndpoint.authType === 'apikey' && selectedApiKey === 'session') {
        toast.warning('This endpoint requires an API key');
      }

      if (selectedEndpoint.requiresAuth && !headers['Authorization']) {
        toast.warning('Authentication required for this endpoint');
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
        // Store signed content for Quick Start flow
        // Unified /sign returns data.document.signed_text
        const signedDoc = data?.data?.document;
        if (selectedEndpoint.id === 'sign' && data.success && signedDoc?.signed_text) {
          setLastSignedContent(signedDoc.signed_text);
          setQuickStartStep(1);
        } else if (selectedEndpoint.id === 'sign' && data.success && data.signed_text) {
          // Legacy format fallback
          setLastSignedContent(data.signed_text);
          setQuickStartStep(1);
        }
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

  const signedTextPlain = useMemo(() => extractSignedTextFromResponse(response ?? ''), [response]);

  const copySignedTextPlain = () => {
    if (!signedTextPlain) {
      toast.error('No signed_text found in this response');
      return;
    }

    navigator.clipboard.writeText(signedTextPlain);
    toast.success('Signed text copied (plain text)');
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
            <h1 className="text-2xl font-bold text-delft-blue dark:text-white">API Playground</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Test API endpoints interactively with your credentials.
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
        {/* Mode toggle */}
        <div className="flex gap-1 mt-4 bg-slate-100 dark:bg-slate-800 p-1 rounded-xl w-fit">
          <button
            onClick={() => setPlaygroundMode('explorer')}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              playgroundMode === 'explorer'
                ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
            }`}
          >
            API Explorer
          </button>
          <button
            onClick={() => setPlaygroundMode('copy-paste-test')}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              playgroundMode === 'copy-paste-test'
                ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
            }`}
          >
            Copy-Paste Test
          </button>
        </div>
      </div>

      {playgroundMode === 'copy-paste-test' ? (
        <Card>
          <CardContent className="pt-6">
            <CopyPasteSurvivalTester apiKey={effectiveApiKey} />
          </CardContent>
        </Card>
      ) : (<>

      {/* How It Works Guide */}
      <Card className="mb-6 border-slate-200 dark:border-slate-700">
        <details>
          <summary className="cursor-pointer px-6 py-4 flex items-center gap-3 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg transition-colors">
            <svg className="w-5 h-5 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <span className="font-semibold text-delft-blue dark:text-white">How It Works — Quick Reference</span>
            <span className="text-xs text-muted-foreground ml-auto">Click to expand</span>
          </summary>
          <CardContent className="pt-0 pb-5">
            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-100 dark:border-blue-800">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold">1</div>
                  <h4 className="font-semibold text-blue-900 dark:text-blue-200">Sign</h4>
                </div>
                <p className="text-xs text-blue-800 dark:text-blue-300 leading-relaxed">
                  Send your text to <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">POST /sign</code>.
                  We embed invisible cryptographic signatures using Unicode variation selectors.
                  The signed text looks identical to the original.
                </p>
                <div className="mt-2 p-2 bg-white dark:bg-slate-800 rounded text-xs font-mono text-slate-600 dark:text-slate-300">
                  <span className="text-blue-600">Recommended:</span> segmentation: sentence, mode: micro
                </div>
              </div>
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-100 dark:border-green-800">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-6 h-6 rounded-full bg-green-600 text-white flex items-center justify-center text-xs font-bold">2</div>
                  <h4 className="font-semibold text-green-900 dark:text-green-200">Publish</h4>
                </div>
                <p className="text-xs text-green-800 dark:text-green-300 leading-relaxed">
                  Use the <code className="bg-green-100 dark:bg-green-800 px-1 rounded">signed_text</code> from the response everywhere you publish.
                  The invisible signatures survive copy-paste and travel with the text across platforms.
                </p>
              </div>
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-100 dark:border-purple-800">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-6 h-6 rounded-full bg-purple-600 text-white flex items-center justify-center text-xs font-bold">3</div>
                  <h4 className="font-semibold text-purple-900 dark:text-purple-200">Verify</h4>
                </div>
                <p className="text-xs text-purple-800 dark:text-purple-300 leading-relaxed">
                  Send the signed text to <code className="bg-purple-100 dark:bg-purple-800 px-1 rounded">POST /verify</code>.
                  Get back: who signed it, when, and whether it has been tampered with.
                  Sentence-level signing pinpoints exactly which sentence changed.
                </p>
              </div>
            </div>
          </CardContent>
        </details>
      </Card>

      {/* Quick Start Banner */}
      {showQuickStart && (
        <Card className="mb-6 border-blue-200 dark:border-blue-800 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                    <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-semibold text-delft-blue dark:text-white">Guided Tour: API Key → Sign → Verify</h3>
                    <p className="text-sm text-muted-foreground">Complete walkthrough in 4 steps</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <div className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${tourActive && tourStep >= 0 ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300' : 'bg-slate-100 text-slate-500'}`}>
                    <span className={tourStep > 0 ? 'text-green-600' : ''}>1</span> API Key
                    {tourStep > 0 && <svg className="w-3 h-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
                  </div>
                  <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <div className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${tourActive && tourStep >= 1 ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300' : 'bg-slate-100 text-slate-500'}`}>
                    <span className={tourStep > 1 ? 'text-green-600' : ''}>2</span> Sign
                    {tourStep > 1 && <svg className="w-3 h-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
                  </div>
                  <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <div className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${tourActive && tourStep >= 2 ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300' : 'bg-slate-100 text-slate-500'}`}>
                    <span className={tourStep > 2 ? 'text-green-600' : ''}>3</span> Copy
                    {tourStep > 2 && <svg className="w-3 h-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
                  </div>
                  <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <div className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${tourActive && tourStep >= 3 ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300' : 'bg-slate-100 text-slate-500'}`}>
                    <span className={tourStep > 3 ? 'text-green-600' : ''}>4</span> Verify
                    {tourStep > 3 && <svg className="w-3 h-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {!tourActive && quickStartStep === 0 && (
                  <Button variant="secondary" size="sm" onClick={startGuidedTour}>
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
                    Start Guided Tour
                  </Button>
                )}
                {quickStartStep === 1 && lastSignedContent && (
                  <Button variant="primary" size="sm" onClick={handleCopyToVerify} data-tour-target="copy-to-verify">
                    Copy to Verify →
                  </Button>
                )}
                <button
                  onClick={() => setShowQuickStart(false)}
                  className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Panel - Endpoint Selection */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Endpoints</CardTitle>
                <span className="text-xs text-muted-foreground">{filteredEndpoints.length} available</span>
              </div>
              {/* Search Input */}
              <div className="relative mt-2">
                <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <Input
                  type="text"
                  placeholder="Search endpoints..."
                  value={endpointSearch}
                  onChange={(e) => setEndpointSearch(e.target.value)}
                  className="pl-9 text-sm"
                />
                {endpointSearch && (
                  <button
                    onClick={() => setEndpointSearch('')}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                )}
              </div>
            </CardHeader>
            <CardContent className="p-0">
              {/* Grouped Vertical Navigation */}
              <div className="max-h-96 overflow-y-auto">
                {!endpointSearch ? (
                  <div className="px-4 pb-3 space-y-4">
                    {categories.map((category) => {
                      const categoryEndpoints = endpoints.filter((e) => e.category === category);

                      return (
                        <div key={category}>
                          <div className="flex items-center justify-between text-xs font-semibold text-slate-600 dark:text-slate-300 mb-2">
                            <span>{category}</span>
                            <span className="text-muted-foreground">{categoryEndpoints.length}</span>
                          </div>
                          <div className="rounded-lg border overflow-hidden">
                            {categoryEndpoints.map((endpoint) => {
                              const endpointHasAccess = hasTierAccess(userTier, endpoint.minTier);
                              return (
                                <button
                                  key={endpoint.id}
                                  onClick={() => {
                                    setSelectedEndpoint(endpoint);
                                  }}
                                  className={`w-full text-left px-3 py-3 border-b last:border-0 transition-colors ${
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
                                      <span
                                        className={`px-1.5 py-0.5 text-[10px] font-medium rounded ${tierColors[endpoint.minTier]}`}
                                      >
                                        {!endpointHasAccess && (
                                          <svg
                                            className="w-3 h-3 inline mr-0.5"
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                          >
                                            <path
                                              strokeLinecap="round"
                                              strokeLinejoin="round"
                                              strokeWidth={2}
                                              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                                            />
                                          </svg>
                                        )}
                                        {tierLabels[endpoint.minTier]}+
                                      </span>
                                    )}
                                  </div>
                                  <p className="text-xs text-muted-foreground truncate">{endpoint.path}</p>
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="px-4 pb-3 space-y-4">
                    {Object.entries(filteredEndpointsByCategory).map(([category, categoryEndpoints]) => (
                      <div key={category}>
                        <div className="flex items-center justify-between text-xs font-semibold text-slate-600 dark:text-slate-300 mb-2">
                          <span>{category}</span>
                          <span className="text-muted-foreground">{categoryEndpoints.length}</span>
                        </div>
                        <div className="rounded-lg border overflow-hidden">
                          {categoryEndpoints.map((endpoint) => {
                            const endpointHasAccess = hasTierAccess(userTier, endpoint.minTier);
                            return (
                              <button
                                key={endpoint.id}
                                onClick={() => {
                                  setSelectedEndpoint(endpoint);
                                }}
                                className={`w-full text-left px-3 py-3 border-b last:border-0 transition-colors ${
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
                                      {!endpointHasAccess && (
                                        <svg
                                          className="w-3 h-3 inline mr-0.5"
                                          fill="none"
                                          stroke="currentColor"
                                          viewBox="0 0 24 24"
                                        >
                                          <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                                          />
                                        </svg>
                                      )}
                                      {tierLabels[endpoint.minTier]}+
                                    </span>
                                  )}
                                </div>
                                <p className="text-xs text-muted-foreground truncate">{endpoint.path}</p>
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Authentication */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Authentication</CardTitle>
              {selectedEndpoint.authType && (
                <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                  {selectedEndpoint.authType === 'session' && (
                    <>
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                      This endpoint uses session auth
                    </>
                  )}
                  {selectedEndpoint.authType === 'apikey' && (
                    <>
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" /></svg>
                      This endpoint requires an API key
                    </>
                  )}
                  {selectedEndpoint.authType === 'both' && (
                    <>
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                      Supports both session and API key
                    </>
                  )}
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
                  <option value="generated">API Key (Generate for Playground)</option>
                  <option value="custom">API Key (Paste Below)</option>
                  <option value="session">Session Token (Dashboard Only)</option>
                </select>
                <p className="text-xs text-muted-foreground mt-2">
                  All playground requests use authentication so they appear in your activity timeline.
                </p>
              </div>

              {selectedApiKey === 'custom' && (
                <div>
                  <label className="block text-sm font-medium mb-2">Your API Key</label>
                  <Input
                    type="text"
                    value={customApiKey}
                    onChange={(e) => setCustomApiKey(e.target.value)}
                    placeholder="ek_live_..."
                    className="font-mono text-sm"
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    Paste your organization API key.
                  </p>
                </div>
              )}

              {selectedApiKey === 'generated' && (
                <div className="space-y-3">
                  <Button
                    variant="secondary"
                    onClick={handleGenerateKey}
                    disabled={!accessToken || isGeneratingKey}
                    className="w-full"
                    data-tour-target="generate-api-key"
                  >
                    {isGeneratingKey ? 'Generating...' : 'Generate New API Key'}
                  </Button>
                  {generatedApiKey ? (
                    <div className="space-y-2">
                      <p className="text-xs text-green-600 dark:text-green-400">
                        ✓ Generated key is ready to use in this playground.
                      </p>
                      <Input
                        type="text"
                        value={generatedApiKey}
                        readOnly
                        className="font-mono text-sm"
                      />
                      <Button
                        variant="ghost"
                        onClick={() => copyToClipboard(generatedApiKey)}
                        className="w-full"
                      >
                        Copy Generated Key
                      </Button>
                    </div>
                  ) : (
                    <p className="text-xs text-muted-foreground">
                      Generate a new API key using your dashboard session. The key will be shown once.
                    </p>
                  )}

                  {apiKeysQuery.data && apiKeysQuery.data.length > 0 && (
                    <p className="text-xs text-muted-foreground">
                      Existing keys are listed in API Keys, but for security the full secret cannot be retrieved.
                    </p>
                  )}
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
                      <svg className="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                      No session token available. You may have logged in via OAuth. Use an API key for authentication, or log out and log in with email/password.
                    </p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    Session tokens are for dashboard endpoints. Use an API key for signing.
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

              {/* Template Selector (for Sign endpoint only) */}
              {selectedEndpoint.id === 'sign' && (
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Rights Template
                    <span className="ml-2 text-xs font-normal text-muted-foreground">(Enterprise tier)</span>
                  </label>
                  <TemplateSelector
                    value={selectedTemplateId}
                    onValueChange={setSelectedTemplateId}
                    className="w-full"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Select a template to embed rights assertions (AI training permissions, licensing terms) into your signed content.
                  </p>
                </div>
              )}

              {/* Request Body */}
              {['POST', 'PUT'].includes(selectedEndpoint.method) && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <label className="block text-sm font-medium">Request Body</label>
                      {supportsFormBuilder && (
                        <div className="flex items-center gap-1">
                          <button
                            type="button"
                            onClick={() => {
                              setRequestEditorMode('form');
                              if (selectedEndpoint.id === 'sign') {
                                setSelectedTemplateId(formValues.template_id.trim() || undefined);
                              }
                            }}
                            className={`px-2 py-0.5 text-xs rounded border transition-colors ${
                              requestEditorMode === 'form'
                                ? 'bg-blue-ncs text-white border-blue-ncs'
                                : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
                            }`}
                          >
                            Guided Form
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              setRequestEditorMode('json');
                            }}
                            className={`px-2 py-0.5 text-xs rounded border transition-colors ${
                              requestEditorMode === 'json'
                                ? 'bg-blue-ncs text-white border-blue-ncs'
                                : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
                            }`}
                          >
                            Advanced JSON
                          </button>
                        </div>
                      )}

                      {requestEditorMode === 'json' && !jsonValidation.valid && (
                        <Badge variant="destructive" className="text-xs">Invalid JSON</Badge>
                      )}
                      {requestEditorMode === 'json' && jsonValidation.valid && requestBody.trim() && (
                        <Badge
                          variant="secondary"
                          className="text-xs bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                        >
                          Valid
                        </Badge>
                      )}

                      {requestEditorMode === 'form' && !formValidation.valid && (
                        <Badge variant="destructive" className="text-xs">Missing required fields</Badge>
                      )}
                      {requestEditorMode === 'form' && formValidation.valid && requestBody.trim() && (
                        <Badge
                          variant="secondary"
                          className="text-xs bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                        >
                          Ready
                        </Badge>
                      )}
                    </div>

                    <button
                      onClick={() => copyToClipboard(requestBody)}
                      className="text-xs text-blue-ncs hover:underline"
                    >
                      Copy
                    </button>
                  </div>

                  {supportsFormBuilder && requestEditorMode === 'form' ? (
                    <div className="space-y-3">
                      {selectedEndpoint.id === 'sign' && (
                        <>
                          <div>
                            <label className="block text-sm font-medium mb-1">Text <span className="text-red-500">*</span></label>
                            <textarea
                              value={formValues.text}
                              onChange={(e) => setFormValues((prev) => ({ ...prev, text: e.target.value }))}
                              rows={6}
                              className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 resize-y dark:bg-slate-700 dark:text-slate-100 border-slate-200 dark:border-slate-600 focus:ring-blue-ncs"
                              placeholder="Paste or type the content you want to sign..."
                              style={{ WebkitUserSelect: 'text', userSelect: 'text' }}
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium mb-1">Document Title</label>
                            <Input
                              value={formValues.document_title}
                              onChange={(e) => setFormValues((prev) => ({ ...prev, document_title: e.target.value }))}
                              placeholder="My Article"
                            />
                          </div>
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <label className="block text-sm font-medium mb-1">Segmentation</label>
                              <select
                                value={formValues.segmentation_level}
                                onChange={(e) => setFormValues((prev) => ({ ...prev, segmentation_level: e.target.value }))}
                                className="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 dark:bg-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-ncs"
                              >
                                <option value="">Default (document)</option>
                                <option value="sentence">Sentence (recommended)</option>
                                <option value="paragraph">Paragraph</option>
                                <option value="section">Section</option>
                                <option value="word">Word (Enterprise)</option>
                              </select>
                              <p className="text-xs text-muted-foreground mt-1">Sentence-level lets you pinpoint exactly which sentence was changed.</p>
                            </div>
                            <div>
                              <label className="block text-sm font-medium mb-1">Manifest Mode</label>
                              <select
                                value={formValues.manifest_mode}
                                onChange={(e) => setFormValues((prev) => ({ ...prev, manifest_mode: e.target.value }))}
                                className="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 dark:bg-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-ncs"
                              >
                                <option value="">Default (full)</option>
                                <option value="micro">Micro (recommended)</option>
                                <option value="full">Full C2PA</option>
                                <option value="lightweight_uuid">Lightweight UUID</option>
                              </select>
                              <p className="text-xs text-muted-foreground mt-1">micro: compact per-sentence markers + C2PA manifest. Use ecc/embed_c2pa flags for control.</p>
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <label className="block text-sm font-medium mb-1">Document Type</label>
                              <select
                                value={formValues.document_type}
                                onChange={(e) => setFormValues((prev) => ({ ...prev, document_type: e.target.value }))}
                                className="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 dark:bg-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-ncs"
                              >
                                <option value="">Default (article)</option>
                                <option value="article">Article</option>
                                <option value="legal_brief">Legal Brief</option>
                                <option value="contract">Contract</option>
                                <option value="ai_output">AI Output</option>
                              </select>
                            </div>
                            <div>
                              <label className="block text-sm font-medium mb-1">Embedding Strategy</label>
                              <select
                                value={formValues.embedding_strategy}
                                onChange={(e) => setFormValues((prev) => ({ ...prev, embedding_strategy: e.target.value }))}
                                className="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 dark:bg-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-ncs"
                              >
                                <option value="">Default (single_point)</option>
                                <option value="single_point">Single Point</option>
                                <option value="distributed">Distributed</option>
                                <option value="distributed_redundant">Distributed Redundant</option>
                              </select>
                            </div>
                          </div>
                          {/* Print Leak Detection — Enterprise only */}
                          {hasTierAccess(userTier, 'enterprise') && (
                            <label className="flex items-center gap-2 text-sm mt-1 cursor-pointer select-none">
                              <input
                                type="checkbox"
                                checked={formValues.enable_print_fingerprint}
                                onChange={(e) =>
                                  setFormValues((prev) => ({
                                    ...prev,
                                    enable_print_fingerprint: e.target.checked,
                                  }))
                                }
                                className="rounded border-slate-300 text-blue-ncs focus:ring-blue-ncs"
                              />
                              <span className="font-medium">Print Leak Detection</span>
                              <span className="text-xs text-muted-foreground">
                                — spacing fingerprint for print/scan tracing
                              </span>
                              <span className="text-xs bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded font-medium">
                                Enterprise
                              </span>
                            </label>
                          )}
                        </>
                      )}

                      {selectedEndpoint.id === 'verify' && (
                        <div>
                          <label className="block text-sm font-medium mb-1">Signed Text (required)</label>
                          <textarea
                            value={formValues.text}
                            onChange={(e) => setFormValues((prev) => ({ ...prev, text: e.target.value }))}
                            rows={8}
                            className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 resize-y dark:bg-slate-700 dark:text-slate-100 border-slate-200 dark:border-slate-600 focus:ring-blue-ncs"
                            placeholder="Paste signed content to verify..."
                            style={{ WebkitUserSelect: 'text', userSelect: 'text' }}
                          />
                        </div>
                      )}

                      {selectedEndpoint.id === 'lookup' && (
                        <div>
                          <label className="block text-sm font-medium mb-1">Sentence Text (required)</label>
                          <textarea
                            value={formValues.sentence_text}
                            onChange={(e) => setFormValues((prev) => ({ ...prev, sentence_text: e.target.value }))}
                            rows={4}
                            className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 resize-y dark:bg-slate-700 dark:text-slate-100 border-slate-200 dark:border-slate-600 focus:ring-blue-ncs"
                            placeholder="Enter a sentence to look up..."
                            style={{ WebkitUserSelect: 'text', userSelect: 'text' }}
                          />
                        </div>
                      )}

                      {!formValidation.valid && formValidation.error && (
                        <p className="text-xs text-red-600 dark:text-red-400">
                          <svg
                            className="w-4 h-4 inline mr-1"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                            />
                          </svg>
                          {formValidation.error}
                        </p>
                      )}

                      <details className="mt-2">
                        <summary className="text-xs text-muted-foreground cursor-pointer hover:text-blue-ncs">
                          Generated JSON
                        </summary>
                        <div className="mt-2">
                          <textarea
                            value={requestBody}
                            readOnly
                            rows={6}
                            className="w-full px-3 py-2 border rounded-lg font-mono text-xs resize-y dark:bg-slate-700 dark:text-slate-100 border-slate-200 dark:border-slate-600"
                            style={{ WebkitUserSelect: 'text', userSelect: 'text' }}
                          />
                        </div>
                      </details>
                    </div>
                  ) : (
                    <>
                      <textarea
                        value={requestBody}
                        onChange={(e) => {
                          setRequestBody(e.target.value);
                          if (supportsFormBuilder) {
                            const parsed = parseRequestBodyJson(selectedEndpoint.id, e.target.value) as
                              | Partial<PlaygroundFormState>
                              | null;
                            if (parsed) {
                              setFormValues((prev) => ({
                                ...prev,
                                text: parsed.text ?? prev.text,
                                document_title: parsed.document_title ?? prev.document_title,
                                document_type: parsed.document_type ?? prev.document_type,
                                template_id: parsed.template_id ?? prev.template_id,
                                sentence_text: parsed.sentence_text ?? prev.sentence_text,
                                segmentation_level: parsed.segmentation_level ?? prev.segmentation_level,
                                manifest_mode: parsed.manifest_mode ?? prev.manifest_mode,
                                embedding_strategy: parsed.embedding_strategy ?? prev.embedding_strategy,
                              }));
                            }
                          }
                        }}
                        rows={8}
                        className={`w-full px-3 py-2 border rounded-lg font-mono text-sm focus:outline-none focus:ring-2 resize-y dark:bg-slate-700 dark:text-slate-100 ${
                          !jsonValidation.valid
                            ? 'border-red-300 dark:border-red-700 focus:ring-red-500'
                            : 'border-slate-200 dark:border-slate-600 focus:ring-blue-ncs'
                        }`}
                        placeholder="Enter JSON request body..."
                        style={{ WebkitUserSelect: 'text', userSelect: 'text' }}
                      />
                      {!jsonValidation.valid && jsonValidation.error && (
                        <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                          <svg className="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                          {jsonValidation.error}
                        </p>
                      )}
                    </>
                  )}

                  {/* Field Documentation */}
                  {fieldDocs[selectedEndpoint.id] && (
                    <details className="mt-2">
                      <summary className="text-xs text-muted-foreground cursor-pointer hover:text-blue-ncs">
                        <svg className="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                        Field documentation
                      </summary>
                      <div className="mt-2 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg text-xs space-y-1">
                        {Object.entries(fieldDocs[selectedEndpoint.id]).map(([field, desc]) => (
                          <div key={field} className="flex gap-2">
                            <code className="font-mono text-blue-600 dark:text-blue-400">{field}</code>
                            <span className="text-muted-foreground">— {desc}</span>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              )}

              {/* Tier Access Warning */}
              {!hasAccess && selectedEndpoint.minTier && (
                <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <svg className="w-6 h-6 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
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
                disabled={!canSendRequest}
                className="w-full"
                data-tour-target="send-request"
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
                <div className="space-y-4">
                  {/* Human-Readable Summary Card */}
                  {responseSummary && (
                    <div className={`p-4 rounded-lg border ${
                      responseSummary.warning
                        ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800'
                        : responseSummary.success
                          ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                          : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                    }`}>
                      <div className="flex items-start gap-3">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            responseSummary.warning
                              ? 'bg-amber-100 dark:bg-amber-900'
                              : responseSummary.success
                                ? 'bg-green-100 dark:bg-green-900'
                                : 'bg-red-100 dark:bg-red-900'
                          }`}
                        >
                          {responseSummary.warning ? (
                            <svg className="w-5 h-5 text-amber-700 dark:text-amber-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                          ) : responseSummary.success ? (
                            <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                          ) : (
                            <svg className="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                          )}
                        </div>
                        <div className="flex-1">
                          {responseSummary.type === 'verify' && (
                            <>
                              <h4
                                className={`font-semibold ${
                                  responseSummary.warning
                                    ? 'text-amber-900 dark:text-amber-200'
                                    : responseSummary.success
                                      ? 'text-green-800 dark:text-green-200'
                                      : 'text-red-800 dark:text-red-200'
                                }`}
                              >
                                {responseSummary.warning
                                  ? 'Signature Valid (Untrusted Signer)'
                                  : responseSummary.valid
                                    ? 'Signature Valid'
                                    : responseSummary.tampered
                                      ? 'Content Tampered'
                                      : 'Verification Failed'}
                              </h4>
                              <div className="mt-2 text-sm space-y-1">
                                <p className="text-muted-foreground">
                                  <span className="font-medium">Signer:</span> {responseSummary.signerName}
                                </p>
                                {responseSummary.warning && (
                                  <p className="text-muted-foreground">
                                    <span className="font-medium">Trust:</span> Not in trust list (signature valid)
                                  </p>
                                )}
                                {responseSummary.embeddingsFound > 1 && (
                                  <p className="text-muted-foreground">
                                    <span className="font-medium">Embeddings found:</span> {responseSummary.embeddingsFound}
                                  </p>
                                )}
                                {responseSummary.reasonCode && (
                                  <p className="text-muted-foreground">
                                    <span className="font-medium">Reason:</span> {responseSummary.reasonCode}
                                  </p>
                                )}
                              </div>
                            </>
                          )}
                          {responseSummary.type === 'sign' && (
                            <>
                              <h4 className="font-semibold text-green-800 dark:text-green-200">
                                Content Signed Successfully
                              </h4>
                              <div className="mt-2 text-sm space-y-1">
                                {responseSummary.documentId && (
                                  <p className="text-muted-foreground">
                                    <span className="font-medium">Document ID:</span>{' '}
                                    <code className="text-xs bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded font-mono">{responseSummary.documentId}</code>
                                  </p>
                                )}
                                {responseSummary.totalSegments && (
                                  <p className="text-muted-foreground">
                                    <span className="font-medium">Segments signed:</span> {responseSummary.totalSegments}
                                  </p>
                                )}
                                {responseSummary.instanceId && (
                                  <p className="text-muted-foreground">
                                    <span className="font-medium">Instance ID:</span>{' '}
                                    <code className="text-xs bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded font-mono">{responseSummary.instanceId}</code>
                                  </p>
                                )}
                                {responseSummary.merkleRoot && (
                                  <p className="text-muted-foreground">
                                    <span className="font-medium">Merkle root:</span>{' '}
                                    <code className="text-xs bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded font-mono">{String(responseSummary.merkleRoot).substring(0, 16)}...</code>
                                  </p>
                                )}
                              </div>
                              <p className="mt-3 text-xs text-green-700 dark:text-green-300">
                                The signed text contains invisible Unicode signatures. Copy it and paste into Verify to confirm.
                              </p>
                              {signedTextPlain && (
                                <div className="mt-3 rounded-lg border border-green-200 dark:border-green-800 bg-white/80 dark:bg-slate-900/40 p-3">
                                  <div className="flex items-center justify-between gap-2">
                                    <p className="text-xs font-medium text-green-900 dark:text-green-200">
                                      Signed text (plain text, ready to paste)
                                    </p>
                                    <Button
                                      variant="primary"
                                      size="sm"
                                      onClick={copySignedTextPlain}
                                      data-testid="copy-signed-text-plain"
                                    >
                                      Copy signed_text
                                    </Button>
                                  </div>
                                  <pre
                                    className="mt-2 max-h-40 overflow-auto rounded bg-slate-950 text-slate-100 p-3 text-xs"
                                    style={{
                                      whiteSpace: 'pre-wrap',
                                      wordBreak: 'break-word',
                                      WebkitUserSelect: 'text',
                                      userSelect: 'text',
                                    }}
                                    data-testid="signed-text-plain-preview"
                                  >
                                    {signedTextPlain}
                                  </pre>
                                </div>
                              )}
                              {showQuickStart && lastSignedContent && (
                                <Button
                                  variant="secondary"
                                  size="sm"
                                  className="mt-3"
                                  onClick={handleCopyToVerify}
                                >
                                  Next: Verify this content →
                                </Button>
                              )}
                            </>
                          )}
                          {responseSummary.type === 'lookup' && (
                            <>
                              <h4 className={`font-semibold ${responseSummary.found ? 'text-green-800 dark:text-green-200' : 'text-amber-800 dark:text-amber-200'}`}>
                                {responseSummary.found ? 'Provenance Found' : 'No Provenance Record'}
                              </h4>
                              {responseSummary.found && (
                                <div className="mt-2 text-sm space-y-1">
                                  {responseSummary.documentTitle && (
                                    <p className="text-muted-foreground">
                                      <span className="font-medium">Document:</span> {responseSummary.documentTitle}
                                    </p>
                                  )}
                                  {responseSummary.organizationName && (
                                    <p className="text-muted-foreground">
                                      <span className="font-medium">Organization:</span> {responseSummary.organizationName}
                                    </p>
                                  )}
                                </div>
                              )}
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Raw JSON Response */}
                  <div className="relative">
                    <div className="absolute top-2 right-2 flex gap-2 z-10">
                      <button
                        onClick={copySelection}
                        className="text-xs bg-slate-700 hover:bg-slate-600 text-slate-200 px-2 py-1 rounded transition-colors"
                      >
                        Copy Selection
                      </button>
                      <button
                        onClick={() => copyToClipboard(response ?? '')}
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
                      {response ?? ''}
                    </pre>
                  </div>
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

      {/* Guided Tour Spotlights */}
      <TourSpotlight
        active={tourActive && tourStep === 0}
        message="Click 'Generate New API Key' to create your API key for testing."
        targetSelector="[data-tour-target='generate-api-key']"
        position="top"
        onNext={() => {
          // Don't show next button - user must click the actual Generate button
        }}
        onSkip={skipTour}
        nextLabel=""
      />

      <TourSpotlight
        active={tourActive && tourStep === 1}
        message="Great! Now let's sign some content. Click 'Send Request' to sign the demo text with your API key."
        targetSelector="[data-tour-target='send-request']"
        position="top"
        onNext={nextTourStep}
        onSkip={skipTour}
        nextLabel="Continue"
      />

      <TourSpotlight
        active={tourActive && tourStep === 2 && lastSignedContent !== null}
        message="Perfect! Your content is signed. Now click 'Copy to Verify →' to move the signed content to the verify endpoint."
        targetSelector="[data-tour-target='copy-to-verify']"
        position="top"
        onNext={nextTourStep}
        onSkip={skipTour}
        nextLabel="Continue"
      />

      <TourSpotlight
        active={tourActive && tourStep === 3}
        message="Final step! Click 'Send Request' to verify the signed content and see the cryptographic proof."
        targetSelector="[data-tour-target='send-request']"
        position="top"
        onNext={nextTourStep}
        onSkip={skipTour}
        nextLabel="Finish Tour"
      />
      </>)}
    </DashboardLayout>
  );
}
