'use client';

import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent } from '@encypher/design-system';
import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { OnboardingChecklist } from '../components/onboarding/OnboardingChecklist';
import { OnboardingLaunchpad } from '../components/onboarding/OnboardingLaunchpad';
import apiClient, { TimeSeriesData } from '../lib/api';
import { useOrganization } from '../contexts/OrganizationContext';
import { useDemoMode, DEMO_STATS, DEMO_STATS_60D, DEMO_SPARKLINE, DEMO_DOCS_SPARKLINE, DEMO_API_KEYS, DEMO_SETUP_STATUS, DEMO_ACTIVITY } from '../contexts/DemoModeContext';

// ---- Custom Provenance Icons ----
// Domain-specific SVGs for signing, verification, provenance, and content protection.
// Generic UI actions (arrows, plus) remain simple stroked icons.

// Signing quill -- represents document signing / content attestation
const IconSign = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <path d="M17 3l4 4L7.5 20.5 2 22l1.5-5.5L17 3z" />
    <path d="M15 5l4 4" />
    <path d="M2 22c2-2 4-3.5 8-3.5" />
  </svg>
);

// Verification lens -- magnifier with checkmark, represents proof verification
const IconVerify = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <circle cx="10.5" cy="10.5" r="7" />
    <path d="M21 21l-4.35-4.35" />
    <path d="M7.5 10.5l2 2 4-4" />
  </svg>
);

// Provenance shield -- shield with chain link, represents content provenance
const IconProvenance = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2l8 4v6c0 5.25-3.5 9.74-8 11-4.5-1.26-8-5.75-8-11V6l8-4z" />
    <circle cx="10" cy="12" r="2" />
    <circle cx="14" cy="12" r="2" />
    <path d="M12 12h0" />
  </svg>
);

// Signed document -- document with embedded seal/stamp
const IconSignedDoc = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" />
    <path d="M14 2v6h6" />
    <circle cx="12" cy="15" r="3" />
    <path d="M10.5 13.5l1.5 1.5 2-2" />
  </svg>
);

// Formal notice -- gavel / legal stamp
const IconFormalNotice = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="18" width="20" height="3" rx="1" />
    <path d="M10 18V8l-3 3" />
    <path d="M14 18V8l3 3" />
    <rect x="8" y="4" width="8" height="4" rx="1" />
  </svg>
);

// Content protection funnel -- layered shield with flow
const IconContentProtection = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2l8 4v6c0 5.25-3.5 9.74-8 11-4.5-1.26-8-5.75-8-11V6l8-4z" />
    <path d="M8 10h8M8 13h6M8 16h4" />
  </svg>
);

// API key -- key with circuit/digital pattern
const IconApiKey = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <circle cx="8" cy="15" r="5" />
    <path d="M11.5 11.5L21 2" />
    <path d="M18 5l3-1" />
    <path d="M17 8l3-1" />
    <circle cx="8" cy="15" r="1.5" fill="currentColor" />
  </svg>
);

// Generic UI icons (kept simple -- these are navigation/action affordances, not domain concepts)
const IconArrowRight = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  </svg>
);

const IconPlus = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
);

const IconBook = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
  </svg>
);

const IconLink = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
  </svg>
);

const IconChart = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>
);

// ---- Animated number counter ----
function useCountUp(target: number, duration = 800) {
  const [value, setValue] = useState(0);
  const prevTarget = useRef(0);

  useEffect(() => {
    if (target === prevTarget.current) return;
    const start = prevTarget.current;
    prevTarget.current = target;
    const startTime = performance.now();

    function tick(now: number) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(start + (target - start) * eased));
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }, [target, duration]);

  return value;
}

// Skeleton loader component
function StatCardSkeleton() {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-6 animate-pulse">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="h-4 w-24 bg-muted rounded mb-3" />
          <div className="h-10 w-20 bg-muted rounded mb-2" />
          <div className="h-3 w-32 bg-muted rounded" />
        </div>
        <div className="w-12 h-12 bg-muted rounded-xl" />
      </div>
    </div>
  );
}

const VERIFICATION_THRESHOLD = 500;

function ProgressRing({ value, max, size = 48, strokeWidth = 4, color = '#2a87c4' }: {
  value: number; max: number; size?: number; strokeWidth?: number; color?: string;
}) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(1, value / max);
  const offset = circumference * (1 - pct);
  return (
    <svg width={size} height={size} className="transform -rotate-90">
      <circle cx={size / 2} cy={size / 2} r={radius} fill="none"
        stroke="currentColor" className="text-muted/30" strokeWidth={strokeWidth} />
      <circle cx={size / 2} cy={size / 2} r={radius} fill="none"
        stroke={color} strokeWidth={strokeWidth} strokeLinecap="round"
        strokeDasharray={circumference} strokeDashoffset={offset}
        style={{ transition: 'stroke-dashoffset 600ms ease-out' }} />
    </svg>
  );
}

