'use client';

import {
  Badge,
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@encypher/design-system';
import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { EmptyState } from '../../components/ui/empty-state';
import apiClient from '../../lib/api';
import { downloadCsv } from '../../lib/exportCsv';
import { toast } from 'sonner';

// -- Skeletons --

function StatCardSkeleton() {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="h-4 w-24 bg-muted rounded animate-pulse mb-2" />
        <div className="h-8 w-20 bg-muted rounded animate-pulse mb-1" />
        <div className="h-3 w-32 bg-muted rounded animate-pulse" />
      </CardContent>
    </Card>
  );
}

function ChartSkeleton() {
  return (
    <div className="h-64 flex items-end justify-between space-x-2">
      {[1, 2, 3, 4, 5, 6, 7].map((i) => (
        <div key={i} className="flex-1 flex flex-col items-center">
          <div
            className="w-full bg-muted rounded-t animate-pulse"
            style={{ height: `${20 + (i * 8) % 60}%` }}
          />
          <div className="h-3 w-8 bg-muted rounded animate-pulse mt-2" />
        </div>
      ))}
    </div>
  );
}

function TableSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="h-10 bg-muted rounded animate-pulse" />
      ))}
    </div>
  );
}

// -- Lock icon for enterprise gating --

function LockIcon() {
  return (
    <svg className="w-4 h-4 text-muted-foreground inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
    </svg>
  );
}

// -- Constants --

const CRAWLER_NAME_TO_COMPANY: Record<string, string> = {
  gptbot: 'OpenAI',
  'chatgpt-user': 'OpenAI',
  'oai-searchbot': 'OpenAI',
  claudebot: 'Anthropic',
  'claude-web': 'Anthropic',
  'anthropic-ai': 'Anthropic',
  'google-extended': 'Google',
  googlebot: 'Google',
  perplexitybot: 'Perplexity AI',
  'meta-externalagent': 'Meta',
  'meta-externalfetcher': 'Meta',
  applebot: 'Apple',
  'applebot-extended': 'Apple',
  bytespider: 'ByteDance',
  ccbot: 'Common Crawl',
};

const CRAWLER_COLORS = ['#2A87C4', '#00A8B5', '#4A9E6B', '#8B6DBF', '#C46A2A', '#C4A62A'];

const COMPANY_COLORS: Record<string, string> = {
  OpenAI: '#10a37f',
  Anthropic: '#d97706',
  Google: '#4285f4',
  Meta: '#0866ff',
  'Perplexity AI': '#20b2aa',
  Bytedance: '#fe2c55',
  Apple: '#6b7280',
  Amazon: '#f59e0b',
  'Common Crawl': '#7c3aed',
  Microsoft: '#00adef',
};

