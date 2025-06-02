'use client';

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useRouter } from 'next/navigation';
import { 
  ArrowPathIcon, 
  StopIcon, 
  EyeIcon,
  DocumentArrowDownIcon,
  FunnelIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import Table from '@/components/ui/Table';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import Modal from '@/components/ui/Modal';
import { useNotifications } from '@/lib/notifications';
import cliService, { CliScan } from '@/services/cliService';

// Define the interface for the ScanList component props
interface ScanListProps {
  title?: string;
  activeOnly?: boolean;
  limit?: number;
  showAllLink?: boolean;
  className?: string;
  onScanSelect?: (scanId: number) => void;
  status?: string;
  onRefresh?: () => void;
  enableFiltering?: boolean;
  enablePagination?: boolean;
}

// Define interface for CLI scan response with pagination
interface CliScanResponse {
  items: CliScan[];
  total: number;
  page: number;
  limit: number;
}

export default function ScanList({ 
  title = 'CLI Scans', 
  activeOnly = false, 
  limit, 
  showAllLink = true,
  className = '',
  onScanSelect,
  status,
  onRefresh,
  enableFiltering = false,
  enablePagination = false
}: ScanListProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { addNotification } = useNotifications();
  const [stopScanId, setStopScanId] = useState<number | null>(null);
  const [isStopModalOpen, setIsStopModalOpen] = useState(false);
  const [isStoppingMap, setIsStoppingMap] = useState<Record<number, boolean>>({});
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  
  // Filter states
  const [filterType, setFilterType] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>(status || '');
  const [filterApplied, setFilterApplied] = useState(false);

  // Reset to first page when filters change
  useEffect(() => {
    if (filterApplied) {
      setCurrentPage(1);
    }
  }, [filterType, filterStatus, filterApplied]);

  // Query to fetch scans
  const { 
    data, 
    isLoading, 
    isError, 
    error, 
    refetch,
    isRefetching
  } = useQuery<CliScanResponse, Error>(
    activeOnly 
      ? 'activeScans' 
      : filterApplied 
        ? `cliScans-filtered-${filterType}-${filterStatus}-${currentPage}` 
        : status 
          ? `cliScans-${status}-${currentPage}` 
          : `cliScans-${currentPage}`,
    () => {
      const filters: Record<string, any> = {
        page: currentPage,
        limit: enablePagination ? itemsPerPage : undefined
      };
      
      if (activeOnly) {
        return cliService.getActiveScans();
      } else {
        if (status && !filterApplied) {
          filters.status = status;
        }
        
        if (filterApplied) {
          if (filterType) filters.scan_type = filterType;
          if (filterStatus) filters.status = filterStatus;
        }
        
        return cliService.getScans(filters);
      }
    },
    {
      refetchInterval: activeOnly ? 5000 : false, // Poll active scans every 5 seconds
      staleTime: 30000, // Consider data fresh for 30 seconds
      onError: (err: Error) => {
        addNotification({
          type: 'error',
          title: 'Error fetching scans',
          message: err.message || 'An unexpected error occurred',
        });
      }
    }
  );

  // Mutation to stop a scan
  const stopScanMutation = useMutation(
    (scanId: number) => cliService.stopScan(scanId),
    {
      onSuccess: () => {
        addNotification({
          type: 'success',
          title: 'Scan stopped',
          message: 'The CLI scan has been stopped successfully.',
        });
        queryClient.invalidateQueries('cliScans');
        queryClient.invalidateQueries('activeScans');
        setIsStopModalOpen(false);
        setIsStoppingMap(prev => ({
          ...prev,
          [stopScanId as number]: false
        }));
      },
      onError: (err: Error) => {
        addNotification({
          type: 'error',
          title: 'Failed to stop scan',
          message: err.message || 'An unexpected error occurred',
        });
        setIsStoppingMap(prev => ({
          ...prev,
          [stopScanId as number]: false
        }));
      }
    }
  );

  // Handle view scan details
  const handleViewScan = (scan: CliScan) => {
    if (onScanSelect) {
      onScanSelect(scan.id);
    } else {
      router.push(`/dashboard/cli-integration/${scan.id}`);
    }
  };

  // Handle stop scan
  const handleStopScan = (scanId: number) => {
    setStopScanId(scanId);
    setIsStoppingMap(prev => ({
      ...prev,
      [scanId]: true
    }));
    setIsStopModalOpen(true);
  };

  // Confirm stop scan
  const confirmStopScan = () => {
    if (stopScanId !== null) {
      stopScanMutation.mutate(stopScanId);
    }
  };

  // Format date for display
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  // Table columns definition with proper typing
  const columns: Array<{
    header: string;
    accessor: keyof CliScan | ((item: CliScan) => React.ReactNode);
    className?: string;
  }> = [
    {
      header: 'ID',
      accessor: 'id' as const,
      className: 'w-16',
    },
    {
      header: 'Type',
      accessor: (scan: CliScan) => (
        <span className="capitalize">
          {scan.scan_type.replace('_', ' ')}
        </span>
      ),
    },
    {
      header: 'Status',
      accessor: (scan: CliScan) => {
        const getStatusBadgeClass = (status: string) => {
          switch (status.toLowerCase()) {
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
        
        return (
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(scan.status)}`}>
            {scan.status.charAt(0).toUpperCase() + scan.status.slice(1).toLowerCase()}
          </span>
        );
      },
    },
    {
      header: 'Started',
      accessor: (scan: CliScan) => formatDate(scan.started_at),
    },
    {
      header: 'Completed',
      accessor: (scan: CliScan) => formatDate(scan.completed_at),
    },
    {
      header: 'Actions',
      accessor: (scan: CliScan) => (
        <div className="flex space-x-2">
          <Button
            variant="ghost"
            size="xs"
            onClick={(e: React.MouseEvent) => {
              e.stopPropagation();
              handleViewScan(scan);
            }}
            title="View Details"
          >
            <EyeIcon className="h-4 w-4" />
          </Button>
          
          {scan.status.toLowerCase() === 'running' && (
            <Button
              variant="ghost"
              size="xs"
              onClick={(e: React.MouseEvent) => {
                e.stopPropagation();
                handleStopScan(scan.id);
              }}
              title="Stop Scan"
              disabled={isStoppingMap[scan.id]}
            >
              <StopIcon className="h-4 w-4 text-red-500" />
            </Button>
          )}
          
          {scan.status.toLowerCase() === 'completed' && (
            <Button
              variant="ghost"
              size="xs"
              onClick={(e: React.MouseEvent) => {
                e.stopPropagation();
                // In a real app, this would download the scan results
                addNotification({
                  type: 'info',
                  title: 'Download Not Available',
                  message: 'Download functionality is not available in this version.',
                });
              }}
              title="Download Results"
            >
              <DocumentArrowDownIcon className="h-4 w-4" />
            </Button>
          )}
        </div>
      ),
      className: 'text-right',
    },
  ];

  // Process scan data from response
  const scans = data?.items || [];
  const totalItems = data?.total || 0;
  const totalPages = enablePagination ? Math.ceil(totalItems / itemsPerPage) : 1;
  
  // Filter and limit scans if needed
  const displayScans = !enablePagination && limit ? scans.slice(0, limit) : scans;
  
  // Handle page change
  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };
  
  // Apply filters
  const applyFilters = () => {
    setFilterApplied(true);
    refetch();
    setIsFilterOpen(false);
  };
  
  // Clear filters
  const clearFilters = () => {
    setFilterType('');
    setFilterStatus(status || '');
    setFilterApplied(false);
    refetch();
  };

  return (
    <>
      <Card 
        title={
          <div className="flex justify-between items-center">
            <span>{title}</span>
            <div className="flex items-center space-x-2">
              {activeOnly && !isLoading && !isRefetching && (
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  Auto-refreshing
                </span>
              )}
              {enableFiltering && (
                <Button
                  variant="ghost"
                  size="xs"
                  onClick={() => setIsFilterOpen(!isFilterOpen)}
                  title="Filter"
                  className={filterApplied ? 'text-blue-600 dark:text-blue-400' : ''}
                >
                  <FunnelIcon className="h-4 w-4" />
                </Button>
              )}
              <Button
                variant="ghost"
                size="xs"
                onClick={() => {
                  refetch();
                  if (onRefresh) onRefresh();
                }}
                isLoading={isRefetching}
                title="Refresh"
              >
                <ArrowPathIcon className="h-4 w-4" />
              </Button>
            </div>
          </div>
        } 
        className={className}
      >
        {/* Filter panel */}
        {enableFiltering && isFilterOpen && (
          <div className="border-b border-gray-200 dark:border-gray-700 p-4 mb-4">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-sm font-medium">Filter Scans</h3>
              <Button
                variant="ghost"
                size="xs"
                onClick={() => setIsFilterOpen(false)}
                title="Close Filters"
              >
                <XMarkIcon className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Scan Type
                </label>
                <select
                  className="w-full rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm"
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                >
                  <option value="">All Types</option>
                  <option value="audit_log">Audit Log</option>
                  <option value="policy_validation">Policy Validation</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Status
                </label>
                <select
                  className="w-full rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm"
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <option value="">All Statuses</option>
                  <option value="running">Running</option>
                  <option value="queued">Queued</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3">
              <Button
                variant="secondary"
                size="sm"
                onClick={clearFilters}
                disabled={!filterApplied}
              >
                Clear Filters
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={applyFilters}
              >
                Apply Filters
              </Button>
            </div>
          </div>
        )}
        
        {isError ? (
          <div className="p-6 text-center">
            <div className="text-red-500 mb-2">
              {error?.message || 'An error occurred while fetching scans'}
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => {
                refetch();
                if (onRefresh) onRefresh();
              }}
              isLoading={isRefetching}
            >
              Try Again
            </Button>
          </div>
        ) : (
          <Table
            columns={columns}
            data={displayScans}
            keyExtractor={(scan: CliScan) => scan.id}
            isLoading={isLoading}
            emptyMessage={
              <div className="py-8 text-center">
                <p className="text-gray-500 dark:text-gray-400 mb-4">No scans found</p>
                {!activeOnly && (
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => router.push('/dashboard/cli-integration/new')}
                  >
                    Create New Scan
                  </Button>
                )}
              </div>
            }
            onRowClick={handleViewScan}
          />
        )}
        
        {/* Pagination controls */}
        {enablePagination && totalPages > 1 && (
          <div className="mt-4 flex items-center justify-between border-t border-gray-200 dark:border-gray-700 px-4 py-3 sm:px-6">
            <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  Showing <span className="font-medium">{((currentPage - 1) * itemsPerPage) + 1}</span> to{' '}
                  <span className="font-medium">
                    {Math.min(currentPage * itemsPerPage, totalItems)}
                  </span>{' '}
                  of <span className="font-medium">{totalItems}</span> results
                </p>
              </div>
              <div>
                <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="relative inline-flex items-center rounded-l-md px-2 py-2"
                  >
                    <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
                  </Button>
                  
                  {/* Page numbers */}
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    // Show pages around current page
                    let pageNum;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (currentPage <= 3) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = currentPage - 2 + i;
                    }
                    
                    return (
                      <Button
                        key={pageNum}
                        variant={currentPage === pageNum ? 'primary' : 'ghost'}
                        size="sm"
                        onClick={() => handlePageChange(pageNum)}
                        className="relative inline-flex items-center px-4 py-2"
                      >
                        {pageNum}
                      </Button>
                    );
                  })}
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="relative inline-flex items-center rounded-r-md px-2 py-2"
                  >
                    <ChevronRightIcon className="h-5 w-5" aria-hidden="true" />
                  </Button>
                </nav>
              </div>
            </div>
          </div>
        )}
        
        {showAllLink && !enablePagination && limit && scans.length > limit && (
          <div className="mt-4 text-right">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push('/dashboard/cli-integration')}
            >
              View All Scans
            </Button>
          </div>
        )}
      </Card>
      
      {/* Stop Scan Confirmation Modal */}
      <Modal
        isOpen={isStopModalOpen}
        onClose={() => setIsStopModalOpen(false)}
        title="Stop Scan"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Are you sure you want to stop this scan? This action cannot be undone.
          </p>
          
          <div className="flex justify-end space-x-3">
            <Button
              variant="secondary"
              onClick={() => setIsStopModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={confirmStopScan}
              isLoading={stopScanMutation.isLoading}
            >
              Stop Scan
            </Button>
          </div>
        </div>
      </Modal>
    </>
  );
}