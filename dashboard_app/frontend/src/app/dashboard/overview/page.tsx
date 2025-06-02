'use client';

import React, { useState, useCallback } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import { useNotifications } from '@/lib/notifications';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Loading from '@/components/ui/Loading';
import ErrorDisplay from '@/components/ui/ErrorDisplay';
import ScanStatusChart from '@/components/charts/ScanStatusChart';
import ScanTypeChart from '@/components/charts/ScanTypeChart';
import ScansTimeSeriesChart from '@/components/charts/ScansTimeSeriesChart';
import { ArrowPathIcon } from '@heroicons/react/24/outline';
import cliService from '@/services/cliService';

// Define the time range type for the time series chart
type TimeRange = 'day' | 'week' | 'month';

export default function DashboardOverviewPage() {
  const { addNotification } = useNotifications();
  const queryClient = useQueryClient();
  const [timeRange, setTimeRange] = useState<TimeRange>('week');

  // Fetch scan status distribution data
  const { 
    data: statusData, 
    isLoading: isLoadingStatus, 
    error: statusError,
    refetch: refetchStatus
  } = useQuery(
    ['scanStatusDistribution'],
    async () => {
      const result = await cliService.getScans();
      
      // Process data to count scans by status
      const statusCounts: Record<string, number> = {};
      result.items.forEach(scan => {
        const status = scan.status || 'unknown';
        statusCounts[status] = (statusCounts[status] || 0) + 1;
      });
      
      // Convert to array format for the chart
      return Object.entries(statusCounts).map(([status, count]) => ({
        status,
        count
      }));
    },
    {
      staleTime: 60000, // 1 minute
      retry: 3,
      onError: (error: Error) => {
        console.error('Error fetching scan status distribution:', error);
      }
    }
  );

  // Fetch scan type distribution data
  const { 
    data: typeData, 
    isLoading: isLoadingType, 
    error: typeError,
    refetch: refetchType
  } = useQuery(
    ['scanTypeDistribution'],
    async () => {
      const result = await cliService.getScans();
      
      // Process data to count scans by type
      const typeCounts: Record<string, number> = {};
      result.items.forEach(scan => {
        const type = scan.scan_type || 'unknown';
        typeCounts[type] = (typeCounts[type] || 0) + 1;
      });
      
      // Convert to array format for the chart
      return Object.entries(typeCounts).map(([type, count]) => ({
        type,
        count
      }));
    },
    {
      staleTime: 60000, // 1 minute
      retry: 3,
      onError: (error: Error) => {
        console.error('Error fetching scan type distribution:', error);
      }
    }
  );

  // Fetch time series data
  const { 
    data: timeSeriesData, 
    isLoading: isLoadingTimeSeries, 
    error: timeSeriesError,
    refetch: refetchTimeSeries
  } = useQuery(
    ['scansTimeSeries', timeRange],
    async () => {
      const result = await cliService.getScans();
      
      // Process data to group scans by date
      const dateMap: Record<string, { 
        date: string, 
        count: number,
        completed: number,
        failed: number,
        running: number
      }> = {};
      
      // Determine date format based on time range
      const formatDate = (date: Date): string => {
        switch (timeRange) {
          case 'day':
            return date.toISOString().slice(0, 13) + ':00:00Z'; // Hour precision
          case 'week':
            return date.toISOString().slice(0, 10); // Day precision
          case 'month':
            return date.toISOString().slice(0, 10); // Day precision
          default:
            return date.toISOString().slice(0, 10);
        }
      };
      
      // Group scans by date and status
      result.items.forEach(scan => {
        const scanDate = new Date(scan.started_at || new Date());
        const dateKey = formatDate(scanDate);
        
        if (!dateMap[dateKey]) {
          dateMap[dateKey] = { 
            date: dateKey, 
            count: 0,
            completed: 0,
            failed: 0,
            running: 0
          };
        }
        
        dateMap[dateKey].count += 1;
        
        // Count by status
        if (scan.status === 'completed') {
          dateMap[dateKey].completed += 1;
        } else if (scan.status === 'failed') {
          dateMap[dateKey].failed += 1;
        } else if (scan.status === 'running' || scan.status === 'queued') {
          dateMap[dateKey].running += 1;
        }
      });
      
      // Convert to array and sort by date
      return Object.values(dateMap).sort((a, b) => 
        new Date(a.date).getTime() - new Date(b.date).getTime()
      );
    },
    {
      staleTime: 60000, // 1 minute
      retry: 3,
      onError: (error: Error) => {
        console.error('Error fetching time series data:', error);
      }
    }
  );

  // Fetch active scans count
  const { 
    data: activeScansData, 
    isLoading: isLoadingActiveScans,
    error: activeScansError 
  } = useQuery<{ count: number }, Error>(
    ['activeScansCount'],
    async () => {
      const result = await cliService.getScans({ activeOnly: true, limit: 1 });
      return { count: result.total || 0 };
    },
    {
      refetchInterval: 10000, // 10 seconds
      staleTime: 5000,
      retry: 3,
      onError: (error: Error) => {
        console.error('Error fetching active scans count:', error);
      }
    }
  );

  // Fetch total scans count
  const { 
    data: totalScansData, 
    isLoading: isLoadingTotalScans,
    error: totalScansError 
  } = useQuery<{ count: number }, Error>(
    ['totalScansCount'],
    async () => {
      const result = await cliService.getScans({ limit: 1 });
      return { count: result.total || 0 };
    },
    {
      staleTime: 60000, // 1 minute
      retry: 3,
      onError: (error: Error) => {
        console.error('Error fetching total scans count:', error);
      }
    }
  );

  // Handle refresh all data
  const handleRefresh = useCallback(() => {
    refetchStatus();
    refetchType();
    refetchTimeSeries();
    queryClient.invalidateQueries('activeScansCount');
    queryClient.invalidateQueries('totalScansCount');
    
    addNotification({
      type: 'success',
      title: 'Refreshed',
      message: 'Dashboard data has been refreshed',
    });
  }, [queryClient, refetchStatus, refetchType, refetchTimeSeries, addNotification]);

  // Handle time range change
  const handleTimeRangeChange = useCallback((range: TimeRange) => {
    setTimeRange(range);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-white">Dashboard Overview</h1>
        <Button 
          variant="outline" 
          onClick={handleRefresh} 
          className="flex items-center gap-2 px-3 sm:px-4 py-2"
        >
          <ArrowPathIcon className="h-4 w-4" />
          <span className="hidden sm:inline">Refresh</span>
        </Button>
      </div>
      
      {/* Stats summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card title="Active Scans" className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 flex flex-col">
          <div className="flex flex-col items-center justify-center h-full p-4">
            {isLoadingActiveScans ? (
              <Loading size="md" />
            ) : activeScansError ? (
              <span className="text-4xl font-bold text-red-600 dark:text-red-400">?</span>
            ) : (
              <span className="text-4xl font-bold text-blue-600 dark:text-blue-400">
                {activeScansData?.count || 0}
              </span>
            )}
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Running or queued</p>
          </div>
        </Card>
        
        <Card title="Total Scans" className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 flex flex-col">
          <div className="flex flex-col items-center justify-center h-full p-4">
            {isLoadingTotalScans ? (
              <Loading size="md" />
            ) : totalScansError ? (
              <span className="text-4xl font-bold text-red-600 dark:text-red-400">?</span>
            ) : (
              <span className="text-4xl font-bold text-green-600 dark:text-green-400">
                {totalScansData?.count || 0}
              </span>
            )}
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">All time</p>
          </div>
        </Card>
        
        <Card title="Valid Signatures" className="bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800 flex flex-col">
          <div className="flex flex-col items-center justify-center h-full p-4">
            <span className="text-4xl font-bold text-purple-600 dark:text-purple-400">
              98%
            </span>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Last 30 days</p>
          </div>
        </Card>
        
        <Card title="Policy Violations" className="bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800 flex flex-col">
          <div className="flex flex-col items-center justify-center h-full p-4">
            <span className="text-4xl font-bold text-amber-600 dark:text-amber-400">
              3
            </span>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Last 30 days</p>
          </div>
        </Card>
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ScanStatusChart 
          data={statusData || []} 
          isLoading={isLoadingStatus}
          error={statusError as Error}
        />
        
        <ScanTypeChart 
          data={typeData || []} 
          isLoading={isLoadingType}
          error={typeError as Error}
        />
      </div>
      
      <div className="mt-6">
        <ScansTimeSeriesChart 
          data={timeSeriesData || []} 
          isLoading={isLoadingTimeSeries}
          error={timeSeriesError as Error}
          timeRange={timeRange}
          onTimeRangeChange={handleTimeRangeChange}
        />
      </div>
      
      {/* Recent Activity */}
      <div className="mt-6">
        <Card title="Recent Activity">
          <div className="space-y-4 py-2">
            <div className="flex items-start p-3 border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/20">
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-800 dark:text-blue-300">New scan started</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Audit Log scan #123 started at 10:15 AM</p>
              </div>
            </div>
            
            <div className="flex items-start p-3 border-l-4 border-green-500 bg-green-50 dark:bg-green-900/20">
              <div className="ml-3">
                <p className="text-sm font-medium text-green-800 dark:text-green-300">Scan completed</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Policy Validator scan #122 completed successfully</p>
              </div>
            </div>
            
            <div className="flex items-start p-3 border-l-4 border-red-500 bg-red-50 dark:bg-red-900/20">
              <div className="ml-3">
                <p className="text-sm font-medium text-red-800 dark:text-red-300">Policy violation detected</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Missing required metadata field 'department_id' in 3 documents</p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