function MiniSparkline({ data, color = '#2a87c4' }: { data: number[]; color?: string }) {
  if (!data || data.length < 2) return null;
  const max = Math.max(...data, 1);
  const width = 80;
  const height = 24;
  const points = data.map((v, i) => `${(i / (data.length - 1)) * width},${height - (v / max) * height}`).join(' ');
  const areaPoints = `0,${height} ${points} ${width},${height}`;
  return (
    <svg width={width} height={height} className="mt-1 sparkline-draw">
      <polyline points={areaPoints} fill={`${color}20`} stroke="none" />
      <polyline points={points} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function TrendBadge({ current, prior }: { current: number; prior: number }) {
  if (prior === 0 && current === 0) {
    return <span className="text-xs text-muted-foreground">No activity</span>;
  }
  if (prior === 0) {
    return (
      <span className="inline-flex items-center px-1.5 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs font-medium">
        +{current} new
      </span>
    );
  }
  const pctChange = Math.round(((current - prior) / prior) * 100);
  if (Math.abs(pctChange) <= 2) {
    return (
      <span className="inline-flex items-center gap-0.5 text-xs font-medium text-amber-600 dark:text-amber-400">
        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
        </svg>
        Steady
      </span>
    );
  }
  const isUp = pctChange > 0;
  return (
    <span className={`inline-flex items-center gap-0.5 text-xs font-medium ${isUp ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isUp ? 'M5 10l7-7m0 0l7 7m-7-7v18' : 'M19 14l-7 7m0 0l-7-7m7 7V3'} />
      </svg>
      {Math.abs(pctChange)}%
    </span>
  );
}

function ApiKeysSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2].map((i) => (
        <div key={i} className="bg-gradient-to-r from-slate-50 to-white dark:from-slate-800 dark:to-slate-700 rounded-xl border border-border p-5 animate-pulse">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-muted rounded-lg" />
            <div className="flex-1">
              <div className="h-5 w-32 bg-muted rounded mb-2" />
              <div className="h-4 w-48 bg-muted rounded" />
            </div>
            <div className="h-6 w-16 bg-muted rounded-full" />
          </div>
        </div>
      ))}
    </div>
  );
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

// Content Protection Funnel -- three-step visual journey
function ContentProtectionFunnel({ stats, isLoading }: { stats?: UsageStats; isLoading: boolean }) {
  const docsSigned = stats?.total_documents_signed || 0;
  const verifications = stats?.total_verifications || 0;
  const pct = Math.min(100, Math.round((verifications / VERIFICATION_THRESHOLD) * 100));
  const noticeReady = verifications >= VERIFICATION_THRESHOLD;

  const steps = [
    {
      label: 'Signed',
      value: `${docsSigned.toLocaleString()} articles`,
      done: docsSigned > 0,
      href: '/analytics',
      color: 'text-blue-ncs',
      bgColor: 'bg-blue-ncs',
    },
    {
      label: 'Verified',
      value: verifications > 0 ? `${verifications.toLocaleString()} external` : 'No verifications yet',
      done: verifications > 0,
      href: '/docs',
      color: 'text-[#00CED1]',
      bgColor: 'bg-[#00CED1]',
    },
    {
      label: 'Notice Ready',
      value: noticeReady ? 'Eligible' : `${pct}% -- ${(VERIFICATION_THRESHOLD - verifications).toLocaleString()} more`,
      done: noticeReady,
      href: '/rights',
      color: noticeReady ? 'text-green-600' : 'text-muted-foreground',
      bgColor: noticeReady ? 'bg-green-500' : 'bg-muted-foreground/30',
    },
  ];

  return (
    <div className="bg-gradient-to-br from-delft-blue/5 to-blue-ncs/5 dark:from-delft-blue/20 dark:to-blue-ncs/10 rounded-xl border border-blue-ncs/20 p-5">
      <div className="flex items-center gap-2 mb-5">
        <div className="w-7 h-7 bg-gradient-to-br from-blue-ncs to-columbia-blue rounded-lg flex items-center justify-center text-white">
          <IconContentProtection />
        </div>
        <div>
          <h3 className="text-sm font-semibold tracking-tight text-delft-blue dark:text-white">Content Protection Journey</h3>
          <p className="text-xs text-muted-foreground">Your path to formal notice</p>
        </div>
      </div>
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => <div key={i} className="h-12 bg-muted rounded-lg animate-pulse" />)}
        </div>
      ) : (
        <div className="space-y-0">
          {steps.map((step, i) => (
            <div key={step.label}>
              <Link href={step.href} className="group flex items-start gap-3 py-2.5 hover:bg-white/50 dark:hover:bg-white/5 rounded-lg px-2 -mx-2 transition-colors">
                <div className="flex flex-col items-center mt-0.5">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${step.done ? step.bgColor + ' text-white' : 'border-2 border-muted-foreground/30 text-muted-foreground'}`}>
                    {step.done ? (
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <span className="text-[10px] font-bold">{i + 1}</span>
                    )}
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className={`text-xs font-semibold ${step.done ? step.color : 'text-muted-foreground'}`}>{step.label}</p>
                    <span className="text-xs text-muted-foreground group-hover:text-blue-ncs transition-colors"><IconArrowRight /></span>
                  </div>
                  <p className={`text-[13px] font-medium ${step.done ? 'text-delft-blue dark:text-white' : 'text-muted-foreground'}`}>
                    {step.value}
                  </p>
                </div>
              </Link>
              {i < steps.length - 1 && (
                <div className="ml-[22px] h-3 border-l-2 border-dashed border-muted-foreground/20" />
              )}
            </div>
          ))}
        </div>
      )}
      {/* Progress bar for formal notice */}
      {!isLoading && !noticeReady && (
        <div className="mt-3 pt-3 border-t border-blue-ncs/10">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[11px] text-muted-foreground">Formal Notice progress</span>
            <span className="text-[11px] font-medium text-blue-ncs">{pct}%</span>
          </div>
          <div className="h-1.5 bg-muted rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-blue-ncs to-columbia-blue rounded-full transition-all duration-700" style={{ width: `${pct}%` }} />
          </div>
        </div>
      )}
      <Link href="/analytics" className="block mt-4">
        <button className="w-full py-1.5 text-xs font-medium text-blue-ncs border border-blue-ncs/30 rounded-lg hover:bg-blue-ncs/10 transition-colors">
          View Content Performance
        </button>
      </Link>
    </div>
  );
}

