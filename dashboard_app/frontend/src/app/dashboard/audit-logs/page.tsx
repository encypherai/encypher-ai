'use client';

import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { useRouter } from 'next/navigation';
import { 
  ArrowDownTrayIcon,
  FunnelIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Table from '@/components/ui/Table';
import Pagination from '@/components/ui/Pagination';
import { auditLogService, AuditLog, AuditLogFilters } from '@/lib/services/audit-logs';
import { useNotifications } from '@/lib/notifications';
import { ExclamationTriangleIcon } from '@heroicons/react/24/solid';

export default function AuditLogsPage() {
  const router = useRouter();
  const { addNotification } = useNotifications();
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [filters, setFilters] = useState<AuditLogFilters>({
    start_date: '',
    end_date: '',
    user_id: '',
    action: '',
    resource_type: '',
    success: undefined,
    department: '',
  });
  const [showFilters, setShowFilters] = useState(false);

  // Fetch audit logs with pagination and filters
  const { 
    data, 
    isLoading, 
    isError,
    error,
    refetch 
  } = useQuery<{
    items: AuditLog[];
    total: number;
    page: number;
    limit: number;
  }, Error>(
    ['auditLogs', page, limit, filters],
    () => auditLogService.getAuditLogs({
      ...filters,
      page,
      limit,
    }),
    {
      keepPreviousData: true,
      onError: (err) => {
        addNotification({
          type: 'error',
          title: 'Failed to fetch audit logs',
          message: err.message || 'An unexpected error occurred.',
        });
      },
    }
  );

  const handleFilterChange = (name: keyof AuditLogFilters, value: string | boolean | undefined) => {
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
    setPage(1); // Reset to first page when filters change
  };

  const clearFilters = () => {
    setFilters({
      start_date: '',
      end_date: '',
      user_id: '',
      action: '',
      resource_type: '',
      success: undefined,
      department: '',
    });
    setPage(1);
  };

  const handleViewDetails = (auditLog: AuditLog) => {
    router.push(`/dashboard/audit-logs/${auditLog.id}`);
  };

  const exportToCsv = async () => {
    try {
      // This would typically call an API endpoint that returns a CSV file
      // For now, we'll just create a CSV from the current data
      if (!data?.items) return;
      
      const headers = [
        'ID',
        'Timestamp',
        'User ID',
        'Action',
        'Resource Type',
        'Resource ID',
        'Details',
        'Source IP',
        'Success',
        'Department',
      ];
      
      const csvContent = [
        headers.join(','),
        ...data.items.map((log) => [
          log.id,
          log.timestamp,
          log.user_id,
          log.action,
          log.resource_type,
          log.resource_id,
          `"${log.details.replace(/"/g, '""')}"`, // Escape quotes
          log.source_ip,
          log.success,
          log.department,
        ].join(',')),
      ].join('\n');
      
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `audit-logs-${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error exporting CSV:', error);
    }
  };

  const columns = [
    { header: 'Timestamp', accessor: 'timestamp' },
    { header: 'User ID', accessor: 'user_id' },
    { header: 'Action', accessor: 'action' },
    { header: 'Resource Type', accessor: 'resource_type' },
    { header: 'Resource ID', accessor: 'resource_id', className: 'max-w-xs truncate' },
    { 
      header: 'Success', 
      accessor: (item: AuditLog) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          item.success ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
        }`}>
          {item.success ? 'Success' : 'Failed'}
        </span>
      ) 
    },
    { header: 'Department', accessor: 'department' },
  ] as const;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Audit Logs</h1>
        <div className="flex space-x-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
          >
            <FunnelIcon className="h-4 w-4 mr-1" />
            {showFilters ? 'Hide Filters' : 'Show Filters'}
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={exportToCsv}
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
            Export CSV
          </Button>
        </div>
      </div>
      
      {/* Filters */}
      {showFilters && (
        <Card className="bg-gray-50 dark:bg-gray-800/50">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white">Filters</h2>
            <Button
              variant="secondary"
              size="sm"
              onClick={clearFilters}
            >
              <XMarkIcon className="h-4 w-4 mr-1" />
              Clear Filters
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Input
              label="Start Date"
              type="date"
              value={filters.start_date}
              onChange={(e) => handleFilterChange('start_date', e.target.value)}
            />
            <Input
              label="End Date"
              type="date"
              value={filters.end_date}
              onChange={(e) => handleFilterChange('end_date', e.target.value)}
            />
            <Input
              label="User ID"
              value={filters.user_id || ''}
              onChange={(e) => handleFilterChange('user_id', e.target.value)}
            />
            <Input
              label="Action"
              value={filters.action || ''}
              onChange={(e) => handleFilterChange('action', e.target.value)}
            />
            <Input
              label="Resource Type"
              value={filters.resource_type || ''}
              onChange={(e) => handleFilterChange('resource_type', e.target.value)}
            />
            <Select
              label="Success"
              options={[
                { value: '', label: 'All' },
                { value: 'true', label: 'Success' },
                { value: 'false', label: 'Failed' },
              ]}
              value={filters.success === undefined ? '' : String(filters.success)}
              onChange={(value) => {
                if (value === '') {
                  handleFilterChange('success', undefined);
                } else {
                  handleFilterChange('success', value === 'true');
                }
              }}
            />
            <Input
              label="Department"
              value={filters.department || ''}
              onChange={(e) => handleFilterChange('department', e.target.value)}
            />
          </div>
          <div className="mt-4 flex justify-end">
            <Button
              variant="primary"
              size="sm"
              onClick={() => refetch()}
            >
              Apply Filters
            </Button>
          </div>
        </Card>
      )}
      
      {/* Audit Logs Table */}
      <Card>
        {isError ? (
          <div className="p-4 text-center">
            <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-2" />
            <p className="text-red-600 dark:text-red-400 mb-1">Failed to load audit logs.</p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">{error?.message}</p>
            <Button onClick={() => refetch()} variant="outline" size="sm">Retry</Button>
          </div>
        ) : (
          <>
            <Table
          columns={[...columns]}
          data={data?.items || []}
          keyExtractor={(item) => item.id}
          isLoading={isLoading}
          emptyMessage="No audit logs found"
          onRowClick={handleViewDetails}
        />
        
        {data && (
          <div className="mt-4">
            <Pagination
              currentPage={page}
              totalPages={Math.ceil((data.total || 0) / limit)}
              onPageChange={setPage}
            />
          </div>
        )}
          </>
        )}
      </Card>
    </div>
  );
}
