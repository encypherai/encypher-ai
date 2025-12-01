'use client';

import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent } from '@encypher/design-system';
import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { useState } from 'react';
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

  // Format numbers
  const formatNumber = (num: number) => num?.toLocaleString() ?? '0';

  // Get max value for chart scaling
  const maxValue = Math.max(...timeSeries.map(d => d.count), 1);

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-delft-blue dark:text-white mb-2">Usage & Analytics</h2>
        <p className="text-muted-foreground">
          Track your API usage, performance metrics, and activity history
        </p>
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
            Export CSV
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

      {/* Usage Chart */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>API Calls Over Time</CardTitle>
          <CardDescription>Daily API usage for the selected period</CardDescription>
        </CardHeader>
        <CardContent>
          {timeSeriesQuery.isLoading ? (
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
                href="https://docs.encypherai.com" 
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

