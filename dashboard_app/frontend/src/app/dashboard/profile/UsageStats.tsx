'use client';

import React from 'react';
import Card from '@/components/ui/Card';
import { StatsSkeleton } from '@/components/ui/Skeleton';
import ErrorDisplay from '@/components/ui/ErrorDisplay';

interface UsageStatsProps {
  isLoading: boolean;
  isError?: boolean;
  error?: Error | null;
  onRetry?: () => void;
  stats?: {
    auditLogsViewed: number;
    policyValidations: number;
    cliScansInitiated: number;
  };
}

const UsageStats: React.FC<UsageStatsProps> = ({
  isLoading,
  isError = false,
  error = null,
  onRetry,
  stats = {
    auditLogsViewed: 0,
    policyValidations: 0,
    cliScansInitiated: 0
  }
}) => {
  return (
    <Card title="Usage Statistics">
      {isLoading ? (
        <StatsSkeleton count={3} />
      ) : isError ? (
        <ErrorDisplay 
          message={error?.message || 'Failed to load usage statistics'} 
          onRetry={onRetry}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Audit Logs Viewed</h3>
            <p className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">{stats.auditLogsViewed}</p>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Last 30 days</p>
          </div>
          
          <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Policy Validations</h3>
            <p className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">{stats.policyValidations}</p>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Last 30 days</p>
          </div>
          
          <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">CLI Scans Initiated</h3>
            <p className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">{stats.cliScansInitiated}</p>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Last 30 days</p>
          </div>
        </div>
      )}
    </Card>
  );
};

export default UsageStats;
