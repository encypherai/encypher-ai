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
                <h2 className="text-xl font-medium text-gray-900 dark:text-white">{auditLog.action}</h2>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {auditLog.resource_type} - {auditLog.resource_id}
                </p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                auditLog.success ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
              }`}>
                {auditLog.success ? 'Success' : 'Failed'}
              </span>
            </div>
            
            <div className="mt-6 space-y-4">
              <div className="flex items-start">
                <ClockIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Timestamp</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{formatDate(auditLog.timestamp)}</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <UserIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">User ID</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{auditLog.user_id}</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <DocumentIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Resource</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Type: {auditLog.resource_type}<br />
                    ID: {auditLog.resource_id}
                  </p>
                </div>
              </div>
              
              <div className="flex items-start">
                <ServerIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Source IP</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{auditLog.source_ip}</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <BuildingOfficeIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Department</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{auditLog.department}</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
        
        {/* Details Card */}
        <div className="lg:col-span-1">
          <Card title="Details">
            <div className="bg-gray-50 dark:bg-gray-800 rounded-md p-4">
              <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200 font-mono overflow-auto max-h-96">
                {formatJson(auditLog.details)}
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
