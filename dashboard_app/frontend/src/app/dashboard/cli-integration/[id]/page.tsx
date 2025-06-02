'use client';

import React, { useEffect, useState } from 'react';
import { useQuery } from 'react-query';
import { ArrowLeftIcon, DocumentArrowDownIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import Link from 'next/link';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import Loading from '@/components/ui/Loading';
import ErrorDisplay from '@/components/ui/ErrorDisplay';
import { useNotifications } from '@/lib/notifications';
import cliService, { CliScan } from '@/services/cliService';

interface PageProps {
  params: {
    id: string;
  };
}

export default function CliScanDetailsPage({ params }: PageProps) {
  const { id } = params;
  const scanId = parseInt(id, 10);
  const { addNotification } = useNotifications();
  const [autoRefresh, setAutoRefresh] = useState(false);

  // Define scan state to avoid circular reference
  const [scanState, setScanState] = useState<'running' | 'queued' | 'completed' | 'failed' | null>(null);
  
  // Fetch scan details
  const { 
    data: scan, 
    isLoading, 
    error, 
    refetch,
    isRefetching
  } = useQuery<CliScan, Error>(
    ['cliScan', scanId],
    () => cliService.getScan(scanId),
    {
      refetchInterval: autoRefresh && (scanState === 'running' || scanState === 'queued') ? 3000 : false,
      onError: (err: any) => {
        addNotification({
          type: 'error',
          title: 'Error fetching scan details',
          message: err.message || 'An unexpected error occurred'
        });
      }
    }
  );

  // Update scan state and turn off auto-refresh when scan completes
  useEffect(() => {
    if (scan) {
      setScanState(scan.status as 'running' | 'queued' | 'completed' | 'failed');
      if (scan.status !== 'running' && scan.status !== 'queued') {
        setAutoRefresh(false);
      }
    }
  }, [scan]);

  // Format date for display
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  // Calculate duration
  const calculateDuration = () => {
    if (!scan) return 'N/A';
    
    const start = new Date(scan.started_at).getTime();
    const end = scan.completed_at 
      ? new Date(scan.completed_at).getTime() 
      : new Date().getTime();
    
    const durationMs = end - start;
    const seconds = Math.floor(durationMs / 1000) % 60;
    const minutes = Math.floor(durationMs / (1000 * 60)) % 60;
    const hours = Math.floor(durationMs / (1000 * 60 * 60));
    
    return `${hours > 0 ? `${hours}h ` : ''}${minutes}m ${seconds}s`;
  };

  // Get status badge class
  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'running':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'queued':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  // Toggle auto-refresh
  const toggleAutoRefresh = () => {
    setAutoRefresh(prev => !prev);
  };

  // Handle manual refresh
  const handleRefresh = () => {
    refetch();
  };

  if (isLoading) {
    return <Loading text="Loading scan details..." />;
  }

  if (error) {
    return (
      <ErrorDisplay 
        title="Error Loading Scan Details" 
        message={(error as Error).message}
        onRetry={refetch}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <Link href="/dashboard/cli-integration" className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300">
            <ArrowLeftIcon className="h-5 w-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            CLI Scan Details
          </h1>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={toggleAutoRefresh}
            className={autoRefresh ? 'bg-primary-100 dark:bg-primary-900' : ''}
          >
            {autoRefresh ? 'Auto-refreshing' : 'Auto-refresh'}
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleRefresh}
            isLoading={isRefetching}
          >
            <ArrowPathIcon className="h-4 w-4 mr-1" />
            Refresh
          </Button>
        </div>
      </div>

      {scan && (
        <>
          <Card title="Scan Information">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Scan ID</p>
                <p className="font-medium">{scan.id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Status</p>
                <p>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(scan.status)}`}>
                    {scan.status.charAt(0).toUpperCase() + scan.status.slice(1)}
                  </span>
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Scan Type</p>
                <p className="font-medium capitalize">{scan.scan_type.replace('_', ' ')}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Started At</p>
                <p className="font-medium">{formatDate(scan.started_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Completed At</p>
                <p className="font-medium">{formatDate(scan.completed_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Duration</p>
                <p className="font-medium">{calculateDuration()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">User</p>
                <p className="font-medium">{scan.user_email}</p>
              </div>
              {scan.progress !== undefined && (
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Progress</p>
                  <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 mt-2">
                    <div 
                      className="bg-primary-600 h-2.5 rounded-full" 
                      style={{ width: `${scan.progress}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-right mt-1">{scan.progress}%</p>
                </div>
              )}
            </div>
            
            {scan.target_path && (
              <div className="mt-4">
                <p className="text-sm text-gray-500 dark:text-gray-400">Target Path</p>
                <p className="font-medium break-all">{scan.target_path}</p>
              </div>
            )}
            
            {scan.parameters && Object.keys(scan.parameters).length > 0 && (
              <div className="mt-4">
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Parameters</p>
                <div className="bg-gray-50 dark:bg-gray-800 rounded-md p-3">
                  <pre className="text-xs overflow-auto whitespace-pre-wrap">
                    {JSON.stringify(scan.parameters, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </Card>

          <Card title="Scan Output">
            {scan.status === 'running' && (
              <div className="flex items-center mb-2">
                <Loading size="sm" className="mr-2" />
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  Scan in progress...
                </span>
              </div>
            )}
            
            <div className="bg-gray-50 dark:bg-gray-800 rounded-md p-4 font-mono text-sm overflow-auto max-h-96">
              {scan.output ? (
                <pre className="whitespace-pre-wrap">{scan.output}</pre>
              ) : (
                <p className="text-gray-500 dark:text-gray-400">No output available</p>
              )}
            </div>
          </Card>

          {scan.error_message && (
            <Card title="Error Details" className="border-red-200 dark:border-red-900">
              <div className="bg-red-50 dark:bg-red-900/20 rounded-md p-4 text-red-800 dark:text-red-300">
                <pre className="whitespace-pre-wrap font-mono text-sm">{scan.error_message}</pre>
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
