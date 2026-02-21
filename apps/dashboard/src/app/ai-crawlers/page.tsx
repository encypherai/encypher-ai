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
import { useState } from 'react';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
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

const CRAWLER_COLORS = ['#2A87C4', '#00A8B5', '#4A9E6B', '#8B6DBF', '#C46A2A', '#C4A62A'];

const SOURCE_LABELS: Record<string, string> = {
  rsl_olp_check: 'RSL Lookup',
  api_verification: 'Rights API',
  chrome_extension: 'Chrome Extension',
  http_header_lookup: 'HTTP Header',
  crawl_detected: 'Crawl Detected',
};

function getComplianceBadgeClass(label?: string): string {
  switch (label) {
    case 'Excellent': return 'bg-emerald-100 text-emerald-800';
    case 'Good': return 'bg-blue-100 text-blue-800';
    case 'Fair': return 'bg-yellow-100 text-yellow-800';
    case 'Poor': return 'bg-orange-100 text-orange-800';
    case 'Non-compliant': return 'bg-red-100 text-red-800';
    default: return 'bg-slate-100 text-slate-700';
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
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-delft-blue dark:text-white">AI Crawler Intelligence</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Track which systems access your content, measure rights compliance, and build licensing evidence.
        </p>
      </div>

      {/* Time Range + Export */}
      <div className="flex items-center justify-between mb-6">
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
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {isLoading ? (
          <>
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
              <div className="h-64 flex items-center justify-center text-muted-foreground">
                No timeseries data available for this period
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
              <div className="text-sm text-muted-foreground py-8 text-center">
                No crawlers detected yet
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
            <div className="text-sm text-muted-foreground py-12 text-center">
              No AI crawler activity detected in this period.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
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
              <div className="text-sm text-muted-foreground py-8 text-center">
                No detection source data available
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
            <CardTitle>Bot Categories</CardTitle>
            <CardDescription>Crawler types by category</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <TableSkeleton />
            ) : Object.keys(byCat).length === 0 ? (
              <div className="text-sm text-muted-foreground py-8 text-center">
                No category data available
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(byCat)
                  .sort(([, a], [, b]) => b - a)
                  .map(([category, count]) => (
                    <div key={category} className="rounded-lg border border-border bg-muted/30 p-3">
                      <p className="text-xs text-muted-foreground capitalize">{category.replace(/_/g, ' ')}</p>
                      <p className="text-lg font-semibold text-delft-blue dark:text-white">
                        {formatNumber(count)}
                      </p>
                    </div>
                  ))}
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
