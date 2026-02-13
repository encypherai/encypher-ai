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
import { ActivityFeed } from '../../components/ActivityFeed';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import apiClient from '../../lib/api';
import { exportAnalyticsData, exportTimeSeriesData } from '../../lib/exportCsv';
import { toast } from 'sonner';

// Skeleton components
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

function formatDateRange(start?: string, end?: string): string {
  if (!start || !end) return '';
  const startDate = new Date(start);
  const endDate = new Date(end);
  return `${startDate.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })} – ${endDate.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })}`;
}

function formatShortDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function ChartSkeleton() {
  return (
    <div className="h-64 flex items-end justify-between space-x-2">
      {[1, 2, 3, 4, 5, 6, 7].map((i) => (
        <div key={i} className="flex-1 flex flex-col items-center">
          <div 
            className="w-full bg-muted rounded-t animate-pulse"
            style={{ height: `${Math.random() * 60 + 20}%` }}
          />
          <div className="h-3 w-8 bg-muted rounded animate-pulse mt-2" />
        </div>
      ))}
    </div>
  );
}

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<'7' | '30' | '90'>('30');
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;

  // Fetch usage stats
  const statsQuery = useQuery({
    queryKey: ['analytics-stats', timeRange],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getUsageStats(accessToken, parseInt(timeRange));
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
  });

  // Fetch time series data
  const timeSeriesQuery = useQuery({
    queryKey: ['analytics-timeseries', timeRange],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getTimeSeries(accessToken, 'api_call', parseInt(timeRange), 'day');
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
  });

  const stats = statsQuery.data;
  const timeSeries = timeSeriesQuery.data || [];
  const isLoading = statsQuery.isLoading;
  const isTimeSeriesLoading = timeSeriesQuery.isLoading;

  // Format numbers
  const formatNumber = (num: number) => num?.toLocaleString() ?? '0';

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
    : { label: '—', variant: 'secondary' as const };

  // Get max value for chart scaling
  const maxValue = Math.max(...timeSeries.map(d => d.count), 1);

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-delft-blue dark:text-white">Usage &amp; Analytics</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Track your API usage, performance metrics, and activity history.
        </p>
        <p className="text-xs text-muted-foreground mt-2">Reporting window: {periodLabel}</p>
      </div>

      {/* Time Range Selector + Export */}
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
              Last {range}d
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
            Export Summary
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              if (timeSeries.length > 0) {
                exportTimeSeriesData(timeSeries);
                toast.success('Time series exported');
              }
            }}
            disabled={timeSeries.length === 0}
          >
            <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v16h16m-4-9l-4 4-2-2-4 4" />
            </svg>
            Export Time Series
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
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
                  <p className="text-xs font-medium text-muted-foreground mb-1">Total API Calls</p>
                  <p className="text-2xl font-bold text-delft-blue dark:text-white">
                    {formatNumber(stats?.total_api_calls || 0)}
                  </p>
                </div>
                <div className="w-9 h-9 bg-gradient-to-br from-blue-ncs to-columbia-blue rounded-lg flex items-center justify-center text-white">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                </div>
              </div>
              <p className="text-[11px] text-muted-foreground mt-2">Last {timeRange} days</p>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">Documents Signed</p>
                  <p className="text-2xl font-bold text-delft-blue dark:text-white">
                    {formatNumber(stats?.total_documents_signed || 0)}
                  </p>
                </div>
                <div className="w-9 h-9 bg-gradient-to-br from-delft-blue to-blue-ncs rounded-lg flex items-center justify-center text-white">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                </div>
              </div>
              <p className="text-[11px] text-muted-foreground mt-2">Last {timeRange} days</p>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">Verifications</p>
                  <p className="text-2xl font-bold text-delft-blue dark:text-white">
                    {formatNumber(stats?.total_verifications || 0)}
                  </p>
                </div>
                <div className="w-9 h-9 bg-gradient-to-br from-columbia-blue to-blue-ncs rounded-lg flex items-center justify-center text-white">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                </div>
              </div>
              <p className="text-[11px] text-muted-foreground mt-2">Last {timeRange} days</p>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">Success Rate</p>
                  <p className="text-2xl font-bold text-delft-blue dark:text-white">
                    {stats?.success_rate?.toFixed(1) || '0'}%
                  </p>
                </div>
                <div className="w-9 h-9 bg-gradient-to-br from-[#00CED1] to-[#2A87C4] rounded-lg flex items-center justify-center text-white">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                </div>
              </div>
              <p className="text-[11px] text-muted-foreground mt-2">Last {timeRange} days</p>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-xl border border-border p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">Avg Response</p>
                  <p className="text-2xl font-bold text-delft-blue dark:text-white">
                    {stats?.avg_response_time_ms?.toFixed(0) || '0'}ms
                  </p>
                </div>
                <div className="w-9 h-9 bg-gradient-to-br from-[#2A87C4] to-[#1B2F50] rounded-lg flex items-center justify-center text-white">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                </div>
              </div>
              <p className="text-[11px] text-muted-foreground mt-2">Last {timeRange} days</p>
            </div>
          </>
        )}
      </div>

      {/* Usage Chart + Highlights */}
      <div className="grid lg:grid-cols-3 gap-6 mb-8">
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
                {/* Y-axis labels */}
                <div className="flex flex-col justify-between pr-3 text-[10px] text-muted-foreground" style={{ paddingBottom: '24px' }}>
                  <span>{formatNumber(maxValue)}</span>
                  <span>{formatNumber(Math.round(maxValue / 2))}</span>
                  <span>0</span>
                </div>
                {/* Bars */}
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
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Usage Highlights</CardTitle>
              <CardDescription>Key signals for the selected period</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-muted-foreground">Peak day</p>
                    <p className="text-sm font-medium text-slate-800 dark:text-slate-100">
                      {peakDay ? formatShortDate(peakDay.timestamp) : '—'}
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
                      {averageDailyCalls ? `${formatNumber(averageDailyCalls)} calls` : '—'}
                    </p>
                  </div>
                  <Badge variant="outline" size="sm">{periodLabel}</Badge>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="rounded-lg border border-border bg-muted/30 p-3">
                    <p className="text-xs text-muted-foreground">Signing share</p>
                    <p className="text-lg font-semibold text-delft-blue dark:text-white">
                      {signShare ? signShare.toFixed(1) : '0'}%
                    </p>
                  </div>
                  <div className="rounded-lg border border-border bg-muted/30 p-3">
                    <p className="text-xs text-muted-foreground">Verification share</p>
                    <p className="text-lg font-semibold text-delft-blue dark:text-white">
                      {verifyShare ? verifyShare.toFixed(1) : '0'}%
                    </p>
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
                  <p className="text-xs uppercase tracking-wide text-muted-foreground">Current status</p>
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{responseStatus.label}</p>
                </div>
                <Badge variant={responseStatus.variant} size="sm">
                  {avgResponseTime ? `${avgResponseTime.toFixed(0)}ms avg` : 'No data'}
                </Badge>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg border border-border bg-muted/30 p-3">
                  <p className="text-xs text-muted-foreground">Success rate</p>
                  <p className="text-lg font-semibold text-emerald-600">
                    {successRate.toFixed(1)}%
                  </p>
                </div>
                <div className="rounded-lg border border-border bg-muted/30 p-3">
                  <p className="text-xs text-muted-foreground">Error rate</p>
                  <p className="text-lg font-semibold text-amber-600">
                    {errorRate.toFixed(1)}%
                  </p>
                </div>
              </div>
              <div className="rounded-lg border border-border bg-muted/20 p-3 text-xs text-muted-foreground">
                Target latency under 400ms for real-time signing and verification workloads.
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Activity Timeline + Ops Notes */}
      <div className="grid lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <ActivityFeed title="Activity Timeline" limit={6} />
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Quick Reference</CardTitle>
            <CardDescription>Analytics tips</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3 text-sm text-muted-foreground">
              <li className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-blue-ncs" />
                <span>Use the time range selector to compare 7-day, 30-day, or 90-day windows.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-emerald-500" />
                <span>Export summary or time series data as CSV for your records.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-amber-500" />
                <span>Target response latency under 400ms for real-time signing workloads.</span>
              </li>
            </ul>
            <div className="mt-4 rounded-lg border border-border bg-muted/30 p-3 text-xs text-muted-foreground">
              Need help? Visit the <a href="/docs" className="text-blue-ncs hover:underline">documentation</a> or <a href="/support" className="text-blue-ncs hover:underline">contact support</a>.
            </div>
          </CardContent>
        </Card>
      </div>

    </DashboardLayout>
  );
}

