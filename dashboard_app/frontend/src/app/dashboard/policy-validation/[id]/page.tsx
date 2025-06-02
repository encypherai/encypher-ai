'use client';

import React from 'react';
import { useQuery } from 'react-query';
import { useRouter } from 'next/navigation';
import { 
  ArrowLeftIcon,
  ClockIcon,
  DocumentIcon,
  BuildingOfficeIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { policyValidationService, ValidationResult, PolicySchema } from '@/lib/services/policy-validation';
import { useNotifications } from '@/lib/notifications';
import { ExclamationTriangleIcon as SolidExclamationTriangleIcon } from '@heroicons/react/24/solid';

interface PolicyValidationDetailsProps {
  params: {
    id: string;
  };
}

export default function PolicyValidationDetailsPage({ params }: PolicyValidationDetailsProps) {
  const router = useRouter();
  const { addNotification } = useNotifications();
  const { id } = params;
  
  // Fetch validation result details
  const {
    data: validationResult,
    isLoading: isLoadingResult,
    error: resultError,
    isError: isResultError,
    refetch: refetchResult,
  } = useQuery<ValidationResult, Error>(
    ['validationResult', id],
    () => policyValidationService.getValidationResult(parseInt(id, 10)),
    {
      staleTime: 300000, // 5 minutes
      onError: (err) => {
        addNotification({
          type: 'error',
          title: 'Failed to fetch validation result',
          message: err.message || 'An unexpected error occurred.',
        });
      },
    }
  );

  // Fetch policy schema details if we have the validation result
  const {
    data: policySchema,
    isLoading: isLoadingSchema,
    error: schemaError,
    isError: isSchemaError,
    refetch: refetchSchema,
  } = useQuery<PolicySchema, Error>(
    ['policySchema', validationResult?.policy_schema_id],
    () => policyValidationService.getPolicySchema(validationResult!.policy_schema_id),
    {
      enabled: !!validationResult?.policy_schema_id,
      staleTime: 300000, // 5 minutes
      onError: (err) => {
        addNotification({
          type: 'error',
          title: 'Failed to fetch policy schema',
          message: err.message || 'An unexpected error occurred while fetching schema details.',
        });
      },
    }
  );

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      second: 'numeric',
      timeZoneName: 'short',
    }).format(date);
  };

  const formatJson = (jsonString: string) => {
    try {
      const parsed = JSON.parse(jsonString);
      return JSON.stringify(parsed, null, 2);
    } catch (e) {
      return jsonString;
    }
  };

  const isLoading = isLoadingResult || isLoadingSchema;

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (isResultError) {
    return (
      <div className="text-center py-10">
        <SolidExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-red-600 dark:text-red-400">Error loading validation result</h2>
        <p className="text-gray-500 dark:text-gray-400 mt-2 mb-4">
          {(resultError as Error)?.message || 'Could not load the requested validation result.'}
        </p>
        <Button 
          onClick={() => refetchResult()} 
          variant="outline" 
          className="mr-2"
        >
          Retry
        </Button>
        <Button
          variant="primary"
          className="mt-4"
          onClick={() => router.push('/dashboard/policy-validation')}
        >
          Back to Policy Validation
        </Button>
      </div>
    );
  }

  // Handle case where data is not available after loading and no error state
  if (!validationResult) {
    return (
      <div className="text-center py-10">
        <SolidExclamationTriangleIcon className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-yellow-600 dark:text-yellow-400">Validation Result Not Available</h2>
        <p className="text-gray-500 dark:text-gray-400 mt-2 mb-4">
          The requested validation result could not be found or is still loading. Please try again or go back.
        </p>
        <Button 
          onClick={() => refetchResult()} 
          variant="outline" 
          className="mr-2"
        >
          Retry
        </Button>
        <Button
          variant="primary"
          className="mt-4"
          onClick={() => router.push('/dashboard/policy-validation')}
        >
          Back to Policy Validation
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/dashboard/policy-validation')}
          className="mr-4"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          Back to Policy Validation
        </Button>
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Validation Result Details</h1>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info Card */}
        <div className="lg:col-span-2">
          <Card>
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-xl font-medium text-gray-900 dark:text-white">
                  {isSchemaError && <span className='text-red-500 text-sm'>(Error loading schema name)</span>}
                  {!isSchemaError && policySchema ? `${policySchema.name} (v${policySchema.version})` : 
                    !isSchemaError && !policySchema && !isLoadingSchema ? `Schema ID: ${validationResult.policy_schema_id} (Not found)` : 
                    isLoadingSchema ? 'Loading schema...' : `Schema ID: ${validationResult.policy_schema_id}`}
                </h2>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {validationResult.resource_type} - {validationResult.resource_id}
                </p>
              </div>
              <div className="flex items-center">
                {validationResult.is_valid ? (
                  <CheckCircleIcon className="h-6 w-6 text-green-500 mr-2" />
                ) : (
                  <ExclamationCircleIcon className="h-6 w-6 text-red-500 mr-2" />
                )}
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  validationResult.is_valid ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                }`}>
                  {validationResult.is_valid ? 'Valid' : 'Invalid'}
                </span>
              </div>
            </div>
            
            <div className="mt-6 space-y-4">
              <div className="flex items-start">
                <ClockIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Timestamp</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{formatDate(validationResult.timestamp)}</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <DocumentIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Resource</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Type: {validationResult.resource_type}<br />
                    ID: {validationResult.resource_id}
                  </p>
                </div>
              </div>
              
              <div className="flex items-start">
                <BuildingOfficeIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Department</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{validationResult.department}</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <DocumentIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Source Type</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{validationResult.source_type}</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
        
        {/* Details Card */}
        <div className="lg:col-span-1">
          <Card title="Validation Details">
            <div className="bg-gray-50 dark:bg-gray-800 rounded-md p-4">
              <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200 font-mono overflow-auto max-h-96">
                {formatJson(validationResult.validation_details)}
              </pre>
            </div>
          </Card>
          
          {/* Policy Schema Card */}
          {policySchema && (
            <Card title="Policy Schema" className="mt-6">
              <div className="space-y-2">
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Name</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{policySchema.name}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Version</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{policySchema.version}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Description</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{policySchema.description}</p>
                </div>
                {/* TODO: Add display for full schema content if available/required from a different endpoint or property */}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
