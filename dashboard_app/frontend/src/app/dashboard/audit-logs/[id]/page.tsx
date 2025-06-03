'use client';

import React from 'react';
import { useQuery } from 'react-query';
import { useRouter } from 'next/navigation';
import { 
  ArrowLeftIcon,
  ClockIcon,
  UserIcon,
  DocumentIcon,
  ServerIcon,
  BuildingOfficeIcon,
} from '@heroicons/react/24/outline';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { auditLogService, AuditLog } from '@/lib/services/audit-logs';
import { useNotifications } from '@/lib/notifications';
import { ExclamationTriangleIcon } from '@heroicons/react/24/solid';

interface AuditLogDetailsProps {
  params: {
    id: string;
  };
}

export default function AuditLogDetailsPage({ params }: AuditLogDetailsProps) {
  const router = useRouter();
  const { addNotification } = useNotifications();
  const { id } = params;
  
  // Fetch audit log details
  const { 
    data: auditLog, 
    isLoading, 
    error,
    isError,
    refetch 
  } = useQuery<AuditLog, Error>(
    ['auditLog', id],
    () => auditLogService.getAuditLog(parseInt(id, 10)),
    {
      staleTime: 300000, // 5 minutes
      onError: (err) => {
        addNotification({
          type: 'error',
          title: 'Failed to fetch audit log details',
          message: err.message || 'An unexpected error occurred.',
        });
      },
    }
  );

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return 'N/A';
    
    try {
      const date = new Date(dateString);
      
      // Check if date is valid
      if (isNaN(date.getTime())) {
        return 'Invalid date';
      }
      
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric',
        timeZoneName: 'short',
      }).format(date);
    } catch (error) {
      console.error('Date formatting error:', error);
      return 'Error formatting date';
    }
  };

  const formatJson = (jsonString: string) => {
    try {
      const parsed = JSON.parse(jsonString);
      return JSON.stringify(parsed, null, 2);
    } catch (e) {
      return jsonString;
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-center py-10">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-red-600 dark:text-red-400">Error loading audit log</h2>
        <p className="text-gray-500 dark:text-gray-400 mt-2 mb-4">{(error as Error)?.message || 'Could not load the requested audit log.'}</p>
        <Button 
          onClick={() => refetch()} 
          variant="outline" 
          className="mr-2"
        >
          Retry
        </Button>
        <Button
          variant="primary"
          className="mt-4"
          onClick={() => router.push('/dashboard/audit-logs')}
        >
          Back to Audit Logs
        </Button>
      </div>
    );
  }

  // Handle case where data is not available after loading and no error state
  if (!auditLog) {
    return (
      <div className="text-center py-10">
        <ExclamationTriangleIcon className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-yellow-600 dark:text-yellow-400">Audit Log Not Available</h2>
        <p className="text-gray-500 dark:text-gray-400 mt-2 mb-4">
          The requested audit log could not be found or is still loading. Please try again or go back.
        </p>
        <Button 
          onClick={() => refetch()} 
          variant="outline" 
          className="mr-2"
        >
          Retry
        </Button>
        <Button
          variant="primary"
          className="mt-4"
          onClick={() => router.push('/dashboard/audit-logs')}
        >
          Back to Audit Logs
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
          onClick={() => router.push('/dashboard/audit-logs')}
          className="mr-4"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          Back to Audit Logs
        </Button>
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Audit Log Details</h1>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info Card */}
        <div className="lg:col-span-2">
          <Card>
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-xl font-medium text-gray-900 dark:text-white">{auditLog.status}</h2>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {auditLog.source_type || 'N/A'} - {auditLog.source}
                </p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                auditLog.is_verified ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
              }`}>
                {auditLog.is_verified ? 'Success' : 'Failed'}
              </span>
            </div>
            
            <div className="mt-6 space-y-4">
              <div className="flex items-start">
                <ClockIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Verification Time</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{formatDate(auditLog.verification_time)}</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <ClockIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Created At</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{formatDate(auditLog.created_at)}</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <UserIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Model ID</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{auditLog.model_id || 'N/A'}</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <DocumentIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Source</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Type: {auditLog.source_type || 'N/A'}<br />
                    Source: {auditLog.source}
                  </p>
                </div>
              </div>
              
              <div className="flex items-start">
                <BuildingOfficeIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Department</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{auditLog.department || 'N/A'}</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
        
        {/* Details Card */}
        <div className="lg:col-span-1">
          <Card title="Event Data">
            <div className="bg-gray-50 dark:bg-gray-800 rounded-md p-4">
              <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200 font-mono overflow-auto max-h-96">
                {auditLog.event_data ? formatJson(JSON.stringify(auditLog.event_data)) : 'No event data available'}
              </pre>
            </div>
          </Card>
          
          {/* Related Logs Card (placeholder) */}
          <Card title="Related Logs" className="mt-6">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No related logs found for this action.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
