'use client';

import React from 'react';

interface SkeletonProps {
  className?: string;
  height?: string | number;
  width?: string | number;
  borderRadius?: string;
  animate?: boolean;
}

export default function Skeleton({
  className = '',
  height,
  width,
  borderRadius = '0.25rem',
  animate = true,
}: SkeletonProps) {
  const style: React.CSSProperties = {
    height: height,
    width: width,
    borderRadius: borderRadius,
  };

  return (
    <div
      className={`bg-gray-200 dark:bg-gray-700 ${
        animate ? 'animate-pulse' : ''
      } ${className}`}
      style={style}
      aria-hidden="true"
    />
  );
}

// Card Skeleton
export function CardSkeleton() {
  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-sm">
      <Skeleton height="1.5rem" width="50%" className="mb-4" />
      <Skeleton height="1rem" width="100%" className="mb-2" />
      <Skeleton height="1rem" width="90%" className="mb-2" />
      <Skeleton height="1rem" width="80%" className="mb-4" />
      <Skeleton height="2rem" width="30%" />
    </div>
  );
}

// Table Skeleton
export function TableSkeleton({ rows = 5, columns = 4 }) {
  return (
    <div className="w-full overflow-hidden border border-gray-200 dark:border-gray-700 rounded-lg">
      <div className="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex space-x-4">
          {Array(columns)
            .fill(0)
            .map((_, i) => (
              <Skeleton key={i} height="1.5rem" width={`${100 / columns - 5}%`} />
            ))}
        </div>
      </div>
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {Array(rows)
          .fill(0)
          .map((_, rowIndex) => (
            <div key={rowIndex} className="p-4">
              <div className="flex space-x-4">
                {Array(columns)
                  .fill(0)
                  .map((_, colIndex) => (
                    <Skeleton
                      key={colIndex}
                      height="1.25rem"
                      width={`${100 / columns - 5}%`}
                    />
                  ))}
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}

// Form Skeleton
export function FormSkeleton({ fields = 3 }) {
  return (
    <div className="space-y-6">
      {Array(fields)
        .fill(0)
        .map((_, i) => (
          <div key={i} className="space-y-1">
            <Skeleton height="1rem" width="30%" className="mb-1" />
            <Skeleton height="2.5rem" width="100%" />
          </div>
        ))}
      <Skeleton height="2.5rem" width="100%" />
    </div>
  );
}

// Profile Skeleton
export function ProfileSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Skeleton height="4rem" width="4rem" borderRadius="9999px" />
        <div className="space-y-2">
          <Skeleton height="1.5rem" width="10rem" />
          <Skeleton height="1rem" width="8rem" />
        </div>
      </div>
      <FormSkeleton fields={4} />
    </div>
  );
}

// Dashboard Stats Skeleton
export function StatsSkeleton({ count = 4 }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array(count)
        .fill(0)
        .map((_, i) => (
          <div
            key={i}
            className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700"
          >
            <Skeleton height="1.25rem" width="50%" className="mb-2" />
            <Skeleton height="2rem" width="70%" className="mb-4" />
            <Skeleton height="0.75rem" width="90%" />
          </div>
        ))}
    </div>
  );
}

// Activity Log Skeleton specifically designed for the timeline view in profile page
export function ActivityLogSkeleton({ count = 5 }) {
  return (
    <div className="flow-root">
      <ul className="-mb-8">
        {Array(count)
          .fill(0)
          .map((_, index) => (
            <li key={index}>
              <div className="relative pb-8">
                {index !== count - 1 && (
                  <span
                    className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200 dark:bg-gray-700"
                    aria-hidden="true"
                  />
                )}
                <div className="relative flex space-x-3">
                  <div>
                    <div className="relative px-1">
                      <div className="h-8 w-8 bg-gray-200 dark:bg-gray-700 rounded-full ring-8 ring-white dark:ring-gray-900 flex items-center justify-center animate-pulse">
                      </div>
                    </div>
                  </div>
                  <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                    <div className="space-y-1">
                      <Skeleton height="0.875rem" width={`${Math.random() * 30 + 50}%`} />
                      <Skeleton height="0.75rem" width={`${Math.random() * 40 + 40}%`} />
                    </div>
                    <div className="text-right">
                      <Skeleton height="0.75rem" width="5rem" />
                    </div>
                  </div>
                </div>
              </div>
            </li>
          ))}
      </ul>
    </div>
  );
}
