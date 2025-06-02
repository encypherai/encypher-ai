'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { useNotifications } from '@/lib/notifications';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Loading from '@/components/ui/Loading';
import ErrorDisplay from '@/components/ui/ErrorDisplay';
import { 
  UserIcon, 
  BuildingOfficeIcon, 
  EnvelopeIcon, 
  ClockIcon,
  DocumentTextIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

interface ActivityLog {
  id: number;
  action: string;
  timestamp: string;
  details: string;
}

export default function ProfilePage() {
  const { user, isLoading: authLoading } = useAuth();
  const { addNotification } = useNotifications();
  
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    // Simulate fetching user activity logs
    const fetchActivityLogs = async () => {
      try {
        // This would be an API call in a real application
        // For now, we'll use mock data
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const mockLogs: ActivityLog[] = [
          {
            id: 1,
            action: 'Login',
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            details: 'Successful login from Chrome on Windows'
          },
          {
            id: 2,
            action: 'Audit Log Export',
            timestamp: new Date(Date.now() - 86400000).toISOString(),
            details: 'Exported 150 audit log entries to CSV'
          },
          {
            id: 3,
            action: 'Password Changed',
            timestamp: new Date(Date.now() - 604800000).toISOString(),
            details: 'Password updated successfully'
          },
          {
            id: 4,
            action: 'CLI Scan Initiated',
            timestamp: new Date(Date.now() - 1209600000).toISOString(),
            details: 'Started policy validation scan on project X'
          },
          {
            id: 5,
            action: 'Profile Updated',
            timestamp: new Date(Date.now() - 2592000000).toISOString(),
            details: 'Updated profile information'
          }
        ];
        
        setActivityLogs(mockLogs);
        setIsLoading(false);
      } catch (error: any) {
        setError(error.message || 'Failed to fetch activity logs');
        setIsLoading(false);
      }
    };
    
    if (user) {
      fetchActivityLogs();
    }
  }, [user]);
  
  if (authLoading) {
    return <Loading text="Loading profile..." />;
  }
  
  if (!user) {
    return <ErrorDisplay message="User not found. Please login again." />;
  }
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      hour12: true
    }).format(date);
  };
  
  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSec = Math.round(diffMs / 1000);
    const diffMin = Math.round(diffSec / 60);
    const diffHour = Math.round(diffMin / 60);
    const diffDay = Math.round(diffHour / 24);
    
    if (diffSec < 60) {
      return `${diffSec} second${diffSec !== 1 ? 's' : ''} ago`;
    } else if (diffMin < 60) {
      return `${diffMin} minute${diffMin !== 1 ? 's' : ''} ago`;
    } else if (diffHour < 24) {
      return `${diffHour} hour${diffHour !== 1 ? 's' : ''} ago`;
    } else if (diffDay < 30) {
      return `${diffDay} day${diffDay !== 1 ? 's' : ''} ago`;
    } else {
      return formatDate(dateString);
    }
  };
  
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">User Profile</h1>
      
      {/* User Profile Card */}
      <Card>
        <div className="flex flex-col md:flex-row items-start md:items-center space-y-4 md:space-y-0 md:space-x-6">
          <div className="bg-primary-100 dark:bg-primary-900 rounded-full p-6">
            <UserIcon className="h-12 w-12 text-primary-600 dark:text-primary-400" />
          </div>
          
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">{user.name || 'User'}</h2>
            
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <EnvelopeIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
                <span className="text-gray-700 dark:text-gray-300">{user.email || 'No email set'}</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <BuildingOfficeIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
                <span className="text-gray-700 dark:text-gray-300">{user.department || 'No department set'}</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <ClockIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
                <span className="text-gray-700 dark:text-gray-300">
                  Member since {user.createdAt ? formatDate(user.createdAt) : 'N/A'}
                </span>
              </div>
              
              <div className="flex items-center space-x-2">
                <ShieldCheckIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
                <span className="text-gray-700 dark:text-gray-300">
                  Role: {user.role || 'User'}
                </span>
              </div>
            </div>
            
            <div className="mt-6">
              <Button
                variant="primary"
                onClick={() => window.location.href = '/dashboard/settings'}
              >
                Edit Profile
              </Button>
            </div>
          </div>
        </div>
      </Card>
      
      {/* Recent Activity Card */}
      <Card title="Recent Activity">
        {isLoading ? (
          <Loading text="Loading activity..." />
        ) : error ? (
          <ErrorDisplay message={error} />
        ) : (
          <div className="space-y-4">
            {activityLogs.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-4">No recent activity found.</p>
            ) : (
              <div className="flow-root">
                <ul className="-mb-8">
                  {activityLogs.map((log, index) => (
                    <li key={log.id}>
                      <div className="relative pb-8">
                        {index !== activityLogs.length - 1 && (
                          <span
                            className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200 dark:bg-gray-700"
                            aria-hidden="true"
                          />
                        )}
                        <div className="relative flex space-x-3">
                          <div>
                            <span className="h-8 w-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center ring-8 ring-white dark:ring-gray-900">
                              <DocumentTextIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
                            </span>
                          </div>
                          <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                            <div>
                              <p className="text-sm text-gray-800 dark:text-gray-200">
                                <span className="font-medium">{log.action}</span>
                              </p>
                              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{log.details}</p>
                            </div>
                            <div className="text-right text-sm whitespace-nowrap text-gray-500 dark:text-gray-400">
                              <time dateTime={log.timestamp} title={formatDate(log.timestamp)}>
                                {getTimeAgo(log.timestamp)}
                              </time>
                            </div>
                          </div>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            <div className="flex justify-end mt-4">
              <Button variant="ghost" size="sm">
                View All Activity
              </Button>
            </div>
          </div>
        )}
      </Card>
      
      {/* Usage Statistics Card */}
      <Card title="Usage Statistics">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Audit Logs Viewed</h3>
            <p className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">247</p>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Last 30 days</p>
          </div>
          
          <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Policy Validations</h3>
            <p className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">32</p>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Last 30 days</p>
          </div>
          
          <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">CLI Scans Initiated</h3>
            <p className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">18</p>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Last 30 days</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
