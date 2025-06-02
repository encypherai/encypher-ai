'use client';

import React, { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useNotifications } from '@/lib/notifications';
import CreateScanForm from '@/components/cli/CreateScanForm';
import ScanList from '@/components/cli/ScanList';
import ScanOutput from '@/components/cli/ScanOutput';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Loading from '@/components/ui/Loading';
import ErrorDisplay from '@/components/ui/ErrorDisplay';
import { useQuery, useQueryClient } from 'react-query';
import cliService from '@/services/cliService';
import { ArrowPathIcon, ChartBarIcon, ClipboardDocumentCheckIcon } from '@heroicons/react/24/outline';

export default function CliIntegrationPage() {
  const { addNotification } = useNotifications();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [selectedScanId, setSelectedScanId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'active' | 'all' | 'history'>('active');
  
  // Fetch scan details if a scan is selected
  const { data: selectedScan, isLoading: isLoadingScan, error: scanError } = useQuery(
    ['cliScan', selectedScanId],
    () => selectedScanId ? cliService.getScan(selectedScanId) : null,
    { 
      enabled: !!selectedScanId,
      refetchInterval: selectedScanId ? 3000 : false,
      retry: 3,
      onError: (error: Error) => {
        addNotification({
          type: 'error',
          title: 'Error fetching scan details',
          message: error.message || 'An unexpected error occurred',
        });
      }
    }
  );

  // Fetch active scans count for badge
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
      refetchInterval: 5000,
      staleTime: 2000,
      retry: 3,
      onError: (error: Error) => {
        console.error('Error fetching active scans count:', error);
        // Don't show notification for this background query to avoid spam
      }
    }
  );

  // Handle scan selection
  const handleScanSelect = useCallback((scanId: number) => {
    setSelectedScanId(scanId);
  }, []);

  // Handle scan creation success
  const handleScanCreated = useCallback((scanId?: number) => {
    if (scanId) {
      setSelectedScanId(scanId);
      setActiveTab('active');
    }
    // Refresh all scan-related queries
    queryClient.invalidateQueries('cliScans');
    queryClient.invalidateQueries('activeScans');
    queryClient.invalidateQueries('activeScansCount');
    
    addNotification({
      type: 'success',
      title: 'Scan Created',
      message: `New scan ${scanId ? `#${scanId}` : ''} has been created and started.`,
    });
  }, [queryClient, addNotification]);
  
  // Handle refresh all scans
  const handleRefreshScans = useCallback(() => {
    queryClient.invalidateQueries('cliScans');
    queryClient.invalidateQueries('activeScans');
    queryClient.invalidateQueries('activeScansCount');
    if (selectedScanId) {
      queryClient.invalidateQueries(['cliScan', selectedScanId]);
      queryClient.invalidateQueries(['scanOutput', selectedScanId]);
    }
    
    addNotification({
      type: 'success',
      title: 'Refreshed',
      message: 'All scan data has been refreshed',
    });
  }, [queryClient, selectedScanId, addNotification]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">CLI Integration Dashboard</h1>
        <Button 
          variant="outline" 
          onClick={handleRefreshScans} 
          className="flex items-center gap-2"
        >
          <ArrowPathIcon className="h-4 w-4" />
          Refresh
        </Button>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column - Create scan form */}
        <div className="lg:col-span-1">
          <Card title="Start New Scan">
            <CreateScanForm onSuccess={handleScanCreated} className="p-1" />
          </Card>
          
          {/* Stats summary */}
          <div className="grid grid-cols-2 gap-4 mt-6">
            <Card title="Active Scans" className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
              <div className="flex items-center justify-center py-4">
                <div className="text-center">
                  {isLoadingActiveScans ? (
                    <div className="flex justify-center">
                      <Loading size="sm" />
                    </div>
                  ) : activeScansError ? (
                    <span className="text-3xl font-bold text-red-600 dark:text-red-400">?</span>
                  ) : (
                    <span className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                      {activeScansData?.count || 0}
                    </span>
                  )}
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Running or queued</p>
                </div>
              </div>
            </Card>
            <Card title="Scan Types" className="bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800">
              <div className="flex items-center justify-center py-4">
                <div className="flex flex-col items-center">
                  <div className="flex space-x-2">
                    <ClipboardDocumentCheckIcon className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                    <ChartBarIcon className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Audit & Policy</p>
                </div>
              </div>
            </Card>
          </div>
        </div>
        
        {/* Right column - Tabs, active scans and selected scan output */}
        <div className="lg:col-span-2 space-y-6">
          {/* Tabs for different scan views */}
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('active')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'active' 
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'}`}
              >
                Active Scans
                {activeScansData && activeScansData.count > 0 && (
                  <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    {activeScansData?.count ?? 0}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveTab('all')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'all' 
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'}`}
              >
                All Scans
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'history' 
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'}`}
              >
                History
              </button>
            </nav>
          </div>
          
          {/* Tab content */}
          <div className="mt-4">
            {activeTab === 'active' && (
              <ScanList 
                title="" 
                activeOnly={true} 
                limit={10}
                onScanSelect={handleScanSelect}
                onRefresh={() => {
                  queryClient.invalidateQueries('cliScans');
                  queryClient.invalidateQueries('activeScans');
                  queryClient.invalidateQueries('activeScansCount');
                }}
              />
            )}
            
            {activeTab === 'all' && (
              <ScanList 
                title="" 
                onScanSelect={handleScanSelect}
                enableFiltering={true}
                enablePagination={true}
                onRefresh={() => {
                  queryClient.invalidateQueries('cliScans');
                }}
              />
            )}
            
            {activeTab === 'history' && (
              <ScanList 
                title="" 
                status="completed,failed" // Pre-filter for history, but user can change
                onScanSelect={handleScanSelect}
                enableFiltering={true}
                enablePagination={true}
                onRefresh={() => {
                  queryClient.invalidateQueries('cliScans');
                }}
              />
            )}
          </div>
          
          {/* Selected scan output */}
          {selectedScanId && (
            <div className="mt-6">
              {isLoadingScan ? (
                <Card title="Loading Scan Details">
                  <div className="flex justify-center items-center py-8">
                    <Loading size="lg" />
                  </div>
                </Card>
              ) : scanError ? (
                <Card title="Error Loading Scan">
                  <div className="p-4 text-red-600 dark:text-red-400">
                    <ErrorDisplay error={scanError} />
                  </div>
                </Card>
              ) : (
                <ScanOutput 
                  scanId={selectedScanId} 
                  autoRefresh={selectedScan?.status === 'running' || selectedScan?.status === 'queued'}
                />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