function formatRelativeTime(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffMs = now - then;
  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days === 1) return '1 day ago';
  return `${days} days ago`;
}

export default function DashboardPage() {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const { activeOrganization } = useOrganization();
  const orgId = activeOrganization?.id;
  const { isDemoMode, setDemoMode } = useDemoMode();

  const [greeting, setGreeting] = useState('Hello');

  useEffect(() => {
    const hour = new Date().getHours();
    const nextGreeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';
    setGreeting(nextGreeting);
  }, []);

  // Fetch usage stats
  const statsQuery = useQuery({
    queryKey: ['usage-stats'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getUsageStats(accessToken, 30);
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
    // Return mock data on error for demo purposes
    placeholderData: {
      total_api_calls: 0,
      total_documents_signed: 0,
      total_verifications: 0,
      success_rate: 0,
      avg_response_time_ms: 0,
      period_start: '1970-01-01T00:00:00.000Z',
      period_end: '1970-01-01T00:00:00.000Z',
    },
  });

  // Fetch prior 60-day stats (subtract 30d to get prior 30-day period)
  const priorStatsQuery = useQuery({
    queryKey: ['usage-stats-prior'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getUsageStats(accessToken, 60);
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
    staleTime: 5 * 60_000,
    retry: false,
  });

  // Fetch 30-day daily API call sparkline
  const sparklineQuery = useQuery({
    queryKey: ['api-calls-sparkline'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getTimeSeries(accessToken, 'api_calls', 30, 'day');
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
    staleTime: 5 * 60_000,
    retry: false,
  });

  // Fetch 30-day daily documents signed sparkline
  const docsSparklineQuery = useQuery({
    queryKey: ['docs-signed-sparkline'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getTimeSeries(accessToken, 'documents_signed', 30, 'day');
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
    staleTime: 5 * 60_000,
    retry: false,
  });

  // Fetch API keys
  const keysQuery = useQuery({
    queryKey: ['api-keys-summary', orgId],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getApiKeys(accessToken, orgId);
    },
    enabled: Boolean(accessToken && orgId),
    refetchOnWindowFocus: false,
  });

  const setupQuery = useQuery({
    queryKey: ['setup-status'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getSetupStatus(accessToken);
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
    staleTime: 60_000,
  });

  // Demo mode overrides
  const stats = isDemoMode ? DEMO_STATS : statsQuery.data;
  const apiKeys = isDemoMode ? DEMO_API_KEYS : (keysQuery.data || []);
  const setupStatus = isDemoMode ? DEMO_SETUP_STATUS : setupQuery.data;
  const isLoadingStats = isDemoMode ? false : statsQuery.isLoading;
  const isLoadingKeys = isDemoMode ? false : (keysQuery.isLoading || !orgId);
  const hasApiKeys = apiKeys.length > 0;

  // Format numbers with commas
  const formatNumber = (num: number) => num?.toLocaleString() ?? '0';

  // Compute prior period values (60d total - 30d total = prior 30d)
  const priorStats = isDemoMode ? DEMO_STATS_60D : priorStatsQuery.data;
  const priorApiCalls = (priorStats?.total_api_calls || 0) - (stats?.total_api_calls || 0);
  const priorDocsSigned = (priorStats?.total_documents_signed || 0) - (stats?.total_documents_signed || 0);
  const priorVerifications = (priorStats?.total_verifications || 0) - (stats?.total_verifications || 0);
  const sparklineData = isDemoMode
    ? DEMO_SPARKLINE.map(d => d.count)
    : (sparklineQuery.data?.map((d: TimeSeriesData) => d.count) || []);
  const docsSparklineData = isDemoMode
    ? DEMO_DOCS_SPARKLINE.map(d => d.count)
    : (docsSparklineQuery.data?.map((d: TimeSeriesData) => d.count) || []);
  // Activity feed with real-time polling (30s interval)
  const activityQuery = useQuery({
    queryKey: ['activity-feed', orgId],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      const response = await apiClient.getDiscoveryEvents(accessToken, { days: 7, limit: 8 });
      return (response?.data || []).map((item) => ({
        type: item.is_external_domain ? 'verify' : 'sign',
        title: `${item.is_external_domain ? 'Verification from' : 'Content signed:'} ${item.page_domain || item.page_title || 'unknown'}`,
        time: formatRelativeTime(item.discovered_at),
      }));
    },
    enabled: Boolean(accessToken && !isDemoMode),
    refetchInterval: 30_000,
    refetchOnWindowFocus: true,
    staleTime: 15_000,
    retry: false,
  });
  const activityFeed = isDemoMode ? DEMO_ACTIVITY : (activityQuery.data || []);

  // Animated count-up values for metric cards
  const animApiCalls = useCountUp(stats?.total_api_calls || 0);
  const animDocsSigned = useCountUp(stats?.total_documents_signed || 0);
  const animVerifications = useCountUp(stats?.total_verifications || 0);

  const userName = isDemoMode ? 'Demo Publisher' : (session?.user?.name || session?.user?.email?.split('@')[0] || 'there');
  const workflowCategory = setupStatus?.workflow_category || (setupStatus?.dashboard_layout === 'publisher' ? 'media_publishing' : 'enterprise');
  const heroContent = workflowCategory === 'media_publishing'
    ? {
        title: 'Your publisher provenance workspace',
        description: 'Protect your content, connect your CMS, and get signed publishing live quickly.',
        primaryHref: '/integrations',
        primaryLabel: 'Open Integrations',
        secondaryHref: 'https://api.encypher.com/docs',
        secondaryLabel: 'Publisher Docs',
      }
    : workflowCategory === 'ai_provenance_governance'
      ? {
          title: 'Your AI provenance and governance workspace',
          description: 'Stand up attested workflows, governance controls, and verification-ready records for high-stakes AI use cases.',
          primaryHref: '/api-keys',
          primaryLabel: 'Generate API Key',
          secondaryHref: 'https://api.encypher.com/docs',
          secondaryLabel: 'Governance Docs',
        }
      : {
          title: 'Your enterprise provenance workspace',
          description: 'Launch your implementation, validate your first workflow, and scale trusted content operations with confidence.',
          primaryHref: '/api-keys',
          primaryLabel: 'New API Key',
          secondaryHref: 'https://api.encypher.com/docs',
          secondaryLabel: 'API Docs',
        };
  const formatDateUtc = (value: string, options: Intl.DateTimeFormatOptions) =>
    new Date(value).toLocaleDateString('en-US', { ...options, timeZone: 'UTC' });

  return (
    <DashboardLayout>
      {/* Demo Mode Banner */}
      {isDemoMode && (
        <div className="mb-4 flex items-center justify-between rounded-lg border border-amber-300 dark:border-amber-700 bg-amber-50 dark:bg-amber-900/20 px-4 py-2.5">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm font-medium text-amber-800 dark:text-amber-300">Demo Mode</span>
            <span className="text-xs text-amber-600 dark:text-amber-400">Sample data for demonstration purposes</span>
          </div>
          <button
            onClick={() => setDemoMode(false)}
            className="text-xs font-medium text-amber-700 dark:text-amber-300 hover:text-amber-900 dark:hover:text-amber-100 underline"
          >
            Exit Demo
          </button>
        </div>
      )}

      {/* Welcome Hero Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-delft-blue via-delft-blue to-blue-ncs p-8 mb-8">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-96 h-96 bg-white rounded-full blur-3xl transform translate-x-1/2 -translate-y-1/2" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-columbia-blue rounded-full blur-3xl transform -translate-x-1/2 translate-y-1/2" />
        </div>

        <div className="relative z-10">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-2 tracking-tight">
                {greeting}, {userName}
              </h1>
              <p className="text-columbia-blue text-lg font-medium">
                {heroContent.title}
              </p>
              <p className="text-columbia-blue/80 text-sm mt-2 max-w-2xl leading-relaxed">
                {heroContent.description}
              </p>
              <div className="flex items-center gap-2 mt-3">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-white/10 border border-white/20 rounded-full">
                  <svg className="w-3.5 h-3.5 text-columbia-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  <span className="text-xs font-medium text-columbia-blue">C2PA Compliant</span>
                </div>
                <span className="text-xs text-white/50">Coalition for Content Provenance and Authenticity</span>
              </div>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link href={heroContent.primaryHref}>
                <button className="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-delft-blue font-medium rounded-lg hover:bg-columbia-blue transition-colors">
                  <IconPlus />
                  {heroContent.primaryLabel}
                </button>
              </Link>
              <a href={heroContent.secondaryHref} target="_blank" rel="noopener noreferrer">
                <button className="inline-flex items-center gap-2 px-5 py-2.5 bg-white/10 text-white font-medium rounded-lg hover:bg-white/20 transition-colors border border-white/20">
                  <IconBook />
                  {heroContent.secondaryLabel}
                </button>
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Hide onboarding in demo mode (post-onboarding state) */}
      {!isDemoMode && (
        <OnboardingLaunchpad
          className="mb-8"
          hasApiKeys={hasApiKeys}
          documentsSigned={stats?.total_documents_signed || 0}
          verifications={stats?.total_verifications || 0}
        />
      )}

      {/* Recommended Next Action -- contextual single-line banner */}
      {!isLoadingStats && (() => {
        const vCount = stats?.total_verifications || 0;
        const docCount = stats?.total_documents_signed || 0;
        let actionText = '';
        let actionHref = '';
        let actionCta = '';

        if (docCount === 0) {
          actionText = 'Sign your first document to start building your provenance record.';
          actionHref = '/playground';
          actionCta = 'Try Signing';
        } else if (vCount === 0) {
          actionText = 'Share your verification page to start building toward formal notice eligibility.';
          actionHref = '/docs';
          actionCta = 'Learn How';
        } else if (vCount < VERIFICATION_THRESHOLD) {
          const pct = Math.round((vCount / VERIFICATION_THRESHOLD) * 100);
          actionText = `You're ${pct}% toward formal notice eligibility. Share your verification page with partners to accelerate.`;
          actionHref = '/analytics';
          actionCta = 'View Progress';
        } else {
          actionText = 'You\'re eligible for formal notice. Start your first notice package.';
          actionHref = '/rights';
          actionCta = 'Start Notice';
        }

        return (
          <div className="mb-6 flex items-center gap-3 rounded-lg bg-gradient-to-r from-blue-ncs/5 to-transparent dark:from-blue-ncs/10 border border-blue-ncs/15 px-4 py-3">
            <div className="w-6 h-6 rounded-full bg-blue-ncs/10 flex items-center justify-center flex-shrink-0">
              <svg className="w-3.5 h-3.5 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </div>
            <p className="text-sm text-foreground flex-1">{actionText}</p>
            <Link href={actionHref} className="text-xs font-medium text-blue-ncs hover:underline whitespace-nowrap flex-shrink-0">
              {actionCta} &rarr;
            </Link>
          </div>
        );
      })()}

      {/* Stats Overview - Enhanced Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-8">
        {isLoadingStats ? (
          <>
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
          </>
        ) : (
          <>
            {/* API Calls Card */}
            <Link href="/analytics" className="block group animate-fade-in-up" style={{ animationDelay: '0ms' }}>
              <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-5 lg:p-6 hover:shadow-md hover:border-blue-ncs/30 transition-all duration-200 cursor-pointer group-hover:scale-[1.02]">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-1">API Calls</p>
                    <p className="text-2xl sm:text-3xl lg:text-4xl font-bold text-delft-blue dark:text-white animate-count-up">
                      {formatNumber(animApiCalls)}
                    </p>
                    <MiniSparkline data={sparklineData} />
                    <p className="text-xs mt-2 flex items-center gap-1.5">
                      <TrendBadge current={stats?.total_api_calls || 0} prior={Math.max(0, priorApiCalls)} />
                      <span className="text-muted-foreground">vs prior 30 days</span>
                    </p>
                  </div>
                  <div className="w-11 h-11 bg-gradient-to-br from-blue-ncs to-columbia-blue rounded-xl flex items-center justify-center text-white">
                    <IconChart />
                  </div>
                </div>
              </div>
            </Link>

            {/* Documents Signed Card */}
            {(stats?.total_documents_signed || 0) === 0 ? (
              <Link href="/playground" className="block animate-fade-in-up" style={{ animationDelay: '80ms' }}>
                <div className="bg-white dark:bg-slate-800 rounded-xl border-2 border-blue-ncs/30 p-5 lg:p-6 hover:shadow-md transition-shadow ring-2 ring-blue-ncs/20 animate-pulse-slow">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground mb-2">Documents Signed</p>
                      <p className="text-sm font-semibold text-delft-blue dark:text-white mb-1">
                        Sign your first document
                      </p>
                      <p className="text-xs text-muted-foreground mb-3">
                        Try signing content in the API playground
                      </p>
                      <span className="inline-flex items-center gap-1 text-xs font-medium text-blue-ncs">
                        Try Signing
                        <IconArrowRight />
                      </span>
                    </div>
                    <div className="w-11 h-11 bg-gradient-to-br from-delft-blue to-blue-ncs rounded-xl flex items-center justify-center text-white">
                      <IconSign />
                    </div>
                  </div>
                </div>
              </Link>
            ) : (
              <Link href="/analytics" className="block group animate-fade-in-up" style={{ animationDelay: '80ms' }}>
                <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-5 lg:p-6 hover:shadow-md hover:border-blue-ncs/30 transition-all duration-200 cursor-pointer group-hover:scale-[1.02]">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground mb-1">Documents Signed</p>
                      <p className="text-2xl sm:text-3xl lg:text-4xl font-bold text-delft-blue dark:text-white animate-count-up">
                        {formatNumber(animDocsSigned)}
                      </p>
                      <MiniSparkline data={docsSparklineData} color="#1b2f50" />
                      <p className="text-xs mt-2 flex items-center gap-1.5">
                        <TrendBadge current={stats?.total_documents_signed || 0} prior={Math.max(0, priorDocsSigned)} />
                        <span className="text-muted-foreground">vs prior 30 days</span>
                      </p>
                    </div>
                    <div className="w-11 h-11 bg-gradient-to-br from-delft-blue to-blue-ncs rounded-xl flex items-center justify-center text-white">
                      <IconSignedDoc />
                    </div>
                  </div>
                </div>
              </Link>
            )}

            {/* Verifications Card -- 4-state progression */}
            {(() => {
              const vCount = stats?.total_verifications || 0;
              const pct = Math.round((vCount / VERIFICATION_THRESHOLD) * 100);

              // Zero state -- CTA to try verification
              if (vCount === 0) return (
                <Link href="/playground" className="block animate-fade-in-up" style={{ animationDelay: '160ms' }}>
                  <div className="bg-white dark:bg-slate-800 rounded-xl border-2 border-blue-ncs/30 p-5 lg:p-6 hover:shadow-md transition-shadow ring-2 ring-blue-ncs/20 animate-pulse-slow">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground mb-2">Verifications</p>
                        <p className="text-sm font-semibold text-delft-blue dark:text-white mb-1">
                          Verify your first signed document
                        </p>
                        <p className="text-xs text-muted-foreground mb-3">
                          Confirm your content is authentically signed
                        </p>
                        <span className="inline-flex items-center gap-1 text-xs font-medium text-blue-ncs">
                          Try Verification
                          <IconArrowRight />
                        </span>
                      </div>
                      <div className="w-11 h-11 bg-gradient-to-br from-columbia-blue to-blue-ncs rounded-xl flex items-center justify-center text-white">
                        <IconVerify />
                      </div>
                    </div>
                  </div>
                </Link>
              );

              // Qualified state (500+) -- green checkmark
              if (vCount >= VERIFICATION_THRESHOLD) return (
                <Link href="/rights" className="block group animate-fade-in-up" style={{ animationDelay: '160ms' }}>
                  <div className="bg-white dark:bg-slate-800 rounded-xl border border-green-300 dark:border-green-700 p-5 lg:p-6 hover:shadow-md transition-all duration-200 cursor-pointer group-hover:scale-[1.02]">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground mb-1">Verifications</p>
                        <p className="text-2xl sm:text-3xl lg:text-4xl font-bold text-delft-blue dark:text-white animate-count-up">
                          {formatNumber(animVerifications)}
                        </p>
                        <p className="text-xs mt-2">
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium">
                            Formal Notice eligible
                          </span>
                        </p>
                        <span className="inline-flex items-center gap-1 text-xs font-medium text-green-600 dark:text-green-400 mt-1.5">
                          Start Formal Notice <IconArrowRight />
                        </span>
                      </div>
                      <div className="w-11 h-11 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center text-white">
                        <IconFormalNotice />
                      </div>
                    </div>
                  </div>
                </Link>
              );

              // Early (1-99) / Momentum (100-499) states -- progress ring
              const isMomentum = vCount >= 100;
              return (
                <Link href="/analytics" className="block group animate-fade-in-up" style={{ animationDelay: '160ms' }}>
                  <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-5 lg:p-6 hover:shadow-md hover:border-blue-ncs/30 transition-all duration-200 cursor-pointer group-hover:scale-[1.02]">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-muted-foreground mb-1">Verifications</p>
                        <div className="flex items-center gap-3">
                          <p className="text-2xl sm:text-3xl lg:text-4xl font-bold text-delft-blue dark:text-white animate-count-up">
                            {formatNumber(animVerifications)}
                          </p>
                          <ProgressRing
                            value={vCount}
                            max={VERIFICATION_THRESHOLD}
                            size={40}
                            strokeWidth={3.5}
                            color={isMomentum ? '#2a87c4' : '#00CED1'}
                          />
                        </div>
                        <p className="text-xs mt-2 flex items-center gap-1.5">
                          <span className={`font-medium ${isMomentum ? 'text-blue-ncs' : 'text-muted-foreground'}`}>
                            {pct}% toward formal notice
                          </span>
                        </p>
                        <p className="text-[11px] text-muted-foreground mt-0.5">
                          {isMomentum
                            ? `${formatNumber(VERIFICATION_THRESHOLD - vCount)} more to qualify`
                            : 'Share your verification page to grow'}
                        </p>
                      </div>
                      <div className="w-11 h-11 bg-gradient-to-br from-columbia-blue to-blue-ncs rounded-xl flex items-center justify-center text-white">
                        <IconVerify />
                      </div>
                    </div>
                  </div>
                </Link>
              );
            })()}

            {/* Success Rate Card */}
            <Link href="/analytics" className="block group animate-fade-in-up" style={{ animationDelay: '240ms' }}>
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-5 lg:p-6 hover:shadow-md hover:border-blue-ncs/30 transition-all duration-200 cursor-pointer group-hover:scale-[1.02]">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Success Rate</p>
                  <p className="text-2xl sm:text-3xl lg:text-4xl font-bold text-delft-blue dark:text-white">
                    {stats?.success_rate?.toFixed(1) || '100'}%
                  </p>
                  <p className="text-xs mt-2 flex items-center gap-1.5">
                    {(() => {
                      const rate = stats?.success_rate ?? 100;
                      const priorRate = priorStats ? (priorStats.success_rate ?? 100) : rate;
                      const rateDelta = rate - priorRate;
                      if (rate >= 95) return (
                        <>
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium">
                            Excellent
                          </span>
                          {Math.abs(rateDelta) <= 2
                            ? <span className="text-muted-foreground">Consistent</span>
                            : rateDelta > 0
                              ? <span className="text-green-600 dark:text-green-400">Up from {priorRate.toFixed(1)}%</span>
                              : <span className="text-amber-600 dark:text-amber-400">from {priorRate.toFixed(1)}%</span>
                          }
                        </>
                      );
                      if (rate >= 80) return (
                        <>
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded-full bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 text-xs font-medium">
                            {rateDelta >= 0 ? 'Good' : 'Trending down'}
                          </span>
                          <span className="text-muted-foreground">{rateDelta > 0 ? 'Improving' : rateDelta === 0 ? 'Stable' : 'From ' + priorRate.toFixed(1) + '%'}</span>
                        </>
                      );
                      if (rate >= 60) return (
                        <>
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded-full bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 text-xs font-medium">
                            Needs attention
                          </span>
                          <span className="text-muted-foreground">Investigate errors</span>
                        </>
                      );
                      return (
                        <>
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs font-medium">
                            Critical
                          </span>
                          <span className="text-muted-foreground">Investigate errors</span>
                        </>
                      );
                    })()}
                  </p>
                </div>
                <div className="w-11 h-11 bg-gradient-to-br from-[#00CED1] to-[#2A87C4] rounded-xl flex items-center justify-center text-white">
                  <IconProvenance />
                </div>
              </div>
            </div>
            </Link>
          </>
        )}
      </div>

      {/* Main Content -- Full-width sections to avoid lopsided layout */}
      <div className="space-y-6 lg:space-y-8">
        {/* API Keys Section - Full width */}
        <div>
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-border overflow-hidden">
            <div className="p-6 border-b border-border">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold tracking-tight text-delft-blue dark:text-white uppercase">API Keys</h2>
                  <p className="text-[13px] text-muted-foreground mt-0.5">Manage your authentication credentials</p>
                </div>
                <Link href="/api-keys">
                  <button className="inline-flex items-center gap-2 px-4 py-2 bg-blue-ncs text-white font-medium rounded-lg hover:bg-blue-ncs/90 transition-colors text-sm">
                    <IconPlus />
                    Manage Keys
                  </button>
                </Link>
              </div>
            </div>

            <div className="p-6">
              {isLoadingKeys ? (
                <ApiKeysSkeleton />
              ) : apiKeys.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-20 h-20 bg-gradient-to-br from-columbia-blue/20 to-blue-ncs/20 rounded-2xl flex items-center justify-center mx-auto mb-5">
                    <div className="w-12 h-12 bg-gradient-to-br from-columbia-blue to-blue-ncs rounded-xl flex items-center justify-center text-white">
                      <IconApiKey />
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold text-delft-blue dark:text-white mb-2">No API Keys Yet</h3>
                  <p className="text-muted-foreground mb-6 max-w-sm mx-auto">
                    Generate your first API key to start authenticating your content with cryptographic proof.
                  </p>
                  <Link href="/api-keys">
                    <button className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-ncs to-delft-blue text-white font-medium rounded-lg hover:opacity-90 transition-opacity">
                      <IconPlus />
                      Generate Your First Key
                    </button>
                  </Link>
                </div>
              ) : (
                <div className="space-y-3">
                  {apiKeys.slice(0, 3).map((key) => (
                    <Link
                      key={key.id}
                      href="/api-keys"
                      className="group flex items-center gap-4 p-4 rounded-xl border border-border hover:border-blue-ncs/30 hover:bg-gradient-to-r hover:from-columbia-blue/5 hover:to-transparent transition-all cursor-pointer"
                    >
                      <div className="w-10 h-10 bg-gradient-to-br from-columbia-blue to-blue-ncs rounded-lg flex items-center justify-center text-white flex-shrink-0">
                        <IconApiKey />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-delft-blue dark:text-white truncate">{key.name}</h3>
                          <span className={`px-2 py-0.5 text-xs font-medium rounded-full flex-shrink-0 ${
                            key.is_revoked
                              ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                              : 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                          }`}>
                            {key.is_revoked ? 'Revoked' : 'Active'}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          Created {formatDateUtc(key.created_at, { month: 'short', day: 'numeric', year: 'numeric' })}
                          {key.last_used_at && ` • Last used ${formatDateUtc(key.last_used_at, { month: 'short', day: 'numeric' })}`}
                        </p>
                      </div>
                      <div className="text-muted-foreground group-hover:text-blue-ncs transition-colors">
                        <IconArrowRight />
                      </div>
                    </Link>
                  ))}
                  {apiKeys.length > 3 && (
                    <Link href="/api-keys" className="block">
                      <button className="w-full py-3 text-sm font-medium text-blue-ncs hover:text-delft-blue dark:text-white transition-colors">
                        View all {apiKeys.length} keys →
                      </button>
                    </Link>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Recent Activity Feed -- shows when activity data exists (demo mode or real) */}
        {activityFeed.length > 0 && (
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-border overflow-hidden">
            <div className="p-5 border-b border-border">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <h2 className="text-sm font-semibold tracking-tight text-delft-blue dark:text-white uppercase">Recent Activity</h2>
                  <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-green-100 dark:bg-green-900/30 text-[10px] font-medium text-green-700 dark:text-green-400">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                    Live
                  </span>
                </div>
                <Link href="/settings?tab=security" className="text-xs font-medium text-blue-ncs hover:underline">
                  View all activity &rarr;
                </Link>
              </div>
            </div>
            <div className="divide-y divide-border">
              {activityFeed.slice(0, 6).map((event, i) => {
                const borderColor = event.type === 'sign' ? 'border-l-blue-ncs' : event.type === 'verify' ? 'border-l-green-500' : event.type === 'detection' ? 'border-l-amber-500' : 'border-l-slate-400';
                const dotColor = event.type === 'sign' ? 'bg-blue-ncs' : event.type === 'verify' ? 'bg-green-500' : event.type === 'detection' ? 'bg-amber-500' : 'bg-slate-400';
                return (
                  <div key={i} className={`flex items-center gap-3 px-5 py-3 border-l-2 ${borderColor} animate-slide-in-right`} style={{ animationDelay: `${i * 60}ms` }}>
                    <div className={`w-2 h-2 rounded-full flex-shrink-0 ${dotColor}`} />
                    <p className="text-sm text-foreground flex-1 truncate">{event.title}</p>
                    <span className="text-xs text-muted-foreground whitespace-nowrap flex-shrink-0">{event.time}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Onboarding Checklist - Full width (hidden in demo mode) */}
        {!isDemoMode && <OnboardingChecklist />}

        {/* Two-column grid: Content Protection Funnel + Quick Links */}
        <div className="grid lg:grid-cols-2 gap-6 lg:gap-8">
          <ContentProtectionFunnel stats={stats} isLoading={isLoadingStats} />

          {/* Quick Links */}
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-5">
            <h3 className="text-sm font-semibold tracking-tight text-delft-blue dark:text-white uppercase mb-4">Quick Links</h3>
            <div className="space-y-2">
              <Link href="/integrations" className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted transition-colors group">
                <div className="w-9 h-9 bg-[#00CED1]/10 rounded-lg flex items-center justify-center text-[#00CED1]">
                  <IconLink />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-delft-blue dark:text-white text-sm">Integrations</p>
                  <p className="text-xs text-muted-foreground">Connect your CMS</p>
                </div>
                <IconArrowRight />
              </Link>

              <Link href="/analytics" className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted transition-colors group">
                <div className="w-9 h-9 bg-blue-ncs/10 rounded-lg flex items-center justify-center text-blue-ncs">
                  <IconChart />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-delft-blue dark:text-white text-sm">Content Performance</p>
                  <p className="text-xs text-muted-foreground">Track your protection timeline</p>
                </div>
                <IconArrowRight />
              </Link>

              <Link href="/docs" className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted transition-colors group">
                <div className="w-9 h-9 bg-delft-blue/10 dark:bg-slate-600 rounded-lg flex items-center justify-center text-delft-blue dark:text-white">
                  <IconBook />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-delft-blue dark:text-white text-sm">Documentation</p>
                  <p className="text-xs text-muted-foreground">Guides and SDK references</p>
                </div>
                <IconArrowRight />
              </Link>
            </div>
          </div>

        </div>
      </div>
    </DashboardLayout>
  );
}
