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
        <h2 className="text-3xl font-bold text-delft-blue dark:text-white mb-2">Usage & Analytics</h2>
        <p className="text-muted-foreground">
          Track your API usage, performance metrics, and activity history
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
      <div className="grid md:grid-cols-5 gap-6 mb-8">
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
            <Card>
              <CardContent className="pt-6">
                <div className="text-sm text-muted-foreground mb-1">Total API Calls</div>
                <div className="text-3xl font-bold text-delft-blue dark:text-white">
                  {formatNumber(stats?.total_api_calls || 0)}
                </div>
                <div className="text-xs text-muted-foreground mt-1">Last {timeRange} days</div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="text-sm text-muted-foreground mb-1">Documents Signed</div>
                <div className="text-3xl font-bold text-delft-blue dark:text-white">
                  {formatNumber(stats?.total_documents_signed || 0)}
                </div>
                <div className="text-xs text-muted-foreground mt-1">Last {timeRange} days</div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="text-sm text-muted-foreground mb-1">Verifications</div>
                <div className="text-3xl font-bold text-delft-blue dark:text-white">
                  {formatNumber(stats?.total_verifications || 0)}
                </div>
                <div className="text-xs text-muted-foreground mt-1">Last {timeRange} days</div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="text-sm text-muted-foreground mb-1">Success Rate</div>
                <div className="text-3xl font-bold text-delft-blue dark:text-white">
                  {stats?.success_rate?.toFixed(1) || '0'}%
                </div>
                <div className="text-xs text-muted-foreground mt-1">Last {timeRange} days</div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="text-sm text-muted-foreground mb-1">Avg Response</div>
                <div className="text-3xl font-bold text-delft-blue dark:text-white">
                  {stats?.avg_response_time_ms?.toFixed(0) || '0'}ms
                </div>
                <div className="text-xs text-muted-foreground mt-1">Last {timeRange} days</div>
              </CardContent>
            </Card>
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
              <div className="h-64 flex items-end justify-between space-x-2">
                {timeSeries.slice(-14).map((day, idx) => (
                  <div key={idx} className="flex-1 flex flex-col items-center">
                    <div
                      className="w-full bg-columbia-blue rounded-t hover:bg-blue-ncs transition-colors cursor-pointer"
                      style={{ height: `${(day.count / maxValue) * 100}%`, minHeight: day.count > 0 ? '4px' : '0' }}
                      title={`${day.count} calls`}
                    />
                    <div className="text-xs text-muted-foreground mt-2">
                      {new Date(day.timestamp).toLocaleDateString('en-US', { weekday: 'short' })}
                    </div>
                  </div>
                ))}
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
            <CardTitle>Operational Notes</CardTitle>
            <CardDescription>Daily signals for your team</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3 text-sm text-muted-foreground">
              <li className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-blue-ncs" />
                <span>Audit log exports are refreshed every 15 minutes for enterprise teams.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-emerald-500" />
                <span>Set webhook alerts when error rate exceeds 5% in a 30-minute window.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-amber-500" />
                <span>Daily usage snapshots are available for compliance reporting.</span>
              </li>
            </ul>
            <div className="mt-4 rounded-lg border border-border bg-muted/30 p-3 text-xs text-muted-foreground">
              Need deeper detail? Visit the audit logs page for structured event history.
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Info Cards */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
            <CardDescription>Tips to maximize your Encypher usage</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start gap-3">
                <div className="w-6 h-6 bg-columbia-blue rounded flex items-center justify-center text-white text-xs font-bold shrink-0">1</div>
                <span>Generate an API key from the <a href="/api-keys" className="text-blue-ncs hover:underline">API Keys page</a></span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-6 h-6 bg-columbia-blue rounded flex items-center justify-center text-white text-xs font-bold shrink-0">2</div>
                <span>Install our SDK or WordPress plugin</span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-6 h-6 bg-columbia-blue rounded flex items-center justify-center text-white text-xs font-bold shrink-0">3</div>
                <span>Start signing and verifying your content</span>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Need Help?</CardTitle>
            <CardDescription>Resources and support</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <a 
                href="https://api.encypherai.com/docs" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-3 p-3 border border-border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="w-8 h-8 bg-delft-blue rounded flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <div>
                  <div className="font-medium text-sm">Documentation</div>
                  <div className="text-xs text-muted-foreground">API reference and guides</div>
                </div>
              </a>
              <a 
                href="mailto:support@encypherai.com"
                className="flex items-center gap-3 p-3 border border-border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="w-8 h-8 bg-blue-ncs rounded flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <div className="font-medium text-sm">Contact Support</div>
                  <div className="text-xs text-muted-foreground">Get help from our team</div>
                </div>
              </a>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

