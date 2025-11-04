'use client';

import React from 'react';
import {
  DocumentTextIcon,
  CheckCircleIcon,
  CurrencyDollarIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import StatCard from '@/components/ui/StatCard';
import Card from '@/components/ui/Card';
import { useCoalitionStats } from '@/lib/hooks/useCoalition';
import { useNotifications } from '@/lib/notifications';
import RevenueChart from '@/components/coalition/RevenueChart';
import ContentPerformanceTable from '@/components/coalition/ContentPerformanceTable';
import AccessLogsTable from '@/components/coalition/AccessLogsTable';

export default function CoalitionPage() {
  const { addNotification } = useNotifications();

  const {
    data: stats,
    isLoading,
    isError,
    error
  } = useCoalitionStats({
    onError: (err) => {
      addNotification({
        type: 'error',
        title: 'Failed to load coalition stats',
        message: err.message || 'An unexpected error occurred.',
      });
    },
  });

  if (isError) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <h3 className="text-red-800 dark:text-red-200 font-medium">Error Loading Coalition Dashboard</h3>
          <p className="text-red-600 dark:text-red-400 text-sm mt-1">{error?.message}</p>
        </div>
      </div>
    );
  }

  const formatNextPayoutDate = (dateString?: string) => {
    if (!dateString) return 'Not scheduled';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Coalition Dashboard</h1>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Signed Documents"
          value={isLoading ? '-' : stats?.content_stats.total_documents.toLocaleString() || '0'}
          change={
            stats?.content_stats.trend_percentage
              ? {
                  value: `${stats.content_stats.trend_percentage.toFixed(1)}%`,
                  isPositive: stats.content_stats.trend_percentage >= 0
                }
              : undefined
          }
          icon={<DocumentTextIcon className="h-8 w-8" />}
        />
        <StatCard
          title="Verifications"
          value={isLoading ? '-' : stats?.content_stats.verification_count.toLocaleString() || '0'}
          icon={<CheckCircleIcon className="h-8 w-8" />}
        />
        <StatCard
          title="Total Earned"
          value={isLoading ? '-' : `$${stats?.revenue_stats.total_earned.toFixed(2) || '0.00'}`}
          icon={<CurrencyDollarIcon className="h-8 w-8" />}
        />
        <StatCard
          title="Pending Payout"
          value={isLoading ? '-' : `$${stats?.revenue_stats.pending.toFixed(2) || '0.00'}`}
          icon={<ClockIcon className="h-8 w-8" />}
        />
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Next Payout Date</h3>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {isLoading ? '-' : formatNextPayoutDate(stats?.revenue_stats.next_payout_date)}
          </p>
        </Card>
        <Card>
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Monthly Average</h3>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {isLoading ? '-' : `$${stats?.revenue_stats.monthly_average.toFixed(2) || '0.00'}`}
          </p>
        </Card>
        <Card>
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Recent Documents (30 days)</h3>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {isLoading ? '-' : stats?.content_stats.recent_documents.toLocaleString() || '0'}
          </p>
        </Card>
      </div>

      {/* Revenue Chart */}
      <Card>
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Revenue Over Time</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">Monthly earnings and payouts</p>
        </div>
        <RevenueChart
          data={stats?.revenue_history || []}
          isLoading={isLoading}
        />
      </Card>

      {/* Content Performance */}
      <Card>
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Top Performing Content</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">Your highest earning content items</p>
        </div>
        <ContentPerformanceTable
          data={stats?.top_content || []}
          isLoading={isLoading}
        />
      </Card>

      {/* Access Logs */}
      <Card>
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Recent Content Access</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">AI companies accessing your content</p>
        </div>
        <AccessLogsTable
          data={stats?.recent_access || []}
          isLoading={isLoading}
        />
      </Card>
    </div>
  );
}