// Bot purpose labels keyed by user_agent_category value
const CATEGORY_LABELS: Record<string, { label: string; desc: string; colorClass: string }> = {
  training: { label: 'Training Data', desc: 'Building AI datasets from your content', colorClass: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300' },
  rag: { label: 'RAG / Inference', desc: 'Retrieving context for AI-generated answers', colorClass: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' },
  rag_inference: { label: 'RAG / Inference', desc: 'Retrieving context for AI-generated answers', colorClass: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' },
  search_index: { label: 'Search Indexing', desc: 'Building search and answer indices', colorClass: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300' },
  search: { label: 'Search Indexing', desc: 'Building search and answer indices', colorClass: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300' },
  browser: { label: 'User Browser', desc: 'Standard user agent access', colorClass: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300' },
  unknown: { label: 'Unclassified', desc: 'Purpose not yet identified', colorClass: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' },
};

const SOURCE_LABELS: Record<string, string> = {
  rsl_olp_check: 'RSL Lookup',
  api_verification: 'Rights API',
  chrome_extension: 'Chrome Extension',
  http_header_lookup: 'HTTP Header',
  crawl_detected: 'Crawl Detected',
  cloudflare_logpush: 'Cloudflare Logpush',
};

function getComplianceBadgeClass(label?: string): string {
  switch (label) {
    case 'Excellent': return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400';
    case 'Good': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
    case 'Fair': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
    case 'Poor': return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400';
    case 'Non-compliant': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
    default: return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300';
  }
}

function formatNumber(num: number): string {
  return num?.toLocaleString() ?? '0';
}

function formatPercent(val: number | undefined): string {
  if (val === undefined || val === null) return '0%';
  return `${(val * 100).toFixed(1)}%`;
}

function formatShortDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function formatLastSeen(dateStr?: string | null): string {
  if (!dateStr) return '--';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// -- Main page --

export default function AICrawlersPage() {
  const [timeRange, setTimeRange] = useState<'7' | '30' | '90'>('30');
  const { data: session } = useSession();
  const router = useRouter();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const userTier = (session?.user as any)?.tier || 'free';
  const isEnterprise = userTier === 'enterprise';

  // Data fetching
  const crawlerQuery = useQuery({
    queryKey: ['crawler-analytics', timeRange],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getCrawlerAnalytics(accessToken, parseInt(timeRange));
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
  });

  const detectionQuery = useQuery({
    queryKey: ['detection-analytics', timeRange],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getDetectionAnalytics(accessToken, parseInt(timeRange));
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
  });

  const timeseriesQuery = useQuery({
    queryKey: ['crawler-timeseries', timeRange],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getCrawlerTimeseries(accessToken, parseInt(timeRange));
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
  });

  const crawlerData = crawlerQuery.data;
  const detectionData = detectionQuery.data;
  const timeseriesData = timeseriesQuery.data;
  const isLoading = crawlerQuery.isLoading || detectionQuery.isLoading;
  const isTimeseriesLoading = timeseriesQuery.isLoading;

  // Compute stat card values
  const totalCrawlEvents = detectionData?.total_events ?? 0;
  const uniqueCrawlers = crawlerData?.crawlers?.length ?? 0;
  const bypassCount = detectionData?.robots_txt_bypass_count ?? 0;

  const avgRslCheckRate = crawlerData?.crawlers?.length
    ? crawlerData.crawlers.reduce((sum, c) => sum + (c.rsl_check_rate ?? 0), 0) / crawlerData.crawlers.length
    : 0;

  const avgRightsAckRate = crawlerData?.crawlers?.length
    ? crawlerData.crawlers.reduce((sum, c) => sum + (c.rights_acknowledged_rate ?? 0), 0) / crawlerData.crawlers.length
    : 0;

  // Sort crawlers by total_events desc
  const sortedCrawlers = [...(crawlerData?.crawlers ?? [])].sort(
    (a, b) => b.total_events - a.total_events
  );

  // Timeseries chart data
  const crawlerNames = timeseriesData ? Object.keys(timeseriesData.by_crawler) : [];
  const displayDates = timeseriesData?.dates?.slice(-14) ?? [];
  const dateStartIdx = timeseriesData?.dates
    ? timeseriesData.dates.length - displayDates.length
    : 0;
  const maxDailyTotal = displayDates.length > 0 && timeseriesData
    ? Math.max(...timeseriesData.total_by_date.slice(dateStartIdx), 1)
    : 1;

  // Detection source data
  const bySrc = detectionData?.by_source ?? {};
  const maxSrcVal = Math.max(...Object.values(bySrc), 1);

  // Bot categories
  const byCat = detectionData?.by_category ?? {};

  // Group crawlers by company for company spotlight cards
  const companySummary = useMemo(() => {
    const map: Record<string, {
      total_events: number;
      crawlers: string[];
      bypass_count: number;
      compliance_labels: string[];
    }> = {};
    for (const c of sortedCrawlers) {
      const co = c.company
        || CRAWLER_NAME_TO_COMPANY[c.crawler_name?.toLowerCase() ?? '']
        || 'Unknown';
      if (!map[co]) map[co] = { total_events: 0, crawlers: [], bypass_count: 0, compliance_labels: [] };
      map[co].total_events += c.total_events;
      map[co].crawlers.push(c.crawler_name);
      map[co].bypass_count += c.bypass_count ?? 0;
      if (c.compliance_label) map[co].compliance_labels.push(c.compliance_label);
    }
    const COMPLIANCE_RANK: Record<string, number> = {
      'Non-compliant': 0, 'Poor': 1, 'Fair': 2, 'Good': 3, 'Excellent': 4,
    };
    return Object.entries(map)
      .map(([company, data]) => ({
        company,
        ...data,
        worst_label: data.compliance_labels.length
          ? data.compliance_labels.reduce((worst, l) =>
              (COMPLIANCE_RANK[l] ?? 5) < (COMPLIANCE_RANK[worst] ?? 5) ? l : worst
            )
          : null,
      }))
      .sort((a, b) => b.total_events - a.total_events);
  }, [sortedCrawlers]);

  // CSV export handler
  const handleExportCsv = () => {
    if (!sortedCrawlers.length) return;
    const rows = sortedCrawlers.map((c) => ({
      crawler_name: c.crawler_name,
      company: c.company ?? '',
      total_events: c.total_events,
      rsl_check_rate: c.rsl_check_rate !== undefined ? (c.rsl_check_rate * 100).toFixed(1) + '%' : '',
      rights_acknowledged_rate: c.rights_acknowledged_rate !== undefined ? (c.rights_acknowledged_rate * 100).toFixed(1) + '%' : '',
      compliance_label: c.compliance_label ?? '',
      last_seen: c.last_seen ?? '',
    }));
    downloadCsv(rows, {
      filename: `encypher-ai-crawlers-${new Date().toISOString().split('T')[0]}`,
      headers: ['crawler_name', 'company', 'total_events', 'rsl_check_rate', 'rights_acknowledged_rate', 'compliance_label', 'last_seen'],
    });
    toast.success('Crawler data exported');
  };

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-delft-blue dark:text-white">AI Crawler Analytics</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Which AI companies are crawling your content, how often, and whether they are respecting your rights -- plus cryptographic proof of where your content appears after scraping.
        </p>
      </div>

      {/* Capability callout */}
      <div className="rounded-xl border border-blue-200 bg-blue-50 dark:bg-blue-950/20 dark:border-blue-900/40 p-4 mb-6">
        <div className="flex items-start gap-3">
          <div className="mt-0.5 w-5 h-5 flex-shrink-0 text-blue-600 dark:text-blue-400">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-blue-800 dark:text-blue-300 mb-1">
              Two layers of crawler intelligence
            </p>
            <p className="text-sm text-blue-700 dark:text-blue-400">
              <strong>Layer 1 -- Crawl detection:</strong> RSL lookups, API verifications, and Cloudflare Logpush identify which AI companies
              are hitting your site, how often, and whether they checked your rights terms first.{' '}
              <strong>Layer 2 -- Content spread:</strong> Encypher&apos;s cryptographic watermarks track where your content surfaces after
              scraping -- AI products, aggregators, and syndication partners -- with court-admissible proof.
            </p>
          </div>
        </div>
      </div>

      {/* AI Company Spotlight */}
      {(isLoading || companySummary.length > 0) && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
              AI Company Breakdown
            </h2>
            <span className="text-xs text-muted-foreground">Last {timeRange} days</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {isLoading
              ? [1, 2, 3, 4, 5, 6].map((i) => <StatCardSkeleton key={i} />)
              : companySummary.slice(0, 6).map(({ company, total_events, crawlers, bypass_count, worst_label }) => {
                  const accentColor = COMPANY_COLORS[company] ?? '#6b7280';
                  return (
                    <div
                      key={company}
                      className="bg-white dark:bg-slate-800 rounded-xl border border-border p-4 hover:shadow-md transition-shadow"
                      style={{ borderTopWidth: '3px', borderTopColor: accentColor }}
                    >
                      <div className="flex items-center gap-1.5 mb-2">
                        <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: accentColor }} />
                        <p className="text-xs font-semibold text-slate-700 dark:text-slate-200 truncate">{company}</p>
                      </div>
                      <p className="text-xl font-bold text-delft-blue dark:text-white mb-0.5">
                        {formatNumber(total_events)}
                      </p>
                      <p className="text-[10px] text-muted-foreground mb-2">
                        {crawlers.length === 1 ? '1 crawler' : `${crawlers.length} crawlers`}
                      </p>
                      {bypass_count > 0 && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-medium text-red-600 dark:text-red-400">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                          {bypass_count} bypass{bypass_count !== 1 ? 'es' : ''}
                        </span>
                      )}
                      {isEnterprise && worst_label ? (
                        <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded-full ${getComplianceBadgeClass(worst_label)}`}>
                          {worst_label}
                        </span>
                      ) : !isEnterprise && (
                        <span className="text-[10px] text-muted-foreground blur-[2px] select-none">Compliance</span>
                      )}
                    </div>
                  );
                })
            }
          </div>
        </div>
      )}

      {/* Time Range + Export */}
      <div className="flex items-center justify-between flex-wrap gap-2 mb-6">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-muted-foreground">Time range:</span>
          {(['7', '30', '90'] as const).map((range) => (
            <Button
              key={range}
              variant={timeRange === range ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setTimeRange(range)}
            >
              {range}d
            </Button>
          ))}
        </div>
        {isEnterprise && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleExportCsv}
            disabled={!sortedCrawlers.length}
          >
            <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export CSV
          </Button>
        )}
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        {isLoading ? (
          <>
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
          </>
        ) : (
          <>
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">Total Crawl Events</p>
                  <p className="text-2xl font-bold text-delft-blue dark:text-white">
                    {formatNumber(totalCrawlEvents)}
                  </p>
                </div>
                <div className="w-9 h-9 bg-gradient-to-br from-blue-ncs to-columbia-blue rounded-lg flex items-center justify-center text-white">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>
              <p className="text-[11px] text-muted-foreground mt-2">Last {timeRange} days</p>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">Unique Crawlers</p>
                  <p className="text-2xl font-bold text-delft-blue dark:text-white">
                    {formatNumber(uniqueCrawlers)}
                  </p>
                </div>
                <div className="w-9 h-9 bg-gradient-to-br from-delft-blue to-blue-ncs rounded-lg flex items-center justify-center text-white">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-[11px] text-muted-foreground mt-2">Last {timeRange} days</p>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">RSL Compliance Rate</p>
                  <p className="text-2xl font-bold text-delft-blue dark:text-white">
                    {formatPercent(avgRslCheckRate)}
                  </p>
                </div>
                <div className="w-9 h-9 bg-gradient-to-br from-[#00CED1] to-[#2A87C4] rounded-lg flex items-center justify-center text-white">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
              </div>
              <p className="text-[11px] text-muted-foreground mt-2">Last {timeRange} days</p>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">Rights Acknowledged</p>
                  <p className="text-2xl font-bold text-delft-blue dark:text-white">
                    {formatPercent(avgRightsAckRate)}
                  </p>
                </div>
                <div className="w-9 h-9 bg-gradient-to-br from-[#2A87C4] to-[#1B2F50] rounded-lg flex items-center justify-center text-white">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              <p className="text-[11px] text-muted-foreground mt-2">Last {timeRange} days</p>
            </div>

            <div className={`rounded-xl border p-4 hover:shadow-md transition-shadow ${bypassCount > 0 ? 'bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-900/40' : 'bg-white dark:bg-slate-800 border-border'}`}>
              <div className="flex items-start justify-between">
                <div>
                  <p className={`text-xs font-medium mb-1 ${bypassCount > 0 ? 'text-red-600 dark:text-red-400' : 'text-muted-foreground'}`}>
                    Bypass Attempts
                  </p>
                  <p className={`text-2xl font-bold ${bypassCount > 0 ? 'text-red-700 dark:text-red-300' : 'text-delft-blue dark:text-white'}`}>
                    {formatNumber(bypassCount)}
                  </p>
                </div>
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center text-white ${bypassCount > 0 ? 'bg-gradient-to-br from-red-500 to-red-700' : 'bg-gradient-to-br from-slate-400 to-slate-600'}`}>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
              </div>
              <p className="text-[11px] text-muted-foreground mt-2">
                {bypassCount > 0 ? 'Bots that skipped RSL check' : 'No bypass events detected'}
              </p>
            </div>
          </>
        )}
      </div>

      {/* Two-column: Crawler Activity + Compliance Summary */}
      <div className="grid lg:grid-cols-5 gap-6 mb-8">
        {/* Left 60%: Crawler Activity Over Time */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Crawler Activity Over Time</CardTitle>
            <CardDescription>Daily crawl events by crawler for the selected period</CardDescription>
          </CardHeader>
          <CardContent>
            {isTimeseriesLoading ? (
              <ChartSkeleton />
            ) : !displayDates.length ? (
              <div className="h-64 flex flex-col items-center justify-center gap-2 text-muted-foreground">
                <svg className="w-8 h-8 text-slate-300 dark:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span className="text-sm">No activity data for this period</span>
              </div>
            ) : (
              <div>
                <div className="h-64 flex">
                  {/* Y-axis labels */}
                  <div className="flex flex-col justify-between pr-3 text-[10px] text-muted-foreground" style={{ paddingBottom: '24px' }}>
                    <span>{formatNumber(maxDailyTotal)}</span>
                    <span>{formatNumber(Math.round(maxDailyTotal / 2))}</span>
                    <span>0</span>
                  </div>
                  {/* Stacked bars */}
                  <div className="flex-1 flex items-end gap-1 border-l border-b border-border pl-2 relative" style={{ paddingBottom: '24px' }}>
                    {displayDates.map((dateStr, idx) => {
                      const globalIdx = dateStartIdx + idx;
                      const dayTotal = timeseriesData!.total_by_date[globalIdx] || 0;
                      const pctTotal = dayTotal > 0 ? Math.max((dayTotal / maxDailyTotal) * 100, 3) : 0;
                      return (
                        <div key={idx} className="flex-1 relative group flex items-end justify-center" style={{ height: '100%' }}>
                          <div className="w-full flex flex-col-reverse rounded-t-sm overflow-hidden" style={{ height: `${pctTotal}%` }}>
                            {crawlerNames.map((name, ci) => {
                              const val = timeseriesData!.by_crawler[name]?.[globalIdx] || 0;
                              if (val === 0 && dayTotal === 0) return null;
                              const segPct = dayTotal > 0 ? (val / dayTotal) * 100 : 0;
                              return (
                                <div
                                  key={name}
                                  style={{
                                    height: `${segPct}%`,
                                    backgroundColor: CRAWLER_COLORS[ci % CRAWLER_COLORS.length],
                                    minHeight: val > 0 ? '2px' : '0px',
                                  }}
                                />
                              );
                            })}
                          </div>
                          <div className="absolute -top-1 left-1/2 -translate-x-1/2 bg-delft-blue text-white text-[10px] px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
                            {formatNumber(dayTotal)}
                          </div>
                          <div className="absolute -bottom-5 left-1/2 -translate-x-1/2 text-[10px] text-muted-foreground whitespace-nowrap">
                            {formatShortDate(dateStr)}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
                {/* Legend */}
                <div className="flex flex-wrap gap-3 mt-6">
                  {crawlerNames.map((name, ci) => (
                    <div key={name} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <div
                        className="w-3 h-3 rounded-sm"
                        style={{ backgroundColor: CRAWLER_COLORS[ci % CRAWLER_COLORS.length] }}
                      />
                      <span>{name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Right 40%: Compliance Summary */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Compliance Summary</CardTitle>
            <CardDescription>Crawler compliance at a glance</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <TableSkeleton />
            ) : sortedCrawlers.length === 0 ? (
              <div className="flex flex-col items-center justify-center gap-2 py-8 text-muted-foreground">
                <svg className="w-7 h-7 text-slate-300 dark:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <span className="text-sm">No crawlers detected yet</span>
              </div>
            ) : (
              <div className="space-y-3">
                {sortedCrawlers.map((crawler) => (
                  <div
                    key={crawler.crawler_name}
                    className="flex items-center justify-between py-2 border-b border-border last:border-0"
                  >
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-slate-800 dark:text-slate-100 truncate">
                        {crawler.crawler_name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatNumber(crawler.total_events)} events
                      </p>
                    </div>
                    {isEnterprise ? (
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${getComplianceBadgeClass(crawler.compliance_label)}`}>
                        {crawler.compliance_label ?? 'Unknown'}
                      </span>
                    ) : (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-400 blur-[2px] select-none">
                        Locked
                      </span>
                    )}
                  </div>
                ))}
                {!isEnterprise && (
                  <div className="text-center pt-2">
                    <a href="/billing" className="text-xs text-blue-ncs hover:underline inline-flex items-center gap-1">
                      <LockIcon />
                      Upgrade to Enterprise for compliance scores
                    </a>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Encypher Differentiator: Beyond Crawl Detection */}
      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        {/* Content Spread CTA */}
        <div className="rounded-xl border border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/20 dark:border-blue-900/40 p-5">
          <div className="flex items-start gap-3 mb-3">
            <div className="w-8 h-8 bg-blue-ncs/15 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg className="w-4 h-4 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-semibold text-blue-900 dark:text-blue-200 mb-1">
                Encypher goes where TollBit can&apos;t
              </p>
              <p className="text-xs text-blue-700 dark:text-blue-400 leading-relaxed">
                Cloudflare logs show who scraped your site. Encypher&apos;s cryptographic watermarks show{' '}
                <span className="font-semibold">where your content appeared after</span> -- AI answers, paywalled
                summaries, syndicated articles, and third-party aggregators -- with cryptographic proof admissible in
                licensing negotiations.
              </p>
            </div>
          </div>
          <a href="/analytics" className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-ncs hover:underline">
            View Content Spread Analytics
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </a>
        </div>

        {/* Scrape-to-Referral Ratio */}
        <div className="rounded-xl border border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/20 dark:to-orange-950/20 dark:border-amber-900/40 p-5">
          <div className="flex items-start gap-3 mb-3">
            <div className="w-8 h-8 bg-amber-500/15 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg className="w-4 h-4 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 11h.01M12 11h.01M15 11h.01M4 19h16a2 2 0 002-2V7a2 2 0 00-2-2H4a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-semibold text-amber-900 dark:text-amber-200 mb-1">
                Scrape-to-Referral Ratio
              </p>
              <p className="text-xs text-amber-700 dark:text-amber-400 leading-relaxed">
                Are AI companies scraping your content and sending traffic back? Connect your analytics to see the ratio
                of AI crawl events to human referrals from AI products -- the key metric for licensing negotiations.
                Industry benchmarks show ratios of 10,000:1 or worse.
              </p>
            </div>
          </div>
          <a href="/settings?tab=integrations" className="inline-flex items-center gap-1.5 text-xs font-medium text-amber-700 dark:text-amber-400 hover:underline">
            Connect Analytics Integration
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </a>
        </div>
      </div>

      {/* Full-width Crawler Detail Table */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Crawler Details</CardTitle>
          <CardDescription>Detailed breakdown of each detected AI crawler</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <TableSkeleton />
          ) : sortedCrawlers.length === 0 ? (
            <EmptyState
              icon={
                <svg className="w-8 h-8 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="12" r="3"/>
                  <path d="M12 1v2m0 18v2m8.66-17.66l-1.41 1.41M4.75 19.25l-1.41 1.41M23 12h-2M3 12H1m17.66 8.66l-1.41-1.41M4.75 4.75L3.34 3.34"/>
                </svg>
              }
              title="No AI crawler activity detected"
              description="Connect Cloudflare Logpush or wait for crawlers to access your content. Activity will appear here automatically."
              actionLabel="Set Up Integration"
              onAction={() => router.push('/integrations')}
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm min-w-[700px]">
                <thead>
                  <tr className="border-b border-border text-left">
                    <th className="pb-3 font-medium text-muted-foreground">Crawler</th>
                    <th className="pb-3 font-medium text-muted-foreground">Company</th>
                    <th className="pb-3 font-medium text-muted-foreground text-right">Total Events</th>
                    <th className="pb-3 font-medium text-muted-foreground text-right">
                      RSL Check Rate
                      {!isEnterprise && <span className="ml-1 inline-flex items-center"><LockIcon /></span>}
                    </th>
                    <th className="pb-3 font-medium text-muted-foreground text-right">Rights Acknowledged</th>
                    <th className="pb-3 font-medium text-muted-foreground text-right">Bypasses</th>
                    <th className="pb-3 font-medium text-muted-foreground">
                      Compliance
                      {!isEnterprise && <span className="ml-1 inline-flex items-center"><LockIcon /></span>}
                    </th>
                    <th className="pb-3 font-medium text-muted-foreground">Last Seen</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedCrawlers.map((crawler) => (
                    <tr key={crawler.crawler_name} className="border-b border-border/50 hover:bg-muted/30">
                      <td className="py-3 font-medium text-slate-800 dark:text-slate-100">
                        {crawler.crawler_name}
                      </td>
                      <td className="py-3 text-muted-foreground">{crawler.company ?? '--'}</td>
                      <td className="py-3 text-right">{formatNumber(crawler.total_events)}</td>
                      <td className="py-3 text-right">
                        {isEnterprise
                          ? formatPercent(crawler.rsl_check_rate)
                          : <span className="text-muted-foreground blur-[3px] select-none">---%</span>
                        }
                      </td>
                      <td className="py-3 text-right">{formatPercent(crawler.rights_acknowledged_rate)}</td>
                      <td className="py-3 text-right">
                        {(crawler.bypass_count ?? 0) > 0 ? (
                          <span className="text-red-600 dark:text-red-400 font-medium">
                            {formatNumber(crawler.bypass_count ?? 0)}
                          </span>
                        ) : (
                          <span className="text-muted-foreground">0</span>
                        )}
                      </td>
                      <td className="py-3">
                        {isEnterprise ? (
                          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${getComplianceBadgeClass(crawler.compliance_label)}`}>
                            {crawler.compliance_label ?? 'Unknown'}
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                            <LockIcon />
                            <Badge variant="outline" size="sm">Enterprise</Badge>
                          </span>
                        )}
                      </td>
                      <td className="py-3 text-muted-foreground text-xs">{formatLastSeen(crawler.last_seen)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Two-column: Detection Sources | Bot Categories */}
      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        {/* Detection Sources */}
        <Card>
          <CardHeader>
            <CardTitle>Detection Sources</CardTitle>
            <CardDescription>How crawlers were detected</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <ChartSkeleton />
            ) : Object.keys(bySrc).length === 0 ? (
              <div className="flex flex-col items-center justify-center gap-2 py-8 text-muted-foreground">
                <svg className="w-7 h-7 text-slate-300 dark:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" />
                </svg>
                <span className="text-sm">No detection source data yet</span>
              </div>
            ) : (
              <div className="space-y-3">
                {Object.entries(bySrc)
                  .sort(([, a], [, b]) => b - a)
                  .map(([key, val]) => {
                    const pct = (val / maxSrcVal) * 100;
                    return (
                      <div key={key}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-slate-700 dark:text-slate-200">
                            {SOURCE_LABELS[key] || key}
                          </span>
                          <span className="text-sm font-medium text-slate-800 dark:text-slate-100">
                            {formatNumber(val)}
                          </span>
                        </div>
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-blue-ncs to-columbia-blue rounded-full"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Bot Categories */}
        <Card>
          <CardHeader>
            <CardTitle>Bot Purpose Breakdown</CardTitle>
            <CardDescription>What are AI crawlers doing with your content?</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <TableSkeleton />
            ) : Object.keys(byCat).length === 0 ? (
              <div className="flex flex-col items-center justify-center gap-2 py-8 text-muted-foreground">
                <svg className="w-7 h-7 text-slate-300 dark:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
                <span className="text-sm">No category data yet</span>
              </div>
            ) : (
              <div className="space-y-3">
                {Object.entries(byCat)
                  .sort(([, a], [, b]) => b - a)
                  .map(([category, count]) => {
                    const meta = CATEGORY_LABELS[category] ?? {
                      label: category.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
                      desc: '',
                      colorClass: 'bg-slate-100 text-slate-700',
                    };
                    return (
                      <div key={category} className="flex items-start justify-between gap-3 py-2 border-b border-border last:border-0">
                        <div className="min-w-0">
                          <span className={`inline-block text-[10px] font-semibold px-1.5 py-0.5 rounded-full mb-1 ${meta.colorClass}`}>
                            {meta.label}
                          </span>
                          {meta.desc && (
                            <p className="text-[11px] text-muted-foreground">{meta.desc}</p>
                          )}
                        </div>
                        <p className="text-lg font-bold text-delft-blue dark:text-white flex-shrink-0">
                          {formatNumber(count)}
                        </p>
                      </div>
                    );
                  })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Info callout */}
      <Card className="mb-8">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 bg-blue-ncs/10 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg className="w-4 h-4 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              RSL compliance measures whether a system fetched your Rights Statement Listing before accessing content.
              Rights Acknowledged means they confirmed your terms. Both are admissible as constructive notice evidence
              in licensing negotiations.
            </p>
          </div>
        </CardContent>
      </Card>
    </DashboardLayout>
  );
}
