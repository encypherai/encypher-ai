'use client';

import React from 'react';
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
import { useState } from 'react';
import Link from 'next/link';
import { ActivityFeed } from '../../components/ActivityFeed';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import apiClient from '../../lib/api';
import { exportAnalyticsData, exportTimeSeriesData } from '../../lib/exportCsv';
import { toast } from 'sonner';

// -- Skeleton components --

function FunnelSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <div key={i} className="h-16 bg-muted rounded-xl animate-pulse" />
      ))}
    </div>
  );
}

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

// -- Helpers --

function formatNumber(num: number) {
  return num?.toLocaleString() ?? '0';
}

function formatCurrency(cents: number) {
  if (!cents) return '$0';
  return `$${(cents / 100).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function formatDateRange(start?: string, end?: string): string {
  if (!start || !end) return '';
  const startDate = new Date(start);
  const endDate = new Date(end);
  return `${startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${endDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
}

function formatShortDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// -- Funnel stage component --

interface ContentSpreadDomain {
  domain: string;
  detection_count: number;
  unique_documents: number;
  last_detected: string | null;
}

interface ContentSpreadResponse {
  total_external_detections: number;
  unique_external_domains: number;
  domains: ContentSpreadDomain[];
  documents: { document_id: string; detection_count: number; unique_domains: number; last_detected: string | null }[];
}

interface FunnelStageProps {
  step: number;
  label: string;
  value: string;
  sublabel?: string;
  status: 'active' | 'pending' | 'locked' | 'cta';
  ctaLabel?: string;
  ctaHref?: string;
  description?: string;
  isLast?: boolean;
  children?: React.ReactNode;
}

function FunnelStage({
  step,
  label,
  value,
  sublabel,
  status,
  ctaLabel,
  ctaHref,
  description,
  isLast,
  children,
}: FunnelStageProps) {
  const bgColor = {
    active: 'bg-white dark:bg-slate-800 border-blue-ncs/30',
    pending: 'bg-white dark:bg-slate-800 border-border',
    locked: 'bg-muted/30 dark:bg-slate-900/50 border-border opacity-60',
    cta: 'bg-gradient-to-r from-blue-ncs/5 to-columbia-blue/5 border-blue-ncs/40',
  }[status];

  const stepColor = {
    active: 'bg-gradient-to-br from-blue-ncs to-columbia-blue text-white',
    pending: 'bg-muted text-muted-foreground',
    locked: 'bg-muted/50 text-muted-foreground',
    cta: 'bg-gradient-to-br from-delft-blue to-blue-ncs text-white',
  }[status];

  return (
    <div className="relative">
      <div className={`rounded-xl border ${bgColor} p-4 transition-shadow hover:shadow-sm`}>
        <div className="flex items-center gap-4">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${stepColor}`}>
            {status === 'active' || status === 'cta' ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              step
            )}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-baseline gap-2 flex-wrap">
              <span className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">{label}</span>
            </div>
            <div className="flex items-baseline gap-2 mt-0.5 flex-wrap">
              <span className="text-lg font-bold text-delft-blue dark:text-white">{value}</span>
              {sublabel && <span className="text-xs text-muted-foreground">{sublabel}</span>}
            </div>
            {description && <p className="text-xs text-muted-foreground mt-0.5">{description}</p>}
          {children && <div className="mt-2">{children}</div>}
          </div>
          {ctaLabel && ctaHref && (
            <Link href={ctaHref} className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-ncs text-white text-xs font-semibold rounded-lg hover:bg-delft-blue transition-colors flex-shrink-0">
              {ctaLabel}
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          )}
        </div>
      </div>
      {!isLast && (
        <div className="flex justify-start pl-8 py-0.5">
          <div className="w-0.5 h-3 bg-border" />
        </div>
      )}
    </div>
  );
}

// -- Main page --

export default function ContentPerformancePage() {
  const [timeRange, setTimeRange] = useState<'7' | '30' | '90'>('30');
  const [apiHealthOpen, setApiHealthOpen] = useState(false);
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;

  const statsQuery = useQuery({
    queryKey: ['analytics-stats', timeRange],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getUsageStats(accessToken, parseInt(timeRange));
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
  });

  const timeSeriesQuery = useQuery({
    queryKey: ['analytics-timeseries', timeRange],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getTimeSeries(accessToken, 'api_call', parseInt(timeRange), 'day');
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
  });

  const coalitionQuery = useQuery({
    queryKey: ['coalition-earnings'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getCoalitionEarnings(accessToken);
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
    retry: false,
  });

  const contentSpreadQuery = useQuery({
    queryKey: ['content-spread', timeRange],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      const data = await apiClient.getContentSpread(accessToken, parseInt(timeRange));
      return data as ContentSpreadResponse;
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
    retry: false,
  });

  const stats = statsQuery.data;
  const timeSeries = timeSeriesQuery.data || [];
  const coalition = coalitionQuery.data;
  const isLoading = statsQuery.isLoading;
  const isTimeSeriesLoading = timeSeriesQuery.isLoading;

  const periodLabel = stats
    ? formatDateRange(stats.period_start, stats.period_end)
    : `Last ${timeRange} days`;

  const peakDay = timeSeries.reduce<null | { timestamp: string; count: number }>((max, day) => {
    if (!max || day.count > max.count) return day;
    return max;
  }, null);
  const averageDailyCalls = timeSeries.length && stats?.total_api_calls
    ? Math.round(stats.total_api_calls / timeSeries.length)
    : 0;
  const signShare = stats?.total_api_calls
    ? (stats.total_documents_signed / stats.total_api_calls) * 100
    : 0;
  const verifyShare = stats?.total_api_calls
    ? (stats.total_verifications / stats.total_api_calls) * 100
    : 0;
  const successRate = stats?.success_rate ?? 0;
  const errorRate = Math.max(0, 100 - successRate);
  const avgResponseTime = stats?.avg_response_time_ms ?? 0;
  const responseStatus = avgResponseTime
    ? avgResponseTime <= 350
      ? { label: 'Healthy', variant: 'success' as const }
      : avgResponseTime <= 650
        ? { label: 'Monitor', variant: 'warning' as const }
        : { label: 'At Risk', variant: 'destructive' as const }
    : { label: '--', variant: 'secondary' as const };

  const maxValue = Math.max(...timeSeries.map(d => d.count), 1);

  // Funnel stage derivations
  const docsSigned = stats?.total_documents_signed || 0;
  const totalVerifications = stats?.total_verifications || 0;
  const PRELIMINARY_THRESHOLD = 100;
  const NOTICE_THRESHOLD = 500;
  const preliminaryReady = totalVerifications >= PRELIMINARY_THRESHOLD && totalVerifications < NOTICE_THRESHOLD;
  const noticeReady = totalVerifications >= NOTICE_THRESHOLD;
  const coalitionActive = coalition && coalition.member && !coalition.opted_out;
  const totalEarnings = coalition?.total_earnings || 0;
  const pendingEarnings = coalition?.pending_earnings || 0;

  const contentSpread = contentSpreadQuery.data;
  const contentSpreadLoading = contentSpreadQuery.isLoading;
  const contentSpreadAccessDenied = (contentSpreadQuery.error as any)?.status === 403;
  const totalDetections = contentSpread?.total_external_detections || 0;
  const uniqueDomains = contentSpread?.unique_external_domains || 0;

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-delft-blue dark:text-white">Content Performance</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Track how your signed content is spreading and earning -- your path from signing to licensing revenue.
        </p>
        <p className="text-xs text-muted-foreground mt-2">Reporting window: {periodLabel}</p>
      </div>

      {/* Time Range Selector + Export */}
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
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              if (stats) {
                exportAnalyticsData(stats, timeSeries);
                toast.success('Analytics data exported');
              }
            }}
            disabled={!stats}
          >
            <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export
          </Button>
        </div>
      </div>

      {/* Value Accumulation Timeline -- primary view */}
      <div className="grid lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <div className="mb-4">
            <h2 className="text-base font-semibold text-delft-blue dark:text-white">Value Accumulation Timeline</h2>
            <p className="text-xs text-muted-foreground mt-0.5">Each stage represents progress toward licensing revenue. Activity here proves your content is working.</p>
          </div>
          {isLoading ? (
            <FunnelSkeleton />
          ) : (
            <div>
              <FunnelStage
                step={1}
                label="Signed"
                value={`${formatNumber(docsSigned)} articles`}
                sublabel="your protected corpus"
                description="Content you can enforce on -- every signed article is evidence in a licensing dispute."
                status="active"
              />
              <FunnelStage
                step={2}
                label="Verified"
                value={`${formatNumber(totalVerifications)} provenance checks`}
                sublabel={`this ${timeRange === '7' ? 'week' : timeRange === '30' ? 'month' : 'quarter'}`}
                description="External entities verifying your content's authenticity and rights status. Each check is logged as enforcement evidence."
                status={totalVerifications > 0 ? 'active' : 'pending'}
              />
              <FunnelStage
                step={3}
                label="Spread"
                value={
                  contentSpreadLoading
                    ? 'Loading...'
                    : contentSpreadAccessDenied
                    ? 'Upgrade to view'
                    : totalDetections > 0
                    ? `${formatNumber(totalDetections)} detection${totalDetections !== 1 ? 's' : ''} across ${formatNumber(uniqueDomains)} domain${uniqueDomains !== 1 ? 's' : ''}`
                    : 'No external detections yet'
                }
                sublabel="external domain detections"
                description={
                  contentSpreadAccessDenied
                    ? 'Content spread analytics is available on the Enterprise plan or with the Attribution Analytics add-on.'
                    : totalDetections > 0
                    ? `Your signed content has been detected on ${uniqueDomains} external domain${uniqueDomains !== 1 ? 's' : ''} in the last ${timeRange} days.`
                    : 'Where your signed content appears outside your domain -- detections via the Encypher network. As your content spreads, detections appear here.'
                }
                status={totalDetections > 0 ? 'active' : 'pending'}
                ctaLabel={contentSpreadAccessDenied ? 'Upgrade Plan' : undefined}
                ctaHref={contentSpreadAccessDenied ? '/settings/billing' : undefined}
              >
                {!contentSpreadLoading && !contentSpreadAccessDenied && contentSpread && contentSpread.domains.length > 0 && (
                  <div className="mt-1 flex flex-wrap gap-1">
                    {contentSpread.domains.slice(0, 5).map((d) => (
                      <span key={d.domain} className="text-xs bg-blue-ncs/10 text-blue-ncs border border-blue-ncs/20 rounded px-1.5 py-0.5">
                        {d.domain}
                      </span>
                    ))}
                    {contentSpread.domains.length > 5 && (
                      <span className="text-xs text-muted-foreground px-1">
                        +{contentSpread.domains.length - 5} more
                      </span>
                    )}
                  </div>
                )}
              </FunnelStage>
              <FunnelStage
                step={4}
                label="Enforcement Readiness"
                value={
                  noticeReady
                    ? `${formatNumber(totalVerifications)} documented encounters`
                    : preliminaryReady
                    ? `${formatNumber(totalVerifications)} documented encounters`
                    : `${formatNumber(totalVerifications)} / ${formatNumber(NOTICE_THRESHOLD)} recommended`
                }
                sublabel={
                  noticeReady
                    ? 'Maximum legal leverage -- formal notice recommended'
                    : preliminaryReady
                    ? `${formatNumber(NOTICE_THRESHOLD - totalVerifications)} more encounters for maximum leverage`
                    : `${formatNumber(PRELIMINARY_THRESHOLD - totalVerifications)} more to unlock preliminary notice`
                }
                description={
                  noticeReady
                    ? `${formatNumber(totalVerifications)} documented encounters. Formal notices backed by 500+ verified encounters carry substantially stronger standing in willful infringement proceedings -- courts recognize the pattern of documented awareness.`
                    : preliminaryReady
                    ? `${formatNumber(totalVerifications)} documented encounters qualifies you to send a Preliminary Awareness Notice. This puts AI companies on formal documented notice without yet triggering willful infringement proceedings. Reach 500 encounters for maximum legal leverage and the full formal notice.`
                    : `Each verification is a documented moment of AI company awareness they must account for in court. Preliminary awareness notice available at 100 encounters | Full formal notice recommended at 500 for maximum willful infringement standing.`
                }
                status={noticeReady || preliminaryReady ? 'cta' : 'pending'}
                ctaLabel={noticeReady ? 'Send Formal Notice' : preliminaryReady ? 'Send Awareness Notice' : undefined}
                ctaHref={noticeReady || preliminaryReady ? '/rights' : undefined}
              />
              <FunnelStage
                step={5}
                label="Licensing"
                value={coalitionActive ? 'Coalition negotiation active' : 'Not yet active'}
                sublabel={coalitionActive ? 'Encypher negotiating on your behalf' : 'Triggered after Formal Notice'}
                description={coalitionActive
                  ? 'Encypher is actively negotiating licensing terms with AI companies on behalf of coalition members.'
                  : 'Once Formal Notice is served, Encypher opens coalition licensing negotiation with AI companies.'}
                status={coalitionActive ? 'active' : 'locked'}
                ctaLabel={coalitionActive ? 'View Status' : undefined}
                ctaHref={coalitionActive ? '/rights' : undefined}
              />
              <FunnelStage
                step={6}
                label="Earnings"
                value={totalEarnings > 0 ? formatCurrency(totalEarnings) : '$0 earned'}
                sublabel={pendingEarnings > 0 ? `${formatCurrency(pendingEarnings)} pending` : 'Coalition revenue distributes as negotiations close'}
                description={totalEarnings === 0 && pendingEarnings === 0
                  ? 'Coalition licensing revenue materializes as Encypher closes deals with AI companies. Verifications above are building your case now.'
                  : `Total coalition licensing revenue distributed to your account.`}
                status={totalEarnings > 0 ? 'active' : 'locked'}
                isLast
              />
            </div>
          )}
        </div>

        {/* Right column: summary cards */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">This Period</CardTitle>
              <CardDescription className="text-xs">{periodLabel}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Articles signed</span>
                <span className="font-semibold text-sm text-delft-blue dark:text-white">{formatNumber(docsSigned)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Provenance checks</span>
                <span className="font-semibold text-sm text-delft-blue dark:text-white">{formatNumber(totalVerifications)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Evidence strength</span>
                <Badge variant={noticeReady ? 'success' : preliminaryReady ? 'warning' : 'secondary'} size="sm">
                  {noticeReady ? 'Full notice ready' : preliminaryReady ? 'Preliminary ready' : `${Math.min(100, Math.round((totalVerifications / NOTICE_THRESHOLD) * 100))}%`}
                </Badge>
              </div>
              {coalition && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Coalition status</span>
                  <Badge variant={coalition.member ? 'success' : 'secondary'} size="sm">
                    {coalition.member ? 'Member' : 'Not joined'}
                  </Badge>
                </div>
              )}
              <div className="pt-2 border-t border-border">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-muted-foreground">Lifetime earnings</span>
                  <span className="font-bold text-sm text-delft-blue dark:text-white">
                    {formatCurrency(totalEarnings)}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Evidence Strength</CardTitle>
              <CardDescription className="text-xs">Documented encounters toward maximum enforcement leverage</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-2 flex items-baseline justify-between">
                <span className="text-2xl font-bold text-delft-blue dark:text-white">{formatNumber(totalVerifications)}</span>
                <span className="text-xs text-muted-foreground">/ {formatNumber(NOTICE_THRESHOLD)} for maximum leverage</span>
              </div>
              {/* Dual-threshold progress bar */}
              <div className="relative h-2.5 bg-muted rounded-full overflow-hidden mb-1">
                <div
                  className={`h-full rounded-full transition-all ${noticeReady ? 'bg-gradient-to-r from-emerald-500 to-emerald-400' : preliminaryReady ? 'bg-gradient-to-r from-amber-400 to-amber-300' : 'bg-gradient-to-r from-blue-ncs to-columbia-blue'}`}
                  style={{ width: `${Math.min(100, (totalVerifications / NOTICE_THRESHOLD) * 100)}%` }}
                />
                {/* Preliminary threshold marker at 20% (100/500) */}
                <div className="absolute top-0 bottom-0 w-px bg-white/60" style={{ left: '20%' }} />
              </div>
              <div className="flex justify-between text-xs text-muted-foreground mb-3">
                <span>0</span>
                <span className={preliminaryReady || noticeReady ? 'text-amber-500 font-medium' : ''}>100 preliminary</span>
                <span className={noticeReady ? 'text-emerald-500 font-medium' : ''}>500 full notice</span>
              </div>
              <p className="text-xs text-muted-foreground">
                {noticeReady
                  ? `${formatNumber(totalVerifications)} documented encounters — formal notices backed by 500+ verified encounters have substantially stronger standing in willful infringement proceedings.`
                  : preliminaryReady
                  ? `${formatNumber(totalVerifications)} encounters qualifies for a Preliminary Awareness Notice. This creates a documented moment of awareness without yet triggering formal willful proceedings. ${formatNumber(NOTICE_THRESHOLD - totalVerifications)} more encounters recommended for maximum legal leverage.`
                  : `${formatNumber(Math.max(0, PRELIMINARY_THRESHOLD - totalVerifications))} more encounters to unlock preliminary notice. ${formatNumber(Math.max(0, NOTICE_THRESHOLD - totalVerifications))} recommended for maximum legal leverage.`}
              </p>
              {(noticeReady || preliminaryReady) && (
                <Link href="/rights" className={`mt-3 w-full py-2 text-white text-xs font-semibold rounded-lg transition-colors flex items-center justify-center ${noticeReady ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-amber-500 hover:bg-amber-600'}`}>
                  {noticeReady ? 'Send Formal Notice' : 'Send Awareness Notice'}
                </Link>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">What Each Stage Means</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-xs text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="mt-0.5 w-1.5 h-1.5 rounded-full bg-blue-ncs flex-shrink-0" />
                  <span><strong className="text-slate-700 dark:text-slate-300">Signed</strong> -- evidence base for enforcement</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-0.5 w-1.5 h-1.5 rounded-full bg-blue-ncs flex-shrink-0" />
                  <span><strong className="text-slate-700 dark:text-slate-300">Verified</strong> -- AI companies checking your rights = documented awareness</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-0.5 w-1.5 h-1.5 rounded-full bg-amber-500 flex-shrink-0" />
                  <span><strong className="text-slate-700 dark:text-slate-300">Enforcement Readiness</strong> -- 100 encounters: preliminary notice | 500: maximum willful infringement leverage</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-0.5 w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0" />
                  <span><strong className="text-slate-700 dark:text-slate-300">Earnings</strong> -- coalition licensing revenue distributed</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* API Health -- collapsible */}
      <div className="mb-8">
        <Button
          variant="ghost"
          onClick={() => setApiHealthOpen(v => !v)}
          className="w-full flex items-center justify-between p-4 rounded-xl border border-border bg-muted/20 hover:bg-muted/30 h-auto"
        >
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span className="text-sm font-medium text-delft-blue dark:text-white">API Health Metrics</span>
            <Badge variant="secondary" size="sm">Technical</Badge>
          </div>
          <svg
            className={`w-4 h-4 text-muted-foreground transition-transform ${apiHealthOpen ? 'rotate-180' : ''}`}
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </Button>

        {apiHealthOpen && (
          <div className="mt-4 space-y-6">
            {/* Stat cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {isLoading ? (
                <>
                  <StatCardSkeleton />
                  <StatCardSkeleton />
                  <StatCardSkeleton />
                </>
              ) : (
                <>
                  <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-4">
                    <p className="text-xs font-medium text-muted-foreground mb-1">Total API Calls</p>
                    <p className="text-2xl font-bold text-delft-blue dark:text-white">{formatNumber(stats?.total_api_calls || 0)}</p>
                    <p className="text-[11px] text-muted-foreground mt-1">Last {timeRange} days</p>
                  </div>
                  <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-4">
                    <p className="text-xs font-medium text-muted-foreground mb-1">Success Rate</p>
                    <p className="text-2xl font-bold text-delft-blue dark:text-white">{stats?.success_rate?.toFixed(1) || '0'}%</p>
                    <p className="text-[11px] text-muted-foreground mt-1">
                      <Badge variant={responseStatus.variant} size="sm">{responseStatus.label}</Badge>
                    </p>
                  </div>
                  <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-4">
                    <p className="text-xs font-medium text-muted-foreground mb-1">Avg Response</p>
                    <p className="text-2xl font-bold text-delft-blue dark:text-white">{stats?.avg_response_time_ms?.toFixed(0) || '0'}ms</p>
                    <p className="text-[11px] text-muted-foreground mt-1">Target: under 400ms</p>
                  </div>
                </>
              )}
            </div>

            {/* Chart + Highlights */}
            <div className="grid lg:grid-cols-3 gap-6">
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle>API Calls Over Time</CardTitle>
                  <CardDescription>Daily API usage for the selected period</CardDescription>
                </CardHeader>
                <CardContent>
                  {isTimeSeriesLoading ? (
                    <ChartSkeleton />
                  ) : timeSeries.length === 0 ? (
                    <div className="h-64 flex items-center justify-center text-muted-foreground">
                      No data available for this period
                    </div>
                  ) : (
                    <div className="h-64 flex">
                      <div className="flex flex-col justify-between pr-3 text-[10px] text-muted-foreground" style={{ paddingBottom: '24px' }}>
                        <span>{formatNumber(maxValue)}</span>
                        <span>{formatNumber(Math.round(maxValue / 2))}</span>
                        <span>0</span>
                      </div>
                      <div className="flex-1 flex items-end gap-1 border-l border-b border-border pl-2 relative" style={{ paddingBottom: '24px' }}>
                        {timeSeries.slice(-14).map((day, idx) => {
                          const pct = day.count > 0 ? Math.max((day.count / maxValue) * 100, 3) : 0;
                          return (
                            <div key={idx} className="flex-1 relative group flex items-end justify-center" style={{ height: '100%' }}>
                              <div
                                className="w-full bg-gradient-to-t from-blue-ncs to-columbia-blue rounded-t-sm hover:from-delft-blue hover:to-blue-ncs transition-colors cursor-pointer"
                                style={{ height: `${pct}%` }}
                              />
                              <div className="absolute -top-1 left-1/2 -translate-x-1/2 bg-delft-blue text-white text-[10px] px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
                                {formatNumber(day.count)}
                              </div>
                              <div className="absolute -bottom-5 left-1/2 -translate-x-1/2 text-[10px] text-muted-foreground whitespace-nowrap">
                                {new Date(day.timestamp).toLocaleDateString('en-US', { weekday: 'short' })}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Usage Highlights</CardTitle>
                    <CardDescription>Key signals for the period</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-xs uppercase tracking-wide text-muted-foreground">Peak day</p>
                          <p className="text-sm font-medium text-slate-800 dark:text-slate-100">
                            {peakDay ? formatShortDate(peakDay.timestamp) : '--'}
                          </p>
                        </div>
                        <Badge variant="secondary" size="sm">
                          {peakDay ? `${formatNumber(peakDay.count)} calls` : 'No data'}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-xs uppercase tracking-wide text-muted-foreground">Average per day</p>
                          <p className="text-sm font-medium text-slate-800 dark:text-slate-100">
                            {averageDailyCalls ? `${formatNumber(averageDailyCalls)} calls` : '--'}
                          </p>
                        </div>
                        <Badge variant="outline" size="sm">{periodLabel}</Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="rounded-lg border border-border bg-muted/30 p-3">
                          <p className="text-xs text-muted-foreground">Signing share</p>
                          <p className="text-lg font-semibold text-delft-blue dark:text-white">{signShare ? signShare.toFixed(1) : '0'}%</p>
                        </div>
                        <div className="rounded-lg border border-border bg-muted/30 p-3">
                          <p className="text-xs text-muted-foreground">Verify share</p>
                          <p className="text-lg font-semibold text-delft-blue dark:text-white">{verifyShare ? verifyShare.toFixed(1) : '0'}%</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Response Health</CardTitle>
                    <CardDescription>Latency and success posture</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-xs uppercase tracking-wide text-muted-foreground">Status</p>
                        <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{responseStatus.label}</p>
                      </div>
                      <Badge variant={responseStatus.variant} size="sm">
                        {avgResponseTime ? `${avgResponseTime.toFixed(0)}ms avg` : 'No data'}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="rounded-lg border border-border bg-muted/30 p-3">
                        <p className="text-xs text-muted-foreground">Success</p>
                        <p className={`text-lg font-semibold ${successRate > 0 ? 'text-emerald-600' : 'text-muted-foreground'}`}>{successRate.toFixed(1)}%</p>
                      </div>
                      <div className="rounded-lg border border-border bg-muted/30 p-3">
                        <p className="text-xs text-muted-foreground">Error</p>
                        <p className={`text-lg font-semibold ${errorRate > 0 && successRate > 0 ? 'text-amber-600' : 'text-muted-foreground'}`}>{errorRate.toFixed(1)}%</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Activity Timeline */}
      <div className="grid lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <ActivityFeed title="Activity Timeline" limit={6} />
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Quick Reference</CardTitle>
            <CardDescription>Understanding your timeline</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3 text-sm text-muted-foreground">
              <li className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-blue-ncs" />
                <span>Signed content is your enforcement corpus. More articles = stronger coalition bargaining position.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-emerald-500" />
                <span>Each verification is documented awareness -- evidence that rights were checked before use.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-amber-500" />
                <span>500 verifications triggers Formal Notice eligibility. Willful infringement = up to $150K/work in damages.</span>
              </li>
            </ul>
            <div className="mt-4 rounded-lg border border-border bg-muted/30 p-3 text-xs text-muted-foreground">
              Questions about the timeline? <a href="/docs" className="text-blue-ncs hover:underline">See documentation</a> or contact support.
            </div>
          </CardContent>
        </Card>
      </div>

    </DashboardLayout>
  );
}
