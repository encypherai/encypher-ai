import React from 'react';
import Card from '@/components/ui/Card';

interface StatCardSkeletonProps {
  title?: string;
  className?: string;
}

/**
 * Skeleton loader for stat cards
 * Shows a loading animation while data is being fetched
 */
export default function StatCardSkeleton({ title = 'Loading...', className = '' }: StatCardSkeletonProps) {
  return (
    <Card title={title} className={`animate-pulse ${className}`}>
      <div className="flex flex-col items-center justify-center h-full p-4">
        <div className="h-10 w-20 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
        <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
      </div>
    </Card>
  );
}
