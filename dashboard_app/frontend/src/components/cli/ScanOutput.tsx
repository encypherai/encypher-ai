'use client';

import React, { useEffect, useRef } from 'react';
import { useQuery } from 'react-query';
import { ArrowPathIcon } from '@heroicons/react/24/outline';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import Loading from '@/components/ui/Loading';
import ErrorDisplay from '@/components/ui/ErrorDisplay';
import { useNotifications } from '@/lib/notifications';
import cliService from '@/services/cliService';

interface ScanOutputProps {
  scanId: number;
  autoRefresh?: boolean;
  maxHeight?: string;
  className?: string;
}

export default function ScanOutput({ 
  scanId, 
  autoRefresh = false, 
  maxHeight = '400px',
  className = '' 
}: ScanOutputProps) {
  const outputRef = useRef<HTMLPreElement>(null);
  const { addNotification } = useNotifications();

  // Query to fetch scan output
  const { 
    data: output, 
    isLoading, 
    isError, 
    error, 
    refetch,
    isRefetching,
    dataUpdatedAt
  } = useQuery<string, Error>(
    ['scanOutput', scanId],
    () => cliService.getScanOutput(scanId),
    {
      refetchInterval: autoRefresh ? 3000 : false, // Poll every 3 seconds if autoRefresh is enabled
      staleTime: autoRefresh ? 0 : 30000, // Data is immediately stale when auto-refreshing, otherwise 30s
      retry: 3, // Retry failed requests up to 3 times
      retryDelay: 1000, // Wait 1 second between retries
      onError: (err: Error) => {
        addNotification({
          type: 'error',
          title: 'Error fetching scan output',
          message: err.message || 'An unexpected error occurred',
        });
      }
    }
  );
  
  // Format the last updated time
  const lastUpdated = dataUpdatedAt ? new Date(dataUpdatedAt).toLocaleTimeString() : null;

  // Scroll to bottom when output updates
  useEffect(() => {
    if (outputRef.current && autoRefresh) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output, autoRefresh]);

  return (
    <Card 
      title={
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <span>Scan Output</span>
            {autoRefresh && !isLoading && !isRefetching && (
              <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
                <span className="inline-block h-2 w-2 rounded-full bg-green-500 mr-1"></span>
                Auto-refreshing
              </span>
            )}
            {lastUpdated && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                Last updated: {lastUpdated}
              </span>
            )}
          </div>
          <Button
            variant="ghost"
            size="xs"
            onClick={() => refetch()}
            isLoading={isRefetching}
            title="Refresh Output"
          >
            <ArrowPathIcon className="h-4 w-4" />
          </Button>
        </div>
      } 
      className={className}
    >
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-8">
          <Loading text="Loading scan output..." />
        </div>
      ) : isError ? (
        <ErrorDisplay
          title="Error fetching scan output"
          error={error}
          message="Failed to load scan output"
          onRetry={() => refetch()}
        />
      ) : (
        <div className="relative">
          {autoRefresh && (
            <div className="absolute top-0 right-0 p-1">
              <span className="flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-primary-500"></span>
              </span>
            </div>
          )}
          
          <pre
            ref={outputRef}
            className="bg-gray-50 dark:bg-gray-800 p-4 rounded-md font-mono text-sm overflow-auto whitespace-pre-wrap"
            style={{ maxHeight }}
          >
            {output ? output : (
              <span className="text-gray-500 dark:text-gray-400 italic">No output available yet. The scan may still be initializing or hasn't produced any output.</span>
            )}
          </pre>
        </div>
      )}
    </Card>
  );
}
