'use client';

import React from 'react';
import { useAuth } from '@/lib/auth';
import { useCurrentUser, useUpdateUser } from '@/lib/hooks/useUser';
import { useActivityLogs } from '@/lib/hooks/useActivityLogs';
import { useNotifications } from '@/lib/notifications';
import ProfileForm from './ProfileForm';
import ProfileFormSkeleton from './ProfileFormSkeleton';
import ActivityLogList from './ActivityLogList';
import UsageStats from './UsageStats';
import Card from '@/components/ui/Card';
import ErrorDisplay from '@/components/ui/ErrorDisplay';

export default function ProfilePage() {
  const { isAuthenticated } = useAuth();
  const { addNotification } = useNotifications();
  
  // Use our custom hook for fetching user data with caching
  const { 
    data: user, 
    isLoading: isUserLoading, 
    isError: isUserError,
    error: userError,
    refetch: refetchUser
  } = useCurrentUser({
    onError: (error) => {
      addNotification({
        type: 'error',
        title: 'Failed to load profile',
        message: error.message || 'An unexpected error occurred'
      });
    }
  });
  
  // Use our custom hook for updating user data with optimistic updates
  const { mutate: updateUser, isLoading: isUpdating } = useUpdateUser();
  
  // Fetch user activity logs with React Query
  const { 
    data: activityLogsData,
    isLoading: isActivityLogsLoading,
    isError: isActivityLogsError,
    error: activityLogsError,
    refetch: refetchActivityLogs
  } = useActivityLogs(
    { 
      user_id: user?.id,
      limit: 5 // Show only the 5 most recent activities
    },
    {
      enabled: !!user?.id, // Only fetch when we have a user ID
      onError: (error) => {
        addNotification({
          type: 'error',
          title: 'Failed to load activity logs',
          message: error.message || 'An unexpected error occurred'
        });
      }
    }
  );
  
  // Mock usage statistics data - in a real app, this would come from an API
  const usageStats = {
    auditLogsViewed: 247,
    policyValidations: 32,
    cliScansInitiated: 18
  };
  
  // Handle user profile updates with proper typing
  const handleUpdateUser = (userData: {
    first_name?: string;
    last_name?: string;
    email?: string;
    department?: string;
    profile_image?: string;
  }) => {
    updateUser(userData, {
      onSuccess: () => {
        addNotification({
          type: 'success',
          title: 'Profile updated',
          message: 'Your profile has been successfully updated.'
        });
      }
    });
  };
  
  if (!isAuthenticated) {
    return <ErrorDisplay message="User not found. Please login again." />;
  }
  
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">User Profile</h1>
      
      {/* User Profile Card */}
      <Card>
        {isUserLoading ? (
          <ProfileFormSkeleton />
        ) : isUserError ? (
          <ErrorDisplay 
            message={userError?.message || 'Failed to load profile'} 
            onRetry={() => refetchUser()}
          />
        ) : user ? (
          <ProfileForm 
            user={user}
            isUpdating={isUpdating}
            onUpdate={handleUpdateUser}
          />
        ) : null}
      </Card>

      {/* Recent Activity Card */}
      <ActivityLogList 
        isLoading={isUserLoading || isActivityLogsLoading}
        isError={isActivityLogsError}
        error={activityLogsError}
        onRetry={() => refetchActivityLogs()}
        logs={activityLogsData?.items}
        emptyMessage="No recent activity found."
      />
      
      {/* Usage Statistics Card */}
      <UsageStats 
        isLoading={isUserLoading}
        stats={usageStats}
      />
    </div>
  );
}
