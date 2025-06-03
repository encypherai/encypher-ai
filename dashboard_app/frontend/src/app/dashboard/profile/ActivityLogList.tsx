'use client';

import React from 'react';
import Card from '@/components/ui/Card';
import { ActivityLogSkeleton } from '@/components/ui/Skeleton';
import ErrorDisplay from '@/components/ui/ErrorDisplay';
import { DocumentTextIcon } from '@heroicons/react/24/outline';
import { ActivityLog } from '@/lib/hooks/useActivityLogs';

interface ActivityLogListProps {
  isLoading: boolean;
  isError?: boolean;
  error?: Error | null;
  onRetry?: () => void;
  logs?: ActivityLog[];
  emptyMessage?: string;
}

// Format date for display
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
}

const ActivityLogList: React.FC<ActivityLogListProps> = ({
  isLoading,
  isError = false,
  error = null,
  onRetry,
  logs = [],
  emptyMessage = 'No recent activity found.'
}) => {
  return (
    <Card title="Recent Activity">
      {isLoading ? (
        <ActivityLogSkeleton count={5} />
      ) : isError ? (
        <ErrorDisplay 
          message={error?.message || 'Failed to load activity logs'} 
          onRetry={onRetry}
        />
      ) : (
        <div>
          {logs.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400 text-center py-4">{emptyMessage}</p>
          ) : (
            <div className="flow-root">
              <ul className="-mb-8">
                {logs.map((log, index) => (
                  <li key={log.id}>
                    <div className="relative pb-8">
                      {index !== logs.length - 1 && (
                        <span
                          className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200 dark:bg-gray-700"
                          aria-hidden="true"
                        />
                      )}
                      <div className="relative flex space-x-3">
                        <div>
                          <div className="relative px-1">
                            <div className="h-8 w-8 bg-primary-100 dark:bg-primary-900 rounded-full ring-8 ring-white dark:ring-gray-900 flex items-center justify-center">
                              <DocumentTextIcon className="h-5 w-5 text-primary-600 dark:text-primary-400" aria-hidden="true" />
                            </div>
                          </div>
                        </div>
                        <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                          <div>
                            <p className="text-sm text-gray-900 dark:text-white">{log.action}</p>
                            <p className="text-sm text-gray-500 dark:text-gray-400">{log.details}</p>
                          </div>
                          <div className="text-right text-sm whitespace-nowrap text-gray-500 dark:text-gray-400">
                            <time dateTime={log.timestamp}>{formatDate(log.timestamp)}</time>
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

export default ActivityLogList;
