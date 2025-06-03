import React from 'react';
import { ProfileSkeleton } from '@/components/ui/Skeleton';
import Card from '@/components/ui/Card';

const ProfileFormSkeleton: React.FC = () => {
  return (
    <Card title="Profile Information">
      <div className="animate-pulse">
        <div className="flex items-center space-x-4 mb-6">
          <div className="h-16 w-16 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
          <div className="space-y-2">
            <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-3 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </div>
        
        <div className="space-y-6">
          <div className="space-y-1">
            <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-10 w-full bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
          
          <div className="space-y-1">
            <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-10 w-full bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
          
          <div className="space-y-1">
            <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-10 w-full bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
          
          <div className="space-y-1">
            <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-10 w-full bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
          
          <div className="flex space-x-3">
            <div className="h-10 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-10 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default ProfileFormSkeleton;
