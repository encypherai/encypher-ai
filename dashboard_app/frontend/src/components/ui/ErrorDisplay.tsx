import React from 'react';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import Button from './Button';

export interface ErrorDisplayProps {
  title?: string;
  message?: string;
  error?: Error;
  onRetry?: () => void;
  className?: string;
}

export default function ErrorDisplay({
  title = 'An error occurred',
  message,
  error,
  onRetry,
  className = '',
}: ErrorDisplayProps) {
  // Extract error message if error object is provided
  const errorMessage = error?.message || message || 'An unexpected error occurred';
  return (
    <div className={`rounded-md bg-red-50 dark:bg-red-900/30 p-4 ${className}`}>
      <div className="flex">
        <div className="flex-shrink-0">
          <ExclamationTriangleIcon className="h-5 w-5 text-red-400 dark:text-red-300" aria-hidden="true" />
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800 dark:text-red-200">{title}</h3>
          <div className="mt-2 text-sm text-red-700 dark:text-red-300">
            <p>{errorMessage}</p>
          </div>
          {onRetry && (
            <div className="mt-4">
              <Button
                variant="secondary"
                size="sm"
                onClick={onRetry}
              >
                Try again
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
