import React from 'react';
import Card from '@/components/ui/Card';

interface ChartSkeletonProps {
  title?: string;
  height?: string;
  className?: string;
}

/**
 * Skeleton loader for charts
 * Shows a loading animation while chart data is being fetched
 */
export default function ChartSkeleton({ 
  title = 'Loading Chart...', 
  height = 'h-64',
  className = '' 
}: ChartSkeletonProps) {
  return (
    <Card title={title} className={`animate-pulse ${className}`}>
      <div className={`${height} w-full p-4`}>
        <div className="flex items-center justify-center h-full w-full bg-gray-200 dark:bg-gray-700 rounded">
          <svg className="w-12 h-12 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
        </div>
      </div>
    </Card>
  );
}
