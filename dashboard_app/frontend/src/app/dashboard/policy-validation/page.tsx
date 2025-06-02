'use client';

import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { useRouter } from 'next/navigation';
import { 
  ArrowDownTrayIcon,
  FunnelIcon,
  XMarkIcon,
  PlusIcon,
  ArrowUpTrayIcon,
} from '@heroicons/react/24/outline';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Table from '@/components/ui/Table';
import Pagination from '@/components/ui/Pagination';
import { policyValidationService, ValidationResult, ValidationFilters, PolicySchema } from '@/lib/services/policy-validation';
import { useNotifications } from '@/lib/notifications';
import { ExclamationTriangleIcon } from '@heroicons/react/24/solid';

export default function PolicyValidationPage() {
  const router = useRouter();
  const { addNotification } = useNotifications();
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [filters, setFilters] = useState<ValidationFilters>({
    start_date: '',
    end_date: '',
    policy_schema_id: undefined,
    is_valid: undefined,
    department: '',
    source_type: '',
  });
  const [showFilters, setShowFilters] = useState(false);
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [isImporting, setIsImporting] = useState(false);

  // Fetch policy schemas for filter dropdown
  const { data: schemas, error: schemasError, isError: isSchemasError } = useQuery<PolicySchema[], Error>(
    'policySchemas',
    () => policyValidationService.getPolicySchemas(),
    {
      staleTime: 300000, // 5 minutes
      onError: (err) => {
        addNotification({
          type: 'error',
          title: 'Failed to fetch policy schemas',
          message: err.message || 'An unexpected error occurred while fetching schemas.',
        });
      },
    }
  );

  // Fetch validation results with pagination and filters
  const { 
    data, 
    isLoading, 
    isError,
    error,
    refetch 
  } = useQuery<{
    items: ValidationResult[];
    total: number;
    page: number;
    limit: number;
  }, Error>(
    ['validationResults', page, limit, filters],
    () => policyValidationService.getValidationResults({
      ...filters,
      page,
      limit,
    }),
    {
      keepPreviousData: true,
      onError: (err) => {
        addNotification({
          type: 'error',
          title: 'Failed to fetch validation results',
          message: err.message || 'An unexpected error occurred.',
        });
      },
    }
  );

  const handleFilterChange = (name: keyof ValidationFilters, value: string | number | boolean | undefined) => {
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
      policy_schema_id: undefined,
      is_valid: undefined,
      department: '',
      source_type: '',
    });
    setPage(1);
  };

  const handleViewDetails = (validationResult: ValidationResult) => {
    router.push(`/dashboard/policy-validation/${validationResult.id}`);
  };

  const handleImportCsv = async () => {
    if (!importFile) return;
    
    try {
      setIsImporting(true);
      await policyValidationService.importValidationCsv(importFile);
      addNotification({
        type: 'success',
        title: 'Import Successful',
        message: 'Validation results imported successfully.',
      });
      setIsImportModalOpen(false);
      setImportFile(null);
      refetch();
    } catch (error: any) {
      console.error('Error importing CSV:', error);
      addNotification({
        type: 'error',
        title: 'Import Failed',
        message: error.message || 'An unexpected error occurred during CSV import.',
      });
    } finally {
      setIsImporting(false);
    }
  };

  const exportToCsv = async () => {
    try {
      // This would typically call an API endpoint that returns a CSV file
      // For now, we'll just create a CSV from the current data
      if (!data?.items) return;
      
      const headers = [
        'ID',
        'Policy Schema ID',
        'Timestamp',
        'Resource ID',
        'Resource Type',
        'Is Valid',
        'Validation Details',
        'Department',
        'Source Type',
      ];
      
      const csvContent = [
        headers.join(','),
        ...data.items.map((result) => [
          result.id,
          result.policy_schema_id,
          result.timestamp,
          result.resource_id,
          result.resource_type,
          result.is_valid,
          `"${result.validation_details.replace(/"/g, '""')}"`, // Escape quotes
          result.department,
          result.source_type,
        ].join(',')),
      ].join('\n');
      
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `policy-validation-${new Date().toISOString().split('T')[0]}.csv`);
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
    { 
      header: 'Policy Schema', 
      accessor: (item: ValidationResult) => {
        const schema = schemas?.find((s: PolicySchema) => s.id === item.policy_schema_id);
        return schema ? `${schema.name} (v${schema.version})` : `Schema ID: ${item.policy_schema_id}`;
      } 
    },
    { header: 'Resource Type', accessor: 'resource_type' },
    { header: 'Resource ID', accessor: 'resource_id', className: 'max-w-xs truncate' },
    { 
      header: 'Status', 
      accessor: (item: ValidationResult) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          item.is_valid ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
        }`}>
          {item.is_valid ? 'Valid' : 'Invalid'}
        </span>
      ) 
    },
    { header: 'Department', accessor: 'department' },
    { header: 'Source Type', accessor: 'source_type' },
  ] as const;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Policy Validation</h1>
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
            variant="secondary"
            size="sm"
            onClick={() => setIsImportModalOpen(true)}
          >
            <ArrowUpTrayIcon className="h-4 w-4 mr-1" />
            Import CSV
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={exportToCsv}
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
            Export CSV
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => router.push('/dashboard/policy-validation/schemas/new')}
          >
            <PlusIcon className="h-4 w-4 mr-1" />
            New Schema
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
            <Select
              label="Policy Schema"
              options={[
                { value: '', label: 'All Schemas' },
                ...(schemas || []).map((schema: PolicySchema) => ({
                  value: schema.id.toString(),
                  label: `${schema.name} (v${schema.version})`,
                })),
              ]}
              value={filters.policy_schema_id?.toString() || ''}
              onChange={(value) => handleFilterChange('policy_schema_id', value ? parseInt(value, 10) : undefined)}
            />
            <Select
              label="Validation Status"
              options={[
                { value: '', label: 'All' },
                { value: 'true', label: 'Valid' },
                { value: 'false', label: 'Invalid' },
              ]}
              value={filters.is_valid === undefined ? '' : String(filters.is_valid)}
              onChange={(value) => {
                if (value === '') {
                  handleFilterChange('is_valid', undefined);
                } else {
                  handleFilterChange('is_valid', value === 'true');
                }
              }}
            />
            <Input
              label="Department"
              value={filters.department || ''}
              onChange={(e) => handleFilterChange('department', e.target.value)}
            />
            <Input
              label="Source Type"
              value={filters.source_type || ''}
              onChange={(e) => handleFilterChange('source_type', e.target.value)}
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
      
      {/* Import CSV Modal */}
      {isImportModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true">
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            <div className="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="sm:flex sm:items-start">
                  <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                    <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                      Import Validation Results
                    </h3>
                    <div className="mt-2">
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Upload a CSV file with validation results. The file should have headers matching the API schema.
                      </p>
                      <div className="mt-4">
                        <Input
                          type="file"
                          accept=".csv"
                          onChange={(e) => {
                            const files = e.target.files;
                            if (files && files.length > 0) {
                              setImportFile(files[0]);
                            }
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  variant="primary"
                  onClick={handleImportCsv}
                  isLoading={isImporting}
                  disabled={!importFile || isImporting}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  Import
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => {
                    setIsImportModalOpen(false);
                    setImportFile(null);
                  }}
                  disabled={isImporting}
                  className="mt-3 w-full sm:mt-0 sm:w-auto"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Validation Results Table */}
      <Card>
        {isError ? (
          <div className="p-4 text-center">
            <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-2" />
            <p className="text-red-600 dark:text-red-400 mb-1">Failed to load validation results.</p>
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
          emptyMessage="No validation results found"
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
